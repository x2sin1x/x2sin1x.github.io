---
title: "第 11 章 构建、测试与运行边界"
---

# 第 11 章 构建、测试与运行边界

> 本章回答从源码到可执行 DeepEP kernel 之间有哪些构建阶段，以及仓库测试能证明什么、不能证明什么。

## 11.1 安装和执行时编译是两件事

当前 README 要求 Linux、Python 3.10+、Hopper 或更新 GPU、CUDA Toolkit、支持 C++20 `std::format` 的编译器、带 CUDA 的 PyTorch、满足版本要求的 NCCL，以及 NVLink/RDMA 网络。安装时编译 host C++ extension；device kernels 由 DeepJIT 在运行时针对设备编译。因此 `pip install` 成功并不足以证明第一次 GPU kernel specialization 能成功。

V2 的 `_C.init_jit` 从 DeepEP 包目录、NCCL include path 和 compiler options 初始化运行时。DeepJIT 子模块在开发构建中也需要初始化；源码配置依赖它。本文没有执行依赖安装、DeepEP 构建或 GPU 测试，因为这些步骤会触发特定工具链与硬件需求，并不属于只读源码研究必要动作。

## 11.2 测试覆盖的主要契约

V2 测试按能力组织：

| 测试 | 主要观察点 |
| --- | --- |
| `tests/ep/test_ep.py` | EP dispatch/combine 的 token、top-k、layout 与配置组合 |
| `tests/ep/test_prefetch_weights.py` | 冗余专家权重预取 |
| `tests/ep/test_reduce_grads.py` | 冗余专家梯度规约 |
| `tests/buffer/test_allocation.py` | 对称 buffer 分配规划与物化 |
| `tests/comm/test_barrier.py` | 通信 barrier |
| `tests/bucket/*` | bucket collectives 与 session |
| `tests/engram/test_engram.py` / `tests/pp/test_pp.py` | Engram / PP 专用路径 |

测试直接验证在配置的硬件和进程组下数据结果及可观察行为；它们不能证明所有网络拓扑、所有 NCCL 版本和所有真实 workload 的性能。V1 的 `tests/test_intranode.py`、`test_internode.py`、`test_low_latency.py` 只属于 V1.2.1 快照。

## 11.3 常见边界

- NCCL shared library 不一致会被 Python import 时的 `check_nccl_so()` 拦截。
- NCCL communicator 不支持 Gin/GDAKI 时，Context 会明确报错；不能假设 fallback 到旧 NVSHMEM 路径。
- README 指出 EP dispatch/combine 需要 GPU SM，当前不支持 zero-SM RDMA EP。
- Buffer capacity、对称分配顺序、GPUs 的 NVLink domain、RDMA service level/QP 资源均须与运行环境吻合。
- 设备端超时与 host 等待超时用于暴露未完成通信；当前代码没有把它们抽象成可自动重试的操作事务。

## 11.4 如何复现本书的源码检查

```bash
git clone https://github.com/deepseek-ai/DeepEP.git
git checkout 93eb6eb238127e96c6d7a4a625a6dad158348509
python3 .agents/skills/source-code-book-writer/scripts/repo_inventory.py /path/to/DeepEP
```

V1.2.1 需另外 checkout `9af0e0d0e74f3577af1979c9b9e1ac2cad0104ee`。构建和 GPU 测试命令以 DeepEP 固定快照 README 为准；执行前应确认 GPU、CUDA、NCCL、网络与子模块满足该快照要求。

## 本章收束

- V2 的 host extension 在安装阶段构建，GPU kernels 则运行时 JIT 编译。
- 测试覆盖数据契约、buffer、通信和旁支功能，但其结论受设备与拓扑限制。
- 当前 V2.5 与 V1.2.1 的依赖、API 和测试范围不同，复现时必须 checkout 对应 commit。

## 全书结论

DeepEP 的核心不只是“做一次 all-to-all”。它把路由元数据、分层拓扑、设备通信缓冲、kernel 侧同步、输出排列和回程 combine 组织成一个跨 Python/C++/GPU 的状态协议。V1 将通信服务目标拆成 normal 与 low-latency 两组 API，并把更多 layout 与部署约束交给用户；EPv2 把 EP 调用收敛到 `EPBuffer`，使用 NCCL Gin 和对称 memory window 作为设备侧通信底座，再借助 DeepJIT 按运行配置编译 kernel。代价是对较新的 CUDA/NCCL/Gin 环境提出要求，并要求调用方理解 capacity、handle、stream 和事件生命周期。

这是两组源码快照的实现比较。是否适合具体服务仍需要在目标 GPU、网络拓扑、路由分布、GEMM layout 和 batch 范围内测量。
