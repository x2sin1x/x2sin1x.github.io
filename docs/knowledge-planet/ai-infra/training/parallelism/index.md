---
title: "并行策略"
date: 2026-09-22T18:00:00+08:00
weight: 50
---

# 并行策略

> 一个放不进一张卡、算不完一台机的模型，怎么摊到一万张卡上？&#8203;**并行策略是这个问题的答案集，而组合它们是一门权衡的艺术。**

## 四本账与五种切法

[芯片架构](/knowledge-planet/ai-infra/hardware/chip-architecture)篇给了四本账：算力、显存、显存带宽、通信带宽。并行策略就是沿模型的不同维度切分计算图：

| 策略 | 切什么 | 省什么显存 | 通信代价 | 适合 |
| ---- | ---- | ---- | ---- | ---- |
| [数据并行 DP](/knowledge-planet/ai-infra/training/parallelism/data-parallelism) | 数据 | 只在 ZeRO 下省 | 梯度 allreduce | 默认底座 |
| [张量并行 TP](/knowledge-planet/ai-infra/training/parallelism/tensor-parallelism) | 权重矩阵 | 权重+激活，按层均摊 | 每层 2 次 allreduce | 超节点内 |
| [流水并行 PP](/knowledge-planet/ai-infra/training/parallelism/pipeline-parallelism) | 网络层 | 权重+激活，按层组 | 层边界 P2P | 跨机 |
| [序列并行 SP](/knowledge-planet/ai-infra/training/parallelism/sequence-parallelism) | 序列长度 | 激活为主 | attention 通信 | 长上下文 |
| [专家并行 EP](/knowledge-planet/ai-infra/training/parallelism/expert-parallelism) | 专家（MoE） | 专家权重 | all-to-all | MoE 模型 |

它们**从不互斥**&#8203;：现代大模型训练是 3D/4D 并行（如 TP×PP×DP×SP 同时启用），因为每种策略切的是不同维度、省的是不同资源、付的是不同通信。

## 一个决策框架

按"通信重 → 网络快"的匹配原则排布（呼应[超节点](/knowledge-planet/ai-infra/hardware/supernode)篇）：

::: mermaid
flowchart TB
    Q{"哪些并行能塞进超节点？"}
    Q -- "TP/SP：每层都要通信" --> A["留在 Scale-up 域内"]
    Q -- "EP：all-to-all 密集" --> B["尽量域内，MoE 大 EP 靠超大超节点"]
    Q -- "PP：层边界 P2P，通信稀疏" --> C["可跨机，但气泡要靠 micro-batch 摊薄"]
    Q -- "DP：梯度同步可重叠" --> D["最外层，承担规模扩展"]
:::

再叠加两个正交维度：&#8203;**ZeRO**&#8203;（[显存层次](/knowledge-planet/ai-infra/hardware/memory-hierarchy)篇，切 DP 的状态）与 **重计算**&#8203;（用计算换激活显存）。

## 混合并行的账：一次完整的推演

训练 405B 模型、16384 卡（Llama 3 的配置）。显存账：

- 模型权重 BF16：$810\ \text{GB}$，单卡 80 GB 装不下 $\Rightarrow$ 至少 TP×PP 切 16 份以上；
- PP=16、TP=8：每卡权重 $810/(16\times8)\approx6.3\ \text{GB}$，再叠 DP（$=16384/128=128$ 路）与 ZeRO-1、激活重算——卡上还有空间装 KV 与激活。

通信账：

- TP=8：每层前向 2 次 allreduce（[超节点](/knowledge-planet/ai-infra/hardware/supernode)篇推导），必须放 NVLink 域内 ✓；
- PP=16：每步只有层边界激活 P2P（按 micro-batch 数量摊薄气泡），可跨机但优先域内；
- DP=128：梯度 allreduce 可与反向重叠，放最外层跨机。

**这就是 4D 并行：DP×PP×TP×SP 各司其职，每一维都对准一本账。**

::: details 深入推导：气泡率通用公式与并行组合的搜索

设流水并行深度 $p$、数据并行度 $d$、micro-batch 数 $M$（梯度累积）。PP 气泡率（1F1B 调度）：

