---
title: "分块矩阵的乘法"
description: "讲解分块矩阵乘法的定义与运算规则，并联系大模型训练推理中的张量切分与 GPU 并行计算场景。"
date: 2023-11-28
categories:
  - Knowledge
tags:
  - 线性代数
---

# 分块矩阵的乘法

矩阵乘法是线性代数中最重要的运算之一。在机器学习中，矩阵乘法也是经常用到的运算，最常见于 MLP 线性层。

而在实际的模型训练和推理系统中，模型参数和中间激活的张量可能非常大，而 GPU 显存空间有限。因此，我们需要将张量切分为多个块，以在 GPU 上实现并行计算。而这和分块矩阵的乘法有着紧密的联系。

------

## 分块矩阵的定义

一个 $m \times n$ 维的矩阵 $W$ 定义如下

$$
W_{m\times n}=  
\begin{bmatrix}  
  w_{11}& w_{12}& \cdots  & w_{1n} \\  
  w_{21}& w_{22}& \cdots  & w_{2n} \\  
  \vdots & \vdots & \ddots & \vdots \\  
  w_{m1}& w_{m2}& \cdots  & w_{mn}  
\end{bmatrix}
$$

现在将这个矩阵在行方向上划分为 $X$ 个块，在列方向上划分为 $Y$ 个块。这样，每个块的维度为 $x \times y$，其中

$$
\begin{cases}
    x = \dfrac{m}{X} \\
    y = \dfrac{n}{Y}
\end{cases}
$$

于是，分块后的矩阵可记为

$$
W_{X \times Y}=
\begin{bmatrix}
    W_{11} & W_{12} & \cdots & W_{1Y} \\
    W_{21} & W_{22} & \cdots & W_{2Y} \\
    \vdots & \vdots & \ddots & \vdots \\
    W_{X1} & W_{X2} & \cdots & W_{XY}
\end{bmatrix}
$$

其中，每个块 $W_{ij} \ (1 \leqslant i,j \leqslant X,Y)$ 可以表示为

$$
W_{ij} = \begin{bmatrix}
    w_{(i-1)x+1, (j-1)y+1} & w_{(i-1)x+1, (j-1)y+2} & \cdots & w_{(i-1)x+1, jy} \\
    w_{(i-1)x+2, (j-1)y+1} & w_{(i-1)x+2, (j-1)y+2} & \cdots & w_{(i-1)x+2, jy} \\
    \vdots & \vdots & \ddots & \vdots \\
    w_{ix,(j-1)y+1} & w_{ix, (j-1)y+2} & \cdots & w_{ix, jy}
\end{bmatrix}
$$

## 向量与分块矩阵相乘

设一个 $m$ 维的向量

$$
\lambda = \begin{bmatrix} k_1 \\ k_2 \\ \vdots \\ k_m \end{bmatrix}
$$

要使向量 $\lambda$ 右乘分块矩阵 $W$，需要相应地将向量 $\lambda$ 分成 $X$ 个块，即

$$
\lambda = \begin{bmatrix} \lambda_1 \\ \lambda_2 \\ \vdots \\ \lambda_X \end{bmatrix}
$$

其中，每个块 $\lambda_{i} \ (1 \leqslant i \leqslant X)$ 可以表示为

$$
\lambda_i = \begin{bmatrix}
    k_{(i-1)x+1} \\
    k_{(i-1)x+2} \\
    \vdots \\
    k_{ix}
\end{bmatrix}
$$

因此，向量 $\lambda$ 右乘分块矩阵 $W$ 可以表示为

$$
\lambda^{\top} W = 
\begin{bmatrix}
    \displaystyle \sum_{i=1}^{X} \lambda_{i}^{\top} W_{i1} &
    \displaystyle \sum_{i=1}^{X} \lambda_{i}^{\top} W_{i2} &
    \cdots &
    \displaystyle \sum_{i=1}^{X} \lambda_{i}^{\top} W_{iy}
\end{bmatrix}
$$

## 矩阵与分块矩阵相乘

设一个 $d \times m$ 维的矩阵

$$
A_{d \times m} = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1m} \\ a_{21} & a_{22} & \cdots & a_{2m} \\ \vdots & \vdots & \ddots & \vdots \\ a_{d1} & a_{d2} & \cdots & a_{dm} \end{bmatrix}
$$

仿照向量与分块矩阵相乘的方式，如果对矩阵 $A$ 作 1D 切分，即

$$
A = \begin{bmatrix} A_{1} & A_{2} & \cdots & A_{X} \end{bmatrix}
$$

其中，每个分块矩阵的维度是 $d \times x$。那么，矩阵 $A$ 右乘分块矩阵 $W$ 可以表示为

$$
AW = 
\begin{bmatrix}
    \displaystyle \sum_{i=1}^{X} A_{i} W_{i1} &
    \displaystyle \sum_{i=1}^{X} A_{i} W_{i2} &
    \cdots &
    \displaystyle \sum_{i=1}^{X} A_{i} W_{iy}
\end{bmatrix}
$$

如果对矩阵 $A$ 作 2D 切分，在行方向上切分成 $T$ 个块，在列方向上切分成 $X$ 个块。这样，每个块的维度就变成 $t \times x$，其中

