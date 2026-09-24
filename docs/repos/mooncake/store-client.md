---
title: Store 客户端读写黄金路径
weight: 50
---

# Store 客户端读写黄金路径

> 本章沿主线二追踪 `Client::Put` 与 `Client::Get`：控制面（Master RPC）与数据面（TE 直传）如何在一次读写里交替出现。这是 Mooncake Store 的主干。

## 一次 Put：两阶段提交 + 数据直传

`Client::Put(key, slices, config)`（`mooncake-store/src/client_service.cpp:1884`）的骨架：

```cpp
// 1) 可选的对象校验和；Put 前先清本地热缓存
if (hot_cache_) { hot_cache_->RemoveHotKey(key); }

// 2) 控制面：请求 Master 分配副本与 buffer 描述符
auto start_result = master_client_.PutStart(key, slice_lengths, client_cfg);
if (!start_result && start_result.error() == ErrorCode::OBJECT_ALREADY_EXISTS &&
    healDanglingLocalDiskReplica(key)) {
    start_result = master_client_.PutStart(key, slice_lengths, client_cfg);
}

// 3) 数据面：按副本类型逐个写入
for (const auto& replica : start_result.value()) {
    if (replica.is_memory_replica() || replica.is_nof_replica()) {
        ErrorCode transfer_err = TransferWrite(replica, slices);
        ...
    }
}

// 4) 收尾：PutEnd 提交 / PutRevoke 回滚
auto end_result = master_client_.PutEnd(ObjectMeta{key, object_checksum}, ...);
```

要点（实现可见，`client_service.cpp:1884–2040`）：

- **PutStart 返回的是副本描述符列表**，每个描述符含目标段与 buffer 位置——数据面由此知道往哪传。
- **磁盘副本先行**：`storage_backend_` 存在时先写本地磁盘副本（倒序遍历只写一个），注释解释这是因为磁盘副本的 PutRevoke/PutEnd 必须能被调用。
- **部分失败走 PutRevoke**：`DetermineFinalizeDecision` 汇总各副本传输结果，全成功则 `PutEnd`，部分失败则 `PutRevoke`——Master 端据此提交或丢弃元数据（两阶段语义）。
- `OBJECT_ALREADY_EXISTS` 幂等返回空成功；悬空本地磁盘副本会先被修复再重试一次 PutStart。

数据面 `TransferWrite`（`client_service.cpp:4807`）把副本描述符与 slice 列表交给 TE 的批次写接口——即[第 4 章](/repos/mooncake/te-transfer)追踪的那条链。

## 一次 Get：查副本 → 就近读 → 校验 → 填缓存

`Client::Get` 有两个重载；完整路径从 `Query` 开始（`client_service.cpp:1183`）：

```cpp
tl::expected<QueryResult, ErrorCode> Client::Query(const std::string& object_key) {
    auto result = master_client_.GetReplicaList(object_key);
    ...
    return tl::expected<QueryResult, ErrorCode>(
        tl::in_place, std::move(result.value().replicas),
        start_time + std::chrono::milliseconds(result.value().lease_ttl_ms),
        result.value().object_checksum);
}
```

注意两个细节：**Master 在返回副本列表的同时授予了租约**（`lease_ttl_ms`），**并携带对象校验和**。随后 `Client::Get`（`client_service.cpp:1324`）：

```cpp
// 1) 选第一个"完整"副本
ErrorCode err = FindFirstCompleteReplica(query_result.replicas, replica);

// 2) 内存副本可重定向到本地热缓存
if (hot_cache_ && replica.is_memory_replica()) {
    cache_used = RedirectToHotCache(object_key, replica);
}

// 3) DFS 副本走文件系统读，其余走 TE 直读
if (replica.is_dfs_replica()) {
    err = ReadDfsReplica(object_key, replica, slices);
} else {
    err = TransferRead(replica, slices);
}

// 4) 校验 → 按频率准入热缓存 → 租约过期检查
auto checksum_result = VerifyObjectChecksum(...);
if (ShouldAdmitToHotCache(object_key, cache_used)) {
    ProcessSlicesAsync(object_key, slices, replica);
}
if (query_result.IsLeaseExpired()) { ... LEASE_EXPIRED ... }
```

## 副本选择的次序

`FindFirstCompleteReplica`（`client_service.cpp:5272`）决定读哪份副本。副本类型有 MEMORY / NOF_SSD / LOCAL_DISK / DFS 之分（`Replica::Descriptor` 的判别接口在 pybind 绑定中亦可见，`store_py.cpp:2183–2189`）。优先内存副本、其次各磁盘形态，是"读离自己最近、最快的完整副本"策略的实现（解释；完整排序逻辑见该函数实现）。

::: mermaid
sequenceDiagram
    participant App as 推理引擎
    participant Cl as Store 客户端
    participant M as Master
    participant R as 副本节点（经 TE）
    App->>Cl: Put(key, slices)
    Cl->>M: PutStart（分配副本）
    M-->>Cl: 副本描述符列表
    Cl->>R: TransferWrite（数据面直传）
    Cl->>M: PutEnd / PutRevoke
    App->>Cl: Get(key)
    Cl->>M: GetReplicaList（返回副本 + 租约）
    Cl->>Cl: 热缓存命中？
    Cl->>R: TransferRead
    Cl-->>App: slices + 校验
:::

## 失败边界

- 写：任一副本失败即整体 `PutRevoke`（已写成功的副本数据成为垃圾，由 Master 侧淘汰机制回收）。
- 读：租约在传输完成前过期会得到 `LEASE_EXPIRED`——租约是 Master 防止"读到正被淘汰的数据"的手段（[第 6 章](/repos/mooncake/store-master)）。
- 热缓存只服务内存副本，且用 count-min sketch 做频率准入（`ShouldAdmitToHotCache`，实现见 `client_service.cpp`；CMS 数据结构定义于 `mooncake-store/include/count_min_sketch.h`）。

## 收束

1. Put = PutStart（分配）→ 数据直传 → PutEnd/PutRevoke（两阶段）；Get = GetReplicaList（带租约）→ 就近读 → 校验。
2. 客户端同时握着两个世界：`master_client_`（控制面）与 `transfer_engine_`（数据面），Master 永远不搬数据。
3. 热缓存、校验和、租约检查都发生在客户端侧——Master 保持简单的前提是把复杂性推向端点。下一章深入 Master 本体。