$$\text{bubble} = \frac{p-1}{M + p - 1}$$

$M$ 是关键杠杆：$M\ge4(p-1)$ 时气泡 $<20\%$。但 $M$ 增大即梯度累积加深，等效 batch 变大——&#8203;**气泡率、等效 batch size、显存（M 个 in-flight micro-batch 的激活）三者被同一个变量拴住**&#8203;。

组合搜索：给定目标模型与集群，$(t, p, d, s, e)$ 的可行域受显存（装得下）与网络（通信放得进对应层级）双向约束，且 MFU 是组合的复杂函数。Alpa 等工作把这个问题形式化为整数规划：先算子级、再算子间的两级优化。实践建议：从"TP=超节点内单机 8 卡、PP 与 DP 填满集群"的标准起点出发，用[性能分析](/knowledge-planet/ai-infra/profiling/)实测调参，而非信任闭式解。

（据 Huang et al. 2019 GPipe、Narayanan et al. 2021 PipeDream-2BW 与 2021 Megatron-LM v2。）

:::

## 思考题

1. TP=4、PP=4 的配置总权重切 16 份：对 405B 模型每卡权重多少？若 TP=16、PP=1 呢？两种切法通信有何本质区别？
2. $M=8$、$p=16$ 的流水线气泡率是多少？把 $M$ 加倍到 16 的代价是什么？
3. 为什么 DP 几乎总是存在于最终配置中，而不是被 TP/PP 完全取代？

::: details 参考答案

1. 每卡 $810/16\approx50\ \text{GB}$，两种切法相同。但 TP=16 需要 16 卡全互联（2 台 8 卡机之间 allreduce 走 IB，[超节点](/knowledge-planet/ai-infra/hardware/supernode)篇算过慢 18 倍）；PP=4 只需层边界 P2P、每步每卡一次一收一发。&#8203;**同等显存收益下通信模式完全不同，这就是切法的选择空间**&#8203;。
2. 气泡率 $(16-1)/(8+15)=15/23\approx65\%$；$M=16$ 时 $15/31\approx48\%$。代价：in-flight 激活显存翻倍、等效 batch 翻倍（可能影响收敛），需要三者权衡。
3. TP/PP 切完权重后每卡仍持有完整参数的一个固定分片——它们扩展的是"模型装得下"，不提供数据维度的规模扩展；DP 是唯一随卡数线性增加计算吞吐的维度（通信可重叠），且 ZeRO 已把它的显存劣势修补大半。

:::

## 小结

- 五种并行切五个维度：数据、权重矩阵、网络层、序列、专家；省的资源与付的通信各不相同。
- 组合原则：通信重的靠近卡（Scale-up），通信轻的推远（Scale-out），DP 兜底规模扩展。
- 气泡率 $(p-1)/(M+p-1)$ 把 PP 配置与梯度累积、显存拴在一起。
- 实践路径：标准起点 + 实测调参，并行组合搜索是 NP 难的，直觉与 profile 比闭式解可靠。

## 参考资料

- Shoeybi et al., [Megatron-LM](https://arxiv.org/abs/1909.08053)（arXiv 1909.08053）
- Narayanan et al., [Efficient Large-Scale Language Model Training on Hybrid Data and Model Parallel Systems](https://arxiv.org/abs/2104.04473)（Megatron-LM v2，arXiv 2104.04473）
- Huang et al., [GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism](https://arxiv.org/abs/1811.06965)（arXiv 1811.06965）
- Rajbhandari et al., [ZeRO](https://arxiv.org/abs/1910.02054)（arXiv 1910.02054）
- Zheng et al., [Alpa: Automating Inter- and Intra-Operator Parallelism](https://arxiv.org/abs/2201.12020)（arXiv 2201.12020）

各子篇：[数据并行](/knowledge-planet/ai-infra/training/parallelism/data-parallelism) · [张量并行](/knowledge-planet/ai-infra/training/parallelism/tensor-parallelism) · [流水并行](/knowledge-planet/ai-infra/training/parallelism/pipeline-parallelism) · [序列并行](/knowledge-planet/ai-infra/training/parallelism/sequence-parallelism) · [专家并行](/knowledge-planet/ai-infra/training/parallelism/expert-parallelism)
