---
title: Transfer Engine：一次传输的完整路径
weight: 40
---

# Transfer Engine：一次传输的完整路径

> 本章沿主线一逐跳追踪：一次 `batchTransfer` 调用如何在多协议路由、slice 切分、多网卡选择与异步投递之间流动，以及在哪些点失败。这是 TE 辨识度最高的机制。

## 第一跳：协议路由（MultiTransport）

调用者提交的是与协议无关的 `TransferRequest`（含 `opcode`、`source`、`target_id`、`target_offset`、`length`）。`MultiTransport::submitTransfer` 先为每个 request 选出承担传输的 `Transport*`（`multi_transport.cpp:591` 的 `selectTransports` → `:623` 的 `selectTransport`）。

选路依据是目标段描述符里的 `protocol` 字段。同构段（单协议）直接映射到对应 transport；混合协议段（如 `rdma,hip`）则按"哪个 buffer 覆盖目标地址 + 固定优先级"决定（`multi_transport.cpp:646` 附近的 lambda）：

```cpp
auto protocol_priority = [](const std::string& p) {
    // hip 是节点内 GPU-IPC；跨节点请求必须回落到 rdma
    if (p == "hip") return std::getenv("MC_DISABLE_HIP") ? 0 : 4;
    if (p == "maca") return std::getenv("MC_DISABLE_MACA") ? 0 : 4;
    if (p == "shm")  return 4;
    if (p == "cxl")  return 3;
    if (p == "rdma") return 2;
    if (p == "tcp")  return 1;
    return 0;
};
```

源码注释明说了这个设计：同一块设备 KV 池会同时注册到 rdma 与 hip，节点内走 hip（GPU IPC），跨节点自动回落 rdma——单个混合协议段同时支撑两条路径，无需运维干预（解释，基于该函数实现与其注释）。

## 第二跳：RDMA 传输执行与 slice 切分

选定 `RdmaTransport` 后进入 `submitTransferTask`（`rdma_transport.cpp:856`）。它的骨架是按配置的 slice 大小把每个 request 切成多个 `Slice`，逐个为 slice 选设备并投递：

```cpp
const size_t kBlockSize = globalConfig().slice_size;
const int kMaxRetryCount = globalConfig().retry_cnt;
...
for (uint64_t offset = 0; offset < request.length;) {
    size_t slice_length = slice_calc.calculate(offset);
    Slice *slice = getSliceCache().allocate();
    slice->source_addr = (char *)request.source + offset;
    slice->length = slice_length;
    slice->rdma.dest_addr = request.target_offset + offset;
    slice->rdma.max_retry_cnt = kMaxRetryCount;
    slice->task = &task;
    ...
}
```

slice 是 TE 的最小传输单元：状态机（`PENDING` → 完成/失败）、重试计数、统计都挂在 slice 上，task 的完成判定是 `success + failed == slice_count`。

## 第三跳：多 NIC 选择（带宽聚合的核心）

每个 slice 通过 `selectDevice`（`rdma_transport.cpp:1299` 附近，基于段内 `topology` 的 `selectDeviceByLocalHca` / `selectDevice`）选择本机哪块 HCA 发送。输入是源 buffer 的 `location`（拓扑提示）与本地拓扑矩阵，输出设备 ID 与该设备上的 buffer 注册信息。效果（源码结构可见，量化收益属项目方报告）：多个 slice 交替落在不同网卡上，单流带宽得以聚合；`selectDevice` 携带 `retry_count` 参数，设备忙时换卡重试。

## 第四跳：异步投递与完成

slice 选好设备后交给 `WorkerPool`（`worker_pool.cpp:296` 的 `submitPostSend`），worker 线程池异步发 IB verbs 请求。调用方通过 `getTransferStatus(batch_id, task_id, ...)` 轮询批次状态（`multi_transport.cpp:259` 起实现）。失败路径有三级：slice 级重试（`max_retry_cnt`）、批次级 `fail_task_and_cleanup`（`rdma_transport.cpp:896` 附近的 lambda，把未开始的任务伪造为零长失败 slice 以驱动状态收敛）、以及上层连接器自己的超时处理。

::: mermaid
sequenceDiagram
    participant C as 调用方（Store 客户端 / 连接器）
    participant MT as MultiTransport
    participant RT as RdmaTransport
    participant WP as WorkerPool
    C->>MT: submitTransfer(batch, entries)
    MT->>MT: selectTransport（按段协议路由）
    MT->>RT: submitTransferTask(tasks)
    RT->>RT: 切 slice + selectDevice 选 NIC
    RT->>WP: submitPostSend(slices)
    WP-->>RT: verbs 完成事件
    C->>MT: getTransferStatus(batch_id)
    MT-->>C: COMPLETED / FAILED（含重试后结果）
:::

## 设计取舍

- **切 slice 换来流水线与聚合**：大请求被拆成多个 slice 后，单张网卡的排队不再阻塞整批传输；代价是元数据与状态机开销，slice_size 成为关键调优参数（官方文档 `docs/source/design/transfer-engine/transfer-engine-bench-tuning.md` 专门讨论）。
- **路由在提交时一次决定**：`selectTransports` 在同批次内复用同目标的 transport 结果（`multi_transport.cpp:600` 附近的复用逻辑），批量传输省去重复解析；代价是批次内目标段变化时需显式失效。

## 失败边界

- 目标段协议未安装对应 transport → `NotSupportedTransport`（`multi_transport.cpp:739`）。
- 元数据缓存关闭时，每批都会重新拉取段描述符，路由不复用。
- 本章证据来自经典路径；TENT 的 deadline 调度、QoS、slice spraying 等机制见 `docs/source/design/tent/`（本文未展开）。

## 收束

1. 一次传输 = 协议路由（段描述符）→ slice 切分 → 按拓扑选 NIC → worker 池异步投递 → 状态轮询。
2. 多 NIC 聚合不是魔法，是「slice 粒度 + 拓扑感知的 selectDevice」的组合。
3. 传输与元数据解耦：执行期不再查询元数据服务（缓存命中时）。这是 Store 把数据面整个托付给 TE 的信心来源——下一章看 Store 客户端如何使用它。
