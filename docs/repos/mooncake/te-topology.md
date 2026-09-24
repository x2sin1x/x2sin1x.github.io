---
title: Transfer Engine：拓扑、元数据与段模型
weight: 30
---

# Transfer Engine：拓扑、元数据与段模型

> 本章回答：TE 如何让"向另一台机器的某块内存写数据"变成一个可编程的操作。这是理解第 4 章传输路径的前提。

## 三个核心抽象

TE 的世界模型由三个概念构成（符号均定义于 `mooncake-transfer-engine/include/`）：

1. **Segment（段）**：一个远端节点暴露的内存区间集合，有全局唯一名字（如 `192.168.1.10:12345`）。
2. **Topology（拓扑）**：本机的网卡（HCA）、CPU 与 GPU 的亲和关系，用来选路。
3. **TransferMetadata（元数据）**：把段名字解析成段描述符、把本机段广播出去的注册中心。

`TransferEngine::init` 把三者串起来（`transfer_engine.h:109` 声明）：

```cpp
int init(const std::string& metadata_conn_string,
         const std::string& local_server_name,
         const std::string& ip_or_host_name = "",
         uint64_t rpc_port = 12345);
```

- `metadata_conn_string` 指向元数据服务（支持 `etcd://` 或 `http://`，由 `transfer_metadata_plugin.cpp` 的插件机制解析——该文件引入了 `etcd/SyncClient.hpp` 并实现了 HTTP GET/PUT/DELETE）；
- `local_server_name` 是本段的名字，也写进元数据供他人发现。

## 段描述符：一切路由的依据

远端段经 `openSegment(name)` 打开后得到句柄，此后每次传输只需要句柄 + 偏移量。段描述符 `SegmentDesc` 携带该节点的协议名、buffer 列表和设备拓扑。元数据的读接口（`transfer_metadata.h:240`）：

```cpp
std::shared_ptr<SegmentDesc> getSegmentDescByID(SegmentID segment_id, ...);
int updateLocalSegmentDesc(SegmentID segment_id = LOCAL_SEGMENT_ID);
```

本机侧对称的入口是 `registerLocalMemory(addr, length, location, ...)`（`transfer_engine.h:158` 附近声明，`transfer_engine.cpp:167` 转发实现）：把一块本地内存登记进自己的段描述符并广播到元数据服务，远端才能定位到它。`location` 参数是拓扑提示（如 `cuda:0`），wildcard 值表示"任意位置可达"。

## 拓扑发现：多网卡聚合的地基

`Topology::discover`（`topology.cpp:625`）在初始化时枚举本机 HCA 与 CPU/GPU 的亲和关系，构建 `topology matrix`。它是第 4 章 `selectDevice` 能"按 buffer 位置挑最近网卡"的前提——没有拓扑，多 NIC 只能轮询，有拓扑才能做带宽聚合与就近选路。

::: mermaid
flowchart LR
    A["init(metadata_conn, local_name)"] --> B["Topology::discover<br/>枚举 HCA / CPU / GPU 亲和"]
    B --> C["注册本地 buffer<br/>registerLocalMemory"]
    C --> D["updateLocalSegmentDesc<br/>写段描述符到元数据服务"]
    E["openSegment(remote_name)"] --> F["元数据服务返回 SegmentDesc"]
    F --> G["后续传输：handle + offset"]
:::

## 消费者视角

TE 的使用者（Store 客户端、各推理引擎连接器）典型序列是：`init` → `registerLocalMemory`（本机 KVCache 显存）→ `openSegment`（对端）→ `allocateBatchID` + `submitTransfer`（发起传输）→ `getTransferStatus`（等待完成）。Python 绑定暴露同构的 API（`mooncake-integration/transfer_engine/transfer_engine_py.cpp:1526` 起的 `.def(...)` 列表），详见[第 8 章](/repos/mooncake/integration)。

## 失败边界

- 元数据服务不可用时，`openSegment` 无法解析新段名；已解析段是否可继续传输取决于缓存与探测策略（TE 内置 liveness 探测 `probePeerAliveByID`，`transfer_engine.h:258` 声明）。
- 本章只覆盖控制面；传输执行、slice 切分、重试与多 NIC 选择全部推迟到[第 4 章](/repos/mooncake/te-transfer)。

## 收束

1. TE 用「段 + 偏移」统一寻址，元数据服务是名字到描述符的解析点。
2. `registerLocalMemory` 是把本地内存暴露给远端的前提，拓扑发现支撑后续的设备选择。
3. 默认实现是经典 `MultiTransport` 路径，`MC_USE_TENT` 才切换新一代实现（[第 1 章](/repos/mooncake/overview)）。
