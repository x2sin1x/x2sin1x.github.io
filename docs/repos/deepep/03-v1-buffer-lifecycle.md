---
title: "第 3 章 V1：Buffer 初始化与通信域建立"
weight: 30
---

# 第 3 章 V1：Buffer 初始化与通信域建立

> 本章回答：V1 的 Buffer 在第一次 dispatch 前要建立什么状态？主路径是 Python 汇集 peer 信息，C++ 分配本地资源，再同步 IPC 与 NVSHMEM 通信域。

## 3.1 Python 先确定 rank 与交换句柄

`Buffer.__init__` 接受 PyTorch ProcessGroup 或 MPI communicator，并将 rank、group size 与缓冲区参数交给 C++ runtime（V1 `deep_ep/buffer.py:32-84`）。之后每个 rank 收集本地 device ID 和 CUDA IPC handle；跨节点或 low-latency 模式还会设置 NVSHMEM IBGDA 环境参数，选出唯一 ID 的根 rank，再调用 `runtime.sync(...)` 完成初始化（同文件 `:86-125`）。

Python 先创建 C++ runtime，再交换设备号和 IPC handle：

```python
self.num_nvl_bytes = num_nvl_bytes
self.num_rdma_bytes = num_rdma_bytes
self.low_latency_mode = low_latency_mode
self.explicitly_destroy = explicitly_destroy
self.runtime = deep_ep_cpp.Buffer(self.rank, self.group_size, num_nvl_bytes, num_rdma_bytes, low_latency_mode, explicitly_destroy)

# Synchronize device IDs
local_device_id = self.runtime.get_local_device_id()
device_ids = all_gather_object(local_device_id)

# Synchronize IPC handles
local_ipc_handle = self.runtime.get_local_ipc_handle()
ipc_handles = all_gather_object(local_ipc_handle)
```

跨节点或低延迟分支设置 IBGDA 并交换根 unique ID，最后同步 C++ runtime：

```python
if self.runtime.get_num_rdma_ranks() > 1 or low_latency_mode:
    assert num_qps_per_rank > 0
    os.environ['NVSHMEM_DISABLE_P2P'] = '0' if allow_nvlink_for_low_latency_mode else '1'
    os.environ['NVSHMEM_IB_ENABLE_IBGDA'] = '1'
    os.environ['NVSHMEM_IBGDA_NUM_RC_PER_PE'] = f'{num_qps_per_rank}'

    if (low_latency_mode and self.rank == 0) or (not low_latency_mode and self.runtime.get_rdma_rank() == 0):
        root_unique_id = self.runtime.get_local_nvshmem_unique_id()
    nvshmem_unique_ids = all_gather_object(root_unique_id)
    root_unique_id = nvshmem_unique_ids[0 if low_latency_mode else self.runtime.get_root_rdma_rank(True)]

self.runtime.sync(device_ids, ipc_handles, root_unique_id)
assert self.runtime.is_available()
```

这个初始化顺序意味着 ProcessGroup 并不直接承载 GPU 数据面。它主要用于 rank 编排与对象交换；同节点的数据共享由 CUDA IPC 句柄建立，跨节点数据面则由 NVSHMEM 初始化。

## 3.2 C++ runtime 的资源所有权

C++ 构造函数根据 rank 计算 `rdma_rank = rank / 8` 与 `nvl_rank = rank % 8`，将一组最多 8 个本地 rank 视为 NVLink domain；它申请 local NVLink buffer、barrier 元数据、32 MiB workspace 和映射到 GPU 的 host counters（V1 `csrc/deep_ep.cpp:26-80`）。`get_local_ipc_handle` 导出本地分配的内存句柄，Python 收集后由 `sync` 在 peer 间打开。

rank 拆分和本地 IPC allocation 的核心逻辑如下：

```cpp
// Get ranks
CUDA_CHECK(cudaGetDevice(&device_id));
rdma_rank = rank / NUM_MAX_NVL_PEERS, nvl_rank = rank % NUM_MAX_NVL_PEERS;
num_rdma_ranks = std::max(1, num_ranks / NUM_MAX_NVL_PEERS), num_nvl_ranks = std::min(num_ranks, NUM_MAX_NVL_PEERS);

if (num_nvl_bytes > 0) {
    // Local IPC: alloc local memory and set local IPC handles
    CUDA_CHECK(cudaMalloc(&buffer_ptrs[nvl_rank], num_nvl_bytes + barrier_signal_bytes + buffer_ptr_bytes + barrier_signal_ptr_bytes));
    CUDA_CHECK(cudaIpcGetMemHandle(&ipc_handles[nvl_rank], buffer_ptrs[nvl_rank]));
    buffer_ptrs_gpu = reinterpret_cast<void**>(static_cast<uint8_t*>(buffer_ptrs[nvl_rank]) + num_nvl_bytes + barrier_signal_bytes);
    barrier_signal_ptrs[nvl_rank] = reinterpret_cast<int*>(static_cast<uint8_t*>(buffer_ptrs[nvl_rank]) + num_nvl_bytes);
    barrier_signal_ptrs_gpu = reinterpret_cast<int**>(static_cast<uint8_t*>(buffer_ptrs[nvl_rank]) + num_nvl_bytes + barrier_signal_bytes + buffer_ptr_bytes);

    // No need to synchronize, will do a full device sync during `sync`
    CUDA_CHECK(cudaMemsetAsync(barrier_signal_ptrs[nvl_rank], 0, barrier_signal_bytes, comm_stream));
}
```

