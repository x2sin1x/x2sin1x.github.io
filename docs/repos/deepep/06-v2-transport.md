---
title: "第 6 章 V2：NCCL Gin 与对称内存"
---

# 第 6 章 V2：NCCL Gin 与对称内存

> 本章回答 V2 如何在既有 NCCL communicator 上创建 device-side 通信能力，以及 scale-up / scale-out rank 如何映射到物理网络域。

## 6.1 复用 NCCL communicator

`Context` 从上层收到 NCCL communicator handle，并直接将其转为 `ncclComm_t`；随后查询 communicator properties，再构造 NCCL device communicator requirements（当前 `csrc/kernels/comm/context.cpp:75-159`）。Gin 未禁用时，代码检查 communicator 是否支持对应 Gin 类型和 GDAKI，再设置 Gin context count、exclusive contexts、queue depth、signal count、connection type 和 traffic class。

Context 复用 host communicator，检查 Gin/GDAKI 支持并配置 device communicator：

```cpp
// Reuse the NCCL communicator
comm = reinterpret_cast<ncclComm_t>(nccl_comm);

ncclCommProperties props = NCCL_COMM_PROPERTIES_INITIALIZER;
NCCL_CHECK(ncclCommQueryProperties(comm, &props));

ncclDevCommRequirements_t reqs = NCCL_DEV_COMM_REQUIREMENTS_INITIALIZER;
reqs.lsaMultimem = enable_lsa_multimem;
if (get_env("EP_DISABLE_GIN", 0) == 0) {
    EP_HOST_ASSERT(
        (allow_hybrid_mode ? props.railedGinType : props.ginType) != NCCL_GIN_TYPE_NONE and
        "NCCL GIN is unavailable. This is usually due to a network configuration issue, "
        "such as `allow_hybrid_mode=0` (disable direct RDMA kernels) in multi-plane network.");
    EP_HOST_ASSERT(
        props.ginSupport[NCCL_GIN_TYPE_GDAKI] and
        "NCCL GDAKI is unavailable for this communicator.");

    gin_min_stride = props.ginMinStride;
    reqs.ginType = NCCL_GIN_TYPE_GDAKI;
    reqs.ginContextCount = num_allocated_qps;
    reqs.ginExclusiveContexts = true;
    reqs.ginQueueDepth = qp_depth > 0 ? qp_depth : kDefaultQPDepth;
    // Customized RDMA barrier needs extra signals
    reqs.ginSignalCount = num_ranks + 2 * 2;
    if (allow_hybrid_mode and num_rdma_storage_bytes > 0) {
        reqs.ginCustomStride = gin_min_stride;
        reqs.ginConnectionType = NCCL_GIN_CONNECTION_CUSTOM_STRIDE;
    } else {
        reqs.ginConnectionType = allow_hybrid_mode ? NCCL_GIN_CONNECTION_RAIL : NCCL_GIN_CONNECTION_FULL;
    }
}
```

这条路径让 DeepEP 在现有 NCCL 进程组上申请设备侧通信资源；DeepEP 不必在 EP buffer 初始化时另建一套与 PyTorch ProcessGroup 无关的跨节点 bootstrap。这里的“复用”是指复用 NCCL host communicator，不意味着普通 NCCL collective 本身完成 DeepEP kernel 的 token scatter。

## 6.2 物理 domain 与逻辑 domain

代码用 NCCL LSA team 的 rank 数表示 NVLink 可见的物理域，world rank 数除以该值作为 RDMA peer 数。`allow_hybrid_mode=True` 时，逻辑 scale-up domain 对应本地 NVLink ranks，scale-out domain 对应节点/RDMA ranks；关闭 hybrid 后，逻辑模型把全组放入单一 scale-up domain（`context.cpp:160-177` 与 Python `ep.py:352-358`）。

物理 rank 数确定后，hybrid 开关决定逻辑上的 scale-up / scale-out 切分：

