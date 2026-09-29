---
title: "高性能计算"
date: 2026-09-29T10:00:00+08:00
weight: 4
---

# 高性能计算

[硬件架构](/knowledge-planet/ai-infra/hardware/)章给了 Roofline 模型：性能上限由算力与显存带宽的较小者决定。但真实代码很少自己逼近上限——差距要靠**手写与调优 kernel** 来填补。本章讲 kernel 层的工程：怎么写 CUDA、怎么评估和优化一个算子、以及大模型时代最重要的一个 kernel 家族（attention）是如何被重写的。

本章节内容：

1. [CUDA 编程模型](/knowledge-planet/ai-infra/hpc/cuda-programming)——线程层次、shared memory、stream/event 同步、CUDA Graph 与资源管理。
2. [算子优化与融合](/knowledge-planet/ai-infra/hpc/operator-optimization)——Triton vs CUDA、算子融合的收益评估、coalescing/bank conflict/occupancy 的权衡。
3. [Attention Kernel：FlashAttention 与它的后继者](/knowledge-planet/ai-infra/hpc/attention-kernels)——IO-aware 设计如何把 attention 从显存囚笼里解放出来。

与[框架与编译](/knowledge-planet/ai-infra/framework/)章的分界：本章讲 kernel 本身（换一种框架它依然成立），框架章讲图的构建与编译（Dynamo/Inductor/TVM 如何生成或调度这些 kernel）。
