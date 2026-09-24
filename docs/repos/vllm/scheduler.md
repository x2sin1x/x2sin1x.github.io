---
title: 调度器：token budget、连续批处理与抢占
weight: 60
---

# 调度器：token budget、连续批处理与抢占

> 本章回答：每个 engine step 里调度器如何决定"哪些请求、各推进多少 token"，显存不够时如何取舍，以及为什么源码里没有"prefill 批"和"decode 批"。

## 统一的 token 视角

`Scheduler.schedule()`（`vllm/v1/core/sched/scheduler.py:557`）开头有一段理解全章的注释（`:559`，源自作者 woosuk）：

> There's no "decoding phase" nor "prefill phase" in the scheduler. Each request just has the `num_computed_tokens` and `num_tokens_with_spec`. ... This is general enough to cover chunked prefills, prefix caching, speculative decoding.

调度器唯一的工作是：每步把每个请求的 `num_computed_tokens` 向 `num_tokens_with_spec` 推进若干位，推多少由两个预算约束决定：

- **token budget**：本步全局最多调度的 token 数（`max_num_scheduled_tokens`，`token_budget`，`scheduler.py:577`）；
- **input budget**：`scheduler_config.max_num_batched_tokens`，限制进入模型输入的总 token（含投机草稿槽位 `draft_slots`，`:579`–`:580`）。

对已 running 的请求，每步默认推进 `num_sampled_tokens_per_step` 个 token（decode 就是 1）；对 waiting 的新请求，则把剩余 prompt 一次性纳入，直到被 budget 截断——截断后的剩余部分成为 **chunked prefill**，后续步骤继续推进。运行中请求的单步截断还受 `long_prefill_token_threshold` 保护（`:612`），避免超长 prompt 饿死同批其他请求；当它兼容公平份额时还有自适应上限（`:620`）。

## schedule() 的两轮扫描

::: mermaid
flowchart TB
    A["schedule() 入口<br/>重置预算与统计"] --> B["第一轮：扫描 running<br/>decode 优先，按预算截断"]
    B --> C["第二轮：扫描 waiting<br/>前缀缓存查找 + 分配 KV block"]
    C -- "allocate_slots 成功" --> D["纳入本步批次"]
    C -- "分配失败" --> E["抢占：踢出 running 尾部请求<br/>释放块，重入 waiting"]
    E -- "腾出空间" --> C
    E -- "无可抢占" --> F["break：本请求留到下一步"]
    D --> G["产出 SchedulerOutput"]
    F --> G
:::

**第一轮扫 running**（`:626` 起）：对每个 running 请求计算 `num_new_tokens`，经过多重钳制（预算、`max_model_len`、Mamba 块对齐切分、prefill lookahead 预留），然后调用 `kv_cache_manager.allocate_slots()`（`vllm/v1/core/kv_cache_manager.py:371`）为新 token 分配 KV 块。

**第二轮扫 waiting**（`:881` 起）：队首请求先做前缀缓存查找——`num_computed_tokens == 0` 时调用 `_get_local_prefix_cache_hit()`（`:939`）得到可复用的块；随后同样走 `allocate_slots` 分配剩余部分。waiting 队列由 `request_queue.py` 抽象（`vllm/v1/core/sched/request_queue.py:20`），内置 FCFS 与优先级两种策略（`:13`）。

## 抢占：显存压力的出口

waiting 请求的 `allocate_slots` 返回 `None`（显存不足）时，调度器不会简单放弃，而是启动抢占循环（`scheduler.py:743` 起）：

```python
# The request cannot be scheduled.
# Preempt the lowest-priority request.
if self.policy == SchedulingPolicy.PRIORITY:
    preempted_req = max(
        self.running,
        key=lambda r: (r.priority, r.arrival_time),
    )
else:
    preempted_req = self.running[-1]
```

FCFS 策略下抢 running 队尾（最新进的请求），优先级策略下抢 `(priority, arrival_time)` 最大者。被抢占的请求经 `_preempt_request()`（`:1539`）处理：**释放全部 KV 块、`num_computed_tokens` 归零、状态置为 `PREEMPTED`、重入 waiting**——它将来会重新 prefill 全部序列（recompute-style 抢占）。这是一笔明确的交换：用重复计算换回显存，让批次维持高占用而不死锁。

## 每步产出的计划：SchedulerOutput

两轮扫描的结果是 `SchedulerOutput`（`vllm/v1/core/sched/output.py:232`）：`scheduled_new_reqs`、每请求的 `num_scheduled_tokens` 与块表增量、`scheduled_spec_decode_tokens`、结构化输出用的文法信息，以及 KV Connector 元数据。它是 EngineCore 与 Worker 之间唯一的"施工图纸"——Worker 不做任何调度决策，只照图执行。

执行完成后 `update_from_output()`（`scheduler.py:1967`）负责收账：把采样出的 token 追加进各请求、检查停止条件（`check_stop`，`sched/utils.py`）、更新 `num_computed_tokens`、组装 `EngineCoreOutputs`。schedule 与 update 是严格配对的资产负债表。

## 失败与边界

- token budget 为 0（`PauseState.PAUSED_ALL`，`:581`）时本步不调度任何请求——`pause_generation` API 的实现基础；
- Mamba 混合模型要求块对齐切分，可能产生无法调度的残留预算（`:701` 的注释列举了五种 `num_new_tokens == 0` 的原因）；
- 抢占也有底线：若 `_request_blocks_can_be_freed` 不允许（如 KV 正在被 connector 传输），抢占循环直接 break，宁可让新请求继续等待（`:770`）。

## 本章收束

- 调度器没有阶段概念，只有 `num_computed_tokens` 的推进——chunked prefill、前缀缓存、投机解码都是同一模型的自然结果；
- 双预算（token budget + input budget）决定每步规模；两轮扫描先保 running 再进 waiting；
- 显存不足的出口是抢占重算，牺牲重复计算换取批次不死锁。

下一章进入 KV Cache 层，看 `allocate_slots` 背后的块池与前缀缓存如何工作。
