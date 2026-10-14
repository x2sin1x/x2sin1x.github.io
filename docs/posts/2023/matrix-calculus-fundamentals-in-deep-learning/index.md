---
title: "深度学习中的矩阵求导基础"
description: "从一元微积分出发，循序渐进地讲解深度学习中的矩阵求导：偏导数、梯度与方向导数、Jacobian 矩阵、链式法则与分母布局、反向传播，常见网络层（全连接、激活、卷积、归一化）的导数，以及 Feed Forward 网络与自注意力块的反向传播。"
date: 2026-09-18
categories:
  - Essay
  - Knowledge
tags:
  - 深度学习
  - 线性代数
  - 多元函数微分学
---

# 深度学习中的矩阵求导基础

------

> 本文根据[合集·深度学习中的数学 by 齐宪标](https://space.bilibili.com/1706874133/channel/collectiondetail?sid=1933483)系列视频整理。
>
> 阅读本文只需要一元函数微积分（导数与链式法则）和线性代数（矩阵乘法与转置）的基础。
>
> 在本文中，用小写字母表示标量，用粗体小写字母表示向量，用粗体大写字母表示矩阵；$\mathbf{1}$ 表示元素全为 1 的列向量，$\mathbf{I}$ 表示单位矩阵，$\circ$ 表示逐元素相乘（Hadamard 积）。

## 写在前面

训练神经网络，本质上是在不断微调网络中的海量参数，让损失函数尽可能小。现代神经网络的参数动辄百万甚至上千亿个，而指挥这场大规模微调的指挥棒，就是**梯度**：它告诉每一个参数应该往哪个方向调、调多快。

因此，如何对向量和矩阵求导，就成了理解深度学习训练过程绕不开的一关。本文从读者最熟悉的一元函数导数出发，循序渐进地完成三次推广：

1. 一元函数 → 多元函数：偏导数、梯度、方向导数；
2. 标量函数 → 向量函数：Jacobian 矩阵、Hessian 矩阵；
3. 一元链式法则 → 矩阵链式法则：分子布局与分母布局，进而理解神经网络的反向传播。

在此基础上，本文再备齐常见网络层（全连接、激活、卷积、归一化）的导数积木，并把 Feed Forward 网络与自注意力块组装成端到端的反向传播。至于「为什么对输入求导」「梯度如何在层间传递」这些深入的问题，后文会在合适的地方娓娓道来。

## 从一元导数到偏导数

### 回顾：一元函数的导数

在高等数学和数学分析的课程中，我们知道一元函数 $y = f(x)$ 的导数定义为

$$
\dfrac{\mathrm{d}y}{\mathrm{d}x} = \lim_{h \to 0} \dfrac{f(x + h) - f(x)}{h}
$$

它的几何意义是函数图像在某点处切线的斜率，物理意义则是瞬时变化率。例如 $f(x) = x^2$，有

$$
\dfrac{\mathrm{d}f}{\mathrm{d}x} = \lim_{h \to 0} \dfrac{(x + h)^2 - x^2}{h} = \lim_{h \to 0} (2x + h) = 2x
$$

### 偏导数：固定其他变量

多元函数的输入不止一个，例如 $y = f(x_1, x_2, \dots, x_n)$。想求它的导数，最自然的想法是：**每次只让一个输入变化，把其余输入全部固定**，这样多元函数就退化成了熟悉的一元函数。这样得到的导数称为偏导数，记作

$$
\dfrac{\partial y}{\partial x_i} = \lim_{h \to 0} \dfrac{f(x_1, \dots, x_i + h, \dots, x_n) - f(x_1, \dots, x_i, \dots, x_n)}{h}
$$

计算时，只需把其他自变量当作常数，按一元函数求导即可。

举一个贯穿全文的例子：

$$
f(x_1, x_2) = x_1^2 + 3 x_1 x_2
$$

把 $x_2$ 当作常数，得 $\dfrac{\partial f}{\partial x_1} = 2 x_1 + 3 x_2$；把 $x_1$ 当作常数，得 $\dfrac{\partial f}{\partial x_2} = 3 x_1$。在点 $(1, 2)$ 处，两个偏导数分别为 $8$ 和 $3$。

几何上，曲面 $z = f(x_1, x_2)$ 被平面 $x_2 = 2$ 截出一条曲线，偏导数 $\dfrac{\partial f}{\partial x_1}$ 就是这条曲线在 $x_1$ 方向上的斜率。

### 梯度与方向导数

给定一个多元函数

$$
y = f(\mathbf{x}) = f(x_1, x_2, \dots, x_n) \quad (\mathbf{x} \in \mathbb{R}^n)
$$

其梯度 $\nabla f(\mathbf{x})$ 定义为把 $y$ 对 $\mathbf{x}$ 的所有偏导数按顺序排成的一列：

$$
\nabla f(\mathbf{x}) = \begin{bmatrix}
    \dfrac{\partial y}{\partial x_1} \\
    \dfrac{\partial y}{\partial x_2} \\
    \vdots \\
    \dfrac{\partial y}{\partial x_n}
\end{bmatrix}
$$

对于多元函数而言，其梯度是一个和 $\mathbf{x}$ 同样维度的向量。沿用上面的例子：

$$
\nabla f(\mathbf{x}) = \begin{bmatrix} 2 x_1 + 3 x_2 \\ 3 x_1 \end{bmatrix},
\qquad
\nabla f(1, 2) = \begin{bmatrix} 8 \\ 3 \end{bmatrix}
$$

而方向导数是指函数在某一点处，沿某一给定方向 $\mathbf{v}$ 的变化率，是一个标量。它其实就是把一元导数的定义原封不动地搬到「沿 $\mathbf{v}$ 方向的直线」上：

$$
D_{\mathbf{v}}f(\mathbf{x}) = \lim_{t \to 0} \dfrac{f(\mathbf{x} + t \mathbf{v}) - f(\mathbf{x})}{t}
$$

当 $f$ 可微时，令 $\varphi(t) = f(\mathbf{x} + t \mathbf{v})$，这是一元函数，用一元链式法则对 $t$ 求导即得

$$
D_{\mathbf{v}}f(\mathbf{x}) = \sum_{i=1}^{n} \dfrac{\partial y}{\partial x_i} v_i = \nabla f(\mathbf{x})^{\top} \cdot \mathbf{v}
$$

特别地，当 $\mathbf{v}$ 取第 $i$ 个坐标轴方向的单位向量时，方向导数恰好就是第 $i$ 个偏导数——偏导数只是方向导数的特例。

### 梯度下降：梯度的用武之地

方向导数公式 $D_{\mathbf{v}}f = \lVert \nabla f \rVert \lVert \mathbf{v} \rVert \cos \theta$（$\theta$ 是 $\mathbf{v}$ 与梯度的夹角）告诉我们：当 $\mathbf{v}$ 是单位向量时，

- $\theta = 0$，即 $\mathbf{v}$ 与梯度同向时，函数上升最快；
- $\theta = \pi$，即 $\mathbf{v}$ 与梯度反向时，函数下降最快。

所以，**梯度方向是函数值上升最快的方向，负梯度方向是下降最快的方向**。想让损失函数变小，就应该沿着负梯度方向更新参数：

$$
\mathbf{x} \leftarrow \mathbf{x} - \eta \nabla f(\mathbf{x})
$$

这就是梯度下降法，其中 $\eta$ 称为学习率。深度学习的训练，自始至终都在重复这一行公式。

式中的 $\mathbf{x}$ 是一个泛指的「变量」：在纯数学里它是函数的自变量，而在深度学习的训练场景中，它代表的是被优化的**参数整体**（所有权重矩阵、偏置拼接在一起），而不是网络的输入——数据是给定的，训练中保持不变，改变的只有参数。

## Jacobian 矩阵

前面讨论的都是「多个输入、一个输出」的标量函数。但在神经网络中，一层往往同时输出多个数，例如 $\mathbf{y} = \mathbf{Wx}$。这类定义域和值域都是向量的函数称为**向量函数**：

$$
\mathbf{y} = f(\mathbf{x}) = \begin{bmatrix}
    f_1(\mathbf{x}) \\
    f_2(\mathbf{x}) \\
    \vdots \\
    f_m(\mathbf{x})
\end{bmatrix}
\quad (\mathbf{x} \in \mathbb{R}^n, \mathbf{y} \in \mathbb{R}^m)
$$

向量函数的每一个分量 $f_i$ 都是多元标量函数，都有自己的梯度。把所有梯度组合成一个矩阵，称为 Jacobian 矩阵，记为 $\mathbf{J}(\mathbf{x})$。它定义为

$$
\begin{aligned}
    \mathbf{J}(\mathbf{x}) &= \begin{bmatrix}
        \dfrac{\partial y_1}{\partial x_1} & \dfrac{\partial y_1}{\partial x_2} & \cdots & \dfrac{\partial y_1}{\partial x_n} \\
        \dfrac{\partial y_2}{\partial x_1} & \dfrac{\partial y_2}{\partial x_2} & \cdots & \dfrac{\partial y_2}{\partial x_n} \\
        \vdots & \vdots & \ddots & \vdots \\
        \dfrac{\partial y_m}{\partial x_1} & \dfrac{\partial y_m}{\partial x_2} & \cdots & \dfrac{\partial y_m}{\partial x_n}
    \end{bmatrix} \\
    &= \begin{bmatrix}
        \nabla f_1(\mathbf{x}) &
        \nabla f_2(\mathbf{x}) &
        \cdots &
        \nabla f_m(\mathbf{x})
    \end{bmatrix}^{\top}
\end{aligned}
$$

是一个 $m \times n$ 的矩阵，其中 $m$ 是输出的维度，$n$ 是输入的维度。每一行恰好是 $\mathbf{y}$ 的一个分量对 $\mathbf{x}$ 的梯度。

举一个具体的例子：$\mathbf{y} = \begin{bmatrix} x_1^2 + x_2 \\ 3 x_1 x_2 \end{bmatrix}$，则

$$
\mathbf{J}(\mathbf{x}) = \begin{bmatrix} 2 x_1 & 1 \\ 3 x_2 & 3 x_1 \end{bmatrix}
$$

::: warning
**注意：导数的「形状」取决于约定**

Jacobian 矩阵的维度是 $m \times n$，而不是 $n \times m$。向量函数的求导运算是一种从函数到函数的映射，用形式化的语言表达就是

$$
\mathrm{J}: (\mathbb{R}^{n} \to \mathbb{R}^{m}) \longrightarrow \mathbb{R}^{m \times n}
$$

在文献中存在两种通行的记录方式：

- **分子布局**：$\dfrac{\partial \mathbf{y}}{\partial \mathbf{x}}$ 就是 Jacobian 矩阵（$m \times n$）；
- **分母布局**：$\dfrac{\partial \mathbf{y}}{\partial \mathbf{x}}$ 取其转置（$n \times m$），此时标量函数的导数恰好是与自变量同形状的列向量（梯度）。

本文约定：向量函数的导数按 Jacobian 矩阵（分子布局）记录；而标量函数对向量的导数按惯例写成列向量，即梯度（分母布局）。后文将看到，深度学习习惯使用分母布局来做链式法则，此时对 Jacobian 取转置即可。
:::

## Hessian 矩阵

给定一个多元函数

$$
y = f(\mathbf{x}) = f(x_1, x_2, \dots, x_n) \quad (\mathbf{x} \in \mathbb{R}^n)
$$

其 Hessian 矩阵定义为

$$
\begin{aligned}
    \mathbf{H}(\mathbf{x}) &= \nabla^{2} f(\mathbf{x}) \\
    &= \dfrac{\partial}{\partial \mathbf{x}} \left( \dfrac{\partial y}{\partial \mathbf{x}} \right) \\
    &= \begin{bmatrix}
    \dfrac{\partial^2 y}{\partial x_1^2} & \dfrac{\partial^2 y}{\partial x_1 \partial x_2} & \cdots & \dfrac{\partial^2 y}{\partial x_1 \partial x_n} \\
    \dfrac{\partial^2 y}{\partial x_2 \partial x_1} & \dfrac{\partial^2 y}{\partial x_2^2} & \cdots & \dfrac{\partial^2 y}{\partial x_2 \partial x_n} \\
    \vdots & \vdots & \ddots & \vdots \\
    \dfrac{\partial^2 y}{\partial x_n \partial x_1} & \dfrac{\partial^2 y}{\partial x_n \partial x_2} & \cdots & \dfrac{\partial^2 y}{\partial x_n^2}
\end{bmatrix}
\end{aligned}
$$

Hessian 矩阵收集了所有的二阶偏导数，它是「梯度的导数」：一元情形下对应 $f''(x)$，描述的是函数的弯曲程度（凹凸性）。当二阶偏导数连续时，求导次序可以交换（Schwarz 定理），因此 $\mathbf{H}$ 是对称矩阵。例如对前文的 $f(x_1, x_2) = x_1^2 + 3 x_1 x_2$，有

$$
\mathbf{H} = \begin{bmatrix} 2 & 3 \\ 3 & 0 \end{bmatrix}
$$

在深度学习优化中，Hessian 矩阵描述了损失曲面在各点的曲率，是牛顿法等二阶优化方法的基础。不过由于它的元素个数是 $n^2$，面对上亿参数的网络时存储和计算都不可行，实践中更多是「借用了它的思想」。

## 导数的链式求导法则

### 回顾：一元链式法则

对于一元复合函数，例如 $f(x) = (2x + 1)^3$，令中间变量 $u = 2x + 1$，则

$$
\dfrac{\mathrm{d}f}{\mathrm{d}x} = \dfrac{\mathrm{d}f}{\mathrm{d}u} \cdot \dfrac{\mathrm{d}u}{\mathrm{d}x} = 3(2x+1)^2 \cdot 2
$$

链式法则说的是：复合函数的导数等于各层函数导数的乘积。对于多层复合

$$
\begin{aligned}
    f(x) &= f_n \circ f_{n-1} \circ \cdots \circ f_2 \circ f_1(x) \\
    &= f_n(f_{n-1}(\cdots f_2(f_1(x))))
\end{aligned}
$$

其链式求导法则为

$$
\dfrac{\mathrm{d}f(x)}{\mathrm{d}x} = \dfrac{\mathrm{d}f(x)}{\mathrm{d}f_n(x)} \cdot \dfrac{\mathrm{d}f_n(x)}{\mathrm{d}f_{n-1}(x)} \cdots \dfrac{\mathrm{d}f_2(x)}{\mathrm{d}f_1(x)} \cdot \dfrac{\mathrm{d}f_1(x)}{\mathrm{d}x}
$$

一元情形下，乘法交换律保证了这些因子随便怎么排都行。但如果自变量是一个向量或矩阵，因子变成了矩阵乘积，而矩阵乘法不满足交换律，于是「从哪头开始乘」就有了讲究——这就引出了分子表达式和分母表达式两种形式。

### 分子表达式和分母表达式

这里的分子和分母指的是原微商式 $\dfrac{\mathrm{d}f(x)}{\mathrm{d}x}$ 中的分子和分母。设各层函数的维度依次为 $n_0 \to n_1 \to \cdots \to n_n$（$f_k: \mathbb{R}^{n_{k-1}} \to \mathbb{R}^{n_k}$，$f = f_n$）。顾名思义，分子/分母表达式的含义就是先写出含分子/分母的那一项：

$$
\begin{align}
    \dfrac{\mathrm{d}f(x)}{\mathrm{d}x} &= \dfrac{\mathrm{d}f(x)}{\mathrm{d}f_n(x)} \cdot \dfrac{\mathrm{d}f_n(x)}{\mathrm{d}f_{n-1}(x)} \cdots \dfrac{\mathrm{d}f_2(x)}{\mathrm{d}f_1(x)} \cdot \dfrac{\mathrm{d}f_1(x)}{\mathrm{d}x} \tag{1} \\
    &= \dfrac{\mathrm{d}f_1(x)}{\mathrm{d}x} \cdot \dfrac{\mathrm{d}f_2(x)}{\mathrm{d}f_1(x)} \cdots \dfrac{\mathrm{d}f_n(x)}{\mathrm{d}f_{n-1}(x)} \cdot \dfrac{\mathrm{d}f(x)}{\mathrm{d}f_n(x)} \tag{2}
\end{align}
$$

在分子布局下，$\dfrac{\mathrm{d}f_k(x)}{\mathrm{d}f_{k-1}(x)}$ 是 $n_k \times n_{k-1}$ 的 Jacobian 矩阵，$(1)$ 式各因子从左到右依次为 $1 \times n_n,\ n_n \times n_{n-1},\ \dots$，乘起来恰好是 $1 \times n_0$；在分母布局下，各因子取转置，形状反过来，$(2)$ 式才能乘得通。由此可见：

- 分子表达式是先求**外层**函数，然后逐层深入求导；
- 分母表达式是先求**内层**函数，然后逐层向外求导。

两者只差转置和因子排列顺序，数学上完全等价。但在深度学习中，一般采用**分母表达式**，原因有二：

1. 损失函数 $L$ 是标量，分母布局下 $\dfrac{\mathrm{d}L}{\mathrm{d}\mathbf{x}}$ 与 $\mathbf{x}$ 同形状（列向量），各层梯度的形状与参数矩阵的形状一致，便于直观理解和按形状更新参数；
2. 分母表达式的乘法要从**右往左**进行：先算 $\dfrac{\mathrm{d}L}{\mathrm{d}f_n}$，再逐层左乘更内层的导数——这恰好是「从损失出发、逆着数据流方向」的计算顺序，这正是「反向传播」名字的由来，也与神经网络逐层的结构天然吻合。稍后我们就会看到这种表达方式的方便之处。

## 多项式向量函数的导数

多项式向量函数是指，每个因变量 $y_1, y_2, \cdots, y_m$ 都是关于自变量 $x_1, x_2, \cdots, x_n$ 和常数的多项式函数。本小节主要讨论一次和二次多项式向量函数的导数计算，只需要理解齐次式（不含常数项）的导数计算即可。这两个结论是全连接层、注意力层等很多网络层求导的基石。

### 一次齐次式

$$
\begin{aligned}
    \mathbf{y} &= \mathbf{Wx} \quad (\mathbf{x} \in \mathbb{R}^n, \mathbf{y} \in \mathbb{R}^m) \\
    \dfrac{\partial \mathbf{y}}{\partial \mathbf{x}}
    &= \begin{bmatrix}
        \dfrac{\partial y_1}{\partial x_1} & \dfrac{\partial y_2}{\partial x_1} & \cdots & \dfrac{\partial y_m}{\partial x_1} \\
        \dfrac{\partial y_1}{\partial x_2} & \dfrac{\partial y_2}{\partial x_2} & \cdots & \dfrac{\partial y_m}{\partial x_2} \\
        \vdots & \vdots & \ddots & \vdots \\
        \dfrac{\partial y_1}{\partial x_n} & \dfrac{\partial y_2}{\partial x_n} & \cdots & \dfrac{\partial y_m}{\partial x_n}
    \end{bmatrix} \\
    &= \mathbf{W}^{\top}
\end{aligned}
$$

注意到，$f: \mathbb{R}^n \rightarrow \mathbb{R}^m$ 是一个将向量从 $n$ 维映射到 $m$ 维的向量函数。所以，这里的 $\mathbf{W} \in \mathbb{R}^{m \times n}$ 恰好是其 Jacobian 矩阵，而分母布局下的导数 $\dfrac{\partial \mathbf{y}}{\partial \mathbf{x}}$（$n \times m$）是它的转置。

这个结果直观看非常合理：$\mathbf{y}$ 的每个分量 $y_i = \sum_j w_{ij} x_j$ 对 $x_j$ 的偏导数就是 $w_{ij}$，把这些数按分母布局摆放，自然得到 $\mathbf{W}^{\top}$。

::: info
**常用线性函数求导公式**

$$
\begin{aligned}
    \dfrac{\partial \mathbf{a}^{\top} \mathbf{x}}{\partial \mathbf{x}} &= \mathbf{a} \\
    \dfrac{\partial \mathbf{Wx}}{\partial \mathbf{x}} &= \mathbf{W}^{\top} \\
    \dfrac{\partial \mathbf{Wx}}{\partial \mathbf{W}} &= \mathbf{x}^{\top}
\end{aligned}
$$

第一条是标量函数的情形（分母布局下结果是与 $\mathbf{x}$ 同形状的列向量）；第三条严格的说法是：向量对矩阵的导数是一个三维张量，深度学习文献中常把每个输出分量 $y_i$ 对 $\mathbf{W}$ 的导数（一个 $\mathbf{x}^{\top}$）堆叠起来，简记为 $\mathbf{x}^{\top}$。等它进入链式法则、对具体的标量损失求导时，会具体化为后文的外积形式。
:::

### 二次齐次式（二次型）

$$
\begin{aligned}
    y &= \mathbf{x}^{\top} \mathbf{W} \mathbf{x} \quad (\mathbf{x} \in \mathbb{R}^n, y \in \mathbb{R}) \\
    &= \begin{bmatrix}
        x_1 & x_2 & \cdots & x_n
    \end{bmatrix} \begin{bmatrix}
        w_{11} & w_{12} & \cdots & w_{1n} \\
        w_{21} & w_{22} & \cdots & w_{2n} \\
        \vdots & \vdots & \ddots & \vdots \\
        w_{n1} & w_{n2} & \cdots & w_{nn}
    \end{bmatrix} \begin{bmatrix}
        x_1 \\
        x_2 \\
        \vdots \\
        x_n
    \end{bmatrix} \\
    &= \sum_{i=1}^n \sum_{j=1}^n w_{ij} x_i x_j \\
    \dfrac{\partial y}{\partial \mathbf{x}} &= \begin{bmatrix}
        \dfrac{\partial}{\partial x_1} \sum_{i=1}^n \sum_{j=1}^n w_{ij} x_i x_j \\
        \dfrac{\partial}{\partial x_2} \sum_{i=1}^n \sum_{j=1}^n w_{ij} x_i x_j \\
        \vdots \\
        \dfrac{\partial}{\partial x_n} \sum_{i=1}^n \sum_{j=1}^n w_{ij} x_i x_j
    \end{bmatrix} \\
    &= \begin{bmatrix}
        \dfrac{\partial}{\partial x_1} [w_{11}x_1^2 + (w_{12}x_1x_2 + \cdots + w_{1n}x_1x_n) + (w_{21}x_2x_1 + \cdots + w_{n1}x_nx_1)] \\
        \dfrac{\partial}{\partial x_2} [w_{22}x_2^2 + (w_{21}x_2x_1 + \cdots + w_{2n}x_2x_n) + (w_{12}x_1x_2 + \cdots + w_{n2}x_nx_2)] \\
        \vdots \\
        \dfrac{\partial}{\partial x_n} [w_{nn}x_n^2 + (w_{n1}x_nx_1 + \cdots + w_{n(n-1)}x_nx_{n-1}) + (w_{1n}x_1x_n + \cdots + w_{(n-1)n}x_{n-1}x_n)]
    \end{bmatrix} \\
    &= \begin{bmatrix}
        2w_{11}x_1 + (w_{12}x_2 + \cdots + w_{1n}x_n) + (w_{21}x_2 + \cdots + w_{n1}x_n) \\
        2w_{22}x_2 + (w_{21}x_1 + \cdots + w_{2n}x_n) + (w_{12}x_1 + \cdots + w_{n2}x_n) \\
        \vdots \\
        2w_{nn}x_n + (w_{n1}x_1 + \cdots + w_{n(n-1)}x_{n-1}) + (w_{1n}x_1 + \cdots + w_{(n-1)n}x_{n-1})
    \end{bmatrix} \\
    &= \begin{bmatrix}
        \sum_{i=1}^{n} w_{i1} x_i \\
        \sum_{i=1}^{n} w_{i2} x_i \\
        \vdots \\
        \sum_{i=1}^{n} w_{in} x_i
    \end{bmatrix} + \begin{bmatrix}
        \sum_{j=1}^{n} w_{1j} x_j \\
        \sum_{j=1}^{n} w_{2j} x_j \\
        \vdots \\
        \sum_{j=1}^{n} w_{nj} x_j
    \end{bmatrix} \\
    &= \begin{bmatrix}
        w_{11} & w_{21} & \cdots & w_{n1} \\
        w_{12} & w_{22} & \cdots & w_{n2} \\
        \vdots & \vdots & \ddots & \vdots \\
        w_{1n} & w_{2n} & \cdots & w_{nn}
    \end{bmatrix} \begin{bmatrix}
        x_1 \\
        x_2 \\
        \vdots \\
        x_n
    \end{bmatrix} + \begin{bmatrix}
        w_{11} & w_{12} & \cdots & w_{1n} \\
        w_{21} & w_{22} & \cdots & w_{2n} \\
        \vdots & \vdots & \ddots & \vdots \\
        w_{n1} & w_{n2} & \cdots & w_{nn}
    \end{bmatrix} \begin{bmatrix}
        x_1 \\
        x_2 \\
        \vdots \\
        x_n
    \end{bmatrix} \\
    &= (\mathbf{W}^{\top} + \mathbf{W}) \mathbf{x}
\end{aligned}
$$

推导虽然冗长，但每一步都只是「固定其他变量的一元求导」：$x_k$ 出现在 $x_k^2$ 中（贡献 $2 w_{kk} x_k$），也出现在所有 $x_k x_j$ 与 $x_i x_k$ 的交叉项中（各贡献一次）。注意交叉项 $w_{ij} x_i x_j$ 和 $w_{ji} x_j x_i$ 是两个不同的项，所以两类贡献不能合并，结果才会同时出现 $\mathbf{W}$ 和 $\mathbf{W}^{\top}$。

特别地，当 $\mathbf{W}$ 是对称矩阵时，结果简化为

$$
\dfrac{\partial (\mathbf{x}^{\top} \mathbf{W} \mathbf{x})}{\partial \mathbf{x}} = 2 \mathbf{W} \mathbf{x}
$$

这与一元情形 $\dfrac{\mathrm{d}(w x^2)}{\mathrm{d}x} = 2 w x$ 完全呼应，可以作为记忆的锚点。

## 常见神经网络层的导数计算

有了上面的基础工具，现在可以逐一计算深度学习中常见网络层的导数了。请特别留意一种反复出现的模式：**每个复杂的层，拆开看都是「线性变换、矩阵乘法、逐元素函数」的组合**，于是它们的导数都能用一次齐次式、二次型、矩阵乘法法则和对角 Jacobian 这几块积木拼出来；而 Softmax 这类「不逐元素」的函数，则需要单独推导。

另外提醒一句：本节中出现的「对输入求导」，如前所述都不是要优化输入本身，它们是反向传播让梯度「穿过」这一层的通道；每节里真正要被梯度下降更新的，是各层的可学习参数（权重矩阵、卷积核、$\gamma, \beta$ 等）。

### 全连接层

一层全连接层的函数表达式为

$$
\mathbf{y} = \mathbf{W} \mathbf{x} + \mathbf{b}
\quad (\mathbf{x} \in \mathbb{R}^n, \mathbf{y} \in \mathbb{R}^m)
$$

它是一个典型的一次多项式向量函数（外加一个平移），其中 $\mathbf{b}$ 与 $\mathbf{x}$ 无关，求导时直接消失，因此

$$
\dfrac{\mathrm{d}\mathbf{y}}{\mathrm{d}\mathbf{x}} = \mathbf{W}^{\top}
$$

于是这一层出现了两个方向的导数，用途截然不同：$\dfrac{\mathrm{d}\mathbf{y}}{\mathrm{d}\mathbf{x}} = \mathbf{W}^{\top}$ 不是要拿去调整输入 $\mathbf{x}$，而是链式法则中把梯度继续传给更早一层的通道；$\mathbf{W}$ 才是被梯度下降更新的可学习参数，它的导数才是参数更新的直接依据。逐分量来看，$y_i = \sum_j w_{ij} x_j + b_i$，所以

$$
\dfrac{\partial y_i}{\partial w_{ij}} = x_j
\quad \Longrightarrow \quad
\dfrac{\mathrm{d}\mathbf{y}}{\mathrm{d}\mathbf{W}} = \mathbf{x}^{\top}
$$

严格地说，$\mathbf{y}$ 对 $\mathbf{W}$ 的导数是一个三维张量（每个 $y_i$ 对应一个 $\mathbf{x}^{\top}$）；深度学习文献中习惯简记为 $\mathbf{x}^{\top}$。当链式法则的另一端是标量损失时（下一节），它会具体化为外积 $\dfrac{\partial L}{\partial \mathbf{y}} \mathbf{x}^{\top}$，形状与 $\mathbf{W}$ 相同。

### 激活函数

以 ReLU 为例，其函数表达式为

$$
\mathrm{ReLU}(x) = \max(0, x)
$$

其导函数为

$$
\begin{aligned}
    \dfrac{\mathrm{d}}{\mathrm{d}x} \mathrm{ReLU}(x)
    &= \begin{cases}
        1 & x > 0 \\
        0 & x \leqslant 0
    \end{cases}
\end{aligned}
$$

神经网络中的激活函数是逐元素作用的，即 $\mathbf{y} = \mathrm{ReLU}(\mathbf{x})$ 表示 $y_i = \mathrm{ReLU}(x_i)$。每个输出分量只依赖于同下标的输入分量，所以 Jacobian 矩阵的非对角线元素全为 0：

$$
\begin{aligned}
    \mathbf{J}(\mathbf{x})
    &= \mathrm{diag}(\mathbf{x} > \mathbf{0})
\end{aligned}
$$

它是一个对角线上的元素可能为 0 或 1，而其他元素均为 0 的矩阵。

::: info
**对角矩阵**

$$
\begin{aligned}
    \mathrm{diag}(\begin{bmatrix}
        x_1 \\
        x_2 \\
        \vdots \\
        x_n
    \end{bmatrix}) = \begin{bmatrix}
        x_1 & 0  & \cdots & 0 \\
        0 & x_2  & \cdots & 0 \\
        \vdots & \vdots  & \ddots & \vdots \\
        0 & 0 & \cdots & x_n
    \end{bmatrix}
\end{aligned}
$$
:::

事实上，**任何逐元素函数的 Jacobian 都是对角矩阵**，对角线上就是各分量的一元导数。例如常用的 Sigmoid 函数 $\sigma(x) = \dfrac{1}{1 + e^{-x}}$ 满足 $\sigma'(x) = \sigma(x)(1 - \sigma(x))$，于是 $\mathbf{y} = \sigma(\mathbf{x})$ 的 Jacobian 为 $\mathrm{diag}\big(\sigma(\mathbf{x}) \circ (\mathbf{1} - \sigma(\mathbf{x}))\big)$。这也是反向传播中出现大量「逐元素乘法」的根源。

### 矩阵乘法的导数

矩阵乘法是神经网络里的万金油：全连接层的 $\mathbf{y} = \mathbf{Wx}$、注意力中的缩放点积 $\mathbf{S} = \dfrac{\mathbf{Q}\mathbf{K}^{\top}}{\sqrt{d_k}}$，本质上都是它。设

$$
\mathbf{Y} = \mathbf{A}\mathbf{B} \quad (\mathbf{A} \in \mathbb{R}^{n \times p},\ \mathbf{B} \in \mathbb{R}^{p \times m},\ \mathbf{Y} \in \mathbb{R}^{n \times m})
$$

矩阵乘法是双变量函数，两个输入各有一条梯度通道。逐分量展开 $Y_{ij} = \sum_k A_{ik} B_{kj}$，设上游梯度 $\mathbf{G} = \dfrac{\partial L}{\partial \mathbf{Y}}$ 已知，用一元链式法则对每个分量求导：

$$
\dfrac{\partial L}{\partial A_{ik}} = \sum_j \dfrac{\partial L}{\partial Y_{ij}} B_{kj}
\;\Longrightarrow\;
\dfrac{\partial L}{\partial \mathbf{A}} = \mathbf{G}\mathbf{B}^{\top},
\qquad
\dfrac{\partial L}{\partial B_{kj}} = \sum_i \dfrac{\partial L}{\partial Y_{ij}} A_{ik}
\;\Longrightarrow\;
\dfrac{\partial L}{\partial \mathbf{B}} = \mathbf{A}^{\top}\mathbf{G}
$$

两条通道的形状分别与 $\mathbf{A}$、$\mathbf{B}$ 相同，互为镜像。事实上，一次齐次式正是这里的特例：在 $\mathbf{y} = \mathbf{Wx}$ 中把 $\mathbf{W}$ 看成常参数、$\mathbf{x}$ 看成变量，对 $\mathbf{x}$ 的通道给出 $\mathbf{W}^{\top}$，对 $\mathbf{W}$ 的通道给出外积 $\dfrac{\partial L}{\partial \mathbf{y}}\mathbf{x}^{\top}$。

注意力中的缩放点积 $\mathbf{S} = \dfrac{\mathbf{Q}\mathbf{K}^{\top}}{\sqrt{d_k}}$ 只是给矩阵乘法多乘了一个标量 $\dfrac{1}{\sqrt{d_k}}$，套用上式立得

$$
\dfrac{\partial L}{\partial \mathbf{Q}} = \dfrac{1}{\sqrt{d_k}} \dfrac{\partial L}{\partial \mathbf{S}} \mathbf{K},
\qquad
\dfrac{\partial L}{\partial \mathbf{K}} = \dfrac{1}{\sqrt{d_k}} \left(\dfrac{\partial L}{\partial \mathbf{S}}\right)^{\top} \mathbf{Q}
$$

### Softmax 的导数

ReLU、Sigmoid 这类逐元素函数的 Jacobian 是对角阵，但 softmax 不是逐元素函数——它的分母 $\sum_k e^{s_k}$ 让每一个输出都依赖所有输入，Jacobian 是一个稠密矩阵。先看向量情形：

$$
a_i = \dfrac{e^{s_i}}{\sum_k e^{s_k}}
$$

对它用一元商法则，可以算出

$$
\dfrac{\partial a_i}{\partial s_j} = a_i (\delta_{ij} - a_j)
$$

其中 $\delta_{ij}$ 是 Kronecker 记号（$i = j$ 时取 1，否则取 0）。设上游梯度 $g_i = \dfrac{\partial L}{\partial a_i}$，由链式法则把各分量的贡献加权求和：

$$
\dfrac{\partial L}{\partial s_j} = \sum_i g_i \dfrac{\partial a_i}{\partial s_j} = g_j a_j - a_j \sum_i g_i a_i = a_j \left( g_j - \sum_i g_i a_i \right)
$$

读作：先算上游梯度按 softmax 权重的加权平均，再从每个分量中把它扣掉。当 softmax 逐行作用于矩阵时（$\mathbf{A} = \mathrm{softmax}(\mathbf{S})$，$\mathbf{A}, \mathbf{S}$ 同形状），把上式按行堆起来即得矩阵形式——$\mathrm{rowsum}$ 表示把矩阵每行求和、得到一个列向量：

$$
\dfrac{\partial L}{\partial \mathbf{S}} = \mathbf{A} \circ \left( \dfrac{\partial L}{\partial \mathbf{A}} - \mathbf{1}\, \mathrm{rowsum}\left( \dfrac{\partial L}{\partial \mathbf{A}} \circ \mathbf{A} \right)^{\top} \right)
$$

### 卷积层

深度学习中的卷积（实际上是互相关）也是线性运算。以一维离散卷积为例，设输入 $\mathbf{x} \in \mathbb{R}^4$、卷积核 $\mathbf{w} = (w_1, w_2)^{\top}$、步长为 1 且不填充，则输出为

$$
\mathbf{y} = \begin{bmatrix} w_1 x_1 + w_2 x_2 \\ w_1 x_2 + w_2 x_3 \\ w_1 x_3 + w_2 x_4 \end{bmatrix}
$$

**对输入求导**：既然是线性运算，就可以套用一次齐次式的结论。写成矩阵形式 $\mathbf{y} = \mathbf{W} \mathbf{x}$，其中

$$
\mathbf{W} = \begin{bmatrix}
    w_1 & w_2 & 0 & 0 \\
    0 & w_1 & w_2 & 0 \\
    0 & 0 & w_1 & w_2
\end{bmatrix}
$$

是一个由卷积核平铺而成的带状矩阵，于是 $\dfrac{\partial \mathbf{y}}{\partial \mathbf{x}} = \mathbf{W}^{\top}$。也就是说，对输入求导等价于用卷积核（翻转后）去卷上游传回来的梯度——这正是「转置卷积」操作的经典来源。

**对卷积核求导**：关键在于权重共享——同一个 $w_k$ 出现在每一个输出分量中，求导时这些贡献要全部累加。设标量损失为 $L$，由 $y_i = \sum_k w_k x_{i + k - 1}$ 及一元链式法则：

$$
\dfrac{\partial L}{\partial w_k} = \sum_{i=1}^{3} \dfrac{\partial L}{\partial y_i} x_{i + k - 1}
\qquad \text{例如} \qquad
\dfrac{\partial L}{\partial w_1} = \dfrac{\partial L}{\partial y_1} x_1 + \dfrac{\partial L}{\partial y_2} x_2 + \dfrac{\partial L}{\partial y_3} x_3
$$

把这个和写完整就会发现：核的梯度等于输入与上游梯度做互相关。总结成一句话：

> **卷积的梯度仍然是卷积**：输入的梯度用卷积核去卷上游梯度，卷积核的梯度用输入去卷上游梯度。

二维卷积只需把求和换成横纵两个方向，结论完全类似。（数学上严格的卷积要求先把核翻转 $180^{\circ}$，深度学习框架实现的是不翻转的互相关，二者只差一次翻转，不影响上述结论。）

### 归一化层

不论是 BatchNorm 还是 LayerNorm，其函数形式都相同，都是将任何特征分布转化为均值为 0、方差为 1 的特征分布，区别只在于 $\mu, \sigma^2$ 沿哪个维度统计：

$$
\mathbf{y} = \dfrac{\mathbf{x} - \mu \mathbf{1}}{\sqrt{\sigma^2 + \varepsilon}} \circ \gamma + \beta
\quad (\mathbf{x} \in \mathbb{R}^n, \mathbf{y} \in \mathbb{R}^n)
$$

其中，$\mu = \dfrac{1}{n} \sum_i x_i$ 与 $\sigma^2 = \dfrac{1}{n} \sum_i (x_i - \mu)^2$ 分别是 $\mathbf{x}$ 各分量的均值和方差，$\varepsilon$ 是防止除零的小常数；$\gamma, \beta \in \mathbb{R}^n$ 是两个可学习的参数：$\gamma$ 对每个维度做逐元素的缩放，$\beta$ 做逐元素的平移（$\circ$ 表示逐元素相乘，等价于 $\mathrm{diag}(\gamma)\, \mathbf{z} + \beta$）。

整个函数是「中心化 → 缩放 → 仿射变换」的复合，我们分三步把它翻译成线性代数的语言，再求 Jacobian。

**第一步：中心化。** 分子是用线性代数表示为

$$
\begin{aligned}
    \mathbf{x} - \mu \mathbf{1}
    &= \begin{bmatrix}
        x_1 \\
        x_2 \\
        \vdots \\
        x_n
    \end{bmatrix} - \begin{bmatrix}
        \dfrac{1}{n} \sum_{i=1}^{n} x_i \\
        \dfrac{1}{n} \sum_{i=1}^{n} x_i \\
        \vdots \\
        \dfrac{1}{n} \sum_{i=1}^{n} x_i
    \end{bmatrix} \\
    &= \begin{bmatrix}
        1 & 0 & \cdots & 0 \\
        0 & 1 & \cdots & 0 \\
        \vdots & \vdots & \ddots & \vdots \\
        0 & 0 & \cdots & 1
    \end{bmatrix} \begin{bmatrix}
        x_1 \\
        x_2 \\
        \vdots \\
        x_n
    \end{bmatrix} - \dfrac{1}{n} \begin{bmatrix}
        1 & 1 & \cdots & 1 \\
        1 & 1 & \cdots & 1 \\
        \vdots & \vdots & \ddots & \vdots \\
        1 & 1 & \cdots & 1
    \end{bmatrix} \begin{bmatrix}
        x_1 \\
        x_2 \\
        \vdots \\
        x_n
    \end{bmatrix} \\
    &= \mathbf{I} \mathbf{x} - \dfrac{1}{n} \mathbf{1} \mathbf{1}^{\top} \mathbf{x} \\
    &= \left(\mathbf{I} - \dfrac{1}{n} \mathbf{1} \mathbf{1}^{\top} \right) \mathbf{x}
\end{aligned}
$$

记 $\mathbf{P} = \mathbf{I} - \dfrac{1}{n} \mathbf{1} \mathbf{1}^{\top}$，则 $\mathbf{x} - \mu \mathbf{1} = \mathbf{P}\mathbf{x}$。$\mathbf{P}$ 有两个极好用的性质：对称（$\mathbf{P}^{\top} = \mathbf{P}$）且幂等（$\mathbf{P}^2 = \mathbf{P}$，展开并用 $\mathbf{1}^{\top}\mathbf{1} = n$ 即可验证）。

**第二步：方差。** 分母的被开方数用线性代数表示为

$$
\begin{aligned}
    \sigma^2 + \varepsilon
    &= \dfrac{1}{n} (\mathbf{x} - \mu \mathbf{1})^{\top} (\mathbf{x} - \mu \mathbf{1}) + \varepsilon \\
    &= \dfrac{1}{n} (\mathbf{P}\mathbf{x})^{\top} (\mathbf{P}\mathbf{x}) + \varepsilon \\
    &= \dfrac{1}{n} \mathbf{x}^{\top} \mathbf{P}^{\top} \mathbf{P} \mathbf{x} + \varepsilon \\
    &= \dfrac{1}{n} \mathbf{x}^{\top} \mathbf{P} \mathbf{P} \mathbf{x} + \varepsilon \\
    &= \dfrac{1}{n} \mathbf{x}^{\top} \mathbf{P} \mathbf{x} + \varepsilon
\end{aligned}
$$

记 $s = \sigma^2 + \varepsilon = \dfrac{1}{n} \mathbf{x}^{\top} \mathbf{P} \mathbf{x} + \varepsilon$，其结果是一个标量。于是归一化部分可以写成

$$
\mathbf{z} = \dfrac{\mathbf{P}\mathbf{x}}{\sqrt{s}}
$$

**第三步：求 Jacobian。** 先逐分量考察 $\mathbf{z}$。$z_i = (x_i - \mu)\, s^{-\frac{1}{2}}$，其中 $\mu$ 与 $s$ 都通过求和依赖所有的 $x_j$：$\dfrac{\partial \mu}{\partial x_j} = \dfrac{1}{n}$，$\dfrac{\partial s}{\partial x_j} = \dfrac{2}{n} (x_j - \mu)$。把其余分量当常数，按一元函数的乘积法则与链式法则求导：

$$
\begin{aligned}
    \dfrac{\partial z_i}{\partial x_j}
    &= (\delta_{ij} - \tfrac{1}{n})\, s^{-\frac{1}{2}} + (x_i - \mu) \cdot (-\tfrac{1}{2}) s^{-\frac{3}{2}} \cdot \dfrac{2}{n} (x_j - \mu) \\
    &= \dfrac{\delta_{ij} - \frac{1}{n}}{\sqrt{s}} - \dfrac{(x_i - \mu)(x_j - \mu)}{n\, s^{\frac{3}{2}}}
\end{aligned}
$$

第一项的 $\delta_{ij} - \frac{1}{n}$ 排成矩阵恰好就是 $\mathbf{P}$；第二项的外积形式排成矩阵是 $(\mathbf{P}\mathbf{x})(\mathbf{P}\mathbf{x})^{\top}$（因为 $\mathbf{P}\mathbf{x} = \mathbf{x} - \mu \mathbf{1}$）。于是

$$
\mathbf{J}_{\mathbf{z}}(\mathbf{x}) = \dfrac{1}{\sqrt{s}} \mathbf{P} - \dfrac{1}{n\, s^{\frac{3}{2}}} (\mathbf{P}\mathbf{x})(\mathbf{P}\mathbf{x})^{\top}
$$

最后，$\mathbf{y} = \mathrm{diag}(\gamma)\, \mathbf{z} + \beta$。$\beta$ 与 $\mathbf{x}$ 无关，梯度为零；$\gamma$ 的逐元素缩放作用在输出上，所以左乘 $\mathrm{diag}(\gamma)$：

$$
\mathbf{J}(\mathbf{x}) = \mathrm{diag}(\gamma) \left[ \dfrac{1}{\sqrt{s}} \mathbf{P} - \dfrac{1}{n\, s^{\frac{3}{2}}} (\mathbf{P}\mathbf{x})(\mathbf{P}\mathbf{x})^{\top} \right]
$$

直觉上，两项各有分工：第一项是「先减均值、再除以标准差」这条主路径的线性缩放；第二项则来自「分母 $\sigma$ 本身也在随 $\mathbf{x}$ 变化」——当 $\mathbf{x}$ 沿着自己偏离均值的方向变大时，$\sigma^2$ 随之变大，会把整体的幅度压回去一些，所以表现为一个减去的修正项。

同样地，这里的 Jacobian 是梯度穿过归一化层的通道，而不是用来调整 $\mathbf{x}$ 的。本层自己的可学习参数 $\gamma, \beta$ 的梯度反而简单得多，逐分量求导即得：

$$
\dfrac{\partial L}{\partial \gamma} = \dfrac{\partial L}{\partial \mathbf{y}} \circ \mathbf{z},
\qquad
\dfrac{\partial L}{\partial \beta} = \dfrac{\partial L}{\partial \mathbf{y}}
$$

## 深度神经网络的导数计算

到这里积木已经凑齐：线性层、矩阵乘法、Softmax、逐元素函数。这一节把它们组装成完整的深度网络：先用最简单的 Feed Forward 网络走一遍端到端的反向传播，再把整个自注意力块——它由多个运算复合而成、还带有分支，本身就是一个小型深度网络——组装出来。

先约定两个贯穿本节的比喻，把反向传播路径上的节点分成两类：

- **终点站**：被梯度下降直接更新的参数（如 $\mathbf{W}$、$\mathbf{b}$）。梯度抵达它们就算完成了使命，不再继续传递——优化器会拿着这个梯度对参数做一步更新。
- **换乘站**：中间状态（如 $\mathbf{g}$、$\mathbf{h}$ 这样的激活值，或输入 $\mathbf{x}$）。梯度在这里不作停留，而是借助链式法则「换乘」下一条支路，继续向更早的层传递；虽然 $\dfrac{\partial L}{\partial \mathbf{h}}$ 这类梯度也会被算出来，但它们只是过路的通道，不会被用于更新任何东西。

后文示意图中的蓝色节点就是换乘站，橙色节点就是终点站。

计算顺序上，本节沿用「分子表达式和分母表达式」一节的结论：采用分母表达式。原因有二：其一，损失 $L$ 是标量，分母布局下 $\dfrac{\partial L}{\partial \mathbf{x}}$ 与 $\mathbf{x}$ 同形状，于是每个梯度的形状恰好与分母位置的参数或中间状态一一对应，可以按形状校验公式、按形状更新参数；其二，分母表达式的链式因子要从右往左相乘——先算 $\dfrac{\partial L}{\partial \mathbf{y}}$，再逐层向内左乘各层导数——这恰好是「从损失出发、逆着数据流回传」的计算顺序，与反向传播的实现流程天然一致。套用到两类节点上：终点站收到的是形如 $\dfrac{\partial L}{\partial \mathbf{y}} \mathbf{h}^{\top}$ 的外积，换乘站收到的是形如 $\mathbf{W}^{\top} \dfrac{\partial L}{\partial \mathbf{y}}$ 的回传梯度，两者在分母表达式下都有整齐的形状。

### 前馈网络

以一个两层前馈网络为例，输入 $\mathbf{x}$ 经过一层全连接、ReLU 激活，再经过另一层全连接输出 $\mathbf{y}$。其表达式为

$$
\mathbf{y} = \mathbf{W_{out}} \, \mathrm{ReLU}(\mathbf{W_{in}} \mathbf{x} + \mathbf{b_{in}}) + \mathbf{b_{out}}
$$

将其拆开成 $\mathbf{g}, \mathbf{h}, \mathbf{y}$ 三个函数复合，则整个网络可以写成

$$
\begin{aligned}
  \mathbf{g} &= \mathbf{W_{in}} \mathbf{x} + \mathbf{b_{in}} \\
  \mathbf{h} &= \mathrm{ReLU} (\mathbf{g}) \\
  \mathbf{y} &= \mathbf{W_{out}} \mathbf{h} + \mathbf{b_{out}}
\end{aligned}
$$

其中 $\mathbf{x} \in \mathbb{R}^n$，$\mathbf{g}, \mathbf{h} \in \mathbb{R}^d$，$\mathbf{y} \in \mathbb{R}^m$。

::: mermaid
flowchart TD
    X["$$\mathbf{x}$$（输入）"] --> G["$$\mathbf{g} = \mathbf{W}_{in}\mathbf{x} + \mathbf{b}_{in}$$"] --> H["$$\mathbf{h} = \mathrm{ReLU}(\mathbf{g})$$"] --> Y["$$\mathbf{y} = \mathbf{W}_{out}\mathbf{h} + \mathbf{b}_{out}$$"] --> L["$$L$$（损失）"]

    L -.->|"$$\dfrac{\partial L}{\partial \mathbf{y}} = \mathbf{y} - \mathbf{t}$$"| Y
    Y -.->|"$$\dfrac{\partial L}{\partial \mathbf{W}_{out}} = \dfrac{\partial L}{\partial \mathbf{y}}\mathbf{h}^{\top}$$"| WO["$$\mathbf{W}_{out}$$、$$\mathbf{b}_{out}$$（终点站）"]
    Y -.->|"$$\dfrac{\partial L}{\partial \mathbf{h}} = \mathbf{W}_{out}^{\top}\dfrac{\partial L}{\partial \mathbf{y}}$$"| H
    H -.->|"$$\dfrac{\partial L}{\partial \mathbf{g}} = \mathrm{diag}(\mathbf{g} > \mathbf{0})\dfrac{\partial L}{\partial \mathbf{h}}$$"| G
    G -.->|"$$\dfrac{\partial L}{\partial \mathbf{W}_{in}} = \dfrac{\partial L}{\partial \mathbf{g}}\mathbf{x}^{\top}$$"| WI["$$\mathbf{W}_{in}$$、$$\mathbf{b}_{in}$$（终点站）"]

    classDef terminal fill:#ffe6cc,stroke:#d79b00,color:#333;
    classDef conduit fill:#dae8fc,stroke:#6c8ebf,color:#333;
    class WO,WI terminal;
    class G,H,Y conduit;
:::

上图中，实线是前向传播的数据流，虚线是反向传播的梯度流：蓝色节点是换乘站（中间状态），橙色节点是终点站（被梯度下降更新的参数），各条虚线上的梯度公式将在下文逐步推导。

训练时真正要求导的对象是**标量损失** $L$。设标签为 $\mathbf{t}$，取均方误差 $L = \dfrac{1}{2} \lVert \mathbf{y} - \mathbf{t} \rVert^2$（逐分量展开对 $\mathbf{y}$ 求导即得），则

$$
\dfrac{\partial L}{\partial \mathbf{y}} = \mathbf{y} - \mathbf{t}
$$

反向传播从损失出发，按分母表达式逐层向前（从右往左）传递梯度：

**① 更靠近输出的参数 $\mathbf{W_{out}}, \mathbf{b_{out}}$。** 由 $\mathbf{y} = \mathbf{W_{out}}\mathbf{h} + \mathbf{b_{out}}$，仿照全连接层一节的逐分量分析：

$$
\dfrac{\partial L}{\partial (\mathbf{W_{out}})_{ij}} = \dfrac{\partial L}{\partial y_i} h_j
\quad \Longrightarrow \quad
\dfrac{\partial L}{\partial \mathbf{W_{out}}} = \dfrac{\partial L}{\partial \mathbf{y}} \mathbf{h}^{\top},
\qquad
\dfrac{\partial L}{\partial \mathbf{b_{out}}} = \dfrac{\partial L}{\partial \mathbf{y}}
$$

**② 继续向内传给 $\mathbf{h}$。** 套用一次齐次式的公式 $\dfrac{\partial (\mathbf{Wx})}{\partial \mathbf{x}} = \mathbf{W}^{\top}$：

$$
\dfrac{\partial L}{\partial \mathbf{h}} = \mathbf{W_{out}}^{\top} \dfrac{\partial L}{\partial \mathbf{y}}
$$

**③ 穿过激活函数到 $\mathbf{g}$。** ReLU 的 Jacobian 是对角阵，矩阵乘对角阵即逐元素乘：

$$
\dfrac{\partial L}{\partial \mathbf{g}} = \mathrm{diag}(\mathbf{g} > \mathbf{0})\, \dfrac{\partial L}{\partial \mathbf{h}} = \mathrm{diag}(\mathbf{g} > \mathbf{0})\, \mathbf{W_{out}}^{\top} \dfrac{\partial L}{\partial \mathbf{y}}
$$

**④ 更靠近输入的参数 $\mathbf{W_{in}}, \mathbf{b_{in}}$。** 与 ① 完全同构：

$$
\dfrac{\partial L}{\partial \mathbf{W_{in}}} = \dfrac{\partial L}{\partial \mathbf{g}} \mathbf{x}^{\top},
\qquad
\dfrac{\partial L}{\partial \mathbf{b_{in}}} = \dfrac{\partial L}{\partial \mathbf{g}}
$$

注意，沿途算出的 $\dfrac{\partial L}{\partial \mathbf{h}}$、$\dfrac{\partial L}{\partial \mathbf{g}}$ 并不是用来更新什么的——输入 $\mathbf{x}$ 和中间状态都不是被优化的对象；它们只是链式法则的中转站，负责把梯度继续送往更早的参数。真正被梯度下降使用的，是 $\dfrac{\partial L}{\partial \mathbf{W_{out}}}$、$\dfrac{\partial L}{\partial \mathbf{b_{out}}}$、$\dfrac{\partial L}{\partial \mathbf{W_{in}}}$、$\dfrac{\partial L}{\partial \mathbf{b_{in}}}$ 这四个与参数同形状的梯度。

在 DNN 训练过程中，中间状态是需要存储在显存中的。可以认为，这里的 $\mathbf{x}, \mathbf{g}, \mathbf{h}, \mathbf{y}$ 在反向传播时都是已知的——事实上，计算 $\mathrm{diag}(\mathbf{g} > \mathbf{0})$、外积里的 $\mathbf{h}$ 与 $\mathbf{x}$ 都依赖前向传播留下的中间值，这正是训练比推理更耗显存的主要原因。

参数矩阵从后向前通过梯度下降算法进行更新，即先更新 $\mathbf{W_{out}}, \mathbf{b_{out}}$，再更新 $\mathbf{W_{in}}, \mathbf{b_{in}}$。整个过程只需要一次反向扫描，就能同时得到损失对**全部**参数的梯度，额外计算量约为前向传播的两倍——这正是深度学习能够训练亿级参数网络的关键。

### 自注意力

Feed Forward 网络是一条没有分叉的链，而自注意力块（Attention Block）更接近真实的深度网络：多个运算复合而成，输入还有分支。整个块的计算流程是

$$
\mathbf{Q} = \mathbf{X}\mathbf{W}_Q, \quad
\mathbf{K} = \mathbf{X}\mathbf{W}_K, \quad
\mathbf{V} = \mathbf{X}\mathbf{W}_V
$$

$$
\mathbf{S} = \dfrac{\mathbf{Q}\mathbf{K}^{\top}}{\sqrt{d_k}}, \quad
\mathbf{A} = \mathrm{softmax}(\mathbf{S})\ (\text{逐行}), \quad
\mathbf{O} = \mathbf{A}\mathbf{V}
$$

其中 $\mathbf{X} \in \mathbb{R}^{n \times d}$ 是 $n$ 个 token 的输入矩阵（每个 $d$ 维），$\mathbf{W}_Q, \mathbf{W}_K \in \mathbb{R}^{d \times d_k}$，$\mathbf{W}_V \in \mathbb{R}^{d \times d_v}$ 是三个线性层的可学习参数。

::: mermaid
flowchart TB
    X["$$\mathbf{X}$$（输入，换乘站）"] -->|"$$\times\mathbf{W}_{Q}$$"| Q["$$\mathbf{Q}$$"]
    X -->|"$$\times\mathbf{W}_{K}$$"| K["$$\mathbf{K}$$"]
    X -->|"$$\times\mathbf{W}_{V}$$"| V["$$\mathbf{V}$$"]
    Q -->|"$$\mathbf{Q}\mathbf{K}^{\top} / \sqrt{d_k}$$"| S["$$\mathbf{S}$$"]
    K -->|"$$\mathbf{Q}\mathbf{K}^{\top} / \sqrt{d_k}$$"| S
    S -->|"$$\mathrm{softmax}$$（逐行）"| A["$$\mathbf{A}$$"]
    A -->|"$$\mathbf{A}\mathbf{V}$$"| O["$$\mathbf{O}$$"]
    V -->|"$$\mathbf{A}\mathbf{V}$$"| O
    O --> NEXT["后续层 → 损失"]

    NEXT -.->|"$$\mathbf{G} = \dfrac{\partial L}{\partial \mathbf{O}}$$"| O
    O -.->|"$$\dfrac{\partial L}{\partial \mathbf{V}} = \mathbf{A}^{\top}\mathbf{G}$$"| V
    O -.->|"$$\dfrac{\partial L}{\partial \mathbf{A}} = \mathbf{G}\mathbf{V}^{\top}$$"| A
    A -.->|"softmax 反向"| S
    S -.->|"$$\dfrac{\partial L}{\partial \mathbf{Q}} = \dfrac{\partial L}{\partial \mathbf{S}}\mathbf{K} / \sqrt{d_k}$$"| Q
    S -.->|"$$\dfrac{\partial L}{\partial \mathbf{K}} = \left(\dfrac{\partial L}{\partial \mathbf{S}}\right)^{\top}\mathbf{Q} / \sqrt{d_k}$$"| K
    Q -.->|"$$\dfrac{\partial L}{\partial \mathbf{W}_{Q}} = \mathbf{X}^{\top}\dfrac{\partial L}{\partial \mathbf{Q}}$$"| WQ["$$\mathbf{W}_{Q}$$（终点站）"]
    K -.->|"$$\dfrac{\partial L}{\partial \mathbf{W}_{K}} = \mathbf{X}^{\top}\dfrac{\partial L}{\partial \mathbf{K}}$$"| WK["$$\mathbf{W}_{K}$$（终点站）"]
    V -.->|"$$\dfrac{\partial L}{\partial \mathbf{W}_{V}} = \mathbf{X}^{\top}\dfrac{\partial L}{\partial \mathbf{V}}$$"| WV["$$\mathbf{W}_{V}$$（终点站）"]
    Q -.->|"$$\dfrac{\partial L}{\partial \mathbf{Q}}\mathbf{W}_{Q}^{\top}$$"| X
    K -.->|"$$\dfrac{\partial L}{\partial \mathbf{K}}\mathbf{W}_{K}^{\top}$$"| X
    V -.->|"$$\dfrac{\partial L}{\partial \mathbf{V}}\mathbf{W}_{V}^{\top}$$"| X

    classDef terminal fill:#ffe6cc,stroke:#d79b00,color:#333;
    classDef conduit fill:#dae8fc,stroke:#6c8ebf,color:#333;
    class WQ,WK,WV terminal;
    class X,Q,K,V,S,A,O conduit;
:::

上图中，实线是前向传播的数据流，虚线是反向传播的梯度流：$\mathbf{X}$ 在前向时分支为三路、在反向时收拢三路梯度，橙色节点 $\mathbf{W}_Q, \mathbf{W}_K, \mathbf{W}_V$ 是终点站。设后一层传回的梯度 $\mathbf{G} = \dfrac{\partial L}{\partial \mathbf{O}}$ 已知，我们从损失出发反向走一遍。

**① $\mathbf{O} = \mathbf{A}\mathbf{V}$（矩阵乘法）。** 套用矩阵乘法一节的结论：

$$
\dfrac{\partial L}{\partial \mathbf{V}} = \mathbf{A}^{\top}\mathbf{G},
\qquad
\dfrac{\partial L}{\partial \mathbf{A}} = \mathbf{G}\mathbf{V}^{\top}
$$

**② $\mathbf{A} = \mathrm{softmax}(\mathbf{S})$（逐行 softmax）。** 套用 Softmax 一节的结论：

$$
\dfrac{\partial L}{\partial \mathbf{S}} = \mathbf{A} \circ \left( \dfrac{\partial L}{\partial \mathbf{A}} - \mathbf{1}\, \mathrm{rowsum}\left( \dfrac{\partial L}{\partial \mathbf{A}} \circ \mathbf{A} \right)^{\top} \right)
$$

**③ $\mathbf{S} = \dfrac{\mathbf{Q}\mathbf{K}^{\top}}{\sqrt{d_k}}$（缩放点积）。** 仍然是矩阵乘法：

$$
\dfrac{\partial L}{\partial \mathbf{Q}} = \dfrac{1}{\sqrt{d_k}} \dfrac{\partial L}{\partial \mathbf{S}} \mathbf{K},
\qquad
\dfrac{\partial L}{\partial \mathbf{K}} = \dfrac{1}{\sqrt{d_k}} \left(\dfrac{\partial L}{\partial \mathbf{S}}\right)^{\top} \mathbf{Q}
$$

**④ 三个线性层（终点站）。** 套用全连接层的结论：

$$
\dfrac{\partial L}{\partial \mathbf{W}_Q} = \mathbf{X}^{\top} \dfrac{\partial L}{\partial \mathbf{Q}}, \quad
\dfrac{\partial L}{\partial \mathbf{W}_K} = \mathbf{X}^{\top} \dfrac{\partial L}{\partial \mathbf{K}}, \quad
\dfrac{\partial L}{\partial \mathbf{W}_V} = \mathbf{X}^{\top} \dfrac{\partial L}{\partial \mathbf{V}}
$$

**⑤ 分支汇合（换乘站）。** $\mathbf{X}$ 同时流向 $\mathbf{Q}, \mathbf{K}, \mathbf{V}$ 三条支路，所以它收到的梯度是三条之和：

$$
\dfrac{\partial L}{\partial \mathbf{X}} = \dfrac{\partial L}{\partial \mathbf{Q}} \mathbf{W}_Q^{\top} + \dfrac{\partial L}{\partial \mathbf{K}} \mathbf{W}_K^{\top} + \dfrac{\partial L}{\partial \mathbf{V}} \mathbf{W}_V^{\top}
$$

按「终点站与换乘站」的观点看：$\mathbf{W}_Q, \mathbf{W}_K, \mathbf{W}_V$ 是终点站，梯度直接用于参数更新；$\mathbf{V}, \mathbf{A}, \mathbf{Q}, \mathbf{K}$ 乃至 $\mathbf{X}$ 都是换乘站。在这个块里 $\mathbf{X}$ 是输入数据、不是参数，但只要块前面还有带参数的运算（多头拼接、残差连接、前面的 Transformer 层……），这条梯度就是继续回传的通道——与 Feed Forward 网络里的 $\dfrac{\partial L}{\partial \mathbf{h}}$、$\dfrac{\partial L}{\partial \mathbf{g}}$ 扮演完全相同的角色。遇到更复杂的结构（多头注意力、交叉注意力等），也无非是多接几条这样的支路而已。

### 小结

深度学习中的矩阵求导，主要是利用导数的链式法则，让输出（损失）对深度神经网络中的参数矩阵进行求导。在求导过程中，主要涉及两种情况：一是直接对参数矩阵求导（得到形如 $\dfrac{\partial L}{\partial \mathbf{y}} \mathbf{h}^{\top}$ 的外积），二是对输入中间状态进行求导（得到形如 $\mathbf{W}^{\top} \dfrac{\partial L}{\partial \mathbf{y}}$ 的回传梯度）。再次强调：第二种求导的目的不是优化输入或中间状态——它们是数据，只有参数会被梯度下降更新——而是让梯度得以穿过各层，最终汇聚成对每个参数的梯度。采用分母表达式进行求导，各因子的形状与参数一一对应，且可以按照神经网络「从输出到输入」的顺序进行计算，较为方便和直观。

把全文的积木总结成一张速查表：

| 运算 | 梯度（分母布局） | 关键词 |
| :--- | :--- | :--- |
| $\mathbf{y} = \mathbf{Wx}$ | $\dfrac{\partial \mathbf{y}}{\partial \mathbf{x}} = \mathbf{W}^{\top}$ | 一次齐次式 |
| $y = \mathbf{x}^{\top} \mathbf{W} \mathbf{x}$ | $(\mathbf{W}^{\top} + \mathbf{W})\, \mathbf{x}$ | 二次型 |
| $\mathbf{y} = \phi(\mathbf{x})$ 逐元素 | $\mathrm{diag}(\phi'(\mathbf{x}))$ | 对角 Jacobian |
| $\mathbf{y} = \mathbf{Wx} + \mathbf{b}$，对 $\mathbf{W}$ | $\dfrac{\partial L}{\partial \mathbf{W}} = \dfrac{\partial L}{\partial \mathbf{y}} \mathbf{x}^{\top}$ | 外积 |
| 卷积 | 梯度仍是卷积 | 权重共享、梯度累加 |
| $\mathbf{Y} = \mathbf{A}\mathbf{B}$ | $\dfrac{\partial L}{\partial \mathbf{A}} = \mathbf{G}\mathbf{B}^{\top}$，$\dfrac{\partial L}{\partial \mathbf{B}} = \mathbf{A}^{\top}\mathbf{G}$（$\mathbf{G} = \dfrac{\partial L}{\partial \mathbf{Y}}$） | 矩阵乘法 |
| $\mathbf{A} = \mathrm{softmax}(\mathbf{S})$（逐行） | $\mathbf{A} \circ \left( \mathbf{G} - \mathbf{1}\,\mathrm{rowsum}(\mathbf{G} \circ \mathbf{A})^{\top} \right)$（$\mathbf{G} = \dfrac{\partial L}{\partial \mathbf{A}}$） | 非逐元素 |

## 延伸阅读

- [The Matrix Calculus You Need For Deep Learning](https://arxiv.org/abs/1802.01528)，Terence Parr 与 Jeremy Howard 著，从 Chain Rules 的两种布局讲起，与本文互为补充。
- Ian Goodfellow、Yoshua Bengio 与 Aaron Courville 的《Deep Learning》第 6 章，介绍反向传播在深度学习框架中的工程实现。

------

> 本文根据[合集·深度学习中的数学 by 齐宪标](https://space.bilibili.com/1706874133/channel/collectiondetail?sid=1933483)系列视频整理，由 AI 辅助补全与勘误。如有疏漏，欢迎指正。
