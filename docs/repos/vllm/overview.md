---
title: 定位与总体架构
weight: 20
---

# 定位与总体架构

> 本章回答：vLLM 解决什么问题、由哪些进程与组件构成、一次推理请求如何穿过整个系统。它是后续所有章节的地图。

## LLM 服务的核心矛盾

LLM 推理的算力成本可以摊薄，但**显存容量**无法：每个请求都要为 KV Cache 预留一段随序列长度线性增长、且在生成结束前不能被别人占用的显存。传统实现按"最长可能序列"连续预留，实际利用率常常不到两成——碎片和预留浪费把并发度卡在个位数。

vLLM 的回答是 **PagedAttention**：把每个请求的 KV Cache 切成固定大小的 block（如 16 个 token 一块），按需分配、用完即还，由一个全局块池统一调度。配合**连续批处理**（请求随到随进、随完随走）与**前缀缓存**（相同前缀共享 block），vLLM 把吞吐量从"能不能跑"的问题变成了"调度做得好不好"的问题。

## V1 引擎的进程模型

快照中的 vLLM 只有 V1 引擎（V0 已删除）。它的静态结构是一个三层进程树：

::: mermaid
flowchart TB
    C["客户端<br/>HTTP / WebSocket / Python"] --> API["API 进程<br/>FastAPI 路由 + AsyncLLM + OutputProcessor"]
    API -- "ZMQ + msgpack<br/>EngineCoreRequest" --> EC["EngineCore 进程<br/>Scheduler + 结构化输出"]
    EC -- "ZMQ<br/>EngineCoreOutputs" --> API
    EC -- "execute_model<br/>(进程内 / 子进程 / Ray)" --> W["Worker 进程（每 GPU 一个）<br/>GPUModelRunner + 模型 + KV Cache"]
    W -- "ModelRunnerOutput" --> EC
:::

各层职责用一句话说清：

- **API 进程**：协议解析、tokenizer 渲染（`renderers/`）、流式输出分发。它**不持有任何 GPU 资源**，因此可以水平扩展（`--api-server-count`）。
- **EngineCore 进程**（`vllm/v1/engine/core.py:111`）：全局唯一的调度大脑，持有 Scheduler、KV Cache 元数据和结构化输出管理器，每步产出 `SchedulerOutput` 并消费 `ModelRunnerOutput`。
- **Worker 进程**（`vllm/v1/worker/gpu_worker.py:183`）：每个 GPU 一个，持有真正的模型权重与 KV Cache 张量，执行前向计算。

进程间只有两条消息通道：下行 `EngineCoreRequest`/`SchedulerOutput`（msgspec.msgpack 序列化，`vllm/v1/engine/core_client.py:20`），上行 `EngineCoreOutputs`。张量从不跨 EngineCore↔API 进程边界——只有 token id 和统计信息。

## 一次请求的完整生命周期

以 `/v1/chat/completions` 为例，黄金路径一共九跳：

::: mermaid
sequenceDiagram
    participant C as 客户端
    participant A as API 进程
    participant E as EngineCore 进程
    participant W as Worker / GPU
    C->>A: POST /v1/chat/completions
    A->>A: 渲染 prompt + 多模态预处理
    A->>E: add_request(EngineCoreRequest)
    E->>E: Request 构造 + 文法编译
    loop 每个 engine step
        E->>E: scheduler.schedule() → SchedulerOutput
        E->>W: executor.execute_model()
        W->>W: _update_states → 前向 → 采样
        W-->>E: ModelRunnerOutput
        E->>E: scheduler.update_from_output()
    end
    E-->>A: EngineCoreOutputs（ZMQ）
    A->>A: OutputProcessor + 增量反词元化
    A-->>C: SSE 流式 delta
:::

1. **入口**：`vllm serve` 启动 FastAPI 应用，路由处理函数调用 `AsyncLLM.generate()`（`vllm/v1/engine/async_llm.py:664`）；
2. **跨进程下发**：`AsyncLLM.add_request()`（`async_llm.py:372`）把请求封装后放入 ZMQ input 队列；
3. **EngineCore 收请求**：`EngineCore.preprocess_add_request()`（`vllm/v1/engine/core.py:1049`）构造内部 `Request` 对象（`vllm/v1/request.py:60`），结构化输出在此时异步编译文法；
4. **调度**：`Scheduler.schedule()`（`vllm/v1/core/sched/scheduler.py:557`）在 token budget 内为 running/waiting 请求分配 KV block，产出 `SchedulerOutput`（`vllm/v1/core/sched/output.py:232`）；
5. **执行**：`EngineCore.step()`（`core.py:633`）把 `SchedulerOutput` 交给执行器；Worker 侧 `GPUModelRunner.execute_model()`（`vllm/v1/worker/gpu_model_runner.py:4149`）维护持久批次、构建 attention metadata 并运行前向；
6. **采样**：`Sampler.forward()`（`vllm/v1/sample/sampler.py:72`）完成温度、惩罚、logits 处理器与采样；
7. **回传**：`Scheduler.update_from_output()`（`scheduler.py:1967`）更新请求状态、检测停止条件，产出 `EngineCoreOutputs`；
8. **流式恢复**：API 进程的 `output_handler` 后台任务（`async_llm.py:791`）拉取输出，`OutputProcessor`（`vllm/v1/engine/output_processor.py:464`）做增量反词元化并投递到每请求的流队列；
9. **协议输出**：路由处理函数把 delta 包装成 SSE 事件发回客户端。

这个九跳链条就是本系列的主线：第 4 章展开第 1–3 跳，第 5–8 章逐个深入第 4–7 跳的每个组件。

## 三个最有辨识度的机制

**PagedAttention 与块池**。KV Cache 按 block 分配，`KVCacheManager`（`vllm/v1/core/kv_cache_manager.py:131`）在每步调度时调用 `get_computed_blocks()` 找已缓存前缀、`allocate_slots()` 分配新块。块用 `BlockHash` 作内容寻址键，天然支持前缀共享与 LRU 淘汰。

**统一的 token 视角调度**。源码里有一段关键注释（`scheduler.py:559`）：调度器没有"prefill 阶段"与"decode 阶段"之分——每个请求只有 `num_computed_tokens` 和 `num_tokens_with_spec` 两个计数器，每步调度器把 `num_computed_tokens` 往前推。这一个模型同时表达了 chunked prefill、前缀缓存命中和投机解码，是理解调度器的钥匙。

**进程边界即信任边界**。Scheduler 状态只在 EngineCore 进程存在，模型与 KV 张量只在 Worker 进程存在；任何一端崩溃都可以被检测（`EngineCoreClient` 的 ZMQ 心跳与 `BackgroundResources`，`core_client.py:460`）而不会半死不活。

## 本章收束

- vLLM 用 PagedAttention 把"显存够不够"转化为"块分配算法"，这是它所有调度能力的物质基础；
- V1 引擎是三层进程树：API 无 GPU 状态、EngineCore 独占调度、Worker 独占执行；
- 一次请求依次穿过入口渲染 → 跨进程下发 → 调度 → 执行 → 采样 → 流式恢复九跳。

下一章先给出整个仓库的地图，把上面提到的模块放进各自的目录与依赖方向里。
