---
title: "第 4 章 V1：布局、dispatch 与 combine"
weight: 40
---

# 第 4 章 V1：布局、dispatch 与 combine

> 本章回答：V1 如何把 top-k expert 索引映射成需要发送的数据，并用返回的 handle 把 expert 输出送回原 rank？

## 4.1 布局是 dispatch 的显式输入

`get_dispatch_layout(topk_idx, num_experts)` 计算四类后续计划：每个 rank 的 token 数、每个 RDMA rank 的 token 数、每个 expert 的 token 数，以及布尔矩阵 `is_token_in_rank`（V1 `deep_ep/buffer.py:276-302`）。这些数据允许调用方检查路由，也允许单独缓存布局并复用于后续通信。

Python 层将这些返回值从 C++ runtime 透传，并将 event 包装为 `EventOverlap`：

```python
num_tokens_per_rank, num_tokens_per_rdma_rank, num_tokens_per_expert, is_token_in_rank, event = \
    self.runtime.get_dispatch_layout(topk_idx, num_experts, getattr(previous_event, 'event', None),
                                     async_finish, allocate_on_comm_stream)
return num_tokens_per_rank, num_tokens_per_rdma_rank, num_tokens_per_expert, is_token_in_rank, EventOverlap(event)
```

V1 的普通 `dispatch` 要求调用者提供这些 layout 数据以及 `topk_idx` / `topk_weights`。Python 按 `runtime.get_num_rdma_ranks() > 1` 选 internode 分支，否则走 intranode 分支；首次 dispatch 将 kernel 产生的前缀和、source index、发送 head 等元数据打包成 tuple handle 返回（`:305-384`）。

首次调用会把 kernel 返回的布局元数据组合成 handle；后续缓存调用则从该 handle 中取回 rank-prefix 等信息：

```python
if handle is not None:
    assert topk_idx is None and topk_weights is None
    rank_prefix_matrix, channel_prefix_matrix, recv_channel_prefix_matrix, recv_src_idx, is_token_in_rank, send_head = handle
    num_recv_tokens = recv_src_idx.size(0)
    recv_x, recv_x_scales, _, _, _, _, _, _, _, _, event = self.runtime.intranode_dispatch(
        x, x_scales, None, None,
        None, is_token_in_rank, None, num_recv_tokens, rank_prefix_matrix, channel_prefix_matrix,
        expert_alignment, num_worst_tokens, config,
        getattr(previous_event, 'event', None), async_finish, allocate_on_comm_stream)
else:
    assert num_tokens_per_rank is not None and is_token_in_rank is not None and num_tokens_per_expert is not None
    recv_x, recv_x_scales, recv_topk_idx, recv_topk_weights, num_recv_tokens_per_expert_list, rank_prefix_matrix, channel_prefix_matrix, recv_channel_prefix_matrix, recv_src_idx, send_head, event = \
        self.runtime.intranode_dispatch(x, x_scales, topk_idx, topk_weights,
                                        num_tokens_per_rank, is_token_in_rank, num_tokens_per_expert, 0, None, None,
                                        expert_alignment, num_worst_tokens, config,
                                        getattr(previous_event, 'event', None), async_finish, allocate_on_comm_stream)
    handle = (rank_prefix_matrix, channel_prefix_matrix, recv_channel_prefix_matrix, recv_src_idx, is_token_in_rank, send_head)
```

## 4.2 handle 是反向路由记录

handle 保存的信息对应 dispatch 的顺序与布局，而不只是一个 opaque ID。intranode handle 由 rank prefix matrix、channel prefix matrix、接收 source index、membership mask 和发送 head 组成；internode handle 还含 RDMA / global channel prefix、rank prefix 和 source metadata（`:366-384,448-512`）。combine 解包这些信息后调用底层 kernel，无需重新推导原始 dispatch 的发送关系（`:387-430`）。

intranode combine 将 handle 中的来源与前缀信息交给 C++ runtime，再返回结果和事件：

```python
rank_prefix_matrix, _, channel_prefix_matrix, src_idx, is_recv_token_in_rank, send_head = handle
bias_0, bias_1 = Buffer._unpack_bias(bias)

# Launch the kernel
recv_x, recv_topk_weights, event = self.runtime.intranode_combine(
    x, topk_weights, bias_0, bias_1,
    src_idx, rank_prefix_matrix, channel_prefix_matrix, send_head, config,
    getattr(previous_event, 'event', None), async_finish, allocate_on_comm_stream)
return recv_x, recv_topk_weights, EventOverlap(event)
```

