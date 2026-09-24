---
title: 存储后端、淘汰与生命周期
weight: 70
---

# 存储后端、淘汰与生命周期

> 本章回答：一个对象从内存副本开始，如何被 Offload 到磁盘/DFS、如何被淘汰、如何恢复。这补齐黄金路径之外的「为什么能长期运行」。

## 分层存储：副本类型即层级

第 5 章已见副本有 MEMORY / NOF_SSD / LOCAL_DISK / DFS 四种形态。把它们串起来的是 **Offload（内存 → 慢介质）与 Load（慢介质 → 内存）**。抽象接口是 `StorageBackendInterface`（`mooncake-store/include/storage_backend.h:262`）：

```cpp
virtual tl::expected<int64_t, ErrorCode> BatchOffload(
    const std::unordered_map<std::string, std::vector<Slice>>& batch_object,
    std::function<ErrorCode(const std::vector<std::string>& keys,
                            std::vector<StorageObjectMetadata>& metadatas)>
        complete_handler,
    EvictionHandler eviction_handler = nullptr) = 0;

virtual tl::expected<void, ErrorCode> BatchLoad(
    std::unordered_map<std::string, Slice>& batched_slices) = 0;
```

三个设计点（实现可见）：

- `BatchOffload` 携带 `complete_handler`——后端写完后回调 Master 更新元数据（副本形态迁移），`eviction_handler` 则让后端能在写入前触发容量回收；
- `ScanMeta` + `ResetScanIterator` 支持游标式扫描持久化元数据，用于 Master 重启后从存储后端重建索引（`storage_backend.h:292` 附近的注释说明其用于 cursor-based 迭代）；
- 具体后端按介质分目录实现：`src/local_ssd/`、`src/hf3fs/`（DeepSeek 3FS 分布式文件系统）、`src/spdk/`、`src/nvme_kv/`，另有 S3 等对象存储（`docs/source/design/store/oss-backend.md`）。

## 淘汰策略：可插拔的容量守门人

内存池写满时，Master 需要选key淘汰。策略接口（`mooncake-store/include/eviction_strategy.h:16`）：

```cpp
class EvictionStrategy : public std::enable_shared_from_this<EvictionStrategy> {
   public:
    virtual ErrorCode AddKey(const std::string& key) = 0;
    virtual ErrorCode UpdateKey(const std::string& key) = 0;
    virtual std::string EvictKey(void) = 0;
   protected:
    std::list<std::string> all_key_list_;
    std::unordered_map<std::string, std::list<std::string>::iterator>
        all_key_idx_map_;
};
```

内置 `LRUEvictionStrategy`（`:43`）与 `FIFOEvictionStrategy`（`:79`）。KVCache 的访问模式高度偏向"重复前缀"，纯 LRU 不一定最优——客户端侧的热缓存因此用 **count-min sketch 做频率准入**（[第 5 章](/repos/mooncake/store-client)的 `ShouldAdmitToHotCache`；CMS 头文件 `count_min_sketch.h`），两级缓存一个看频率、一个看时间，分工明确（解释）。

## 客户端热缓存

`local_hot_cache.h/.cpp` 实现节点本地的 DRAM 缓存：`RedirectToHotCache` 在 Get 时命中则把副本描述符改指本地；`ReleaseHotKey` 在 memcpy 完成后释放引用（见 `client_service.cpp:1338–1348`）。它是客户端私有的，不需要 Master 参与——代价是每个节点各留一块内存。

## 快照与恢复

Master 重启不能丢掉整个池的元数据。`src/ha/` 下的 `snapshot/`（含 `MasterSnapshotManager`、oplog 批处理 `batch_oplog/`）与 `master_snapshot_manager.cpp` 负责：周期快照 + 操作日志，重启时经 `ScanMeta`/快照回放重建（细节见[第 9 章](/repos/mooncake/deployment)）。生命周期闭环如下：

::: mermaid
flowchart LR
    W["Put 写入内存副本"] --> H["热度提升：进入本地热缓存"]
    W --> O["容量压力：Offload 到 SSD / DFS"]
    O --> L["Get 未命中内存：Load 回内存"]
    W --> E["淘汰策略选 key：元数据删除 + 存储回收"]
    O --> E
:::

## 失败边界

- Offload 期间的对象同时存在两种副本描述符形态，读路径由 `FindFirstCompleteReplica` 兜底选完整副本。
- 淘汰受租约约束：被读租约保护的对象不能立即淘汰（[第 6 章](/repos/mooncake/store-master)）。
- SPDK / 3FS 等后端依赖特定内核与硬件环境，属部署期选择（`mooncake-store/CMakeLists.txt` 的编译开关）。

## 收束

1. 分层 = 副本形态迁移，接口是 `BatchOffload`/`BatchLoad` + 元数据回调。
2. 淘汰是 Master 侧策略（LRU/FIFO），热缓存是客户端侧策略（频率准入），两者不混在一层。
3. 快照 + oplog + 存储后端扫描，构成 Master 重启恢复的三条证据链。
