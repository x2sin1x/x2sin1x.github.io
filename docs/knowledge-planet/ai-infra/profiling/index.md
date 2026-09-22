---
title: "Profiling 性能分析"
date: 2026-09-22T18:00:00+08:00
weight: 1
---

# Profiling 性能分析

> 前三个板块给了你所有理论模型（Roofline、$6ND$、allreduce、气泡率），这一板块回答：&#8203;**真实的系统到底怎么样？时间去哪了？**

本板块内容：

1. [性能指标](/knowledge-planet/ai-infra/profiling/metrics)——MFU、TTFT/TPOT、goodput、带宽利用率，各自衡量什么、如何计算。
2. [性能分析工具](/knowledge-planet/ai-infra/profiling/tools)——PyTorch Profiler、Nsight、HolisticTraceAnalysis，以及如何读懂一张时间线。

方法论预告：&#8203;**先有模型（理论预期），再有 profile（实测数据），两者的差值就是优化空间**&#8203;。没有理论模型的 profiling 是一堆花哨的火焰图，没有 profiling 的理论模型是纸上谈兵。
