---
title: "框架与编译"
date: 2026-09-29T10:00:00+08:00
weight: 5
---

# 框架与编译

[高性能计算](/knowledge-planet/ai-infra/hpc/)章讲了 kernel 怎么写，但没有人手写大模型的每一个 kernel——框架负责把用户代码变成计算图，编译器负责把计算图变成高效的 kernel 序列。本章讲这一层：框架的内部机制（理解它才能调试和扩展它），以及 torch.compile 与 AI 编译器的技术路线。

本章节内容：

1. [PyTorch 内部机制](/knowledge-planet/ai-infra/framework/pytorch-internals)——autograd、dispatch、CachingAllocator、hook 与混合精度：框架的五个地基。
2. [torch.compile：Dynamo → Inductor → Triton](/knowledge-planet/ai-infra/framework/torch-compile)——PyTorch 2.x 的编译栈如何把 Python 代码变成融合 kernel。
3. [AI 编译器：XLA、TVM、MLIR 与 TensorRT](/knowledge-planet/ai-infra/framework/compilers)——四条技术路线的对比与取舍。

与相邻章节的分界：kernel 本身见[高性能计算](/knowledge-planet/ai-infra/hpc/)章；编译后的执行如何摊到多卡，见[并行策略](/knowledge-planet/ai-infra/parallelism/)章。
