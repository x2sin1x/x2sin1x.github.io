---
title: "数据并行"
date: 2026-09-22T18:00:00+08:00
weight: 10
---

# 数据并行

> 最朴素的并行：**每人一份模型，各算各的数据，算完对答案。** 规模扩展的第一支柱。

## 机制

$N$ 张卡各持有完整模型副本，每卡处理不同的 micro-batch；反向传播得到梯度后做一次 allreduce 求平均，所有卡同步更新：

::: mermaid
flowchart TB
    subgraph card0["卡 0"]
        m0["模型副本"] --> g0["梯度 g0"]
    end
    subgraph card1["卡 1"]
        m1["模型副本"] --> g1["梯度 g1"]
    end
    subgraph cardN["卡 N-1"]
        mN["模型副本"] --> gN["梯度 gN"]
    end
    g0 & g1 & gN --> ar["AllReduce（求平均）"]
    ar --> u["同步更新：w ← w - η·mean(g)"]
:::

数学上等价于大 batch 梯度下降：$\nabla = \frac{1}{N}\sum_i g_i$。**只要 allreduce 够快，数据并行的吞吐随卡数近线性增长**——这是它成为默认底座的原因。

## 显存问题与 ZeRO

朴素 DP 每卡要装下完整训练态 $16\Psi$ 字节（[显存层次](/knowledge-planet/ai-infra/hardware/memory-hierarchy)篇），这限制了可训模型规模。ZeRO 三级切分把优化器状态/梯度/参数分别按 $1/N$ 摊到各卡，通信代价分别为 1×/1×/1.5×——**DP 与 ZeRO 合体后，显存与通信都不再是扩展瓶颈**。

## 通信占比：什么时候 DP 是瓶颈

梯度同步时间（ring，[集合通信](/knowledge-planet/ai-infra/hardware/collective-communication)篇模型）与单步计算时间之比：

$$\rho \approx \frac{2\,m/B_{\text{eff}}}{t_{\text{step}}},\quad m = 2\Psi\ \text{字节}$$

关键杠杆是**梯度累积**：把 $M$ 个 micro-batch 的梯度累积后再同步一次，$t_{\text{step}}$ 放大 $M$ 倍而 $m$ 不变，$\rho$ 缩小 $M$ 倍。再配合**通信与反向重叠**（按层分桶：一层的梯度算完立刻发起该层的 reduce，反向继续算后面的层），DP 的通信几乎可以完全藏进计算里。

::: details 深入推导：大 batch 的收敛代价与 overlap 的上限

**等效 batch 的统计代价**。梯度累积 $M$ 步等效 batch 为 $M\times b\times N$。线性缩放学习率只在 batch 超过"临界 batch size"（损失景观曲率决定）之前有效；超过后每翻一倍 batch 只省一半步数的一部分——大 batch 不是免费的，有实证的次线性区。DP 的 $N$ 扩大与梯度累积 $M$ 共享同一个"等效 batch"预算，**这就是通信与收敛的耦合点**。

**overlap 的深度**。桶化 allreduce 的时间线：反向传播逐层产出梯度 $g_L, g_{L-1},\dots$，桶大小 $s$ 的选择是权衡——桶太大，最后一桶的通信暴露在反向结束后（无法重叠）；桶太小，通信原语启动开销（$2(N-1)\alpha$ 的延迟项）累积。最优桶数通常在 4~16，需用 [Profiling](/knowledge-planet/ai-infra/profiling/) 实测定。

**为什么 DP 通信可重叠而 TP 不行**。DP 的通信对象（梯度）与反向传播的计算对象（后面层的激活）无依赖，可以流水；TP 的 allreduce 在前向/反向的关键路径上（下一层计算依赖本层 allreduce 结果），结构上无法重叠（据 Patarasuk & Yuan 2009、Megatron-LM v2 分析）。

:::

## 思考题

1. 7B 模型、64 卡、$B_{\text{eff}}=450$ GB/s：不累积时单步 60 ms，梯度同步占多少？累积 8 步后呢？
2. ZeRO-3 通信 1.5×，为什么大规模训练仍然普遍开 ZeRO-1/2 而不是 3？
3. DP=128 时等效 batch 已经 4M token，继续加卡到 512 卡该调整什么？

::: details 参考答案

1. $m=14\ \text{GB}$，$T=2\times14/450\approx62\ \text{ms}$？注意 64 卡 ring 的系数 $2\times63/64\approx1.97$：$T\approx61\ \text{ms}$，占比 $\approx100\%$——完全不可接受。累积 8 步后 $t_{\text{step}}=480\ \text{ms}$，占比降至 $\approx13\%$，再叠 overlap 后基本隐藏。
2. ZeRO-3 需要每层前向/反向 allgather 权重，通信在计算关键路径上、只能部分重叠；ZeRO-1/2 通信模式与朴素 DP 相同（可完全重叠）。显存不够时才升级到 3，或改用 TP/PP 把权重先切薄。
3. 等效 batch 已远超临界 batch size，继续线性堆卡收益递减：改用更激进的并行（数据并行维度之外，让每卡的 micro-batch 更小、降低梯度累积）、调大学习率配合 warmup，或接受次线性扩展。

:::

## 小结

- DP = 复制模型 + allreduce 梯度，吞吐近线性扩展，是所有配置的最外层。
- 显存靠 ZeRO 修补，通信靠梯度累积 + 分桶重叠修补，两者都成熟后 DP 几乎免费。
- DP 的隐藏账是等效 batch 的收敛代价，它与梯度累积、卡数共享同一预算。
- 通信可重叠是 DP 区别于 TP 的结构优势。

## 参考资料

- Rajbhandari et al., [ZeRO](https://arxiv.org/abs/1910.02054)（arXiv 1910.02054）
- Patarasuk & Yuan, [Bandwidth Optimal All-Reduce Algorithms](https://doi.org/10.1016/j.jpdc.2008.06.004)（JPDC 2009）
- Goyal et al., [Accurate, Large Minibatch SGD](https://arxiv.org/abs/1706.02677)（arXiv 1706.02677，线性缩放规则）
- McCandlish et al., [An Empirical Model of Large-Batch Training](https://arxiv.org/abs/1812.06162)（arXiv 1812.06162，临界 batch size）
