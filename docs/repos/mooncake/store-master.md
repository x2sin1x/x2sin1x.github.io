---
title: Master 服务：元数据、放置与复制
weight: 60
---

# Master 服务：元数据、放置与复制

> 本章回答：Master 在 PutStart/GetReplicaList 之间到底做什么——对象索引、副本放置策略、租约与配额如何支撑客户端的黄金路径。

## Master 的职责边界

`MasterService`（`mooncake-store/include/master_service.h:127`）持有全部对象的元数据：每个 key 对应一组 `Replica::Descriptor`（副本类型、所在段、buffer 位置、大小）。它提供 gRPC 服务（`rpc_service.cpp`），核心方法与客户端一一对应：

```cpp
auto GetReplicaList(const std::string& key, const TenantId& tenant_id)
    -> tl::expected<GetReplicaListResponse, ErrorCode>;   // master_service.h:416
auto PutStart(const UUID& client_id, const std::string& key, ...)
    -> ...;                                               // master_service.h:452
```

头文件注释区分了两个读语义：`GetReplicaList` 会**授予租约并触发相关机制**，而 `BatchGetReplicaList` 的某些变体"不授予租约、不触发"（`master_service.h:432–437` 附近的注释）——租约与读路径绑定的设计在接口层就已显形。

## 副本放置：策略化的分配器

PutStart 的关键问题是"新副本放在哪些段"。Store 把这件事抽成了可插拔的策略模板 `ReplicaAllocator`（`mooncake-store/include/placement/replica_allocator.h:88`），并显式实例化了五种放置策略（`mooncake-store/src/placement/replica_allocator.cpp:442–446`）：

```cpp
template class ReplicaAllocator<RandomPlacementPolicy>;
template class ReplicaAllocator<FreeRatioFirstPlacementPolicy>;
template class ReplicaAllocator<SsdFreeRatioFirstPlacementPolicy>;
template class ReplicaAllocator<LocalFirstPlacementPolicy>;
template class ReplicaAllocator<PreferredOnlyPlacementPolicy>;
```

| 策略 | 直观语义 |
| --- | --- |
| Random | 随机挑选可用段 |
| FreeRatioFirst | 优先剩余容量比例大的段 |
| SsdFreeRatioFirst | 同上，但面向 SSD 段（设计文档 `docs/source/design/store/ssd-free-ratio-first-allocation.md`） |
| LocalFirst | 优先调用者本地段 |
| PreferredOnly | 只放在 `config.preferred_segment` 指定的段 |

客户端 `ReplicateConfig` 里能看到策略的消费点：`Client::Put` 在 CXL 协议下把 `preferred_segment` 设为本地主机名（`client_service.cpp:1905`），正是给 PreferredOnly / LocalFirst 用的。

## 租约与淘汰的握手

Master 元数据是共享的、可变的；客户端读到的副本列表必须保证在数据搬完之前不被淘汰。Store 的解法是**读租约**：`GetReplicaList` 返回 `lease_ttl_ms`，客户端在传输后检查 `IsLeaseExpired()`（[第 5 章](/repos/mooncake/store-client)）。租约类型与表结构定义于 `mooncake-store/include/lease.h` 与 `dynamic_replication_lease_table.h`。

::: mermaid
stateDiagram-v2
    [*] --> Pending: PutStart（分配副本描述符）
    Pending --> Complete: PutEnd（全部副本传输成功）
    Pending --> [*]: PutRevoke（部分失败，丢弃元数据）
    Complete --> Evicted: 容量压力 / 淘汰策略
    Evicted --> [*]
    note right of Complete: 读操作挂租约，阻止读期间被淘汰
:::

## 多租户配额

Master 还持有租户配额账本：`master_service.h:151–156` 暴露 `GetStorageUsageSnapshot` / `UpsertTenantQuotaPolicy` 等接口，实现分散在 `tenant_quota*.h/cpp` 系列文件（含分片实现 `tenant_quota_sharded_impl.h`）。这是"KVCache 池被多个推理实例共享时防止互相挤占"的控制面手段。

## 失败边界

- Master 是单点元数据权威；其可用性由独立的 HA 体系保障（快照 + oplog + 热备，见[第 9 章](/repos/mooncake/deployment)的 `mooncake-store/src/ha/`）。
- 本文未逐行核对 1.5 万行 `master_service.cpp` 的每个分支；上述内容覆盖主链（PutStart 分配 → 租约 → 提交/回滚），更细的并发与恢复机制留待后续版本补充。

## 收束

1. Master = 对象索引 + 副本分配器 + 租约管理 + 配额账本；数据零经过。
2. 放置策略是编译期实例化的五种模板，面向不同介质（内存/SSD）与亲和性需求。
3. 读租约把"元数据一致性"和"数据搬运窗口"连在一起——这是第 7 章淘汰机制的约束条件。
