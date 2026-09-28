---
title: "第 12 章 结果处理与 Detokenizer"
---

# 第 12 章 结果处理与 Detokenizer

> 本章回答：采样出的 token id 如何变成流式文本？增量反分词解决什么问题？stop 字符串、finish_reason 在哪里处理？overlap 造成的重复输出如何防住？

## 12.1 三段输出链

输出侧经过三个处理站，与第 5 章的输入链对称：

1. **Scheduler 内**&#8203;：`process_batch_result`（`srt/managers/scheduler.py:4765`）分派到 `batch_result_processor.process_batch_result_decode/prefill`（`srt/managers/scheduler_components/batch_result_processor.py:921`），把 token id 写进 `req.output_ids`、判定完成状态、触发 KV 写回；
2. **流式化**&#8203;：`output_streamer.stream_output`（`srt/managers/scheduler_components/output_streamer.py:119`）按 `stream_interval` 攒批，组装 `BatchTokenIDOutput` 发往 Detokenizer；
3. **Detokenizer 进程**&#8203;：增量反分词成文本，`BatchStrOutput` 回流 TokenizerManager（第 5 章 `handle_loop`）。

::: mermaid
flowchart LR
    S1["process_batch_result<br/>(scheduler.py:4765)"] --> S2["output_streamer<br/>(output_streamer.py:119)"]
    S2 -->|"ZMQ BatchTokenIDOutput"| D["DetokenizerManager<br/>(detokenizer_manager.py:179)"]
    D -->|"ZMQ BatchStrOutput"| T["TokenizerManager<br/>_handle_batch_output"]
    T --> HTTP["HTTP 层 yield"]
:::

## 12.2 process_batch_result：账本结算

decode 路径的结算逻辑（`batch_result_processor.py:921` 起）按序处理：

- `result.copy_done.synchronize()`：等 GPU→CPU 拷贝事件（overlap 下该拷贝与前向流并行）；
- 逐请求写 `next_token_id` 进 `req.output_ids`，检查 EOS/stop token/长度上限，落 `finished_reason`；
- overlap 分支特别防御（`:994` 附近）：`if (self.enable_overlap ...) and (req.finished() or req.is_retracted): continue`——注释原文解释：overlap 下一个请求可能多输出一次并在这里命中两次，这个 continue 防止 dummy 输出；
- 完成/中途均调用 `maybe_cache_unfinished_req`（`:383`）把 KV 写回 radix 树（第 9 章）。

prefill 路径（`process_batch_result_prefill`）多做一件事：从 logits 中提取 `return_logprob` 需要的 prompt 部分 logprobs，然后同样走流式化。

## 12.3 stream_output：攒批与切片

`srt/managers/scheduler_components/output_streamer.py:119` 的 `stream_output` 用 `_GenerationStreamAccumulator` 收集本批要外发的片段。频率由两层间隔控制（`output_streamer.py` 构造参数）：`stream_interval`（默认 1，`srt/arg_groups/fields/serving.py:255`——按 token 长度的流式间隔）与 `DEFAULT_FORCE_STREAM_INTERVAL`（无论快慢，攒到阈值必须外发一次，防止长输出请求一直不发流）。聚合后 `send_to_detokenizer.send_output(payload)` 发出，或直推 Rust server（`self.rust_server.push_generation(payload)`，`:214` 分支——Rust server 模式下 detokenizer 由 Rust 侧接管）。

## 12.4 增量反分词

DetokenizerManager（`srt/managers/detokenizer_manager.py:102`）的事件循环极简（`:179`）：

```python
# srt/managers/detokenizer_manager.py:179（节选）
def event_loop(self):
    """The event loop that handles requests"""
    while True:
        with self.soft_watchdog.disable():
            recv_obj = sock_recv(self.recv_from_scheduler)
        output = self._request_dispatcher(recv_obj)
        if output is not None:
            sock_send(self.send_to_tokenizer, output)
        self.soft_watchdog.feed()
```

反分词的核心难点：&#8203;**token 边界 ≠ 字符边界**&#8203;。一个 UTF-8 字符可能被切成多个 token，新 token 到达前无法确定上一段文本是否已经「封口」。`detokenizer_manager.py:79` 起的 `DecodeStatus` 结构用 `decode_ids` / `read_offset` / `surr_offset` 维护每个请求的解码游标；`_decode_batch_token_id_output`（`:303`）按游标解码，把「确定段」发出、「疑似尾部」留待下批。`trim_matched_stop`（`:189`）在文本/整流上做 stop 字符串裁剪：匹配到 stop 串时按 `no_stop_trim` 决定保留还是剔除，stop token（int 型）则直接去掉最后一个 token。

vocab 越界防御：`_clamp_decode_ids`（`:226`）把超过 vocab_size 的 id 钳到合法范围，防御性处理越界 id 的崩溃。

## 12.5 完整回程时序

::: mermaid
sequenceDiagram
    participant MR as ModelRunner
    participant S as Scheduler
    participant DS as Detokenizer
    participant TM as TokenizerManager
    MR-->>S: next_token_ids（GPU→CPU）
    S->>S: process_batch_result：output_ids/finish/KV 写回
    S->>DS: BatchTokenIDOutput（按 stream_interval）
    DS->>DS: 增量反分词 + trim stop
    DS->>TM: BatchStrOutput
    TM->>TM: meta_info 组装（cached_tokens、finish_reason…）
    TM-->>TM: 唤醒 generate_request 的 yield
:::

## 12.6 输出侧的失败边界

- **重复输出**&#8203;：overlap 双发由 `process_batch_result_decode` 的 finished 检查拦截（12.2）；
- **请求被 retract 后又完成**&#8203;：`req.is_retracted` 与 finished 一并检查，避免收回请求吃进脏 token；
- **TM 侧状态已删**&#8203;：`_handle_batch_output` 中 `rid` 查不到状态时警告并丢弃（`srt/managers/tokenizer_manager.py:2369`），health check 请求有专门的静默分支——源码注释承认这是已知竞态；
- **Detokenizer 卡死**&#8203;：事件循环的 `soft_watchdog` 检测消息流停滞（与第 5 章 TM 的狗对称）。

## 12.7 本章收束

- 输出链三站：结算（token → output_ids + finish + KV 写回）、攒批（stream_interval + 强制间隔）、反分词（游标式增量解码）。
- 增量反分词的状态（decode_ids/read_offset/surr_offset）是「token 与字符边界不对齐」这一问题的最小解。
- overlap 的输出侧代价是重复输出风险，用 finished 检查显式防住；这与第 6 章的张量保活、第 11 章的延迟采样构成 overlap 代价的完整清单。
- 至此黄金路径全部走完；第四部分转向「一个进程装不下」之后的并行、分离与路由。
