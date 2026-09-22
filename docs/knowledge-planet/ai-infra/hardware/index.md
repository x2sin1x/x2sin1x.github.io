---
title: "算力、存储与网络"
date: 2026-09-22T16:30:00+08:00
weight: 1
---

# 算力、存储与网络

这是 AI Infra 教程的第一站。训练和推理大模型的一切设计，最终都要落到三个物理约束上：&#8203;**算力（每秒能做多少次运算）、存储（数据放在哪、多快能取到）和网络（数据在设备之间怎么搬）**&#8203;。本板块自底向上建立这三个概念，从一颗芯片讲到一个机柜，再到一座装下上万块加速卡的数据中心。

本板块内容：

1. [芯片架构：算力、显存与带宽](/knowledge-planet/ai-infra/hardware/chip-architecture)——认识一块加速芯片里都有什么，理解 Roofline 模型。
2. [显存层次与存储](/knowledge-planet/ai-infra/hardware/memory-hierarchy)——从寄存器到 NVMe 的金字塔，显存放不下怎么办。
3. [超节点](/knowledge-planet/ai-infra/hardware/supernode)——把一个机柜变成一台"大机器"。
4. [万卡集群](/knowledge-planet/ai-infra/hardware/large-scale-cluster)——从机柜到数据中心规模的互联。
5. [容错与 Checkpoint](/knowledge-planet/ai-infra/hardware/fault-tolerance)——规模越大，故障越日常。
6. [集合通信](/knowledge-planet/ai-infra/hardware/collective-communication)——多卡协作的基本语言。

读完本板块，你应当能够对"一块卡够不够用、卡间和机柜间带宽够不够快"做数量级估算，这是后续[训练](/knowledge-planet/ai-infra/training/)与[推理](/knowledge-planet/ai-infra/inference/)板块所有优化技巧的判断依据。
