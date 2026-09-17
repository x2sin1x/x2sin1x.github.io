---
title: "内核与 Triton"
date: 2026-04-02T10:32:00+08:00
weight: 106
---
# 内核与 Triton

> 对应课程 Lecture 6:Kernels, Triton(Percy)

## 什么时候需要手写内核？

PyTorch 已经把矩阵乘法做得很高效（调用 cuBLAS），大多数时候你不需要手写内核（kernel）。但有三类场景例外：

1. **很多小操作串起来**&#8203;：比如 `softmax(x) + x * y` 会触发多次显存读写，每次都搬一遍中间结果；
2. **库没有的实现**&#8203;：自定义注意力、新的归一化；
3. **省显存**&#8203;：比如注意力里 $O(T^2)$ 的中间矩阵，根本不想物化它。

核心武器是**算子融合（fusion）**&#8203;：把多个操作写进一个内核，中间结果留在寄存器/共享内存里，不回写显存。

## Triton：被 Python 包装的 GPU 编程

NVIDIA 的 CUDA C++ 太难写。&#8203;**Triton** 是 OpenAI 开源的 DSL（领域专用语言），用 Python 写内核，自动处理线程调度、共享内存、张量核心映射。你只需要想清楚**一个块（block）怎么算**&#8203;：

```python
import triton
import triton.language as tl

@triton.jit
def add_kernel(x_ptr, y_ptr, out_ptr, n, BLOCK: tl.constexpr):
    pid = tl.program_id(0)                     # 第几个程序实例
    offs = pid * BLOCK + tl.arange(0, BLOCK)   # 本块负责的元素下标
    mask = offs < n                            # 越界保护
    x = tl.load(x_ptr + offs, mask=mask)       # 从显存读一块
    y = tl.load(y_ptr + offs, mask=mask)
    tl.store(out_ptr + offs, x + y, mask=mask) # 算完写回
```

Triton 的心智模型：&#8203;**内核 = 一个多维网格上的程序，每个程序处理一小块数据**&#8203;。与 CUDA 的区别是你不管单个线程，只管块级逻辑。

### 例：融合 softmax 内核

普通 PyTorch 写 softmax 会产生多次读写；融合版本一遍完成：

```python
@triton.jit
def softmax_kernel(x_ptr, out_ptr, n, BLOCK: tl.constexpr):
    offs = tl.arange(0, BLOCK)
    mask = offs < n
    x = tl.load(x_ptr + offs, mask=mask, other=-float("inf"))
    x = x - tl.max(x, axis=0)              # 数值稳定:减最大值
    e = tl.exp(x)
    e = e / tl.sum(e, axis=0)
    tl.store(out_ptr + offs, e, mask=mask)
```

注意减最大值这步：不做的话大数值的 `exp` 会溢出——**数值稳定性是内核编写中与性能同等重要的主题**&#8203;。

## FlashAttention：分块的艺术

**FlashAttention** 是这一讲的高潮。它解决的问题是：标准注意力要物化 $T \times T$ 的注意力矩阵，显存 $O(T^2)$，读写慢还容易爆显存。

难点：softmax 的分母要对**整行**求和，而分块计算时每次只能看到一部分——怎么办？

### 第一步：分块算，增量更新

把 Q、K、V 都切成块，只装得下当前 K、V 块对应的注意力结果。对每个 K、V 块，先算局部分数 $s = QK^\top$，然后用**在线 softmax(online softmax)** 的技巧：

维护到当前块为止的运行统计量：

- $m$：已见分数的最大值；
- $\ell$：已见的 $\exp(s - m)$ 之和；
- $o$：已累积的未归一化输出。

遇到新块时，更新规则：

$$
m_{new} = \max(m, \max(s_{new})), \quad
o \leftarrow e^{m - m_{new}} o + \exp(s_{new} - m_{new}) V_{new}, \quad
\ell \leftarrow e^{m - m_{new}} \ell + \sum \exp(s_{new} - m_{new})
$$

处理完全部块后，$o / \ell$ 就是精确的 softmax 注意力输出。&#8203;**每一项都精确，没有任何近似。**

### 为什么快？

- 显存从 $O(T^2)$ 降到 $O(T)$（不物化注意力矩阵）；
- 中间结果全程待在 SRAM，显存读写从 $O(T^2)$ 次降到 $O(T)$ 块；
- 分块大小按共享内存容量设计，配合张量核心，实测比朴素实现快 2~4 倍，长序列下优势更大。

::: tip 理解记忆
FlashAttention = **tiling（分块）+ online softmax（增量归一化）+ fusion（融合）**&#8203;，三招都是为了让“每字节显存读写换到更多 FLOPs”。它的后续版本 FlashAttention-2/3 进一步优化并行度和流水线。
:::

### 反向传播怎么办？

训练还需要梯度。FlashAttention 的做法是**前向只保存 $m$ 和 $\ell$**&#8203;（每行两个数），反向时**重新计算**注意力矩阵——典型的“用重计算换显存”，反正注意力是计算受限的，重计算的时间成本可以接受。

## 内核优化的通用方法论

1. **先剖析（profiling）**&#8203;：用 PyTorch profiler / Nsight 找出真正慢的操作，别猜；
2. **数一数**&#8203;：这个操作的 roofline 位置在哪？理想时间和实际时间差多少？
3. **融合 + 分块**&#8203;：减少显存往返，把数据留在 SRAM;
4. **数值稳定**&#8203;：减最大值、防溢出，与性能一起考虑；
5. **基准测试要严谨**&#8203;：预热、同步、多次取均值，排除 Python 开销。

## 小结

- 手写内核的动机是融合与省显存，不是重复造矩阵乘法。
- Triton 让你以“块”为单位写 GPU 程序，自动处理底层调度。
- FlashAttention 用在线 softmax + 分块，把注意力变成显存线性、速度更快、结果完全精确——现代模型的长上下文能力部分归功于它。
