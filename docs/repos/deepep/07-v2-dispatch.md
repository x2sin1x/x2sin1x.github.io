---
title: "第 7 章 V2：dispatch 如何构造专家输入"
---

# 第 7 章 V2：dispatch 如何构造专家输入

> 本章沿一次 V2 前向路由追踪：top-k 元数据进入 `EPBuffer.dispatch` 后，kernel 如何写通信 buffer，接收计数如何决定输出尺寸，copy epilogue 又如何整理出专家可消费的张量。

## 7.1 输入契约与容量

`x` 可以是 BF16 token 矩阵，也可以是 FP8 数据与 scale factors 二元组。`topk_idx` 的形状为 `[tokens, topk]`，`-1` 表示该槽位无选择；`topk_weights` 可选。构造函数可通过 `num_max_tokens_per_rank`、`hidden`、`num_topk` 计算 buffer 尺寸，或由调用方显式给出 `num_bytes`（`deep_ep/buffers/ep.py:242-299,562-636`）。

未提供 `num_bytes` 时，构造函数按 MoE 参数调用 C++ 容量估算：

```python
if num_bytes is None:
    # NOTES: we allow `num_topk == 0`, as the buffer size can also be calculated by number of ranks (maybe bigger though)
    num_bytes = _C.calculate_ep_buffer_size(
        self.nccl_comm_handle.get(),
        num_max_tokens_per_rank, hidden, num_topk, use_fp8_dispatch,
        allow_hybrid_mode, allow_multiple_reduction)
```

API 还要求同一 EP group 对 capacity 有一致认知。对于未同步的 decode 路径，容量是预留上界，调用者必须使用 handle 中的有效 token 计数或前缀和界定真实数据范围，不能把 padding 区当成有效 token。

## 7.2 device kernel 产生布局元数据

Python 对齐参数、决定 SM/QP 数并解包缓存 handle 后，调用 C++ `runtime.dispatch`（`ep.py:638-680`）。C++ 路径检查 dtype、连续性、shape、top-k、expert 数与 SM 范围。GPU kernel 写入 workspace / communication buffer，同时生成接收端所需的计数、source metadata、slot index 等信息。

Python wrapper 将当前参数和从缓存 handle 解出的计数、布局 metadata 一起传给 C++ runtime：

```python
(cached_num_recv_tokens, cached_num_expanded_tokens,
 cached_num_recv_tokens_per_expert_list,
 cached_psum_num_recv_tokens_per_scaleup_rank, cached_psum_num_recv_tokens_per_expert,
 cached_num_unaligned_recv_tokens_per_expert,
 cached_dst_buffer_slot_idx,
 cached_token_metadata_at_forward,
 cached_recv_src_metadata,
 cached_channel_linked_list) = self._unpack_handle(handle)

result, event, deferred_epilogue = self.runtime.dispatch(
    x, sf, topk_idx, topk_weights,
    cumulative_local_expert_recv_stats,
    cached_num_recv_tokens,
    cached_num_expanded_tokens,
    cached_num_recv_tokens_per_expert_list,
    cached_psum_num_recv_tokens_per_scaleup_rank,
    cached_psum_num_recv_tokens_per_expert,
    cached_num_unaligned_recv_tokens_per_expert,
    cached_dst_buffer_slot_idx,
    cached_token_metadata_at_forward,
    cached_recv_src_metadata,
    cached_channel_linked_list,
    num_max_tokens_per_rank,
    num_experts, expert_alignment,
    num_sms, num_qps,
    previous_event,
    async_with_compute_stream, allocate_on_comm_stream,
    do_cpu_sync, do_expand,
    do_zero_padding,
    use_tma_aligned_col_major_sf,
    defer_epilogue)
```

host workspace 映射到 GPU，便于 CPU 读取接收计数。若 `do_cpu_sync=True`，C++ 会等到 rank/expert 计数准备就绪，再按确切接收 token 数分配输出；若关闭同步，则按 `num_max_tokens_per_rank * num_ranks` 的上界分配，并让后续 kernel 依赖 GPU 侧计数。两种选择分别是精确尺寸与避免 CPU 等待，不应混为同一返回语义（`csrc/buffers/ep.hpp:535-669`）。

关闭 CPU 同步时，输出空间按每个 rank 的最大 token capacity 预留；expanded 模式还要乘上每个 token 最多落入本 rank 的 expert 数：

```cpp
} else {
    // Non-cached mode without CPU sync, allocate with the worst case
    num_recv_tokens = num_max_tokens_per_rank * context->num_ranks;
    num_expanded_tokens = context->num_ranks * num_max_tokens_per_rank * std::min(num_topk, num_local_experts);
    num_expanded_tokens += (expert_alignment - 1) * num_local_experts;
    num_expanded_tokens = math::align(num_expanded_tokens, expert_alignment);
}
```

