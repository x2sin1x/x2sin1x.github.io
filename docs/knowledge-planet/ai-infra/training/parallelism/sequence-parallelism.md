---
title: "序列并行"
date: 2026-09-22T18:00:00+08:00
weight: 40
---

# 序列并行

> TP 切不动的地方（LayerNorm、softmax），沿着**序列长度**再切一刀。**长上下文时代的救生圈。**

## 两个动机

1. **TP 的盲区**：Megatron TP 只切矩阵乘，LayerNorm 与 Dropout 仍整份复制在 TP 组内，激活显存的"零头"随 $t$ 不变。序列并行（SP）把这两块沿 $s$ 维切成 $t$ 份，与 TP 共用一组卡；
2. **超长上下文**：$s=10^5$ 级时注意力激活（$\propto s^2$）与计算（[预训练](/knowledge-planet/ai-infra/training/pretraining)篇：注意力项反超参数项）都需要沿序列切分——这催生了 Ring Attention 这类以序列为主维度的并行。

## 机制一：Megatron 式 SP（与 TP 配对）

关键观察：TP 区域之间的边界（allreduce $g$ / identity $f$）可以替换为一对**散射/聚合**：

- 进入 TP 区域前：allreduce 改为 **reduce-scatter**（每卡只留激活的 $1/t$ 序列片）；
- 离开 TP 区域：identity 改为 **allgather**（各卡要完整序列做 LayerNorm 后的矩阵乘）。

通信总量**完全不变**（allreduce = reduce-scatter + allgather，[集合通信](/knowledge-planet/ai-infra/hardware/collective-communication)篇），激活显存却省了：LayerNorm/Dropout 区域的激活从 $sbh$ 降到 $sbh/t$。

## 机制二：Ring Attention（沿序列切注意力）

超长序列时把 $s$ 切到 $p$ 卡，每卡持有 $s/p$ 的 Q/K/V。注意力需要跨卡的 K/V——Ring Attention 的巧思：**卡间沿环传递 K/V 块的同时本地计算分块注意力**，通信被计算完全掩盖：

$$T_{\text{step}} \approx \underbrace{\max\left(\frac{2\,m}{\beta},\ t_{\text{attn}}\right)}_{\text{块级重叠后取大者}}$$

只要单块注意力计算时间 $\ge$ 传递时间，通信免费。代价是负载均衡对因果注意力有偏（对角块先算完，上半环空闲），需要 zigzag 等非对称分块修补。

::: mermaid
flowchart LR
    A["卡0: Q₀K₀V₀"] -- "传 K₀V₀" --> B["卡1: Q₁K₁V₁"]
    B -- "传 K₁V₁" --> C["卡2: Q₂K₂V₂"]
    C -- "传 K₂V₂" --> D["卡3: Q₃K₃V₃"]
    D -- "传 K₃V₃" --> A
:::

*环形 K/V 传递：每步传一块、算一块，$p$ 步后每卡算完自己 Q 行对全部 K/V 的注意力。*

::: details 深入推导：SP 的显存节省量与 Ring Attention 的通信模型

**SP 节省量**。以 7B、TP=8、$s=8192$、$b=4$、$h=4096$：LayerNorm/Dropout 区域每层激活 $sbh\times$（若干份）中可均摊的部分 $\to sbh/t$。按 [Korthikanti 公式](https://arxiv.org/abs/2205.05198) $M_{\text{act}}=sbh(34+5as/h)\cdot L/t$（SP+TP 后），相比纯 TP 的 $sbh(34+5as/h)\cdot L$ 直接除以 $t$——SP 是激活显存公式里唯一的"再除一刀"。

**Ring Attention 通信量**。每卡 $p-1$ 步共传 K/V 各 $2\times(sb h/p)\times(p-1)$ 字节。 $s=128\text{K}$、$h=4096$、$p=16$：每卡传 K/V 约 $2\times128\text{K}\times4096\times2\text{B}\times15/16 \approx 126\ \text{GB}$？—— 实际每步传一份 K/V 块（约 8.4 GB），单步 IB 50 GB/s 下 0.17 s，与该卡的注意力计算（$\propto (s/p)^2$ 规模分块，数十 ms 级）相比偏大——**这就是 Ring Attention 实际依赖域内大带宽或更长分块计算的原因**，也是它常与 TP/ZeRO 组合而非单独跨机的依据。

（据 Korthikanti et al. 2022、Liu et al. 2023。）

:::

## 思考题

1. SP 为什么能做到"通信量不变、显存变少"？代价是什么？
2. $s=200\text{K}$、单卡注意力激活爆炸，你的并行工具箱按什么顺序取用？
3. Ring Attention 的因果注意力负载不均，zigzag 分块怎么补？

::: details 参考答案

1. allreduce 拆成 reduce-scatter + allgather 是恒等变换，总通信字节不变；显存少是因为激活在 LN/Dropout 区域以切片态驻留。代价：通信原语从"大块一次"变成"两段"，对实现与 overlap 调度更挑剔；且 SP 度数必须与 TP 相同（共用卡）。
2. 先 SP+TP（8 卡内把激活压到 $1/t$）→ 激活仍不够加选择性重算（34→18 项）→ 再不够 Ring/Context Parallelism 沿序列扩卡。顺序原则：先域内零成本手段，后跨机手段。
3. 把序列切成 $2p$ 份、交错分配（卡 $i$ 拿第 $i$ 与第 $2p-1-i$ 块），让每卡的"因果下三角"面积相等——一个对角块配一个反对角块，负载差从 $O(p)$ 降到 $O(1)$。

:::

## 小结

- SP 与 TP 共卡：allreduce ↔ reduce-scatter+allgather 等价替换，通信不变、LN/Dropout 激活按 $1/t$ 省。
- Ring Attention 沿序列环形传 K/V，通信藏在分块计算后面，是超长上下文的基础设施。
- SP 是激活显存公式里唯一的免费再切一刀，长上下文配置的默认件。

## 参考资料

- Korthikanti et al., [Reducing Activation Recomputation in Large Transformer Models](https://arxiv.org/abs/2205.05198)（arXiv 2205.05198）
- Liu et al., [Ring Attention with Blockwise Transformers for Near-Infinite Context](https://arxiv.org/abs/2310.01889)（arXiv 2310.01889）
- Li et al., [Sequence Parallelism: Long Sequence Training from System Perspective](https://arxiv.org/abs/2105.13120)（arXiv 2105.13120，另一路线 ColAI-SP）
- Jacobs et al., [Deepspeed Ulysses](https://arxiv.org/abs/2309.14509)（arXiv 2309.14509，沿头切分的序列并行）