常量定义给出了 rank 分组与 workspace 大小：

```cpp
#define NUM_MAX_NVL_PEERS 8
#define NUM_MAX_RDMA_PEERS 20
#define NUM_WORKSPACE_BYTES (32 * 1024 * 1024)
#define NUM_MAX_LOCAL_EXPERTS 1024
#define NUM_BUFFER_ALIGNMENT_BYTES 128
```

资源由 C++ 对象持有：Python 的 buffer 通过 `runtime` 字段持有扩展对象，`destroy()` 最终进入 C++ `Buffer::destroy`。销毁前先设备同步，并在释放 IPC 或 NVSHMEM 资源前执行相应 barrier；若设置 `explicitly_destroy=True`，调用方必须主动调用 `destroy()`，否则析构会警告潜在泄漏（`csrc/deep_ep.cpp:84-90,143-183`）。

析构策略和资源释放顺序如下：

```cpp
Buffer::~Buffer() noexcept(false) {
    if (not explicitly_destroy) {
        destroy();
    } else if (not destroyed) {
        printf("WARNING: destroy() was not called before DeepEP buffer destruction, which can leak resources.\n");
        fflush(stdout);
    }
}

void Buffer::destroy() {
    EP_HOST_ASSERT(not destroyed);
    CUDA_CHECK(cudaDeviceSynchronize());
    if (num_nvl_bytes > 0) {
        intranode::barrier(barrier_signal_ptrs_gpu, nvl_rank, num_nvl_ranks, comm_stream);
        CUDA_CHECK(cudaDeviceSynchronize());
        if (is_available()) {
            for (int i = 0; i < num_nvl_ranks; ++ i) if (i != nvl_rank)
                CUDA_CHECK(cudaIpcCloseMemHandle(buffer_ptrs[i]));
        }
        CUDA_CHECK(cudaFree(buffer_ptrs[nvl_rank]));
    }
#ifndef DISABLE_NVSHMEM
    if (is_available() and num_rdma_bytes > 0) {
        CUDA_CHECK(cudaDeviceSynchronize());
        internode::barrier();
        internode::free(rdma_buffer_ptr);
        internode::finalize();
    }
#endif
    CUDA_CHECK(cudaFree(workspace));
    CUDA_CHECK(cudaFreeHost(const_cast<int*>(moe_recv_counter)));
    CUDA_CHECK(cudaFreeHost(const_cast<int*>(moe_recv_expert_counter)));
    destroyed = true;
    available = false;
}
```

::: mermaid
sequenceDiagram
    participant P as Python Buffer
    participant C as C++ Buffer
    participant G as 同节点 rank
    participant N as NVSHMEM ranks
    P->>C: 创建本地 Buffer
    C->>C: 分配 NVLink buffer / workspace / counters
    P->>G: all_gather device ID 与 CUDA IPC handle
    P->>N: 选 root unique ID 并 all_gather
    P->>C: sync(peer 信息, root ID)
    C->>G: 打开 peer IPC 内存
    C->>N: 初始化 NVSHMEM 与 RDMA storage
    Note over P,N: dispatch / combine 可用
:::

## 3.3 初始化约束来自拓扑假设

V1 C++ 构造中写死 `NUM_MAX_NVL_PEERS == 8`，并要求超过本地 NVLink peer 数时 rank 数能按该值整除。high-throughput internode 路径假定节点内经 NVLink、相同 GPU index 的节点间经 RDMA；低延迟模式另有 IBGDA QP 数和容量约束（`deep_ep/buffer.py:47-52`）。这说明部署拓扑是算法参数的一部分，不是运行环境的无关细节。

## 3.4 失败与释放边界

Python 初始化中途失败时，C++ 对象可能已经分配 CUDA 或 NVSHMEM 资源；V1 文档特别提醒析构清理可能在 Python 异常处理中挂住，因此提供显式销毁选项。销毁本身是集体操作：一边的 rank 离开、另一边仍继续使用缓冲区，会使 barrier 无法完成。源码直接显示了同步和资源释放顺序；它没有提供可由单 rank 安全恢复的故障协议。

## 本章收束

- V1 先通过 host collectives 交换进程信息，再建立 CUDA IPC / NVSHMEM 数据面。
- C++ `Buffer` 持有 workspace、通信缓冲区与计数器，并负责集体清理。
- 节点内 8-rank 分组、NVLink 可见性、RDMA 可达性共同限定可用拓扑。
- 下一章从这些已建好的资源出发，追踪一次 V1 dispatch 到 combine。
