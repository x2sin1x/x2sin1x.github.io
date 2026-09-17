---
title: "PyTorch 与资源估算"
date: 2026-04-02T10:12:00+08:00
weight: 102
---
# PyTorch 与资源估算

> 对应课程 Lecture 2:PyTorch (einops), resource accounting(FLOPs, memory, arithmetic intensity)

训练一个大模型之前，你得先回答：“需要多少算力？多少显存？能跑多快？”这一讲教你怎么**用纸和笔估算出来**&#8203;，这决定了实验设计和硬件预算。

## PyTorch 核心工具箱

### 张量与 einops

PyTorch 里一切都是**张量（Tensor）**&#8203;。写模型时最容易出错的是形状变换（reshape/permute/broadcast）,&#8203;**einops** 用语义化的写法把它变简单：

```python
from einops import rearrange

# 把多头注意力的 q 从 [B, T, H, D] 变成 [B, H, T, D]
q = rearrange(q, "batch seq heads dim -> batch heads seq dim")

# 一个表达式同时完成 reshape 和转置,可读性远高于
# x.view(B, T, H, D).transpose(1, 2)
```

### 模型与训练循环的骨架

```python
model = TransformerLM(vocab_size, ...).to(device)
optimizer = AdamW(model.parameters(), lr=1e-3)

for batch in dataloader:
    optimizer.zero_grad()          # 1. 清空梯度
    logits = model(batch.tokens)   # 2. 前向传播
    loss = cross_entropy(logits[:, :-1], batch.labels[:, 1:])  # 3. 算损失
    loss.backward()                # 4. 反向传播算梯度
    clip_grad_norm_(model.parameters(), 1.0)  # 5. 梯度裁剪
    optimizer.step()               # 6. 更新参数
```

注意第 3 步的错位：`logits[:, :-1]` 预测 `labels[:, 1:]`——**每个位置的预测目标都是下一个词元**&#8203;。

### 混合精度训练

现代训练用 **bf16（bfloat16,16 位浮点）** 存参数和激活值，主权重和优化器状态保留 fp32。bf16 的指数位和 fp32 一样多，所以不容易溢出，比 fp16 更适合训练。

## 算力估算：这个训练要多少 FLOPs?

**FLOPs（floating point operations，浮点运算次数）** 是衡量计算量的单位。

关键事实：&#8203;**一个矩阵乘法 `y = Wx`（W 是 $d_{in} \times d_{out}$）需要 $2 d_{in} d_{out}$ FLOPs**&#8203;（乘加各算一次）。

对 Transformer 来说，每层的主要计算都是权重矩阵乘法。逐层数下来，结论可以压缩成一个近似公式：设参数量为 $N$（不含嵌入），训练 token 数为 $D$，则训练总计算量约为：

$$
C \approx 6 N D \text{ FLOPs}
$$

其中系数 6 的构成：&#8203;**前向 2ND + 反向 4ND**&#8203;（反向约为前向的两倍，因为要算输入梯度和权重梯度两组矩阵乘法）。

::: tip 例：GPT-3 规模的训练要多少算力？
GPT-3 有 $N \approx 175 \times 10^9$ 参数，训练了 $D \approx 3 \times 10^{11}$ token：

$$
C \approx 6 \times 1.75 \times 10^{11} \times 3 \times 10^{11} \approx 3.1 \times 10^{23} \text{ FLOPs}
$$

一块 H100 按 bf16 实际利用 400 TFLOP/s 算，单卡需要约 $3.1\times10^{23} / 4\times10^{14} \approx 7.8\times10^{8}$ 秒 ≈ **25 年**&#8203;。所以必须用几千张卡并行——这就是后面“系统”章节要解决的问题。
:::

## 显存估算：一张卡放得下吗？

训练时显存里躺着四类东西（设参数量为 $N$，以 bf16 混合精度 + AdamW 为例）：

| 组件 | 每参数字节数 | 说明 |
| ---- | ---- | ---- |
| 参数 | 2 | bf16 存储（或 fp32 主权重占 4）|
| 梯度 | 2 | 与参数同精度 |
| AdamW 一阶动量 $m$ | 4 | fp32 |
| AdamW 二阶动量 $v$ | 4 | fp32 |