```cpp
ncclTeam_t lsaTeam = ncclTeamLsa(comm);
num_nvl_ranks = lsaTeam.nRanks, nvl_rank_idx = lsaTeam.rank;
num_rdma_ranks = num_ranks / num_nvl_ranks, rdma_rank_idx = rank_idx / num_nvl_ranks;
EP_HOST_ASSERT(num_ranks % num_nvl_ranks == 0 and nvl_rank_idx == rank_idx % num_nvl_ranks);

if (allow_hybrid_mode) {
    num_scaleout_ranks = num_rdma_ranks, num_scaleup_ranks = num_nvl_ranks;
    scaleout_rank_idx = rdma_rank_idx, scaleup_rank_idx = nvl_rank_idx;
} else {
    num_scaleout_ranks = 1, num_scaleup_ranks = num_ranks;
    scaleout_rank_idx = 0, scaleup_rank_idx = rank_idx;
}
is_scaleup_nvlink = num_scaleup_ranks == num_nvl_ranks;
```

::: mermaid
flowchart LR
    subgraph W[EP world]
        subgraph R0[Scale-out rank 0]
            A[Scale-up rank 0]
            B[Scale-up rank 1]
            C[Scale-up rank N]
        end
        subgraph R1[Scale-out rank 1]
            D[Scale-up rank 0]
            E[Scale-up rank 1]
            F[Scale-up rank N]
        end
    end
    A <-->|NVLink / LSA| B
    D <-->|NVLink / LSA| E
    A <-->|RDMA / Gin| D
    B <-->|RDMA / Gin| E
:::

这是便于理解的拓扑示意，不承诺物理 rank 数固定为图中值。具体的 scale-up 大小取自当前 NCCL communicator 的 LSA team。

## 6.3 对称内存窗口

V2 的 `Context` 通过 symmetric allocator 取得对称内存，注册 NCCL window，再获取 LSA device pointer。workspace 位于窗口起始部分，buffer 从 workspace 偏移之后开始；跨节点 RDMA storage 可以另行注册为 Gin-only window（`context.cpp:180-222`）。这使 kernel 能在一个已注册窗口上定位本 rank workspace、GPU buffer 和 RDMA storage。

Context 将 workspace 与 GPU buffer 放进 symmetric allocation，注册窗口并用 workspace 大小切出普通 buffer；RDMA storage 单独注册为 Gin-only window：

```cpp
if (main_context == nullptr) {
    symmetric_memory = symmetric::alloc(
        num_workspace_bytes + num_gpu_buffer_bytes, num_rdma_storage_bytes,
        use_cpu_rdma_storage,
        allow_hybrid_mode, gin_min_stride, rank_idx / gin_min_stride,
        shared_comm);
} else {
    symmetric_memory = main_context->symmetric_memory;
}

raw_window_ptr = this->symmetric_memory->ptr;
NCCL_CHECK(ncclCommWindowRegister(comm, raw_window_ptr, symmetric_memory->num_sym_bytes, &window, NCCL_WIN_STRICT_ORDERING));
NCCL_CHECK(ncclGetLsaDevicePointer(window, 0, nvl_rank_idx, &workspace));
buffer = math::advance_ptr(workspace, num_workspace_bytes);
```

同一 context 可以由额外 buffer context 共享其 `symmetric_memory`，减少重复申请；这也是拆分 EP、Engram、PP、Bucket buffers 后仍共享底层通信资源的一种方式。共享关系由 `main_context` 参数显式表达，不能将各 Buffer 的上层状态误认为完全独立。

## 6.4 初始化失败条件

Context 会检查 rank/QP 范围、workspace 与 buffer 的对齐、NCCL Gin/GDAKI 能力，并验证 NCCL multimem 是否可用（如果请求启用）。不满足条件会在创建 communicator 或内存窗口时失败，而不是静默退化成普通 PyTorch collective。运行前应核验 README 的 CUDA、NCCL、GPU 与 RDMA 要求，并确保 PyTorch 与 DeepEP 使用同一 NCCL shared library。

## 本章收束

- V2 使用现有 NCCL communicator 创建 device communicator，并要求其具备所需 Gin 能力。
- 物理 NVLink domain 与逻辑 scale-up/scale-out domain 是两个层次，hybrid 开关会改变后者。
- NCCL window 和 symmetric allocation 提供 GPU 侧寻址基础，RDMA storage 可单独注册。
- 下一章把 transport context 接回实际 token dispatch。
