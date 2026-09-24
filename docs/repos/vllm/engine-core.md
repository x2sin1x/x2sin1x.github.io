---
title: AsyncLLM 与 EngineCore：进程边界上的引擎
weight: 50
---

# AsyncLLM 与 EngineCore：进程边界上的引擎

> 本章回答：API 进程与 EngineCore 进程之间如何通信，EngineCore 的主循环每一步做什么，为什么 vLLM 要把调度放到独立进程。

## 为什么要有 EngineCore 进程

把调度与执行放进独立进程有三个直接收益：GPU 忙循环不再被 HTTP 事件循环打断；Python GIL 只约束单进程，API 进程的协议处理与 EngineCore 的调度真正并行；进程崩溃可被检测和隔离（`EngineCoreClient` 侧通过 ZMQ 死连接与消息校验发现，`vllm/v1/engine/core_client.py:543` 的 `validate_alive`）。

客户端侧有两个实现：`InprocClient`（`core_client.py:343`）在进程内直接调用 EngineCore（离线 `LLMEngine` 使用），`MPClient`（`:556`）通过 ZMQ 与子进程通信。二者之上是共享的 `BackgroundResources`（`:460`），持有 ZMQ context 与三条通道：input、output 与 shutdown。

::: mermaid
flowchart LR
    subgraph API["API 进程"]
        AL["AsyncLLM<br/>add_request / generate"]
        OH["output_handler 任务<br/>async_llm.py:791"]
        OP["OutputProcessor"]
    end
    subgraph EC["EngineCore 进程"]
        BL["run_busy_loop<br/>core.py:1470"]
        S["Scheduler"]
        X["Executor"]
    end
    AL -- "msgpack AddRequest" --> IQ["input 队列 (ZMQ)"] --> BL
    BL --> S --> X
    BL -- "EngineCoreOutputs" --> OQ["output 队列 (ZMQ)"] --> OH
    OH --> OP
:::

序列化使用 `msgspec.msgpack`（`core_client.py:19`），比 pickle 更快且是纯类型化编码——所有跨进程消息类型（`EngineCoreRequest`、`EngineCoreOutputs`、`SchedulerOutput`）都定义了完整类型注解。

## AsyncLLM 的三个并发角色

`AsyncLLM`（`vllm/v1/engine/async_llm.py:80`）内部有三个并发角色：

1. **请求侧协程**：`add_request()`（`:372`）渲染输入后把 `EngineCoreRequest` 放入 input 队列，同时为该请求创建一个 `RequestOutputCollector`（`vllm/v1/engine/output_processor.py:51`）——每个流式请求一个，`put()` 覆盖式写入、`get()` 消费（`:67`），这是背压设计：客户端消费慢只会丢中间增量，不会压垮引擎；
2. **output_handler 后台任务**：`_run_output_handler()`（`:791`）创建一个常驻 asyncio task，循环从 EngineCore 拉取 `EngineCoreOutputs`，分块调用 `OutputProcessor.process_outputs()`，把结果投递到对应请求的 collector，并处理 stop string 触发的补发 abort（`:851` 附近）；
3. **控制面方法**：`abort`、`pause_generation`、`start_profile` 等（`:874` 起）直接转发到 EngineCoreClient 的对应方法。

## EngineCore 的忙循环

EngineCore 子进程的入口是 `EngineCoreProc.run_engine_core()`（`vllm/v1/engine/core.py:1351`），它启动 `run_busy_loop()`（`:1470`）：

```python
def run_busy_loop(self):
    """Core busy loop of the EngineCore."""
    while self._handle_shutdown():
        # 1) Poll the input queue until there is work to do.
        self._process_input_queue()
        self._maybe_publish_request_counts()
        # 2) Step the engine core and return the outputs.
        self._process_engine_step()
        self._maybe_publish_request_counts()
```

`_process_input_queue()`（`:1496`）在没有待执行工作时阻塞等待新请求；一旦 `has_work()` 为真就停止收请求，进入 `_process_engine_step()`（`:1526`）。核心一步在 `EngineCore.step()`（`core.py:633`）：

```python
scheduler_output = self.scheduler.schedule(self._should_throttle_prefills())
future = self.model_executor.execute_model(scheduler_output, non_block=True)
grammar_output = self.scheduler.get_grammar_bitmask(scheduler_output)
model_output = future.result()
...
self._process_aborts_queue()
engine_core_outputs = self.scheduler.update_from_output(
    scheduler_output, model_output
)
```

注意两个细节：`execute_model` 与文法位掩码计算是**并发**的（在 GPU 执行前向的同时，CPU 端编译结构化输出的 bitmask）；abort 请求在模型执行期间到达时，会在消费输出之前被处理，避免为已取消请求浪费输出带宽。

EngineCore 初始化时最重要的动作之一是 `_initialize_kv_caches()`（`core.py:258`）：Worker 先探测各层的 KV 形状（`kv_cache_spec`），EngineCore 据此计算总块数并建立块池——这是调度器与 Worker 之间关于显存账本的"握手"。

## 请求在引擎内的表示

`Request`（`vllm/v1/request.py:60`）是调度器视角的请求：token id 列表、`status`（WAITING/RUNNING/PREEMPTED/FINISHED 等状态机）、`num_computed_tokens` 计数器、投机解码用的 `spec_token_ids`，以及用于前缀缓存的 `block_hasher` 回调。`EngineCore.preprocess_add_request()`（`core.py:1049`）从 `EngineCoreRequest` 构造它，并对结构化输出请求调用 `grammar_init`——文法编译是异步的，调度器在排程前会检查编译是否完成。

## 本章收束

- API 进程与 EngineCore 之间只有 msgpack 消息流：下行请求、上行输出，张量不出 Worker；
- `AsyncLLM` 用每请求 collector 实现流式背压，用单一 output_handler 任务集中处理输出；
- `run_busy_loop` 的每一步是"收请求 → schedule → 异步执行 → 收割输出 → update_from_output"，这一步语义在后面调度与模型执行章节反复出现。

下一章深入 `Scheduler.schedule()`——vLLM 最核心的决策逻辑。
