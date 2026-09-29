---
title: "Attention Kernel：FlashAttention 与它的后继者"
date: 2026-09-29T10:30:00+08:00
weight: 30
---

# Attention Kernel：FlashAttention 与它的后继者

> 大模型时代最重要的一次 kernel 重写：**不改数学，只改数据从哪来——attention 的显存占用从 $O(s^2)$ 降到 $O(s)$，速度还更快**。

## 问题：标准 attention 卡在哪

标准实现分三步：$S=QK^\top$ → softmax → $O=PV$。问题在中间矩阵 $S$：序列长 $s$ 时它是 $s\times s$——4K 序列、8K batch、32 头就有 64 GB 量级。更要命的是它对 HBM 的两次完整往返：

$$S \text{ 写入} \to \text{softmax 读取} \to \text{写回} \to \text{PV 读取}$$

运算强度算下来：$s=4\text{K}$ 时 FLOP 与字节同阶——**$s^2$ 矩阵的读写成了瓶颈，张量核心大量空转**。长序列下 attention 从"矩阵乘夹缝里的小开销"变成第一大耗时项。

## FlashAttention 的洞察：IO-aware

FlashAttention（Dao et al., 2022）没有改数学，改的是**遍历顺序**：

1. **分块（tiling）**：把 $Q$、$K$、$V$ 切成小块，$K/V$ 块逐块流入 SRAM（shared memory），在 SRAM 内完成"局部 $QK^\top$ → 局部 softmax → 累积输出"。
2. **在线 softmax（online softmax）**：softmax 的分母需要整行 max/sum，而分块后每块只见局部数据。解法是维护运行统计量（当前行最大值 $m$ 与和 $\ell$），每来一个新块就重缩放已累积的输出：$O \leftarrow O\cdot e^{m_{\text{old}}-m_{\text{new}}} + \dots$。数学上精确等价，物理上从不需要完整的一行。

效果：$S$ 矩阵从未离开 SRAM，HBM 流量从 $\Theta(s^2+d^2)$ 降到 $\Theta(s\,d+d^2)$；GQA/MQA（K/V 头共享）进一步压缩 K/V 读取。16K 序列下实测 2–4 倍加速，且显存随 $s$ 线性——**长上下文训练由此才成为可能**（呼应[序列并行](/knowledge-planet/ai-infra/parallelism/sequence-parallelism)篇）。

## FlashAttention-2 与 -3：往硬件上限逼近

- **FA-2（2023）**：重排了循环——外层遍历 $Q$ 块、内层遍历 $K/V$ 块，让同一输出块的多次累积留在寄存器；并按 warp 重分任务减少非矩阵乘指令。吞吐比 FA-1 再翻近一倍，"接近 GEMM 的 attention"。
- **FA-3（2024，Hopper）**：用 TMA 异步搬运 + warp 专业化（生产者-消费者 warp 组）+ ping-pong 调度（softmax 与 GEMM 在不同 warp 上交错），把 attention 推到 Hopper Tensor Core 峰值的 75% 量级——本质是把[算子优化](/knowledge-planet/ai-infra/hpc/operator-optimization)篇的异步流水技术用到极致。

一句话概括这条演进线：**FA-1 赢在算法（IO 复杂度），FA-2 赢在并行度，FA-3 赢在硬件流水**——每一代都先把上一代的理论下限变成新的起点。

## 生态位：xFormers、cuDNN 与稀疏 attention

- **xFormers**：memory-efficient attention 的早期集大成者（FA 同期的另一实现），以 `memory_efficient_attention` API 提供多种 kernel 后端，适合作为 PyTorch 生态的兼容层；如今多数场景被 FA 系列取代。
- **cuDNN fused attention**：NVIDIA 官方的融合 attention，Hopper 上与 FA-3 性能相当，优点是框架集成（`torch.nn.functional.scaled_dot_product_attention` 的 cudnn 后端）与更广的 shape 覆盖。
- **稀疏 attention**：把 $s\times s$ 里不重要的块跳过（滑窗、块稀疏、hyper-attention 类）。它是唯一能突破 $O(s^2)$ 计算量的路线，但**kernel 实现受制于不规则的访存模式**（gather 打破 coalescing、负载不均），且"哪些块重要"的近似有精度风险——工程上先确认真的被长序列计算卡住，再考虑稀疏（见[芯片架构]篇"先算运算强度再谈优化"）。

::: details 为什么 FA 的分块对训练同样成立（反向传播怎么办）

反向传播需要前向的中间量（softmax 输出），而 FA 没存它们。解法：重计算——反向时用保存的运行统计量（$m$、$\ell$ 与输出 $O$）在 SRAM 里重新计算所需的局部 softmax。用约 1.3 倍的计算换掉 $O(s^2)$ 的显存与两次 HBM 往返，总时间反而更短。这个"重计算换 IO"的模式与训练侧的激活检查点（[显存优化](/knowledge-planet/ai-infra/training/memory-optimization)篇）是同一思想在两个粒度上的应用。

:::

## 小结

- 标准 attention 的瓶颈不是计算而是 $s^2$ 中间矩阵的 HBM 往返；FlashAttention 用分块 + 在线 softmax 把它压进 SRAM。
- FA-1 算法、FA-2 并行、FA-3 硬件流水；每代的共同量尺是"离 GEMM 上限还有多远"。
- 生态上 FA 系列是主力，cuDNN fused attention 是官方集成选项，xFormers 是兼容层。
- 稀疏 attention 是突破平方复杂度的唯一路线，但工程与精度代价要求先测量再采用。

## 思考题

1. $s=32\text{K}$、$h=128$、32 头、BF16：标准实现的 $S$ 矩阵多大？一张 80 GB 的卡装得下吗？
2. 在线 softmax 为什么数学上等价？写出两块的累积更新式。
3. 你的模型 prefill 4K 序列时 attention 只占 8% 时间，值得换 FA-3 吗？

::: details 参考答案

1. $32\times32\text{K}\times32\text{K}\times2\text{ B}\approx 64\text{ GB}$（32 头 × $s^2$ × 2 字节）——单卡装不下，这正是长序列必须 FA/分块的定量理由。
2. 设两块的局部 max 为 $m_1,m_2$、指数和为 $\ell_1,\ell_2$、部分输出为 $O_1$；合并时 $m'=\max(m_1,m_2)$，$\ell'=\ell_1 e^{m_1-m'}+\ell_2 e^{m_2-m'}$，$O'=O_1 e^{m_1-m'}+\dots$——最终归一化时 $e^{m_i-m'}$ 恰好抵消，与整体 softmax 精确一致。
3. 不值得。FA-3 的收益集中在长序列（attention 占比高的场景）；4K 时 attention 占比 8%，即使快一倍也只省 4% 总时间，优先去优化占比更大的项（GEMM、通信、采样）。

:::

## 参考资料

- Dao et al., [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/abs/2205.14135)（arXiv 2205.14135）
- Dao, [FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning](https://arxiv.org/abs/2307.08691)（arXiv 2307.08691）
- Shah et al., [FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision](https://arxiv.org/abs/2407.08608)（arXiv 2407.08608）
- NVIDIA, [cuDNN scaled dot product attention](https://docs.nvidia.com/deeplearning/cudnn/frontend/latest/operations/SDPA.html) 文档

