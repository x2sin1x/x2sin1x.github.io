---
title: "硬件架构"
date: 2026-09-22T16:30:00+08:00
weight: 1
---

# 硬件架构

这是 AI Infra 教程的第一站。一切上层设计最终都落到一颗加速芯片的物理约束上：&#8203;**算力（每秒能做多少次运算）、显存容量（数据放得下吗）、显存带宽（数据多快能取到）**&#8203;。本章自底向上建立这三个概念，先看一颗芯片里有什么，再看数据在芯片内的存储金字塔。

本章节内容：

1. [芯片架构：算力、显存与带宽](/knowledge-planet/ai-infra/hardware/chip-architecture)——计算单元与执行模型、Hopper/Blackwell/达芬奇架构对比、Roofline 模型。
2. [显存层次与存储](/knowledge-planet/ai-infra/hardware/memory-hierarchy)——从寄存器到 NVMe 的金字塔，显存放不下怎么办。

读完本章，你应当能够对"一块卡够不够用、瓶颈在算力还是带宽"做数量级估算。多颗芯片如何协作，见[分布式系统](/knowledge-planet/ai-infra/distributed/)章；跑在芯片上的代码如何逼近硬件极限，见[高性能计算](/knowledge-planet/ai-infra/hpc/)章。
