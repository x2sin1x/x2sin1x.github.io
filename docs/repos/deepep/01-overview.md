---
title: "第 1 章 定位与版本边界"
weight: 10
---

# 第 1 章 定位与版本边界

> 本章回答 DeepEP 在 MoE 执行链中负责什么，以及 V1 和 EPv2 的关系。先固定两代源码边界，后续才能比较机制而不混用调用链。

## 1.1 它解决的是专家并行通信

MoE 层先由 router 为每个 token 选出 top-k experts，再把 token 送到持有这些 experts 的 rank。专家计算完成后，结果还要回到原始 rank 做 combine。DeepEP 承担这两个 all-to-all 风格的阶段，并处理 token 数据、路由元数据、计数、同步以及 NVLink / RDMA 传输。

源码入口证据在当前 README 的能力列表和 Python API：V2 将高吞吐、低延迟 EP 操作收敛到 `EPBuffer.dispatch` / `combine`；实际执行由 C++ buffer 调用 JIT kernel。README 还列有 `BucketBuffer`、`EngramBuffer`、`PPBuffer`，它们属于旁支能力，不是本书的主黄金路径（[README](https://github.com/deepseek-ai/DeepEP/blob/93eb6eb238127e96c6d7a4a625a6dad158348509/README.md)；`deep_ep/buffers/ep.py:208,562,770`）。

下面列出 `dispatch` 的关键参数。其余参数控制容量、布局、同步和句柄缓存：

```python
def dispatch(self,
             x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
             topk_idx: Optional[torch.Tensor] = None,
             topk_weights: Optional[torch.Tensor] = None,
             cumulative_local_expert_recv_stats: Optional[torch.Tensor] = None,
             num_experts: Optional[int] = None,
             num_max_tokens_per_rank: Optional[int] = None,
             expert_alignment: Optional[int] = None,
             num_sms: int = 0, num_qps: int = 0,
             previous_event: Optional[EventHandle] = None,
             async_with_compute_stream: bool = False,
             allocate_on_comm_stream: bool = False,
             handle: Optional[EPHandle] = None,
             do_handle_copy: bool = False,
             do_cpu_sync: Optional[bool] = None,
             do_expand: bool = False,
             do_zero_padding: bool = False,
             use_tma_aligned_col_major_sf: bool = False,
             defer_epilogue: bool = False) \
        -> Union[Tuple[Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
                       Optional[torch.Tensor], Optional[torch.Tensor],
                       EPHandle, EventOverlap], EventOverlap]:
```

## 1.2 两个独立快照，两个运行模型

V1 取 `v1.2.1`，提交 `9af0e0d0e74f3577af1979c9b9e1ac2cad0104ee`。其 Python `Buffer` 负责初始化分布式通信状态，C++ `deep_ep::Buffer` 持有 IPC / NVSHMEM 缓冲区，CUDA kernels 分成 intranode、internode 和 low-latency 实现。关键坐标是 `deep_ep/buffer.py`、`csrc/deep_ep.cpp`、`csrc/kernels/{intranode,internode,internode_ll}.cu`。

V2 取当前 `main` 的 `93eb6eb238127e96c6d7a4a625a6dad158348509`。Python 包公开 `EPBuffer` 等专用 buffer；公共 C++ 扩展初始化 NCCL/Gin 相关上下文，通信 kernel 由 DeepJIT 在运行时编译。V2.5 README 明确记录 V1 被移除（[README: V2.5 release](https://github.com/deepseek-ai/DeepEP/blob/93eb6eb238127e96c6d7a4a625a6dad158348509/README.md)）。

| 维度 | V1.2.1 | V2.5 快照 |
| --- | --- | --- |
| Python 主入口 | `deep_ep.Buffer` | `deep_ep.EPBuffer` |
| 传输组织 | NVLink IPC + NVSHMEM/IBGDA；接口区分 normal 与 low-latency | NCCL communicator + device-side Gin；一个 EP dispatch/combine API |
| kernel 交付 | CUDA 编译期构建的 `.cu` kernel | DeepJIT 按参数生成并缓存 specialization |
| 布局责任 | 调用者可提供 rank/expert 计数与 token-in-rank 矩阵 | runtime 处理路由和布局元数据，句柄支持后续复用 |
| 范围 | EP 为中心 | EP 主链 + Bucket、Engram、PP 等独立 buffer |

这张表是源码形态比较，不是对相同性能条件下的优劣判断。运行时、网络、GPU 与参数都不同，不能由接口变化直接推出吞吐数字。

## 1.3 黄金路径

全书以一次前向 MoE 路由作为主线：调用者给出 token 矩阵 `x`、`topk_idx` 和可选权重；DeepEP 让 token 到达目标 experts，返回收到的数据与通信句柄；模型计算 experts；再把结果传入 combine，按原路由映射回原 rank。

::: mermaid
sequenceDiagram
    participant M as MoE 调用方
    participant P as Python Buffer API
    participant R as C++ Runtime
    participant K as GPU 通信 Kernel
    participant E as 目标专家 rank
    M->>P: x, topk_idx, topk_weights
    P->>R: 校验参数、选择路径
    R->>K: 布局元数据与数据缓冲区
    K->>E: dispatch 到目标 experts
    E->>M: 专家网络输出
    M->>P: combine(x, handle)
    P->>K: 根据 handle 反向聚合
    K-->>M: 原始 rank 上的合并结果
:::

图表示共同的逻辑流程。V1 与 V2 使用不同的通信上下文、缓冲区布局和内核实现，具体调用分别见第 4、7、8 章。

## 1.4 证据边界

“V1 需要调用者先提供 `is_token_in_rank` 等布局张量”是 V1 Python 函数签名直接表达的事实（`deep_ep/buffer.py:305-384`）；“V2 把布局与路由元数据的责任更多移入 EPBuffer”是两代 API 和实现对照后的解释。V2 设计者的动机不能仅由代码推出，本书只陈述可验证的机制和它们带来的约束。

`dispatch` 将 rank、RDMA rank、token membership 与 expert 计数都列为可选入参，直接展示了旧 API 如何暴露布局输入：

```python
def dispatch(self, x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
             handle: Optional[Tuple] = None,
             num_tokens_per_rank: Optional[torch.Tensor] = None, num_tokens_per_rdma_rank: Optional[torch.Tensor] = None,
             is_token_in_rank: Optional[torch.Tensor] = None, num_tokens_per_expert: Optional[torch.Tensor] = None,
             topk_idx: Optional[torch.Tensor] = None, topk_weights: Optional[torch.Tensor] = None,
             expert_alignment: int = 1, num_worst_tokens: int = 0,
             config: Optional[Config] = None,
             previous_event: Optional[EventOverlap] = None, async_finish: bool = False,
             allocate_on_comm_stream: bool = False) -> \
        Tuple[Union[Tuple[torch.Tensor, torch.Tensor], torch.Tensor], Optional[torch.Tensor],
              Optional[torch.Tensor], List[int], Tuple, EventOverlap]:
    # The method body continues below the cited signature.
```

## 本章收束

- DeepEP 位于 MoE router 与专家计算之间，负责 dispatch/combine 和相关资源管理。
- V1 与 V2 是不同运行模型；它们在本书里使用各自固定的 commit。
- 后续先解释 V1 的显式布局和通信路径，再追踪 V2 的统一 API 与 Gin runtime。
