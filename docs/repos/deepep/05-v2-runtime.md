---
title: "第 5 章 V2：Python API、C++ 扩展与 DeepJIT"
---

# 第 5 章 V2：Python API、C++ 扩展与 DeepJIT

> 本章回答一次 V2 API 调用如何到达可执行 GPU kernel。路径由三段组成：Python 参数编排，C++ 运行时与资源验证，DeepJIT specialization 与 launch。

## 5.1 import 建立运行时

V2 的 `deep_ep/__init__.py` 在导出 `EPBuffer` 前先执行 `check_nccl_so()` 和 `init_jit()`（`deep_ep/__init__.py:19-56`）。前者检查当前进程加载的 NCCL 动态库是否重复、是否与 DeepEP 链接时的 NCCL 文件相同；后者把 Python 包目录和 NCCL include 目录传给 `_C.init_jit`。所以包导入会触发环境检查和 JIT runtime 初始化，不只是延迟到第一次 dispatch 才做。

## 5.2 EPBuffer 负责 PyTorch 侧契约

构造 `EPBuffer` 时，Python 取得 ProcessGroup 的 rank 与 size，获取 NCCL communicator handle，根据 token capacity / hidden / top-k 参数计算 buffer 容量，再创建 C++ `EPBuffer`。之后根据物理 domain 和 `allow_hybrid_mode` 计算逻辑 scale-up / scale-out rank，并通过 CUDA synchronize、group barrier 再 synchronize，确保所有 rank 的初始化资源已可见（`deep_ep/buffers/ep.py:242-363`）。

构造路径先拿 communicator 并计算通信 buffer 大小，再创建 C++ runtime：

```python
self.nccl_comm_handle = comm.get_nccl_comm_handle(group)

if num_bytes is None:
    num_bytes = _C.calculate_ep_buffer_size(
        self.nccl_comm_handle.get(),
        num_max_tokens_per_rank, hidden, num_topk, use_fp8_dispatch,
        allow_hybrid_mode, allow_multiple_reduction)

super().__init__(explicitly_destroy)
self.runtime = _C.EPBuffer(
    self.rank_idx, self.num_ranks,
    self.nccl_comm_handle.get(), num_bytes, num_lb_bytes,
    allow_hybrid_mode, allow_multiple_reduction, prefer_overlap_with_compute,
    sl_idx, num_allocated_qps,
    num_cpu_timeout_secs, num_gpu_timeout_secs,
    self.explicitly_destroy)
```

Python 的 `dispatch` 做 API 级检查、默认参数推导和 handle 解包，然后调用 `self.runtime.dispatch(...)`。例如 SM 数为 0 时，函数调用 `get_theoretical_num_sms`；QP 数为 0 时，调用 `get_theoretical_num_qps` 并检查它不超过已分配的 QP 数（`ep.py:641-645`）。这不是调优器：它是带假设的解析估算。

默认 SM/QP 数的选择与上限检查就在 Python wrapper 中：

```python
# Automatic decide SM and QP count
num_topk = (handle.topk_idx if topk_idx is None else topk_idx).shape[1]
num_sms = self.get_theoretical_num_sms(num_experts, num_topk) if num_sms == 0 else align(num_sms, 2)
num_qps = self.get_theoretical_num_qps(num_sms) if num_qps == 0 else num_qps
assert num_qps <= self.num_allocated_qps, f'Allocated QPs are not enough'
```

## 5.3 C++ 层连接状态与内核

`csrc/buffers/ep.hpp` 中的 C++ `EPBuffer` 持有 `Context`、host workspace、映射 workspace 和 buffer 尺寸。Python Tensor 会在 C++ 边界做设备、dtype、shape、连续性与对齐检查；通过检查后，`launch_dispatch` / `launch_combine` 才会取得通信状态并执行 kernel wrapper。

## 5.4 DeepJIT specialization 的组成

`csrc/kernels/ep/dispatch.hpp` 根据 scaleout rank 数选择 `dispatch_impl` 或 `hybrid_dispatch_impl`，把 dtype 元素大小、hidden、最大 token 数、experts、top-k、alignment、SM/QP 等值拼进模板 specialization，再调用 `jit->compile(...)` 和 `jit->launch(...)`（`:31-165`）。Combine 对应 wrapper 也采用参数化函数名与 JIT launch（`combine.hpp:24-132`）。

launch wrapper 把布局和并行参数编码进模板函数名，然后把 JIT 编译得到的 kernel 提交到对应 stream：

```cpp
std::string header_name, func_name;
if (num_scaleout_ranks == 1) {
    header_name = "dispatch";
    func_name = std::format("dispatch_impl<{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}>",
        is_scaleup_nvlink,
        do_cpu_sync,
        reuse_slot_indices,
        num_sms,
        num_notify_warps, num_dispatch_warps,
        num_scaleup_ranks,
        hidden * elem_size, num_sf_packs,
        num_max_tokens_per_rank,
        num_experts, num_topk, expert_alignment,
        num_qps, num_timeout_cycles);
}
const auto kernel = jit->compile("dispatch", std::format(R"(
#include <deep_ep/impls/ep/{}.cuh>

static void __instantiate_kernel() {{
    auto ptr = reinterpret_cast<void*>(&deep_ep::ep::{});
}}
)", header_name, func_name));
const auto options = deep_jit::cuda::LaunchOptions {
    .stream = stream.stream(),
    .num_smem_bytes = num_smem_bytes,
    .grid_dim = dim3(num_sms, 1, 1),
    .block_dim = dim3(num_threads, 1, 1),
    .cluster_dim = dim3(2 - (num_sms % 2), 1, 1),
    .cooperative = true,
};
```

`csrc/runtime/jit.hpp` 创建 DeepJIT CUDA runtime，并把 NCCL include 路径、top-k index bit width 与 Gin 编译开关放进 compiler options。它还将 `jit` 声明为 LazyInit 对象，避免在运行时对象还未准备好时立即构造 CUDA compiler runtime。

源码能证明模板参数参与 kernel specialization，且设备代码在运行时编译。源码没有保证所有环境下 JIT 缓存命中或编译开销为零；安装、导入、第一次 specialization 和后续复用应当区分。

::: mermaid
sequenceDiagram
    participant U as Python 调用方
    participant A as EPBuffer.dispatch
    participant C as C++ EPBuffer
    participant J as DeepJIT Runtime
    participant K as 设备 Kernel
    U->>A: x / topk_idx / 参数
    A->>A: 默认 SM、QP 与 handle 元数据
    A->>C: runtime.dispatch(...)
    C->>C: 校验张量、选择 stream、准备 buffer
    C->>J: 按 topology / shape 编译 specialization
    J->>K: 在通信 stream launch
    K-->>C: 通信完成事件与结果元数据
    C-->>A: Tensor、EPHandle、Event
    A-->>U: 同步结果或 EventOverlap
:::

## 本章收束

- V2 的 Python 包导入会校验 NCCL 动态库并初始化 DeepJIT。
- `EPBuffer` 把 PyTorch API、rank/domain 参数和 runtime 状态连接起来。
- C++ 检查张量契约并负责执行路径；JIT wrapper 将 specialization 参数传给编译和 launch。
- 第 6 章继续看 C++ context 如何使用 NCCL communicator 建立 Gin 和对称通信内存。
