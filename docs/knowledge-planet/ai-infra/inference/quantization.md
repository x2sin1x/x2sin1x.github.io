---
title: "量化"
date: 2026-09-22T18:00:00+08:00
weight: 60
---

# 量化

> 用更少的比特存权重与激活。&#8203;**推理侧性价比最高的单项优化：显存减半、带宽减半，质量几乎不掉。**

## 为什么量化有效

神经网络权重分布对离群值敏感但整体冗余：多数权重落在窄区间。量化把 $s_\Psi$ 比特的表示压到更低精度，配合缩放因子恢复量级：

$$W_{\text{quant}} = \text{round}\left(\frac{W}{\Delta}\right),\quad \Delta = \frac{\max|W|}{2^{b-1}-1}$$

对推理的三重收益（[芯片架构](/knowledge-planet/ai-infra/hardware/chip-architecture)篇的量级复算）：

- **显存**&#8203;：权重 $2\Psi\to0.5\Psi$（W4），KV 也能量化（FP8 KV Cache 再省一半）；
- **带宽**&#8203;：decode 下限 $t\ge s_\Psi\Psi/\beta$ 直接按比例缩短——W4 理论 2 倍加速；
- **计算**&#8203;：INT8/FP8 Tensor Core 吞吐是 BF16 的 2 倍。

## 主要方法谱系

| 方法 | 精度 | 校准方式 | 特点 |
| ---- | ---- | ---- | ---- |
| FP8（E4M3/E5M2） | 8 bit 浮点 | 训练后直接转 | Hopper+ 原生支持，最省心 |
| GPTQ | W4/W3 | 基于 Hessian 的逐层误差补偿 | GPU 推理主流 |
| AWQ | W4 | 激活感知：保护显著通道 | 精度优于同位宽 GPTQ 场景多 |
| SmoothQuant | W8A8 | 把激活离群值"平滑"进权重 | W8A8（激活也量化）代表 |
| NF4（QLoRA） | 4 bit 非均匀 | 信息论最优分布假设 | 面向微调基座 |

**离群值是万恶之源**&#8203;：激活的少数通道量级远超其余（LLM 普遍现象），朴素 W8A8 会把它们截断成灾难。SmoothQuant 的等价变换 $Y=(X\text{diag}(s)^{-1})(\text{diag}(s)W)$ 把激活的离群"搬"进权重——数学上恒等、分布上双赢。

## 质量与速度的现实曲线

- **W8A8 / FP8**&#8203;：几乎所有任务无损，直接默认；
- **W4A16（GPTQ/AWQ）**&#8203;：困惑度上升 1% 内、多数任务无感，少数高精度任务（数学、代码）可测出退化；
- **W4A4 / W2**&#8203;：前沿研究区，需要 GPTQv2、Hadamard 旋转（QuaRot）等复杂手段，尚未稳定落地。

::: details 深入推导：GPTQ 的误差补偿与量化的 roofline 收益核算

**GPTQ 补偿**&#8203;。逐层目标：量化 $\hat W$ 后最小化 $\|\hat W X - W X\|^2$。把量化顺序化为列消元：每量化一列，把该列引入的误差按 Hessian 逆矩阵 $H^{-1}$（$H=2XX^\top$）反馈到未量化的列上——&#8203;**用行波补偿把误差摊薄**&#8203;，4 bit 下保持输出接近。OBQ→GPTQ 的关键贡献是把逐次求逆降到 $O(N^3)$ 一次性 Cholesky。

**收益核算（H100、70B 模型）**&#8203;。decode 下限：BF16 $140\ \text{GB}/3.35\ \text{TB/s}=41.8\ \text{ms}$；W4 $35\ \text{GB}/3.35=10.4\ \text{ms}$——4 倍差距。但实际加速受非权重项（KV 读取、kernel 启动、反量化开销）侵蚀，实测 1.5~2.5 倍。&#8203;**batch 越大、KV 占比越高，量化的相对收益越小**&#8203;（KV 若不同步量化则成为新瓶颈）——这就是"W4A16 + FP8 KV Cache"常打包出现的原因。

**量化的算力侧**&#8203;。W4A16 反量化后在 BF16 Tensor Core 上计算（dequant-in-kernel），吞吐不变、带宽减半；FP8/INT8 则换用原生低精度 Tensor Core（H100 FP8 约 2×BF16）——&#8203;**W4A16 是"带宽优化"，W8A8/FP8 是"带宽+算力双优化"**&#8203;，两者组合（W4A8）是当前前沿。

（据 Frantar et al. 2022 GPTQ、Lin et al. 2023 AWQ、Xiao et al. 2022 SmoothQuant。）

:::

## 思考题

1. 70B 模型、单卡 80 GB：BF16、W4A16 分别能装下吗？各留多少 KV 空间？
2. 为什么激活的离群值比权重的离群值更难处理？
3. 一个长上下文 RAG 服务（32K 上下文、高并发），量化决策的关键是什么？

::: details 参考答案

1. BF16 权重 140 GB 装不下（需 2 卡）；W4 权重 35 GB，剩余 45 GB——按 32 KB/token（GQA）算可容纳约 140 万 token 的 KV，约 40 条 32K 并发。量化的显存收益直接转化成并发空间。
2. 权重离群值是静态的、可离线校准补偿（GPTQ/AWQ 都在权重侧做文章）；激活的离群值随每个输入动态变化，运行时不可预知，只能用变换（SmoothQuant 搬到权重）、或激活保留高精度（W4A16 的 A16）回避。
3. KV 必须与权重同步量化（FP8 KV），否则长上下文下 KV 读取反超权重（[KV Cache](/knowledge-planet/ai-infra/inference/kv-cache)篇推导），W4 权重的带宽红利被 KV 吃掉；其次 prefill 是计算受限，W4A16 对 TTFT 帮助有限，要 FP8 计算才有感。

:::

## 小结

- 量化三收益：显存、带宽（decode 加速）、算力（低精度 Tensor Core），其中 W4A16 主打带宽、FP8/W8A8 兼打算力。
- 离群值是核心难题：AWQ 保护显著通道、SmoothQuant 平滑进权重、GPTQ 用 Hessian 补偿。
- KV 与权重必须同步量化，长上下文场景尤其如此。
- 量化是"免费"的（几乎无质量损失），没有理由不默认开启——没开通常是因为工程债。

## 参考资料

- Frantar et al., [GPTQ: Accurate Post-Training Quantization](https://arxiv.org/abs/2210.17323)（arXiv 2210.17323）
- Lin et al., [AWQ: Activation-aware Weight Quantization](https://arxiv.org/abs/2306.00978)（arXiv 2306.00978）
- Xiao et al., [SmoothQuant](https://arxiv.org/abs/2211.10438)（arXiv 2211.10438）
- Dettmers et al., [QLoRA](https://arxiv.org/abs/2305.14314)（NF4，arXiv 2305.14314）
- Ashkboos et al., [QuaRot](https://arxiv.org/abs/2404.00456)（旋转消除离群值，arXiv 2404.00456）
