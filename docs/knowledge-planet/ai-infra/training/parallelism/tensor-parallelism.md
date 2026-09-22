---
title: "张量并行"
date: 2026-09-22T18:00:00+08:00
weight: 20
---

# 张量并行

> 把一个矩阵乘本身切开。**通信最重、也最依赖高速互联的并行。**

## 机制：行切与列切

Megatron-LM 的洞察：Transformer 的 MLP 与注意力投影可以只用两次通信完成切分。以 MLP 为例，$Y=\text{GeLU}(XA)$、$Z=YB$：

::: mermaid
flowchart LR
    X["X"] --> f["f：identity（列切 A）"]
    f --> XA1["XA₁ → GeLU → Y₁"]
    f --> XA2["XA₂ → GeLU → Y₂"]
    XA1 --> g["g：allreduce（行切 B）"]
    XA2 --> g
    g --> Z["Z"]
:::

- **第一刀（列切 $A=[A_1;A_2]$）**：GeLU 逐元素独立，各卡算各的部分 $Y_i$，**无需通信**；
- **第二刀（行切 $B=[B_1;B_2]$）**：$Y_1B_1+Y_2B_2=Z$，各卡局部结果相加即为全量——一次 **allreduce** 合并。

注意力同理（$Q/K/V$ 按头切，输出投影行切）。**每层前向 2 次、反向 2 次 allreduce**，每次搬运 $2bsh$ 字节（[超节点](/knowledge-planet/ai-infra/hardware/supernode)篇）。

## 显存账：权重、激活、参数三丰收

TP=$t$ 时每卡：权重 $2\Psi/t$ 字节、该层激活也随切分下降（$2bsh/t$），优化器状态同样均摊——**TP 是三种状态全切的唯一策略**，这是"模型装不下"的第一刀几乎总是 TP 的原因。

![Megatron-LM 的 MLP 列切/行切设计：f 处无通信、g 处一次 allreduce](./megatron-mlp-tp.png)

*图源：[Megatron-LM 论文](https://arxiv.org/abs/1909.08053)（arXiv 1909.08053）。*

## 边界：TP 放多大

通信在关键路径上且每层都发生，时间公式代入（[超节点](/knowledge-planet/ai-infra/hardware/supernode)篇）：NVLink 域内 8 卡单次 allreduce 约 0.25 ms，跨机则慢一个数量级。结论：

- **TP 度数 ≤ 单机卡数（8），且留在 Scale-up 域内**；
- 更大的权重切分交给 PP（通信稀疏）或 ZeRO-3（通信可重叠）；
- TP 的隐含收益：度数增大时 allreduce 数据量不变但分母增大？不——数据量 $2bsh$ 与 $t$ 无关，度数越大、通信频次不变而每次参与卡更多，**延迟项与网络压力随 $t$ 上升**，收益递减。

::: details 深入推导：为什么列切 GeLU 免通信，softmax 却不行

GeLU/ReLU 逐元素作用：$\text{GeLU}(XA)_i=\text{GeLU}(XA_i)$，切列后各卡独立成立。而 softmax 需要**整行**的 max 与 sum：若按列切 $QK^\top$ 的结果，每卡只有部分 logit，softmax 无法局部计算。Megatron 的处理：$Q/K/V$ 按注意力**头**切——softmax 本来就按头独立，切头即无通信；单头过大时用 [Sequence Parallelism](/knowledge-planet/ai-infra/training/parallelism/sequence-parallelism) 把 softmax 沿序列维切开配合 allgather。

**通信量下界**。切分 $d\times k$ 的 GEMM 到 $t$ 卡，任何方案至少要交换 $O(bsh)$ 量级的激活（输出矩阵的信息分布在不同卡上）。Megatron 的两次通信（前向 allreduce + 反向 allreduce）已达此下界，故"更聪明的切法"省不掉通信，只能选择通信发生的时机与位置。

（据 Shoeybi et al. 2019。）

:::

## 思考题

1. TP=8、$b=1$（decode）、$s=4096$、$h=8192$：每层前向通信量多少？为什么 decode 时 TP 的相对开销比训练时更大？
2. TP=2 时每卡权重减半，通信也减半吗？
3. 为什么不能把 TP 做到 64 卡跨机，用更多卡摊薄权重？

::: details 参考答案

1. 每层 2 次 × $2bsh=134$ MB（BF16）≈ 268 MB；每 token 每层都付。训练时大 batch 的计算时间随 $b$ 增长而通信量也随 $b$ 增长（比值不变），但 decode 的计算本身是带宽受限的极薄切片，通信/计算比急剧恶化——TP 对 decode 延迟的伤害远大于训练（见[超节点](/knowledge-planet/ai-infra/hardware/supernode)篇 worked example）。
2. 否。allreduce 数据量 $2bsh$ 只与激活大小有关，与 $t$ 无关；只有权重/状态显存按 $1/t$ 减。
3. 通信频次 × 层数 × 关键路径不可重叠：64 卡跨机 TP 的每 token 通信时间会超过计算时间几个数量级（[超节点](/knowledge-planet/ai-infra/hardware/supernode)篇 worked example 算过 18 倍/跨机）；且显存摊薄的需求早已被 PP/ZeRO 满足。

:::

## 小结

- TP 沿矩阵切：列切免通信 + 行切一次 allreduce，每层 4 次通信、全部在关键路径上。
- 三种状态（权重/梯度/优化器+激活）全按 $1/t$ 均摊，是"装不下"的第一刀。
- 度数上限 = 超节点内单机 8 卡；decode 场景的通信/计算比比训练更恶劣。
- 切法已达到通信下界，工程自由度在"放哪"而不在"怎么切"。

## 参考资料

- Shoeybi et al., [Megatron-LM](https://arxiv.org/abs/1909.08053)（arXiv 1909.08053）
- Narayanan et al., [Megatron-LM v2](https://arxiv.org/abs/2104.04473)（arXiv 2104.04473）
- Wang & Komatsuzaki, [GPT-NeoX-20B](https://arxiv.org/abs/2204.06745)（arXiv 2204.06745，TP 工程实践）