## 4.3 V1 把两种服务目标放成两套 API

高吞吐路径接受更大的缓冲区与显式 `Config`，跨节点时先利用 RDMA，再在节点内通过 NVLink 分发。low-latency API 则面向小批量，要求 IBGDA；`low_latency_dispatch` 返回按 local expert 分组的接收区、源信息和布局句柄。该模式复用两个 buffer，API 文档要求同一时刻不要持有超过两次 kernel 的结果（`:530-598`）。low-latency combine 还支持通过 hook 延后等待接收，或提供 RDMA buffer 做 zero-copy（`:600-660`）。

low-latency 路径把 packed source/layout 信息保存在 handle，并在异步模式下记录本次操作的 Tensor 引用：

```python
packed_recv_x, packed_recv_x_scales, packed_recv_count, packed_recv_src_info, packed_recv_layout_range, event, hook = \
    self.runtime.low_latency_dispatch(x, topk_idx,
                                      cumulative_local_expert_recv_stats,
                                      dispatch_wait_recv_cost_stats,
                                      num_max_dispatch_tokens_per_rank, num_experts,
                                      use_fp8, round_scale, use_ue8m0,
                                      async_finish, return_recv_hook)
handle = (packed_recv_src_info, packed_recv_layout_range, num_max_dispatch_tokens_per_rank, x.size(1), num_experts)
tensors_to_record = (x, topk_idx,
                     packed_recv_x, packed_recv_x_scales, packed_recv_count,
                     packed_recv_src_info, packed_recv_layout_range,
                     cumulative_local_expert_recv_stats)
```

这里能直接得出的结论是 V1 暴露了两套调用面和不同资源约束。它们针对不同运行区间，是源码 API 的区分；“V2 统一 API 就一定更快/更容易使用”并非由此可证。

## 4.4 测试验证了什么

`tests/test_intranode.py` 构造 top-k 路由，先比较 layout 结果，再执行 dispatch；测试收到的 token 内容和 expert 计数，并将模拟的 expert 输出传给 combine，最后按路由重复次数归一化后与输入对比。测试也覆盖 FP8 输入、缓存 layout、异步 event 与不同配置（V1 `tests/test_intranode.py:35-165`）。

这是一项重要的可观察契约：combine 对 token 做聚合加法，V1 普通 combine 的文档明确写着“不在通信中乘权重”；权重可以单独通过 `topk_weights` 归约。模型框架要知道是否应在 expert 输出侧预乘 gate 权重。

测试传入 dispatch handle 执行 combine，并将结果按每个 token 被多少 rank 接收进行归一化：

```python
combine_args = {'x': recv_x, 'handle': handle, 'config': config, 'async_finish': async_mode}
if with_topk:
    combine_args.update({'topk_weights': recv_topk_weights})
combined_x, combined_topk_weights, event = buffer.combine(**combine_args)
event.current_stream_wait() if async_mode else ()
check_x = combined_x.float() / is_token_in_rank.sum(dim=1).unsqueeze(1)
ref_x = x_pure_rand if current_x is x_pure_rand else x
assert calc_diff(check_x, ref_x) < 5e-6
```

## 4.5 机制与代价

- 显式 layout 让调用方可以缓存、验证或控制 token 排布，但也把更多张量契约暴露到 API。
- 复用 handle 避免重建路由 metadata；相应地，handle 与输入路由、当前 buffer 生命周期紧密绑定。
- normal / low-latency 分开设计可以针对各自资源和同步语义优化，但使用者必须先选路径并理解各自限制。
- `Config` 中包含 SM、chunk 与 buffer 参数；V1 默认推荐值以 rank 数索引配置表，测试还展示了基于 benchmark 的参数扫描。

## 本章收束

- V1 的 layout 阶段先把 top-k 变为 rank/expert 发送计划。
- dispatch 生成 handle，combine 借助它恢复回传映射。
- normal 与 low-latency 是两套 API；它们的缓冲复用、同步和数据形状契约不同。
- V2 的变化重点之一，就是把 EP 用法收敛到统一接口并把更多布局细节放入 runtime。
