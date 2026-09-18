---
title: "深入理解 AI Infra：量化分析与系统设计"
date: 2026-05-01T10:00:00+08:00
weight: 106
---
# 深入理解 AI Infra：量化分析与系统设计

**数据搬移塑造了 AI Infra 的架构。** 从一次模型执行开始，理解芯片、网络、推理与训练系统如何改变数据的复用、放置和等待。

[下载全书 PDF](https://github.com/bojieli/ai-infra-book/releases/latest/download/AI-Infra-Book.pdf) · [前言](/knowledge-planet/ai-infra-book/preface/) · [GitHub 仓库](https://github.com/bojieli/ai-infra-book)

## 这本书写什么

《深入理解 AI Infra》是 GitHub 上获得 45k+ Star 的[《深入理解 AI Agent：设计原理与工程实践》](https://github.com/bojieli/ai-agent-book)的姊妹篇。

写完《深入理解 AI Agent》后，在与读者交流的过程中，作者越来越感到：要开发好基于模型的应用，还需要理解它赖以运行的基础设施。大多数软件工程师不必亲自开发操作系统、编译器和芯片，却仍要学习操作系统、编译原理和计算机体系结构，因为申请内存、读取文件、调用函数，背后都有资源与时间代价。基于模型开发应用也是如此。延迟相差几倍，产品体验就可能完全不同；成本相差一个数量级，能够支撑的商业模式也随之改变。

更深层的变化是**编程抽象的上移：从操作系统到模型上下文**。传统的操作系统、编译器和硬件要为事先未知的各种程序提供通用能力，系统优化总要在可编程性与性能之间取舍。如今 LLM 成了最重要的应用，从算子执行到分布式调度，都可以针对特定的模型和加速器架构优化；模型设计也开始反过来适应硬件。从某种意义上说，**模型成了 LLM 时代的操作系统，AI Infra 成了 LLM 时代的计算机体系结构**。

贯穿全书的方法是**从约束推导设计**：先明确任务与质量要求，列出计算、存储、通信和依赖关系，对照硬件的容量、带宽和算力做数量级估算。这类估算人容易出错，AI 也一样：只算权重读取而忘了 KV 缓存，按峰值算力推算速度而不查带宽能否供给，把工作平分给多张卡却遗漏卡间通信，漏掉任何一项，结论都可能偏离几倍甚至几个数量级。从 FPGA 加速 Bing 搜索排序、昇腾 AKG 算子生成到 UB 万卡互联，反复出现的是同一条线索：**数据搬移**。本书因此反复追问五个问题：**搬什么、搬多少、搬几次、经过哪里、谁必须等它。**

更多写作背景见[前言](/knowledge-planet/ai-infra-book/preface/)。目前书稿仍是初稿，正在持续修订。

## 十二章导读

从一次模型执行的资源账开始，依次走过模型架构与负载、加速器与算子、超节点与网络、推理与训练系统，最后回到调度与端边云的部署选择。

| 章 | 主题 | 主要问题 |
| :--: | --- | --- |
| 1 | [初识 AI Infra](/knowledge-planet/ai-infra-book/01-introducing-ai-infra/) | 一次生成需要多少显存、计算和数据读写？ |
| 2 | [模型架构](/knowledge-planet/ai-infra-book/02-model-architecture/) | 注意力、历史状态与专家结构如何改变系统需求？ |
| 3 | [推理与训练负载](/knowledge-planet/ai-infra-book/03-inference-training-workloads/) | 任务阶段、到达模式和状态寿命如何影响资源需求？ |
| 4 | [加速器架构](/knowledge-planet/ai-infra-book/04-accelerator-architecture/) | 如何在计算、存储、带宽、功耗与成本之间取舍？ |
| 5 | [算子与运行时](/knowledge-planet/ai-infra-book/05-operators-and-runtime/) | 融合、复用、并发和调度如何减少执行开销？ |
| 6 | [超节点](/knowledge-planet/ai-infra-book/06-supernode/) | 多设备协作如何平衡容量、吞吐和同步代价？ |
| 7 | [数据中心网络](/knowledge-planet/ai-infra-book/07-datacenter-network/) | 网络带宽、通信方式和拥塞怎样影响计算效率？ |
| 8 | [推理优化](/knowledge-planet/ai-infra-book/08-inference-optimization/) | 批处理、KV 管理、卸载与推测解码何时有效？ |
| 9 | [分布式推理](/knowledge-planet/ai-infra-book/09-distributed-inference/) | 如何放置计算和状态，并处理扩缩容与恢复？ |
| 10 | [训练系统](/knowledge-planet/ai-infra-book/10-training-systems/) | 怎样安排显存、通信和重算，让训练更高效？ |
| 11 | [资源调度与运行环境](/knowledge-planet/ai-infra-book/11-resource-scheduling-and-runtime/) | 模型服务和工具环境如何共享资源，减少等待？ |
| 12 | [端边云协同](/knowledge-planet/ai-infra-book/12-device-edge-cloud/) | 任务放在本地、边缘还是云端，怎样兼顾效果、延迟和成本？ |

## 怎么读

按左侧目录从[前言](/knowledge-planet/ai-infra-book/preface/)和第一章顺序读下来最省力，前面章节建立的模型、硬件和负载设定，后面各章会反复用到。也可以用搜索直接查找某个模型、算子或系统机制。每章提供公式、表格、配图与脚注，正文中指向计算结果、实验记录等配套材料的链接会跳转到 GitHub 仓库对应的文件。

书中有大量公式、表格与交叉引用，完整排版以 [PDF 版](https://github.com/bojieli/ai-infra-book/releases/latest/download/AI-Infra-Book.pdf)为准。

## 版权说明

本书由李博杰撰写，原文以 [Apache License 2.0](https://github.com/bojieli/ai-infra-book/blob/main/LICENSE) 协议在 [GitHub 仓库](https://github.com/bojieli/ai-infra-book)开源，本站转载自该仓库 `manuscripts/` 目录下的书稿，内容未作删改，章节结构保持一致。书中的数字大多可以复算，量化计算工具、配套实验与配图脚本均见原仓库。
