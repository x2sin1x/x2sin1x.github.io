---
title: Mooncake
weight: 10
---

# Mooncake 源码解读

![](cover.png)

> 快照：`main` 分支，commit `056f67a5947bc6fb3216ff39d5758086cac0e1ba`，核对日期 2026-09-24。正文中的路径、行号与行为描述均以该快照为准（[GitHub 永久链接](https://github.com/kvcache-ai/Mooncake/tree/056f67a5947bc6fb3216ff39d5758086cac0e1ba)）。

Mooncake 是 Kimi（月之暗面）背后的 LLM 推理服务平台，也是一篇 FAST'25 最佳论文的系统实现。它的核心主张是：**以 KVCache 为中心做分离式架构**——把 Prefill 与 Decode 集群分开，再用集群里闲置的 CPU、DRAM 和 SSD 搭一个分布式 KVCache 池。

本系列沿两条端到端主线读源码：

- **数据面**：一次 RDMA 传输如何在 Transfer Engine 里从 `batchTransfer` 走到多网卡聚合与自动重试；
- **缓存面**：一次 `Put`/`Get` 如何在 Mooncake Store 里经过 Master 元数据、副本放置、传输与分层存储。

## 目录

- [定位与总体架构](/repos/mooncake/overview)——KVCache 中心化的分离式架构，三大组件如何分工
- [仓库地图与模块边界](/repos/mooncake/repo-map)——17 个顶层目录各自的职责与依赖方向
- [Transfer Engine：拓扑、元数据与段模型](/repos/mooncake/te-topology)——段描述符、拓扑发现与元数据服务
- [Transfer Engine：一次传输的完整路径](/repos/mooncake/te-transfer)——从批次提交到多 NIC 聚合与重试
- [Store 客户端读写黄金路径](/repos/mooncake/store-client)——Put/Get 两阶段协议与数据面交接
- [Master 服务：元数据、放置与复制](/repos/mooncake/store-master)——副本分配器与放置策略
- [存储后端、淘汰与生命周期](/repos/mooncake/store-storage)——分层存储、Offload 与淘汰策略
- [Python 绑定与推理引擎集成](/repos/mooncake/integration)——vLLM / SGLang 如何挂上 Mooncake
- [部署形态、可观测性与 HA](/repos/mooncake/deployment)——从 wheel 内嵌二进制到 Master 热备
- [附录 A：推荐阅读路径](/repos/mooncake/appendix-reading)
- [附录 B：核心符号速查](/repos/mooncake/appendix-symbols)
- [附录 C：术语表](/repos/mooncake/appendix-glossary)

## References

- [Mooncake 仓库](https://github.com/kvcache-ai/Mooncake)
- [FAST'25 论文《Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving》](https://www.usenix.org/system/files/fast25-qin.pdf)
- [官方文档站](https://kvcache-ai.github.io/Mooncake/)
