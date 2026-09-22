---
title: "预训练"
date: 2026-09-22T18:00:00+08:00
weight: 10
---

# 预训练

> 预训练是 AI Infra 最极致的负载：&#8203;**一次跑三个月，一步都不能错。**

## 预训练在算什么

预训练的目标朴素而昂贵：给互联网级别的文本，用下一个 token 预测任务把参数 $\Psi$ 调到最优。它的负载特征由三个量决定：

- **计算量**&#8203;：$C = 6ND$（见[芯片架构](/knowledge-planet/ai-infra/hardware/chip-architecture)篇），训练 GPT-3 级模型（$N=175\text{B}$、$D=300\text{B}$）约需 $3.1\times10^{23}$ FLOP；
- **数据量**&#8203;：现代预训练用 $10\sim 20\text{T}$ token，原始网页数据在 PB 级；
- **时间尺度**&#8203;：数月连续运行，跨越数千次故障（见[容错与 Checkpoint](/knowledge-planet/ai-infra/hardware/fault-tolerance)篇）。

## Scaling Law：先算账再开机

训练前最贵的决策是"模型多大、数据多少"。Chinchilla 定律给出的经验结论：&#8203;**计算预算 $C$ 给定时，最优配置满足 $N$ 与 $D$ 大致等比例增长**&#8203;（约每增加 1 个参数配 20 个 token）。工程上的推演方式：

$$D \approx 20\Psi \quad\Rightarrow\quad \text{最优 } \Psi \approx \sqrt{C/120},\ D \approx \sqrt{20C/6}$$

决定训练哪一档模型后，[万卡集群](/knowledge-planet/ai-infra/hardware/large-scale-cluster)篇的时间公式直接给出工期与成本。&#8203;**预训练 Infra 的第一步不是写代码，是算这本账**&#8203;——这也是"量化分析与系统设计"能力的第一个用武之地。

## 数据管道：GPU 断粮的预防针

万亿 token 从 PB 级原始网页到训练样本，是一条多级流水线：

::: mermaid
flowchart LR
    A["原始网页<br/>（PB 级）"] --> B["去重 / 清洗 / 过滤"]
    B --> C["分词 tokenize"]
    C --> D["分片打包<br/>（预写盘）"]
    D --> E["训练集群<br/>（流式读取）"]
    B -.质量过滤.-> F["丢弃 50%+"]
:::

Infra 视角的两个关键点：

1. **清洗决定质量上限，工程决定质量下限**&#8203;。去重（MinHash）、质量分类器过滤会把数据量砍掉一半以上，但这些计算是一次性的 CPU/离线作业，可以用便宜资源慢慢跑。
2. **训练侧只求稳定供给**&#8203;：数据预分片打包成顺序读友好的格式（如 packed 序列），训练时流式读取，保证每步 I/O 时间远小于计算时间——否则上万张卡集体等数据，每秒都是烧钱。

## 训练循环与损失稳定性

单个训练步：前向 → 反向 → 优化器更新，配合[显存层次](/knowledge-planet/ai-infra/hardware/memory-hierarchy)篇的 ZeRO/激活重算把状态装下、用[并行策略](/knowledge-planet/ai-infra/training/parallelism/)把计算摊开。预训练特有的 Infra 问题是**数值稳定性**&#8203;：

- **loss spike**&#8203;：训练数周后 loss 突然跳升，常见诱因是坏数据批次或数值上溢。一线做法：检测到 spike 后回滚到健康 checkpoint 并跳过可疑数据段（Llama 3、MegaScale 均内置）；
- **混合精度护栏**&#8203;：BF16 计算天然稳于 FP16（无需 loss scaling），梯度裁剪兜底；
- **学习率与 warmup**&#8203;：前期 warmup 防止初期大梯度把参数打进饱和区。

::: details 深入推导：为什么是 $6ND$，注意力项什么时候不能忽略

一次前向中，每个参数恰好参与一次乘加（每 token）：$2\Psi$ FLOP/token。反向传播计算各参数梯度及输入梯度，约两倍于前向，故 $C\approx 6ND$。

**注意力项**&#8203;：序列长 $s$ 时，注意力矩阵 $QK^\top$ 与 $\text{softmax}\cdot V$ 各需约 $2Ls$ FLOP/token（$L$ 为层数），合计约 $4Ls$。它与 $2\Psi$ 之比决定能否忽略：

$$\frac{4Ls}{2\Psi} = \frac{2Ls}{\Psi}$$

以 7B 模型（$L=32$、$\Psi=7\times10^9$）：比值 $\approx 9\times10^{-9}\times s$，$s=4096$ 时约 $4\%$，可忽略；但 $s=10^5$（超长上下文）时超过 90%，&#8203;**必须计入，且注意力从矩阵乘退化为平方复杂度**&#8203;——这正是 [Ring Attention](https://arxiv.org/abs/2310.01889) 与[序列并行](/knowledge-planet/ai-infra/training/parallelism/sequence-parallelism)要解决的问题。

（据 Kaplan et al. 2020 与 Hoffmann et al. 2022 的口径。）

:::

## 思考题

1. 你有 1024 张 H100（MFU 按 45%），训练一个 34B 模型、8T token 需要多少天？
2. Chinchilla 最优是每参数 20 token，但 Llama 3 405B 用了约 38 token/参数（15.6T/405B）。为什么一线团队普遍"过训练"？
3. 数据管道中"去重"为什么同时提升质量和效率？

::: details 参考答案

1. $C=6\times34\times10^9\times8\times10^{12}=1.63\times10^{24}$；吞吐 $=1024\times989\times10^{12}\times0.45=4.55\times10^{17}$ FLOP/s；$T\approx3.6\times10^6\ \text{s}\approx41$ 天。
2. 推理成本与参数量挂钩，模型越大服务越贵。&#8203;**推理生命周期内要被调用万亿次的模型，多训一倍的 token（训练成本 +33%）换取更小的参数量是划算的**&#8203;——这是"推理感知的 scaling"（overtraining），Llama 3 系列是典型。
3. 去重后有效 token 密度更高（同样的训练预算学到更多），且重复序列会诱发记忆化；同时数据量减少直接降低了后续所有训练 I/O。

:::

## 小结

- 预训练由 $6ND$ 与 scaling law 定盘：先算工期成本，再开机器。
- 数据管道是一次性离线工程，训练侧只求流式稳定供给。
- loss spike 的标准处置：回滚 + 跳过可疑数据；数值稳定性靠 BF16 与梯度裁剪兜底。
- 长上下文时注意力项不能忽略，引出序列并行（后续）。

## 参考资料

- Hoffmann et al., [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556)（Chinchilla，arXiv 2203.15556）
- Kaplan et al., [Scaling Laws for Neural Language Models](https://arxiv.org/abs/2005.14165)（arXiv 2005.14165）
- Grattafiori et al., [The Llama 3 Herd of Models](https://arxiv.org/abs/2407.21783)（arXiv 2407.21783）
- Li et al., [MegaScale](https://arxiv.org/abs/2402.15627)（arXiv 2402.15627）
- Liu et al., [Ring Attention with Blockwise Transformers for Near-Infinite Context](https://arxiv.org/abs/2310.01889)（arXiv 2310.01889）
