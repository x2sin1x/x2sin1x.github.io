---
title: "架构与超参数"
date: 2026-04-02T10:21:00+08:00
weight: 103
---
# 架构与超参数

> 对应课程 Lecture 3:Architectures, hyperparameters(Tatsu)

## 现代 Transformer 的解剖图

从 GPT-1 到今天的 Llama、Qwen，语言模型的骨干架构高度趋同。一个现代 decoder-only（仅解码器）Transformer 长这样：

```text
输入 token
   │
   ▼
词嵌入 embedding + 位置编码 RoPE
   │
   ▼
┌────────────────────────────── × n_layers ─┐
│  x = x + Attention(RMSNorm(x))   ← 残差   │
│  x = x + MLP(RMSNorm(x))         ← 残差   │
└───────────────────────────────────────────┘
   │
   ▼
RMSNorm → 输出投影 → softmax → 下一个 token 的分布
```

每一讲里，我们把每个零件拆开问：&#8203;**它为什么存在？没有它会怎样？**

## 逐组件拆解

### 归一化：LayerNorm → RMSNorm

**归一化（normalization）** 把每层的激活值拉回稳定范围，让深层网络可以训练。现代模型普遍用 **RMSNorm（均方根归一化）** 取代原始 LayerNorm：

$$
\operatorname{RMSNorm}(x) = \frac{x}{\sqrt{\frac{1}{d}\sum_i x_i^2}} \cdot g
$$

相比 LayerNorm，它**去掉了均值中心化**&#8203;，只缩放方差——省一次计算和一份均值参数，效果几乎不变。

### Pre-norm vs Post-norm

残差连接里归一化放哪儿，曾经是个大事：

- **Post-norm**&#8203;（原始 Transformer）：$x = \operatorname{Norm}(x + \operatorname{Sublayer}(x))$——深层训练不稳定，需要学习率预热和小心的初始化；
- **Pre-norm**&#8203;（现代默认）：$x = x + \operatorname{Sublayer}(\operatorname{Norm}(x))$——梯度可以“无损”地穿过残差通路直通底层，训练稳定得多。

::: tip Pre-norm 的代价与补偿
Pre-norm 相当于给网络加了一条恒等“高速公路”，稳定但削弱了每层的表达能力（顶层输入不经过归一化）。Llama 的做法是在最终输出前再放一个 **final RMSNorm** 来补偿，这已经成为标准配置。
:::

### 位置编码：RoPE

注意力本身是**置换不变**的——打乱 token 顺序，输出不变。必须注入位置信息，模型才知道词序有意义。

现代主流是 **旋转位置编码（Rotary Position Embedding,RoPE）**&#8203;：把 query（查询）和 key（键）向量的每两维看作平面上的点，按位置 $m$ 旋转一个角度 $m\theta$：

$$
q_m = R_m q, \quad k_n = R_n k, \quad q_m^\top k_n = q^\top R_{n-m} k
$$

妙处在于：点积自动只依赖**相对位置** $m - n$，天然满足语言建模的平移性。此外 RoPE 兼容“训练短、外推长”的位置扩展技巧（如 YaRN、NTK-aware scaling），这是长上下文模型的标配。

### 激活函数：SwiGLU

前馈网络（MLP）从经典的两层 GELU 结构升级为 **SwiGLU**&#8203;：

$$
\operatorname{SwiGLU}(x) = (\operatorname{SiLU}(xW_1) \odot xW_3) W_2
$$

即在两个投影之间加了**门控（gating）**&#8203;：一路经过 SiLU 激活，另一路直通，逐元素相乘后再投影。代价是参数多了一个矩阵（三个矩阵 vs 两个），通常把隐藏维度缩小到 $\frac{2}{3}$ 倍来保持参数总量不变，换取实证上更好的效果。

### 注意力：多头 + GQA

标准多头注意力（Multi-Head Attention）里，每个头有独立的 Q、K、V 投影：

$$
\operatorname{Attention}(Q, K, V) = \operatorname{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}} + M\right)V
$$

