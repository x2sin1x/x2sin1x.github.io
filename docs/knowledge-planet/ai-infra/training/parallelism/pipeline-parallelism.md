---
title: "流水并行"
date: 2026-09-22T18:00:00+08:00
weight: 30
---

# 流水并行

> 把网络的层切成段，每段一台设备。**通信最省，但会"漏气"。**

## 机制

$L$ 层切成 $p$ 段（stage），卡 $i$ 持有第 $i$ 段。前向时激活沿流水线传递，反向时梯度反向流动。通信只有**层边界的激活/梯度 P2P**——每步每卡收发各一次，数据量 $2bsh$ 字节，比 TP 每层 4 次 allreduce 轻得多，且可以走跨机网络（Scale-out）。

## 代价：气泡

理想流水线要求所有卡同时忙碌，但真实执行有"充满"与"排空"阶段——部分卡在等。GPipe 式（all-forward-then-all-backward）调度的气泡率：

$$\text{bubble} = \frac{p-1}{M}$$

$M$ 为 micro-batch 数。$M$ 不够大时气泡吞掉一切：$p=16$、$M=16$ 时气泡率 94%！

## 1F1B 与交错流水

两个经典改进：

- **1F1B（one-forward-one-backward）**：每个 worker 交替执行一次前向、一次反向，把 in-flight 激活数从 $M$ 降到 $O(p)$（显存省），气泡率变为 $\frac{p-1}{M+p-1}$（[并行策略](/knowledge-planet/ai-infra/training/parallelism/)篇）；
- **交错流水（interleaved）**：每卡持有多个不连续的层块（virtual stage），流水线上"多点注入"，气泡进一步除以虚拟阶段数 $v$，代价是 P2P 通信次数增加 $v$ 倍。

::: mermaid
gantt
    title 1F1B 流水示意（p=4，M=6，只画前向 F 与反向 B 的时间块）
    dateFormat X
    axisFormat %s
    section 卡1
    F1 F2 F3 F4 :0, 4
    B1 :4, 5
    section 卡2
    等1格 :0, 1
    F1 F2 F3 :1, 4
    B1 B2 :4, 6
    section 卡3
    等2格 :0, 2
    F1 F2 :2, 4
    B1 :4, 5
    section 卡4
    等3格 :0, 3
    F1 :3, 4
:::

*示意图：越靠后的 stage 启动越晚，"充满"阶段的空隙就是气泡。*

## 负载均衡：切段不是均匀切

各层计算量并非相等（embedding/输出头 vs 中间层）。切段要按**计算量**（FLOPs）而非层数均衡，否则最慢的 stage 决定整条流水线的节拍——**流水线吞吐由最慢一段决定**，这是并行里少见的"木桶效应"刚性约束。

::: details 深入推导：气泡、显存与 M 的三体问题

1F1B 下 in-flight 激活为 $O(p)$ 个 micro-batch：卡 1 要等 $p$ 个反向回来才能释放最早的前向激活，故激活显存 $\propto p\times$（单层激活）。三者的耦合：

- 气泡率 $\frac{p-1}{M+p-1}$ 要小 $\Rightarrow$ $M\gg p$；
- 激活显存 $\propto p$（1F1B）与 $M$ 无关（这是 1F1B 相对 GPipe 的核心优势，GPipe 是 $\propto M$）；
- 等效 batch $=M\times b\times d$（$d$ 为 DP 度数）受收敛约束。

解法组合：$M$ 用梯度累积凑够 $4(p-1)$ 以上；显存缺口交给[重计算](/knowledge-planet/ai-infra/hardware/memory-hierarchy)与 [SP](/knowledge-planet/ai-infra/training/parallelism/sequence-parallelism)；等效 batch 超限则加 DP 或降低学习率预期。**PP 配置设计就是在解一个三变量约束优化**。

**zero-bubble 前沿**：把 B 拆成 $B_{\text{in}}$（对输入的梯度）与 $B_{\text{out}}$（对权重的梯度）并允许后者延后执行，可把气泡理论值压到接近 0（Qi et al. 2023），代价是调度复杂度与权重更新延迟。

（据 Huang et al. 2019、Narayanan et al. 2021、Qi et al. 2023。）

:::

## 思考题

1. $p=8$、$M=32$：GPipe 与 1F1B 的气泡率各是多少？
2. 为什么 PP 的 P2P 通信可以走跨机慢网络，而 TP 不行？
3. 切 16 段时某一段计算量比其他段大 20%，整条流水线损失多少吞吐？

::: details 参考答案

1. GPipe：$(p-1)/M=7/32\approx22\%$；1F1B：$(p-1)/(M+p-1)=7/39\approx18\%$。$M$ 越大两者越接近，GPipe 的劣势主要在激活显存。
2. P2P 点对点数据量小（单次 $2bsh$）、频次低（每步每卡一收一发），50 GB/s 的 IB 传输 134 MB 约 2.7 ms，对秒级的训练步可接受且可与计算重叠；TP 的 allreduce 每层 4 次、在关键路径上，慢网络无法容忍。
3. 全流水线节拍由最慢段决定：有效吞吐 $\approx1/1.2=83\%$，损失 17%——比任何气泡都严重，负载均衡是 PP 的第一优先级。

:::

## 小结

- PP 沿层切，通信最省（P2P、可跨机），代价是气泡。
- 1F1B 把激活显存从 $\propto M$ 降到 $\propto p$，气泡率 $(p-1)/(M+p-1)$；交错流水进一步除以 $v$。
- 负载不均直接变成吞吐损失，切段按 FLOPs 而非层数。
- PP 配置 = 气泡、显存、等效 batch 的三体问题。

## 参考资料

- Huang et al., [GPipe](https://arxiv.org/abs/1811.06965)（arXiv 1811.06965）
- Narayanan et al., [PipeDream-2BW](https://arxiv.org/abs/2006.09503)（arXiv 2006.09503）
- Narayanan et al., [Megatron-LM v2](https://arxiv.org/abs/2104.04473)（arXiv 2104.04473，1F1B 与交错流水）
- Qi et al., [Zero Bubble Pipeline Parallelism](https://arxiv.org/abs/2401.10241)（arXiv 2401.10241）