合计约 **16 字节/参数**&#8203;（fp32 主权重时约 18）。直观记忆法：&#8203;**AdamW 训练状态大约是参数量的 16 倍字节**&#8203;。

::: tip 例：7B 模型要多少显存？
$7 \times 10^9 \times 16 = 112$ GB,&#8203;**一块 80GB 的 H100 放不下**&#8203;。还不算激活值！解决办法：
- 优化器状态分片（ZeRO，见[并行策略](/knowledge-planet/cs336/lecture-07-08-parallelism/)）；
- 激活值重计算（activation checkpointing，用时间换显存）；
- 并行切分到多卡。
:::

**激活值（activations）** 的显存和批次大小、序列长度、隐藏维度成正比，粗略地每层每 token 需要 $O(d)$ 级别的存储，序列越长、批次越大越吃显存。注意力矩阵本身是 $O(T^2)$ 的，这也是 FlashAttention（见[内核与 Triton](/knowledge-planet/cs336/lecture-06-kernels-triton/)）要解决的问题。

## 运算强度：GPU 到底“吃”什么？

### 硬件的两面

GPU 有两个独立的引擎：

- **计算引擎**&#8203;：H100 的 bf16 峰值约 **1000 TFLOP/s**&#8203;（稀疏再翻倍）；
- **显存带宽**&#8203;：HBM3 显存带宽约 **3 TB/s**——数据从显存搬到计算单元的速度。

**运算强度（arithmetic intensity）** = FLOPs / 传输字节数，衡量“每搬一字节数据能做多少次计算”。

### Roofline 模型：算力受限 vs 带宽受限

把运算强度画在图上（即 **roofline 模型**&#8203;），存在一个分水岭 $I^* = \text{峰值算力} / \text{峰值带宽} \approx 1000\,\text{TFLOP/s} \div 3\,\text{TB/s} \approx 333 \text{ FLOPs/字节}$：

- $I < I^*$：&#8203;**带宽受限（memory-bound）**——计算单元在等数据，实际性能由带宽决定；
- $I > I^*$：&#8203;**计算受限（compute-bound）**——数据喂饱了，实际性能由算力决定，这才是理想状态。

### 各操作的运算强度

考虑 batch 很大的矩阵乘法 $A_{B\times d} \cdot B_{d \times d}$：

- FLOPs ≈ $2Bd^2$;
- 数据量 ≈ $(Bd + 2d^2) \times 2$ 字节（读 A、B，略去写回）；
- 运算强度 ≈ $Bd^2 / Bd = O(d)$。

当 $d$ 达到几千时，运算强度远超 333,&#8203;**大矩阵乘法是计算受限的，可以达到很高的硬件利用率**&#8203;。相反：

- **逐元素操作**&#8203;（激活函数、加法等）：每读一个数只做一两次运算，$I \approx 1$，严重带宽受限；
- **小批次矩阵乘法**&#8203;：$B$ 小时 $I \propto B$，利用率低；
- **解码阶段的自回归生成**&#8203;：每步 batch 小、还要搬全部权重，典型带宽受限。

::: tip 这个视角贯穿整门课
后面所有的系统优化技术，本质都在回答同一个问题：&#8203;**怎么提高运算强度？**

- **算子融合（fusion）**&#8203;：把逐元素操作合并进矩阵乘法，省掉中间结果搬运 → 提高带宽受限部分的速度；
- **FlashAttention**&#8203;：用分块计算减少 $O(T^2)$ 的显存读写；
- **并行切分**&#8203;：让每张卡上的矩阵乘法尽量大；
- **推理 batching**&#8203;：攒大批次把解码变计算受限。
:::

## 小结

- 训练计算量 $\approx 6ND$：GPT-3 级别需要 $10^{23}$ FLOPs，单卡以年计，必须并行。
- AdamW 训练状态 ≈ 每参数 16 字节，7B 模型一张卡放不下，需要 ZeRO / 重计算 / 并行。
- 用 roofline 模型判断瓶颈：运算强度低于阈值（~333 FLOPs/字节）就是带宽受限；优化的一切目标是提高运算强度。
