---
title: "第 5 章 TokenizerManager：请求的第一站"
---

# 第 5 章 TokenizerManager：请求的第一站

> 本章回答：`generate_request` 之后、调度器收到请求之前，发生了什么？TokenizerManager 如何维护每个请求的状态？流式输出如何从这里回到 HTTP 层？

## 5.1 职责与位置

TokenizerManager（下称 TM）运行在主进程，是 HTTP 层与 Scheduler 之间的翻译与状态保持者。`srt/managers/tokenizer_manager.py:854` 的 `generate_request` 是所有生成类请求的总入口：

```python
# srt/managers/tokenizer_manager.py:854（节选）
async def generate_request(
    self,
    obj: Union[GenerateReqInput, EmbeddingReqInput],
    request: Optional[fastapi.Request] = None,
):
    self.auto_create_handle_loop()
    ...
    self._init_req_state(obj, request)
    ...
    async with self.model_update_lock.reader_lock:
        await self._validate_and_resolve_lora(obj)
        # Tokenize the request and send it to the scheduler
        if obj.is_single:
            tokenized_obj = await self._tokenize_one_request(obj)
            state = self.rid_to_state[obj.rid]
            ...
            await self._send_one_request(tokenized_obj)
            async for response in self._wait_one_response(obj, request):
                yield response
        else:
            async for response in self._handle_batch_request(obj, request, request_rids):
                yield response
```

注意它是 **async generator**&#8203;：HTTP 层直接 `async for` 消费它，流式与非流式的差别只在消费方式（每个片段立刻写 SSE，或攒到最后一个片段）。

## 5.2 状态所有权

TM 维护 `rid_to_state`：每个请求在 TM 侧的状态（原始请求对象、输出缓冲、完成原因）。关键约定是&#8203;**状态生命周期对齐**&#8203;：请求从 `generate_request` 进入时创建状态，`_handle_batch_output` 或 abort 清理时删除；Scheduler 侧的 `Req` 对象是另一份独立状态，两份状态靠 `rid` 字符串对齐。第 12 章会看到这条约定上的一个已知竞态（health check 请求的状态早删）。

多模态请求在这一层走额外路径：图文请求会先生成 multimodal processor 任务（`srt/managers/multimodal_processor.py`），把图像/音频预处理嵌入请求对象后再发往调度器。

## 5.3 下行：发往调度器

`_send_one_request`（`tokenizer_manager.py:1680`）把 `TokenizedGenerateReqInput` 写入 ZMQ。消息携带调度所需的一切：`input_ids`、`sampling_params`、`rid`、多模态输入、会话与 LoRA 信息、PD 分离的 bootstrap 参数（`bootstrap_host/port/room`，为第 14 章埋下伏笔）。

## 5.4 上行：结果事件循环

TM 有一个常驻的 asyncio 任务 `handle_loop`（`tokenizer_manager.py:2332`）：

```python
# srt/managers/tokenizer_manager.py:2332
async def handle_loop(self):
    """The event loop that handles requests"""
    while True:
        with self.soft_watchdog.disable():
            recv_obj = await async_sock_recv(self.recv_from_detokenizer)
        if isinstance(
            recv_obj,
            (BatchStrOutput, BatchEmbeddingOutput, BatchTokenIDOutput),
        ):
            await self._handle_batch_output(recv_obj)
        else:
            self._result_dispatcher(recv_obj)
        self.last_receive_tstamp = real_time()
        self.soft_watchdog.feed()
```

控制流细节值得注意：`soft_watchdog.disable()` 包住的只有「收包」这一步——即循环闲等（没有请求流量）不会喂狗是&#8203;**正常**&#8203;的；喂狗发生在每次收到消息之后。若 Detokenizer 进程卡死、消息停止流动，且此时有在途请求，看门狗超时会把问题暴露出来。

`_handle_batch_output`（`:2347`）逐 rid 恢复状态、拼装 `meta_info`（prompt/completion tokens、cached_tokens、finish_reason、时间统计等），然后两条路：

- 请求在流式：唤醒对应的 `_wait_one_response` 等待者，把片段交给 HTTP 层；
- 非流式：攒齐所有片段，最后一个片段触发完成。

## 5.5 请求状态的时序图

::: mermaid
sequenceDiagram
    participant HTTP
    participant TM as TokenizerManager
    participant S as Scheduler

    HTTP->>TM: async for response
    TM->>TM: rid_to_state[rid] 创建
    TM->>TM: tokenize（含多模态预处理）
    TM->>S: ZMQ TokenizedGenerateReqInput
    loop 每个输出批次
        S->>TM: ZMQ BatchStrOutput / BatchTokenIDOutput
        TM->>TM: handle_loop 收包 → _handle_batch_output
        TM-->>HTTP: yield 片段（含 meta_info）
    end
    S->>TM: 终止片段（finished_reason）
    TM->>TM: 删除 rid_to_state[rid]
    TM-->>HTTP: 终止 yield
:::

失败路径：客户端断连（`request` 对象断开）时 TM 向 Scheduler 发 abort；请求等待期间服务端 flush cache、权重更新等运维操作由 `model_update_lock` 与 TM 的暂停条件（`is_pause_cond`，`tokenizer_manager.py:894`）串行化。

## 5.6 本章收束

- TM 是 async generator 形态的请求通道：tokenize → 发送 → 逐片段 yield，状态在 `rid_to_state`。
- 事件循环 `handle_loop` 的看门狗只在有消息流动时喂——它检测的是「有在途请求但消息流停止」的死锁，不是空闲。
- TM 与 Scheduler 各持请求状态副本，`rid` 是唯一对齐键；这个双份状态模型是理解 abort、retract（第 6 章）和流式重复输出防护（第 12 章）的基础。
- 下一章进入 Scheduler 子进程：请求抵达后最先面对它的是调度循环。
