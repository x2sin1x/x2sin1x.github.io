---
title: "第 7 章 PrefillAdder 与 chunked prefill"
---

# 第 7 章 PrefillAdder 与 chunked prefill

> 本章回答：一个 prefill 批是如何被「装」出来的？token 预算怎么算？chunked prefill 如何处理超长 prompt？前缀缓存在选批时扮演什么角色？

## 7.1 从等待队列到 prefill 批

`get_new_batch_prefill`（`srt/managers/scheduler.py:3804`）先做三道闸门：

- 等待队列为空且无 chunked_req → 直接返回 None；
- `get_num_allocatable_reqs`（`:3794`）综合 `req_to_token_pool.available_size()` 与 pipeline 并行预算，若 ≤ 0 且无 chunked_req → 置 `batch_is_full` 返回；
- 调 `policy.calc_priority` 按调度策略（默认 `fcfs`，可选 `lpm` 等）重排等待队列。

随后构造 **PrefillAdder**&#8203;（`srt/managers/schedule_policy.py:621`），把决定权交给它：

```python
# srt/managers/scheduler.py:3907 附近（节选）
adder = PrefillAdder(
    self.page_size,
    self.tree_cache,
    self.token_to_kv_pool_allocator,
    running_batch,
    self.new_token_ratio_tracker.current,
    self.max_prefill_tokens,
    chunked_prefill_size,
    running_bs if self.is_mixed_chunk else 0,
    ...
)
```

注意参数组合：PrefillAdder 拿到了&#8203;**页大小、radix 树、KV 分配器、当前 decode 批、新 token 比率**——它必须同时为「输入要算多少」与「输出预留多少」负责。

## 7.2 预算模型

`srt/managers/schedule_policy.py:1347` 的 `add_one_req` 对每个候选请求计算：

```python
# srt/managers/schedule_policy.py:1360 附近（节选）
max_new = min(
    max(req.sampling_params.max_new_tokens - len(req.output_ids), 0),
    CLIP_MAX_NEW_TOKENS,
)
cand_extend_input_len = len(req.full_untruncated_fill_ids) - len(
    req.prefix_indices
)
total_tokens = cand_extend_input_len + max_new + self.per_req_token_overhead
```

三个预算项的含义：

- **`rem_chunk_tokens`**&#8203;：本批 prefill 还能吃进多少输入 token（受 `max_prefill_tokens` 与 `chunked_prefill_size` 双重上限）；
- **`rem_total_tokens`**&#8203;（`:798` 的属性）：从 KV 池总量中扣除 decode 中请求的预留，再计入&#8203;**可淘汰部分**——radix 树中未被锁住的缓存 token 可以在需要时被 evict 换出，所以它们计入可用预算。这是前缀缓存与调度耦合最紧的一点：命中缓存既减少 `cand_extend_input_len`（省计算），也使「可淘汰空间」变大（改预算）；
- **`new_token_ratio`**&#8203;：为每个 decode 中请求预留的期望增长 token 数，随 `new_token_ratio_tracker` 衰减（第 6 章的 `decay_step`），retract 发生时上调。

`budget_state`（`:850`）把上述预算折算成 `AddReqResult.CONTINUE / OTHER / STOP` 的决策，驱动 `add_one_req` 循环在等待队列上装批。

## 7.3 chunked prefill

prompt 超过剩余预算时，请求被&#8203;**切块**&#8203;：本轮只 prefill 一个 chunk，对象存入 Scheduler 的 `chunked_req` 槽位，下一拍从上一轮断点继续（`srt/managers/scheduler.py:3660` 对 `self.chunked_req` 的处理，以及 `srt/managers/schedule_policy.py:1114` 的 `add_chunked_req`）。关键不变量（源码可直接看到）：

- `get_new_batch_prefill` 的队空检查在 `chunked_req is not None` 时失效——chunk 必须继续，否则请求挂死；
- 每个 chunk 的 KV 由 `cache_unfinished_req` 写回 radix 树（第 9 章），下一 chunk 用 `prefix_indices` 命中它继续，从而「切块」不等于「重算」；
- `get_next_batch_to_run` 中有专门的分支把 chunked_req 从「上一批并轨」中排除，避免它与已完成的请求混淆。

机制解释：chunked prefill 用「一个请求的 prefill 跨多拍」换来「单拍内 prefill 与 decode 的时间比可控」，代价是长 prompt 请求的 TTFT 变成多拍之和，以及每个 chunk 边界需要一次 KV 槽位续接与树锁切换。

## 7.4 主决策的时序

::: mermaid
flowchart TB
    W["waiting_queue（按策略排序）"] --> G{"batch_is_full 或队列空?"}
    G -->|否| C{"chunked_req 存在?"}
    C -->|是| A1["先装 chunked_req 剩余部分"]
    C -->|否| A2["逐个 add_one_req"]
    A1 --> B{"预算耗尽?<br/>rem_chunk_tokens / rem_total_tokens"}
    A2 --> B
    B -->|否| A2
    B -->|是或队列尽| O["can_run_list 即 prefill 批<br/>超长请求部分成为 chunked_req"]
    G -->|是| E["返回 None：本拍跑 decode"]
:::

## 7.5 失败边界

- **装批时发现放不下**&#8203;：`add_one_req` 返回拒绝，请求留在等待队列，不产生副作用（`_select_prefill_admission` 在真正分配前先做纸面核算，`schedule_policy.py:1380` 附近的注释：*Selection itself neither allocates slots nor materializes host hits*）；
- **真正的分配失败**&#8203;：分配发生在 `ScheduleBatch.prepare_for_extend` → `alloc_for_extend`（第 8 章），若此时分配器返回不足，调度器层面靠 retract 与重试兜底；
- **每个请求预留不足**&#8203;：预留按 `max_new_tokens` 上限与 CLIP 值截断（`CLIP_MAX_NEW_TOKENS`），若实际输出超过预留，留给 decode 阶段的 `check_decode_mem` 检查与 retract 机制（第 6 章）。

## 7.6 本章收束

- PrefillAdder 是「纸面预算器」：输入 token、输出预留、可淘汰缓存共同决定装谁、装多少。
- 前缀缓存命中同时改善计算量与预算两本账——这是 SGLang 调度与其他「先调度后查缓存」系统在结构上的差异点。
- chunked prefill 把超长 prompt 摊到多拍，`chunked_req` 是全调度器唯一的切块暂存槽，且拥有绕过队空检查的特权。
- 下一章看装批之后的形态转换：Req 如何变成 GPU 认识的 ForwardBatch。
