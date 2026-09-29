---
title: "量化与稀疏"
date: 2026-09-29T10:00:00+08:00
weight: 8
---

# 量化与稀疏

训练讲究算得快，服务讲究算得省。&#8203;**量化与稀疏是"用精度换资源"的两大手段**&#8203;：量化降低每个数的比特宽度（显存、带宽、算力三本账同时受益），稀疏与剪枝直接删掉不重要的数。本章从原理讲到工业界的主流方法，再讲到蒸馏、剪枝这条"压缩"支线。

本章节内容：

1. [量化基础](/knowledge-planet/ai-infra/quantization/quantization-basics)——为什么低精度可行：定标、对称/非对称、PTQ 与 QAT、FP8。
2. [主流量化方法：GPTQ、AWQ 与 SmoothQuant](/knowledge-planet/ai-infra/quantization/quantization-methods)——三大算法的核心思想与适用场景。
3. [蒸馏、剪枝与稀疏化](/knowledge-planet/ai-infra/quantization/compression)——结构化/非结构化剪枝的硬件友好性、知识蒸馏与 2:4 稀疏。

阅读前提：[芯片架构](/knowledge-planet/ai-infra/hardware/chip-architecture)的 Roofline 模型（量化为什么能同时省带宽与算力）与 [KV Cache](/knowledge-planet/ai-infra/inference/kv-cache)篇（KV 量化是长上下文服务的关键杠杆）。这些方法最终由[推理引擎](/knowledge-planet/ai-infra/inference/)落地执行。