其中 $M$ 是因果掩码（causal mask），禁止“偷看未来”。

**分组查询注意力（Grouped Query Attention,GQA）** 是现代标配：多个 query 头共享一组 KV 头（比如 32 个 Q 头配 8 个 KV 头）。KV 头少了 4 倍，&#8203;**推理时的 KV 缓存显存和读取量直接降 4 倍**&#8203;，而质量损失可以忽略。这直接决定了推理成本。

## 超参数：模型形状怎么定？

给定参数预算 $N$，核心的形状超参数是层数 $L$、隐藏维度 $d$、头数 $H$：

| 超参数 | 常见取法 | 备注 |
| ------ | -------- | ---- |
| $d / L$ | 每层维度约 100~2000,L 与 $\sqrt{N}$ 近似成正比 | 更深 vs 更宽存在权衡；过深难训练，过宽算力浪费 |
| 头数 $H$ | 每头维度固定约 64~128 | 头太少表达力不足，太多则每头太窄 |
| FFN 隐层维度 | $4d$（SwiGLU 下约 $\frac{8}{3}d$）| 让 FFN 参数 ≈ 注意力参数的 2 倍 |
| 词表 $V$ | 10 万~25 万 | 嵌入层在大模型里占比很小，小模型里占比很大 |

::: warning 嵌入层是个“ unfairly 大”的部件
小模型里词嵌入 + 输出投影（$2Vd$ 参数）占比可观。输出投影（untied）和输入嵌入（tied）是否共享权重、logits 是否 soft-cap 等选择，在小模型上影响明显。这些选择值得通过实验仔细考察。
:::

## 训练超参数：怎么把模型训“稳”?

架构定了之后，训练的成败取决于优化超参数。

### AdamW 与学习率

**AdamW** 是绝对主流的自适应优化器，每个参数维护动量 $m$（梯度的滑动平均）和二阶矩 $v$（梯度平方的滑动平均）：

$$
\theta \leftarrow \theta - \eta \cdot \frac{m}{\sqrt{v} + \epsilon} - \eta\lambda\theta
$$

关键超参数：

- **峰值学习率 $\eta$**&#8203;：越大越快收敛但易发散；经验上 $\eta \approx 10^{-3} \cdot \sqrt{d_{model}/768}$ 随模型变大而调小。
- **$\beta_2$（二阶矩衰减率）**&#8203;：从 0.999（Adam 论文默认）调到 0.95 甚至 0.9，是 Chinchilla 时代的重要发现——训练早期梯度二阶矩变化剧烈，过慢的衰减会让更新方向错误。
- **权重衰减 $\lambda$**&#8203;：通常 0.1。
- **梯度裁剪**&#8203;：按全局范数裁到 1.0，防训练尖峰。

### 学习率调度

标准三段式：&#8203;**线性预热 → 稳定训练 → 余弦/线性衰减**&#8203;。

- **预热（warmup）**&#8203;：前几百步把学习率从 0 线性升到峰值，避免初始化阶段的大步长破坏权重；
- **衰减（decay）**&#8203;：训练后期把学习率降到峰值的约 10%，损失会有一个明显的“第二下降”。衰减后的模型不仅最终 loss 更低，微调效果也更好。

### 批次大小

小批次噪声大、效率低；大批次硬件利用率高。实践用**批次大小预热**&#8203;：训练初期用小批次（模型还在大幅移动），随训练推进按 $\text{batch} \propto 1/L$ 逐渐增大，既省算力又不伤收敛。

## 小结

- 现代 Transformer = RMSNorm(pre-norm)+ RoPE + GQA 注意力 + SwiGLU + final norm，每个组件都是“稳定性/效率/质量”三角中的折衷。
- 形状超参数的经验法则：$d$ 定头，层数适中，每头 64~128 维，FFN 约两倍注意力参数。
- 训练配方：AdamW($\beta_2=0.95$)+ 梯度裁剪 + warmup + 余弦衰减 + 批次预热——这套组合拳是几乎所有开源模型的底座。