$$
t = \dfrac{d}{T}
$$

那么矩阵 $A$ 可表示为

$$
A_{T \times X} = 
\begin{bmatrix}
    A_{11} & A_{12} & \cdots & A_{1X} \\
    A_{21} & A_{22} & \cdots & A_{2X} \\
    \vdots & \vdots & \ddots & \vdots \\
    A_{T1} & A_{T2} & \cdots & A_{TX}
\end{bmatrix}
$$

这样，矩阵 $A$ 右乘分块矩阵 $W$ 可以表示为

$$
AW = 
\begin{bmatrix}
    \displaystyle \sum_{i=1}^{X} A_{1i} W_{i1} &
    \displaystyle \sum_{i=1}^{X} A_{1i} W_{i2} &
    \cdots &
    \displaystyle \sum_{i=1}^{X} A_{1i} W_{iy} \\
    \displaystyle \sum_{i=1}^{X} A_{2i} W_{i1} &
    \displaystyle \sum_{i=1}^{X} A_{2i} W_{i2} &
    \cdots &
    \displaystyle \sum_{i=1}^{X} A_{2i} W_{iy} \\
    \vdots & \vdots & \ddots & \vdots \\
    \displaystyle \sum_{i=1}^{X} A_{Ti} W_{i1} &
    \displaystyle \sum_{i=1}^{X} A_{Ti} W_{i2} &
    \cdots &
    \displaystyle \sum_{i=1}^{X} A_{Ti} W_{iy}
\end{bmatrix}
$$

## 分块矩阵乘法的一般规律

与普通的矩阵乘法相比，分块矩阵乘法多了一个步骤：分块累加。用规范化的数学语言描述，即

$$
\begin{aligned}
    A_{m \times p} &= \begin{bmatrix}
        A_{11} & A_{12} & \cdots & A_{1P} \\
        A_{21} & A_{22} & \cdots & A_{2P} \\
        \vdots & \vdots & \ddots & \vdots \\
        A_{M1} & A_{M2} & \cdots & A_{MP}
    \end{bmatrix} \\
    B_{p \times n} &= \begin{bmatrix}
        B_{11} & B_{12} & \cdots & B_{1N} \\
        B_{21} & B_{22} & \cdots & B_{2N} \\
        \vdots & \vdots & \ddots & \vdots \\
        B_{P1} & B_{P2} & \cdots & B_{PN}
    \end{bmatrix} \\
    AB &= \begin{bmatrix}
        \displaystyle \sum_{i=1}^{P} A_{1i} B_{i1} & \displaystyle \sum_{i=1}^{P} A_{1i} B_{i2} & \cdots & \displaystyle \sum_{i=1}^{P} A_{1i} B_{iN} \\
        \displaystyle \sum_{i=1}^{P} A_{2i} B_{i1} & \displaystyle \sum_{i=1}^{P} A_{2i} B_{i2} & \cdots & \displaystyle \sum_{i=1}^{P} A_{2i} B_{iN} \\
        \vdots & \vdots & \ddots & \vdots \\
        \displaystyle \sum_{i=1}^{P} A_{Mi} B_{i1} & \displaystyle \sum_{i=1}^{P} A_{Mi} B_{i2} & \cdots & \displaystyle \sum_{i=1}^{P} A_{Mi} B_{iN}
    \end{bmatrix}
\end{aligned}
$$

其中，矩阵 $A$ 被 2D 切分为 $M \times P$ 份，矩阵 $B$ 被 2D 切分为 $P \times N$ 份。

而至于向量与分块矩阵的乘法，以及 1D 和 2D 切分的情况，都属于上述一般规律的特例。是否需要将分块累加，取决于是否对 $p$ 维进行切分。

## 图解分块矩阵乘法

设想有 2 个矩阵都被切分成 $2 \times 2$ 的块，每个块在 4 张不同的 GPU 上进行矩阵乘法运算。则每个 GPU 上的计算分别如下面 4 张图所示：

![](5b1754c39f3279088779d105a8ac8fd3.svg)

![](cdffdebf9d18eaacb04b206b64af6266.svg)

![](44432a5b019047ed1de2b056359358aa.svg)

![](dec14c42714e74a73b6df392aa0583fe.svg)

## 分块矩阵乘法的意义

矩阵乘法是线性代数中最重要的运算之一。在机器学习中，矩阵乘法也是经常用到的运算，最常见于 MLP 线性层。

而在实际的模型训练和推理系统中，模型参数和中间激活的张量可能非常大，而 GPU 显存空间有限。因此，我们需要将张量切分为多个块，以在 GPU 上实现并行计算。

而分块矩阵乘法的意义在于，分块意味着一个完整的张量可以进行切分，在 GPU 上进行并行的矩阵乘法计算从理论上说是可行的。

不过，如果我们将矩阵在 $p$ 维上切分，最终的计算结果需要沿着 $p$ 维进行聚合。这样的操作会带来额外的通信开销。

此外，最终的结果从整体上看是多个小块矩阵的拼接，这意味着每个 GPU 可以存储相应的不同的结果。至于是否存在通信开销，取决于后面的算子是否需要完整的张量。
