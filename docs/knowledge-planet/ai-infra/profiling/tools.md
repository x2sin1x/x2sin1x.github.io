---
title: "性能分析工具"
date: 2026-09-22T18:00:00+08:00
weight: 20
---

# 性能分析工具

> 模型有了，指标定了，现在需要显微镜。&#8203;**这一篇讲工具箱和读时间线的手法。**

## 工具地图

| 层次 | 工具 | 看什么 |
| ---- | ---- | ---- |
| 框架级 | PyTorch Profiler / Kineto | 算子耗时、CPU-GPU 异步、内存分配 |
| GPU 内核级 | NVIDIA Nsight Compute | 单 kernel 的 roofline（SOL）、显存/算力瓶颈 |
| 系统级时间线 | NVIDIA Nsight Systems | kernel 间隙、通信、NCCL 流水线 |
| 集群级 | HTA、MegaScale 诊断 | 多卡对齐时间线、慢卡/慢链路定位 |
| 推理服务 | vLLM/SGLang metrics + Prometheus | TTFT/TPOT 分布、batch 满载率、缓存命中 |

**读法由外向内**&#8203;：先系统级时间线找大块异常（间隙、等待、长尾），再下钻内核级找单点原因。反过来先看单 kernel 效率，容易在错误的热点上刨地。

## 训练：一张时间线的读法

以 PyTorch Profiler + Nsight Systems 的典型训练步时间线为例，四个必查点：

1. **kernel 间隙（gap）**&#8203;：相邻 kernel 间的空洞。小间隙是 kernel 启动开销/同步（用 CUDA Graph 消）；大间隙是 CPU 瓶颈（数据预处理、Python 调度）——&#8203;**上万卡集群里 1 ms 的 Python 逻辑就是每天数千 GPU 时**&#8203;；
2. **通信与计算的重叠**&#8203;：NCCL kernel 应与计算 kernel 时间上并行（不同 stream）。顺序执行的 allreduce = overlap 失败，回查[数据并行](/knowledge-planet/ai-infra/training/parallelism/data-parallelism)篇的 bucket 配置；
3. **流水线的对齐**&#8203;：多卡时间线叠放对齐，看 PP 各 stage 是否齐步（[气泡](/knowledge-planet/ai-infra/training/parallelism/pipeline-parallelism)）；MegaScale 式诊断把流水线组事件汇到统一时间线（[容错](/knowledge-planet/ai-infra/hardware/fault-tolerance)篇图示）；
4. **内存水位**&#8203;：allocator 的峰值与碎片（torch.cuda.memory_stats），对照[显存层次](/knowledge-planet/ai-infra/hardware/memory-hierarchy)篇的账目。

## 推理：服务指标下钻

服务级 metric（Prometheus 的 TTFT/TPOT 直方图）发现异常后，下钻路径：

::: mermaid
flowchart TB
    A["SLO 违约<br/>（P99 TTFT/TPOT）"] --> B{"哪段慢？"}
    B -- "排队时间" --> C["准入/扩容<br/>（Little 定律）"]
    B -- "prefill" --> D["[前缀缓存]命中率？chunk 大小？"]
    B -- "decode" --> E["batch 满载率？KV 驱逐？swap？"]
    D --> F["[量化]/[投机采样]开关"]
    E --> F
:::

引擎内置的可观测性（vLLM 的 metrics 端点、SGLang 的 router 统计）已覆盖大部分分层，&#8203;**关键是把业务监控与引擎指标接在一起**&#8203;：一个 TPOT 尖刺要能一路下钻到"那一刻 batch 里有谁、KV 驱逐了谁"。

::: details 深入推导：火焰图与 roofline 的联合解读

**单 kernel 分析**&#8203;。Nsight Compute 对每个 kernel 给出 SOL（Speed of Light）两张数：SM 吞吐（算力侧）与显存吞吐（带宽侧）。判读：

- 两者都 <40%：kernel 不饱和，通常是启动开销或并行度不足 → 合并算子/加大 batch；
- 带宽侧 >80%：带宽受限 → 算子融合、量化（减少字节）；
- 算力侧 >80%：计算受限 → 检查精度是否可降（FP8）。

**定位"该算多快"**&#8203;。[Roofline](/knowledge-planet/ai-infra/hardware/chip-architecture) 公式给出理论值：矩阵乘（计算受限）与逐元素（带宽受限）的期望时间可手算。&#8203;**实测 ÷ 理论 = kernel 效率**&#8203;：FlashAttention 类优化就是把 attention kernel 从 25% 效率推到 70%+ 的故事。

**集群级的慢卡归因**&#8203;。万卡训练的 straggler 定位：HTA 把 $n$ 张卡的时间线对齐聚合，找出系统性偏慢的卡/链路（例如某台机器 NVLink 降速、某卡 HBM 温度降频）。经验：1% 的卡慢 20%，集群 MFU 直接掉约 20%×1%×p（放大系数随流水深度）——&#8203;**集群 profiling 的第一课是"分布"而非"均值"**&#8203;。

（据 NVIDIA Nsight 文档、HTA 论文/仓库、MegaScale。）

:::

## 思考题

1. 训练 MFU 低但单 kernel 全部高效，问题在哪一层？用什么工具定位？
2. decode TPOT 偶发尖刺（每小时几次），服务 metric 与引擎 log 该怎么对照查？
3. Nsight Compute 显示某 kernel 带宽利用率 90%：还能优化吗？往哪个方向？

::: details 参考答案

1. 层间问题（kernel 之外的间隙）：通信暴露、气泡、CPU 调度。用 Nsight Systems 看时间线找 gap 与 NCCL 位置；多卡用 HTA 对齐定位慢源。
2. 尖刺时刻对齐引擎 log：是否 KV 满触发 recompute 抢占/swap（[请求调度](/knowledge-planet/ai-infra/inference/request-scheduling)篇）、是否长 prefill 迭代混入、是否 checkpoint/权重热更。指标：swap/eviction 计数器、迭代时长直方图。
3. 可以。带宽受限 kernel 的优化方向是减少搬运的字节：算子融合（消中间物）、量化（减位宽）、避免不必要的 layout 转换（每转换一次全量读写一遍）。90% 是"时间花在搬运"的确认，不是"无事可做"的结论。

:::

## 小结

- 工具分层：框架 profiler → 内核 Nsight Compute → 系统时间线 Nsight Systems → 集群 HTA → 服务 metrics，读法由外向内。
- 训练四查：kernel 间隙、通信重叠、流水对齐、内存水位。
- 推理按 SLO 违约下钻：排队 → prefill → decode，与引擎指标联合归因。
- kernel 分析 = 实测 SOL 对照手算 roofline；集群分析看分布（straggler），不看均值。

## 参考资料

- PyTorch，[Profiler 官方文档](https://pytorch.org/tutorials/recipes/recipes/profiler_recipe.html)
- NVIDIA，[Nsight Systems](https://developer.nvidia.com/nsight-systems) 与 [Nsight Compute](https://developer.nvidia.com/nsight-compute)
- Facebook Research，[HolisticTraceAnalysis](https://github.com/facebookresearch/HolisticTraceAnalysis)（GitHub）
- Wei et al., [MegaScale](https://arxiv.org/abs/2402.15627)（arXiv 2402.15627，集群诊断系统）
- vLLM，[Production Metrics 文档](https://docs.vllm.ai/en/latest/serving/metrics.html)
