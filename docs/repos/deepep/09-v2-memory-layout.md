---
title: "第 9 章 V2：容量、布局与通信资源"
weight: 90
---

# 第 9 章 V2：容量、布局与通信资源

> 本章回答容量、SM/QP 估算和布局元数据如何约束 V2 主链。焦点是资源决策的源码规则，而非脱离硬件语境的性能数字。

## 9.1 Buffer size hint 是容量估算，不是运行时扩容

`EPBuffer.get_buffer_size_hint` 将 ProcessGroup communicator 与最大 token 数、hidden、top-k、FP8、hybrid 和 reduction 配置交给 C++ 计算，返回按 2 MiB 对齐的建议值（`deep_ep/buffers/ep.py:373-399`）。构造 `EPBuffer` 时也可以显式给 `num_bytes`；源码会在 dispatch/combine 前检查所需 buffer 不超过已分配字节数。

size hint 直接把配置参数传给 C++ 计算函数；返回值已按 2 MiB 对齐：

```python
@staticmethod
def get_buffer_size_hint(group: dist.ProcessGroup,
                         num_max_tokens_per_rank: int, hidden: int,
                         num_topk: int = 0, use_fp8_dispatch: bool = False,
                         allow_hybrid_mode: bool = True,
                         allow_multiple_reduction: bool = True) -> int:
    """
    Get a recommended buffer size (in bytes) for the given MoE settings, without constructing the buffer.
    The returned value is aligned to 2 MB.
    """
    # NOTES: calculate_ep_buffer_size already returns 2 MB-aligned values
    return _C.calculate_ep_buffer_size(
        comm.get_nccl_comm_handle(group).get(),
        num_max_tokens_per_rank, hidden, num_topk, use_fp8_dispatch,
        allow_hybrid_mode, allow_multiple_reduction)
```

容量取决于业务批次上界和布局策略。特别是 `do_cpu_sync=False` 的 dispatch 会按 worst case 预分配返回张量；过小的 capacity 不是靠 API 自动扩容来修复。

## 9.2 SM 估算用拓扑流量模型

`get_theoretical_num_sms` 先计算一个均匀 gate 假设下，top-k 预期分布到多少 scale-up / scale-out rank，再估算 NVLink 和 RDMA 流量与 SM 读写流量；瓶颈链路决定需要的 SM 估计值，最后取偶数并限制到设备 SM 数。代码注明该估算假设 balanced gate，也尚未支持若干 layout / gate 模式（`ep.py:430-541`）。

估算函数明确要求 balanced gate，按分组组合数推算期望 top-k rank 数：

```python
@weak_lru(maxsize=None)
def get_theoretical_num_sms(self, num_experts: int, num_topk: int,
                            num_scaleout_topk: int = 0,
                            rdma_gbs: float = 0, nvlink_gbs: float = 0,
                            sm_read_gbs: float = 0, sm_write_gbs: float = 0) -> int:
    # NOTES: this is for balanced gate
    assert num_scaleout_topk == 0

    def get_expected_topk(num_groups: int) -> float:
        assert num_experts % num_groups == 0
        return num_groups * (1 - math.comb(num_experts - num_experts // num_groups, num_topk) / math.comb(num_experts, num_topk))

    num_expected_scaleout_topk = get_expected_topk(self.num_scaleout_ranks) if self.num_scaleout_ranks > 1 else 0
    num_expected_topk = get_expected_topk(self.num_ranks)
    # 后续代码按流量与带宽计算瓶颈，再得到 SM 数
```

上面最后一行是说明性注释，用来标明摘录的省略部分，并非实际代码。瓶颈选择、对齐及设备 SM 上限裁剪如下：

```python
if self.num_scaleout_ranks > 1 and (rdma_traffic / rdma_gbs) > (nvlink_traffic / nvlink_gbs):
    bounded_traffic, bounded_gbs = rdma_traffic, rdma_gbs
else:
    bounded_traffic, bounded_gbs = nvlink_traffic, nvlink_gbs

num_sms = align(max(4, math.ceil(num_sms * 1.3)), 4)
num_sms = num_sms if self.prefer_overlap_with_compute else max(num_sms, 64)
num_sms = min(num_sms, num_device_sms // 2 * 2)
return num_sms
```

因此它能替代手写初值或 benchmark 搜索的一部分，但不能视为对任意路由分布都准确的测量结果。更改模型 gate 行为、scale-out topology 或展开布局时，应核对估算函数的适用假设。

## 9.3 QP 数与通信模式绑定

`get_theoretical_num_qps` 对 direct mode 使用受 SM 数限制的较小 QP 数；hybrid mode 则按 channel 与 notify 资源估算更多 QP，最终受构造时 `num_allocated_qps` 上限约束（`ep.py:543-560`）。构造时若 QP 数为 0，Python 会根据 hybrid mode 与快速 RDMA atomic 能力给出可分配上限（`ep.py:322-331`）。

QP 数规则由运行模式决定，最后统一受初始化分配上限截断：

```python
def get_theoretical_num_qps(self, num_sms: int) -> int:
    # For direct mode, we encourage less QPs to reduce DB ringing overhead
    num_qps = min(num_sms, 8 + 1)

    # For hybrid mode, we encourage every channel (and notify) to have an independent QP
    if self.allow_hybrid_mode:
        num_qps = num_sms * 16 + 1

    return min(num_qps, self.num_allocated_qps)
```

这解释了为什么“调用时要求的 QP 数”与“初始化时已申请的 QP 数”是两个参数：前者是本次 kernel 计划，后者是 communicator/device context 可提供的资源上界。

## 9.4 BufferAllocator 与资源分区

V2.5 将 buffer 细分为 `EPBuffer`、`EngramBuffer`、`PPBuffer` 和 `BucketBuffer`，它们共享 `BufferBase` 生命周期。`BufferAllocator` 可先规划对称张量分配，再把计划物化到通信 storage；README 指出同一 LSA domain 内 ranks 的 tensor shapes 和 allocation order 必须一致。这是对称地址映射正确工作的契约，不只是内存分配风格。

## 本章收束

- buffer hint 规划容量；真实分配后仍由 runtime 校验是否足够。
- SM 解析估算基于带宽与均匀路由假设；它不等于自动 benchmark 或普适最优。
- QP 请求数量受初始化时分配上限约束，且 hybrid/direct 的资源组织不同。
- 对称内存的跨 rank 一致性要求延伸到了 BufferAllocator 的形状与分配顺序。