## 7.3 copy epilogue 将接收数据变成 expert layout

dispatch kernel 完成通信后，`launch_dispatch_copy_epilogue` 将通信 buffer 中的数据和元数据整理到 Python 返回的张量。若开启 `do_expand`，输出使用按 expert 展开的布局；`expert_alignment` 令每个 expert 的 token 段对齐，`do_zero_padding` 可将对齐空隙清零。FP8 scale factor 还可采用 TMA 对齐的列主序 stride（`ep.py:700-757`、`ep.hpp:671-743`）。

C++ epilogue 接收 buffer、workspace、接收张量、source metadata、expert 对齐及 expand/zero-padding 开关：

```cpp
launch_dispatch_copy_epilogue(context->buffer, context->workspace,
                              psum_num_recv_tokens_per_scaleup_rank.data_ptr<int>(),
                              psum_num_recv_tokens_per_expert.data_ptr<int>(),
                              recv_x.data_ptr(), recv_sf_ptr,
                              recv_topk_idx_ptr, recv_topk_weights_ptr,
                              recv_src_metadata.data_ptr<int>(),
                              channel_linked_list_ptr,
                              num_unaligned_recv_tokens_per_expert_ptr,
                              num_recv_tokens, num_max_tokens_per_rank,
                              num_hidden_bytes,
                              num_sf_packs, recv_sf_token_stride, recv_sf_hidden_stride,
                              num_experts, num_topk, expert_alignment,
                              context->scaleout_rank_idx, context->scaleup_rank_idx,
                              context->num_scaleout_ranks, context->num_scaleup_ranks,
                              jit->device.get_num_sms(),
                              jit->device.get_num_smem_bytes(),
                              num_channels,
                              do_expand, cached_mode,
                              do_zero_padding,
                              stream);
```

::: mermaid
flowchart LR
    A[topk_idx / topk_weights] --> B[dispatch kernel: route 与远端写入]
    X[x / FP8 scales] --> B
    B --> C[workspace: 计数 / source metadata]
    B --> D[通信 buffer: token payload]
    C --> E[CPU 等待或 GPU 计数路径]
    D --> F[copy epilogue]
    E --> F
    F --> G[按 rank 或 expert 整理的接收张量]
    F --> H[EPHandle: combine 所需的路由状态]
:::

## 7.4 扩展布局让通信结果对齐后续 GEMM

普通 layout 保留 `[received_tokens, hidden]` 加 top-k 元数据；expanded layout 可以把 token 按 expert 切分，每个 expert 对应连续片段，结合对齐填充后适配 grouped expert GEMM。V2 API 的 `expert_alignment`、`do_expand` 和 `do_zero_padding` 将这种下游布局选择显式暴露出来。

这里的工程取舍是让通信阶段承担一次 copy/排列成本，以换取专家矩阵乘可以按较规则的连续区间读取。是否值得取决于调用方 GEMM 的布局契约和 token 分布；源码注释列出 layout 能力，但没有给出跨框架、跨 workload 的普遍性能结论。

## 7.5 handle 的复用契约

返回的 `EPHandle` 保存接收计数、prefix sums、expert 对齐信息、目标 buffer slots、source metadata 和 channel linked list 等字段（`ep.py:34-203,401-418`）。再次调用 dispatch 时可以传入旧 handle 复用布局信息，但此时 `topk_idx` 必须为空，且 `num_experts`、alignment、capacity 要与 handle 一致；文档还声明 `topk_idx` 由引用保存在 handle 中，在使用完成前不可修改（`ep.py:593-663`）。

最终整理阶段从结果元组中取回 metadata，并创建或复用 `EPHandle`：

```python
# Create handle if not cached
nonlocal handle
is_cached_dispatch = handle is not None
handle = EPHandle(do_expand,
                  num_experts, expert_alignment,
                  num_max_tokens_per_rank,
                  num_sms,
                  topk_idx,
                  num_recv_tokens, num_expanded_tokens,
                  num_recv_tokens_per_expert_list,
                  psum_num_recv_tokens_per_scaleup_rank,
                  psum_num_recv_tokens_per_expert,
                  num_unaligned_recv_tokens_per_expert,
                  recv_src_metadata,
                  dst_buffer_slot_idx,
                  token_metadata_at_forward,
                  channel_linked_list) if handle is None else handle
```

## 本章收束

- dispatch 同时搬运 payload 与构造 combine 所需元数据。
- CPU 精确计数与 GPU 上界分配是两种不同路径，影响同步和结果尺寸。
- copy epilogue 将接收数据转换为 rank layout 或 expert-expanded layout。
- `EPHandle` 使后续 combine 和缓存 dispatch 有足够的路由上下文；其引用和容量约束必须遵守。
