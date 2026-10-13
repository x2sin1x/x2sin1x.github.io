---
title: "第 8 章 V2：combine、句柄与异步重叠"
---

# 第 8 章 V2：combine、句柄与异步重叠

> 本章回答专家网络输出如何沿 dispatch 记录回到源 rank，以及 `EventOverlap`、deferred epilogue 与 Tensor 引用怎样共同定义异步边界。

## 8.1 combine 沿 handle 反向聚合

调用方将专家计算结果 `x` 和 dispatch 返回的 `EPHandle` 传给 `EPBuffer.combine`。Python 从 handle 读取路由 metadata，再调用 `runtime.combine`；C++ 验证 `x`、top-k、source metadata、prefix sums 和可选 bias 的设备、类型与 shape，随后调用 `launch_combine`（`ep.py:770-844`；`csrc/buffers/ep.hpp:790-915`）。

Python wrapper 直接从 `EPHandle` 取出反向路由所需的元数据，交给 C++ runtime：

```python
num_sms = handle.num_sms if num_sms == 0 else align(num_sms, 2)
num_qps = self.get_theoretical_num_qps(num_sms) if num_qps == 0 else num_qps
assert num_qps <= self.num_allocated_qps, f'Allocated QPs are not enough'

bias_0, bias_1 = EPBuffer._unpack_bias(bias)
result, event, deferred_epilogue = self.runtime.combine(x, topk_weights,
                                                        bias_0, bias_1,
                                                        handle.recv_src_metadata,
                                                        handle.topk_idx,
                                                        handle.psum_num_recv_tokens_per_scaleup_rank,
                                                        handle.token_metadata_at_forward,
                                                        handle.channel_linked_list,
                                                        handle.num_experts,
                                                        handle.num_max_tokens_per_rank,
                                                        num_sms, num_qps,
                                                        previous_event,
                                                        async_with_compute_stream,
                                                        allocate_on_comm_stream,
                                                        handle.do_expand,
                                                        defer_epilogue)
```

在 scale-out 多域时，combine kernel 需要 dispatch 阶段保留的 token metadata 与 channel linked list；单 scale-out 场景则直接使用来源 metadata 和 scale-up 前缀和。combine epilogue 将结果写到原 rank，并可融合 bias 或 gate 权重相关归约（`combine.hpp:24-135`）。具体融合能力取决于调用参数与布局选项。

launch wrapper 根据 scale-out domain 选择普通或 hybrid combine specialization；前者使用 scale-up rank index，后者还传入 forward token metadata 和 channel linked list：

```cpp
if (num_scaleout_ranks == 1) {
    jit->launch(
        kernel, options,
        static_cast<nv_bfloat16*>(x), static_cast<float*>(topk_weights),
        src_metadata, psum_num_recv_tokens_per_scaleup_rank,
        nccl_dev_comm, nccl_window,
        buffer, workspace,
        scaleup_rank_idx,
        num_reduced_tokens
    );
} else {
    jit->launch(
        kernel, options,
        static_cast<nv_bfloat16*>(x), static_cast<float*>(topk_weights),
        src_metadata,
        psum_num_recv_tokens_per_scaleup_rank,
        token_metadata_at_forward,
        channel_linked_list,
        nccl_dev_comm, nccl_window,
        buffer, workspace,
        scaleout_rank_idx, scaleup_rank_idx,
        num_reduced_tokens
    );
}
```

## 8.2 compute stream 与 communication stream

V2 API 提供 `previous_event`、`async_with_compute_stream`、`allocate_on_comm_stream` 等控制。调用方可让通信 stream 等待一个先前 event，也可不让当前 compute stream 阻塞；若内存分配安排在通信 stream，相关张量的所有权记录也要与该 stream 的执行次序相符（`ep.py:607-624`）。

`EventOverlap` 包装 CUDA event 和可延迟执行的 callback。默认 `current_stream_wait()` 让当前 stream 等待通信 event；若存在 deferred callback，它会在等待后完成 CPU-side epilogue 并产生最终 dispatch 结果（`deep_ep/utils/event.py` 与 `ep.py:702-757`）。这意味着“kernel 已发起”不等于“最终接收张量已可用”。

等待方法先等待底层 event，再执行注册的 hook；可选的 `release_handle` 才会清除 event 引用：

```python
assert self.event is not None
self.event.current_stream_wait()

# Call epilogue hook
result = None
if self.hook_after_wait is not None:
    result = self.hook_after_wait()
    self.hook_after_wait = None

if release_handle:
    self.event = None
return result
```

## 8.3 Deferred epilogue 延后何事

设置 `defer_epilogue=True` 必须同时设置 `async_with_compute_stream=True`。此时 dispatch 返回的是 `EventOverlap`，而不是立即返回接收张量和 handle；调用方等待 event 时才执行接收计数等待与 copy epilogue，再取得输出（`ep.py:623-636,702-757`）。这给调用方提供了将其他 compute 插入通信间隙的机会，也要求下游代码延后消费结果。

当 C++ runtime 返回 deferred callback 时，Python 将它挂到 event 上；只有 wait hook 运行后才会调用 `finalize_dispatch` 生成接收张量和 handle：

```python
if deferred_epilogue is not None:
    event_overlap.register_hook_after_wait(
        lambda: finalize_dispatch(deferred_epilogue(), False))
    return event_overlap

# Do epilogue ASAP
assert result is not None
return *finalize_dispatch(result, async_with_compute_stream), event_overlap
```

**注意区别**：Deferred 是 API 对结果整理阶段的延后；是否能够在目标 GPU、网络和 workload 上获得有用的通信计算重叠，需要 runtime 执行与 profiling 验证。源码暴露控制点，不等于自动保证重叠收益。

## 8.4 Tensor 生命周期由事件与记录共同维护

C++ 在异步返回时收集本次操作涉及的 Tensor，供 Python 包装器记录其生命周期，避免用户变量先离开作用域、GPU 尚未读完数据。dispatch 的 handle 还保留 top-k Tensor 引用，API 明确禁止在 handle 被使用期间修改其内容（`ep.py:593-596`）。

取消或异常路径方面，当前源码主要依靠 CUDA event、超时和异常抛出；没有看到将单次 EP 操作回滚成可重试事务的机制。因此，应用侧应按 CUDA stream 顺序管理事件，遇到异步失败时按进程/通信组的故障处理策略处理。

## 本章收束

- combine 依赖 dispatch handle，而不是重新运行 router 来猜测 token 来源。
- `EventOverlap` 表示依赖与延后动作；得到 event 对象并不代表最终 Tensor 已经准备好。
- deferred epilogue 给异步流水更多调度空间，也把等待和结果消费责任交给调用者。
- 第 9 章解释 buffer 容量和布局元数据为什么是这些异步路径的前提。
