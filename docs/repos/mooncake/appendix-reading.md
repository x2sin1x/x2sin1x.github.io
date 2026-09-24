---
title: 附录 A：推荐阅读路径
weight: 100
---

# 附录 A：推荐阅读路径

> 不同读者带着不同问题来。下表按目标组织本系列与源码的对应阅读顺序，不只是目录重排。

## 想快速理解架构（30 分钟）

1. [第 1 章：定位与总体架构](/repos/mooncake/overview)——建立 KVCache 中心化的心智模型。
2. [第 2 章：仓库地图](/repos/mooncake/repo-map)——知道东西在哪。
3. 官方设计文档 `docs/source/design/transfer-engine/index.md` 与 `docs/source/design/store/mooncake-store.md`。

## 想理解核心贡献（传输引擎，半天）

1. [第 3 章：拓扑、元数据与段模型](/repos/mooncake/te-topology)
2. [第 4 章：一次传输的完整路径](/repos/mooncake/te-transfer)——读时对照 `multi_transport.cpp:623`（selectTransport）与 `rdma_transport.cpp:856`（submitTransferTask）。
3. 进阶：`docs/source/design/tent/`（新一代实现的 deadline 调度、QoS、failover）。

## 想理解核心贡献（分布式缓存，半天）

1. [第 5 章：Store 客户端读写黄金路径](/repos/mooncake/store-client)
2. [第 6 章：Master 服务](/repos/mooncake/store-master)——对照 `replica_allocator.h:88` 与五种放置策略。
3. [第 7 章：存储后端与生命周期](/repos/mooncake/store-storage)

## 想做集成开发（连接器 / 二次开发）

1. [第 8 章：Python 绑定与集成](/repos/mooncake/integration)
2. 源码：`mooncake-integration/transfer_engine/transfer_engine_py.cpp`（API 面）与 `mooncake-integration/store/store_py.cpp`（张量 API）。
3. 参考 vLLM 的 Mooncake Connector 实现方式（在上游仓库），或仓库内 `mooncake-transfer-engine/example/` 的 C++ 示例。

## 想做生产运维

1. [第 9 章：部署、可观测性与 HA](/repos/mooncake/deployment)
2. [第 6 章](/repos/mooncake/store-master)的租约语义与 [第 7 章](/repos/mooncake/store-storage)的淘汰机制——故障排查时最常牵涉的两块。
3. `monitoring/` 下的 Prometheus 抓取配置与 Grafana dashboard。

## 想读论文再看代码（研究向）

1. FAST'25 论文（见[仓库首页](/repos/mooncake/)References）。
2. [第 1 章](/repos/mooncake/overview) → [第 4 章](/repos/mooncake/te-transfer)（论文的传输聚合与故障切换机制落地）→ [第 5–7 章](/repos/mooncake/store-client)（KVCache 池，论文之后演进出 Master/HA 体系）。
3. `FAST25-release/traces/` 有论文所用请求 trace，可复现实验语境。
