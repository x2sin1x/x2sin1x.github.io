---
title: "存储与 I/O"
date: 2026-09-29T10:00:00+08:00
weight: 10
---

# 存储与 I/O

GPU 之外的一切慢环节，最终都会显形为存储与 I/O 问题：万卡训练的 checkpoint 轻松超过 10 TB，每几分钟就要写一次；数据管道喂不饱 GPU，再强的集群也在空转。本章讲训练与推理共同依赖的存储基础设施：模型状态怎么存、训练数据怎么流。

本章节内容：

1. [Checkpoint 存储与加载](/knowledge-planet/ai-infra/storage/checkpoint-storage)——safetensors/DCP 格式、TB 级状态的高效写入与加载、多节点一致性。
2. [数据管道与存储选型](/knowledge-planet/ai-infra/storage/data-pipeline)——分布式文件系统选型、缓存策略、GPU 解码与数据分片。

与其他章节的分工：容错视角下"为什么要频繁 checkpoint"见[容错与 Checkpoint](/knowledge-planet/ai-infra/distributed/fault-tolerance)篇，本章只管"怎么存得快、读得快"；数据管道的训练侧应用见[训练 Infra](/knowledge-planet/ai-infra/training/training-infra)篇。
