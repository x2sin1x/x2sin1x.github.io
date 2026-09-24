---
title: 附录 B：核心符号速查
weight: 110
---

# 附录 B：核心符号速查

> 行号与 commit 对应[首页](/repos/mooncake/)固定的快照 `056f67a`；跳转前请核对该快照。

## Transfer Engine

| 符号 | 职责 | 定义位置 | 主要调用者 | 章节 |
| --- | --- | --- | --- | --- |
| `TransferEngine::init` | 初始化引擎、连接元数据服务 | `transfer_engine.h:108` | 所有使用者（Store 客户端、连接器） | 3 |
| `TransferEngine::openSegment` | 打开远端段，取得句柄 | `transfer_engine.cpp:678` | Store 客户端、连接器 | 3 |
| `TransferEngine::registerLocalMemory` | 登记本地 buffer 到段描述符 | `transfer_engine.cpp:167` | Store 客户端、连接器 | 3 |
| `Topology::discover` | 枚举本机 HCA / CPU / GPU 亲和 | `topology.cpp:625` | 引擎初始化 | 3 |
| `MultiTransport::selectTransport` | 按段协议为请求选 transport | `multi_transport.cpp:623` | `submitTransports` 路由 | 4 |
| `RdmaTransport::submitTransferTask` | slice 切分、设备选择与投递 | `rdma_transport.cpp:856` | MultiTransport | 4 |
| `RdmaTransport::selectDevice` | 为 slice 选择本地网卡（多 NIC 聚合） | `rdma_transport.cpp:1299` 附近 | submitTransferTask | 4 |
| `WorkerPool::submitPostSend` | 异步投递 verbs 请求 | `worker_pool.cpp:296` | RdmaTransport | 4 |

## Mooncake Store

| 符号 | 职责 | 定义位置 | 主要调用者 | 章节 |
| --- | --- | --- | --- | --- |
| `Client::Put` | 两阶段写：PutStart → 直传 → PutEnd/Revoke | `client_service.cpp:1884` | Python 绑定 / 上层 | 5 |
| `Client::Get` | 查副本（带租约）→ 就近读 → 校验 | `client_service.cpp:1111` / `:1324` | Python 绑定 / 上层 | 5 |
| `Client::Query` | 调 Master `GetReplicaList` 并封装租约 | `client_service.cpp:1183` | Client::Get | 5 |
| `Client::FindFirstCompleteReplica` | 副本选择次序 | `client_service.cpp:5272` | Client::Get | 5 |
| `Client::TransferWrite / TransferRead` | 数据面交接给 TE | `client_service.cpp:4807` / `:4825` | Put / Get | 5 |
| `MasterService::GetReplicaList` | 元数据读 + 授租约 | `master_service.h:416` | master_client RPC | 6 |
| `MasterService::PutStart` | 副本分配入口 | `master_service.h:452` | master_client RPC | 6 |
| `ReplicaAllocator<Policy>` | 可插拔副本放置（5 种策略） | `placement/replica_allocator.h:88` | MasterService | 6 |
| `EvictionStrategy`（LRU/FIFO） | 容量压力下的 key 淘汰 | `eviction_strategy.h:16` / `:43` / `:79` | MasterService | 7 |
| `StorageBackendInterface` | Offload / Load / 扫描元数据抽象 | `storage_backend.h:262` | 各存储后端 | 7 |
| `LocalHotCache` | 节点本地 DRAM 读缓存 | `local_hot_cache.h` | Client::Get | 5, 7 |

## 集成与运维

| 符号 | 职责 | 定义位置 | 主要调用者 | 章节 |
| --- | --- | --- | --- | --- |
| `MooncakeDistributedStore`（绑定类） | Store 的 Python 门面 | `store_py.cpp:2376` | vLLM / SGLang 连接器 | 8 |
| `pub_tensor` / `get_tensor` | 张量语义读写（含 TP 变体） | `store_py.cpp:2657–2696` | 连接器 | 8 |
| `TransferEnginePy` 绑定 | TE 的 Python 门面 | `transfer_engine_py.cpp:1526` 起 | PD 连接器 | 8 |
| `_launcher.locate` | 定位 wheel 内嵌 C++ 二进制 | `python/mooncake/_launcher.py:19` | CLI shim | 9 |
| `MasterSnapshotManager` | 快照与恢复 | `master_snapshot_manager.cpp` | HA 体系 | 7, 9 |
| `standby_state_machine` | 热备状态机 | `standby_state_machine.h` | HA 体系 | 9 |
