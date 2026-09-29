---
title: "显存优化与 Offload"
date: 2026-09-29T10:30:00+08:00
weight: 60
---

# 显存优化与 Offload

> 训练一启动就 OOM，是所有 Infra 工程师的第一课。本篇给出完整的显存账本：**显存四要素怎么估、激活怎么省、状态怎么搬、碎片怎么治**——所有技巧都只是在"用别的东西换显存"。

## 先算账：显存四要素

训练态显存 = 权重 + 梯度 + 优化器状态 + 激活（+ 临时缓冲）。前三项可精确算（见[显存层次](/knowledge-planet/ai-infra/hardware/memory-hierarchy)篇）：

$$M_{\text{状态}} = \Psi\,(2_{\text{BF16权重}} + 2_{\text{梯度}} + 12_{\text{Adam: 4+4+4}}) = 16\Psi \ \text{字节（混合精度）}$$

激活项依赖 batch/序列/实现，量级：每层 $\sim bsh\times$常数（attention 与 MLP 的中间量之和），开重算前可按每层 $34bsh+5bsh^2/a$ 字节估（Korthikanti et al. 的经典近似）。**7B 模型、序列 4K、batch 4、无并行**：状态 112 GB、激活可达 60 GB 以上——单卡 80 GB 装不下，这就是"为什么需要下面所有技巧"的定量出处。

## 激活：重计算与选择性检查点

激活是唯一"可再生"的显存——它只是前向的中间产物，丢了可以重算：

- **全量重计算**（`checkpoint_sequential`）：每个 Transformer 层只存输入，反向重算整层。显存降一个数量级，计算量 +33%（前向重算一遍）。
- **选择性重计算**（Megatron）：attention 内部的 score 矩阵（$bsh^2/a$ 项，平方增长的重灾区）重算，线性增长的 MLP 激活保留——**计算代价 +2–5% 显存省一半以上**，大序列下的最优默认。
- **`checkpoint_sequential` vs `checkpoint_wrapper`**（题库 078/082）：前者对 `nn.Sequential` 整段包装，粒度粗；后者（torch 的 `apply` 级 API/`non_reentrant` 版）可以任意粒度包函数，且非重入实现支持双前向的 edge case。工程判断：**能选择性就不全量，能按层就不按块**。

梯度检查点与 PP 的配合有专门讲究（题库 065）：PP 的 1F1B 已限制 in-flight 激活数，再叠加重算会让反向时的重算流量与下一 micro-batch 的前向争 SM——大模型实践中通常"重算 + 1F1B"组合调，而不是想当然地都叠满。

## 状态：ZeRO 逐级切分与 offload

参数/梯度/优化器状态的切分在[数据并行](/knowledge-planet/ai-infra/parallelism/data-parallelism)篇推导过（ZeRO-1/2/3）。本篇补 offload 一侧：

- **offload 的带宽账**：CPU 内存约 300–400 GB/s（多通道）、PCIe 4.0 x16 约 32 GB/s、NVMe 3–7 GB/s。**offload 什么取决于"每步搬几次"**：优化器状态每步一次（更新时），梯度一次，参数前反向各一次——参数 offload 的搬运量是状态的三倍，最不划算。这就是 ZeRO-Offload 只下放"优化器状态+梯度"的原因（见[训练框架](/knowledge-planet/ai-infra/training/training-frameworks)篇）。
- **重叠是 offload 的生命线**（题库 083）：裸 offload 意味着每步多一次 PCIe 往返的串行等待；正确做法是**异步预取/回写**——反向进行到第 $i$ 层时，CPU 已在第 $i{-}k$ 层做优化器更新并预取第 $i{+}k$ 层参数，用双缓冲把 PCIe 流量藏进计算。CUDA 流 + pinned memory（`non_blocking=True`）是标准实现。
- **多节点的差异**（题库 084）：单机 offload 主要省显存；多机时代 DP 组变大、ZeRO 切分本身已够，offload 的角色退居"碎片兜底"——GPU 显存曲线更平稳比峰值更低更有价值。

## 碎片与运行时行为

- **碎片在分布式下更严重吗？**（题库 079）：是。TP/PP 引入大量等尺寸小张量（按卡切分的激活/参数），长生命周期的通信缓冲穿插其中——交错分配加剧分裂。对策：`expandable_segments:True`（[PyTorch 内部机制](/knowledge-planet/ai-infra/framework/pytorch-internals)篇）、通信缓冲复用池、统一 bucket 化分配。
- **`empty_cache()` 的副作用**（题库 080）：它只把**池内缓存**还给驱动，不动已分配张量；代价是下次分配重新 cudaMalloc（慢）且失去复用。训练循环里调用它等于自废武功——只在"训练结束→切换推理"这类阶段边界使用。
- **ROI 评估**（题库 085）：任何显存技巧都换成三本账：省了多少显存、多花多少计算/通信、实现复杂度。性价比排序的经验值：重算（+33% 计算省一个量级显存）> ZeRO 切分（+少量通信省状态大头）> selective 重算（+2–5%）> offload（吞吐代价大）> 碎片治理（免费但收益有限）。

## 小结

- 显存账要按四要素分头算：$16\Psi$ 的状态公式给下限，激活按层近似给变量项。
- 激活优化的正确顺序：selective 重算 → 全量重算；与 PP 叠加时要看 SM 争用。
- offload 的铁律是"按每步搬运次数决定对象 + 重叠藏流量"；参数 offload 永远是最后手段。
- 碎片治理与 `empty_cache` 的使用边界，来自对 CachingAllocator 行为的理解。

## 思考题

1. 7B 模型混合精度训练，ZeRO-1（DP=8）下每卡状态多少？ZeRO-3 呢？
2. 选择性重算为什么优先重算 attention 的 score 而不是 MLP 激活？
3. offload 优化器状态后单步时间增加约多少？给出 PCIe 32 GB/s、状态 112 GB、每步一次往返的估算。

::: details 参考答案

1. 状态 16Ψ=112 GB。ZeRO-1 只切优化器状态（12Ψ）：每卡 $4\Psi + 12\Psi/8 = 5.5\Psi \approx 38.5$ GB；ZeRO-3 全切：$16\Psi/8 = 14$ GB。
2. score 矩阵是 $O(s^2)$ 项——序列长时它主导激活总量且重算便宜（就是一次 QK^T+softmax）；MLP 激活只随 $s$ 线性增长，保留的性价比高。
3. 112 GB ÷ 32 GB/s ≈ 3.5 s——对秒级 step 是灾难，所以必须异步重叠把大半藏进计算；裸用 offload 时这个数字就是答案，也是"offload 救命不救产能"的定量出处。

:::

## 参考资料

- Korthikanti et al., [Reducing Activation Recomputation in Large Transformer Models](https://arxiv.org/abs/2205.05198)（arXiv 2205.05198，selective recompute 出处）
- Rajbhandari et al., [ZeRO-Offload: Democratizing Billion-Scale Model Training](https://arxiv.org/abs/2101.06840)（arXiv 2101.06840）
- Ren et al., [ZeRO-Infinity: Breaking the GPU Memory Wall for Extreme Scale Deep Learning](https://arxiv.org/abs/2104.07857)（arXiv 2104.07857）

