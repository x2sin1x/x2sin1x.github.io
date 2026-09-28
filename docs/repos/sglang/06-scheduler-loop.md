---
title: "第 6 章 Scheduler 主循环与重叠调度"
---

# 第 6 章 Scheduler 主循环与重叠调度

> 本章回答：Scheduler 每一拍做什么？「下一个 batch 是 prefill 还是 decode」如何决定？KV 池耗尽时发生了什么（retract）？overlap 调度重叠的是什么？

## 6.1 两种事件循环

Scheduler 是本书最核心的一个类（`srt/managers/scheduler.py:436` 起，单文件 6100+ 行）。它有两个主循环实现，按启动参数择一运行：

**普通循环**&#8203;（`srt/managers/scheduler.py:1906`）：

```python
# srt/managers/scheduler.py:1906（节选）
def event_loop_normal(self):
    """A normal scheduler loop."""
    while True:
        ...
        # Receive requests
        self.ingest_requests()
        ...
        # Get the next batch to run
        plan = self.get_next_batch_to_run(
            running_batch=self.running_batch, last_batch=self.last_batch
        )
        self.running_batch = plan.running_batch
        batch = plan.batch_to_run
        ...
        # Launch the current batch
        if batch:
            result = self.run_batch(batch)
            self.process_batch_result(batch, result)
        else:
            # When the server is idle, do self-check and re-init some states.
            self._sched_idled = True
            self.on_idle()
        # Update last_batch
        self.last_batch = batch
```

每一拍四个动作：收请求 → 选批 → 执行 → 处理结果。&#8203;**同步串行**&#8203;：处理第 N 批结果时 GPU 空转。

**重叠循环**&#8203;（`srt/managers/scheduler.py:1941` 的 `event_loop_overlap`）把「处理上一批结果」与「跑这一批前向」交错：`run_batch` 的结果进 `result_queue`，下一拍再 `pop_and_process()`。GPU 一次前向 10ms 量级、CPU 调度若干毫秒，重叠后 CPU 工作藏进 GPU 计算窗口。代价是第 12 章将看到的「请求可能多产生一个 token 再回退」与本章稍后的一套张量生命周期保全机制。这是 SGLang 源码可见的默认选择（`enable_overlap`），从循环代码中 `self.enable_overlap` 分支的存在即可证实两条路径并存。

## 6.2 选批：get_next_batch_to_run

`srt/managers/scheduler.py:3641` 的 `get_next_batch_to_run` 是调度决策的汇总点，优先级如下：

1. **收尾上一批**&#8203;：若上一批是 extend，`filter_batch` 去掉已完成的请求，把幸存者并入 `running_batch`（正在 decode 的批次）；
2. **尝试组新 prefill 批**&#8203;：`get_new_batch_prefill`（下一章详述）；
3. **有 prefill 就先跑 prefill**&#8203;（`new_batch is not None` → `ret = new_batch`）；
4. **否则推进 decode**&#8203;：`update_running_batch`。

即 **prefill 优先于 decode**&#8203;。机制解释：新请求的 TTFT（首 token 延迟）由 prefill 决定，而 decode 每步只生成一个 token、可暂停一拍而不产生可见后果；prefill 挤占 decode 一拍的成本是所有 decode 请求该步延后，这个不对称性是「prefill 优先」的直接依据。但纯 prefill 优先会饿死 decode——第 7 章的 `chunked_prefill_size` 就是给 prefill 批设置上限、把 GPU 时间还给 decode 的约束。

## 6.3 decode 批的维护与 retract

`srt/managers/scheduler.py:4191` 的 `update_running_batch` 维护 decode 批，核心分支是&#8203;**内存压力检查**&#8203;：

```python
# srt/managers/scheduler.py:4191（节选）
# Check if decode out of memory
if (kv_full_retract_flag := not batch.check_decode_mem()) or (...):
    ...
    retracted_reqs, new_token_ratio, reqs_to_abort = batch.retract_decode()
    ...
    for req in retracted_reqs:
        self._add_request_to_queue(req, is_retracted=True)
else:
    self.new_token_ratio_tracker.decay_step()
```

KV 池放不下「所有在跑序列再加各自下一个 token」时，触发 **retract（收回）**&#8203;：`batch.retract_decode()`（`srt/managers/schedule_batch.py:3291`）按策略（`retraction_policy` 默认 `"length"`：收回短输出长输入的请求，`srt/arg_groups/fields/schedule.py:118`）挑出部分请求，释放它们的 KV 槽位，把它们&#8203;**放回等待队列**&#8203;，从头重新 prefill。被收回请求已生成的 `output_ids` 保留，重算时 RadixCache 若还持有其前缀可减少重算量（依赖缓存未被淘汰，属可推断而非保证）。

成功路径的收尾是 `batch.prepare_for_decode()`（`srt/managers/schedule_batch.py:3551`）：为每条序列的下一个 token 分配 KV 槽位、更新 seq_lens 张量。

## 6.4 状态机视角

一条请求在 Scheduler 内的生命周期可以概括为：

::: mermaid
stateDiagram-v2
    [*] --> waiting: 收到 TokenizedGenerateReqInput
    waiting --> prefill: PrefillAdder 接纳（预算允许）
    prefill --> decoding: prefill 完成，进入 decode 批
    decoding --> decoding: 每拍生成一个 token
    decoding --> waiting: retract（KV 池不足）
    prefill --> prefill: chunked prefill 未完成（留在 chunked_req）
    decoding --> finished: EOS / stop / max_tokens / abort
    finished --> [*]
:::

状态所有权说明：`waiting_queue` 是 Scheduler 的等待列表；`chunked_req` 是「prefill 被切块、剩余部分下一拍继续」的暂存槽（每拍至多一个，见第 7 章）；`running_batch` 是 decode 中集合。三个容器互斥持有每条请求。

## 6.5 overlap 模式的张量安全

重叠循环有一套源码注释明确的保全机制（`srt/managers/scheduler.py:4278` 的 `record_batch_in_overlap` 与 `:4294` 的 `_forward_isolation`）：

- `record_batch_in_overlap` 把整批张量「钉住」两个迭代（双缓冲 `batch_record_buf`），防止前向流还在读的 GPU 张量被 PyTorch 的垃圾回收提前释放——注释原话：*hacky way to keep a reference to avoid GPU tensors being freed by torch GC*；
- `_forward_isolation` 在前向前快照 `ScheduleBatch` 字段、前向后恢复，使投机解码 V2 在前向中途改写字段（forward_mode / input_ids / seq_lens）成为可回滚操作；
- `future_map`（`:1632` 创建）管理 overlap 下「本批的输出 token 要到下一拍才在 CPU 可见」的&#8203;**未来 token 槽位**&#8203;：`resolve_seq_lens_cpu` 在调度时用未来值替换真实 seq_len，前向完成后 `publish` 落账。

这组机制是「overlap 收益」的账单：每一次 CPU/GPU 重叠都以额外的快照、引用保活和延迟可见性为代价。

## 6.6 本章收束

- 每拍四动作：收请求、选批、执行、处理结果；overlap 模式用结果队列把「处理结果」推迟一拍以重叠 GPU 计算。
- 调度优先级：清尾 → prefill 优先 → decode 兜底；chunked prefill 是 prefill 优先策略的安全阀。
- KV 池耗尽触发 retract：请求被收回等待队列重新排队，这是一切「服务在过载下仍不崩溃」行为的基础。
- overlap 的代价被显式写在代码里：双缓冲保活、前向快照、未来槽位发布。
- 下一章进入选批的正面战场：PrefillAdder 如何把等待队列变成一个 prefill 批。
