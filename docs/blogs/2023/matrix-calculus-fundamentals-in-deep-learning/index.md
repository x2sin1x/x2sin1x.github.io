---
title: "深度学习中的矩阵求导基础"
description: "根据视频课程整理深度学习中的矩阵求导基础，涵盖梯度与方向导数、Jacobian 矩阵等内容。"
date: 2023-12-06
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

> 本文根据[合集·深度学习中的数学by齐宪标](https://space.bilibili.com/1706874133/channel/collectiondetail?sid=1933483)系列视频整理。
> 
> 在本文中，用小写字母表示标量，用粗体小写字母表示向量，用粗体大写字母表示矩阵。

## 导数的定义

在高等数学和数学分析的课程中，我们知道一元函数 $y = f(x)$ 的导数定义为

$$
\dfrac{\mathrm{d}y}{\mathrm{d}x} = \lim_{h \to 0} \dfrac{f(x + h) - f(x)}{h}
$$

而对于多元函数，则会引入方向导数和梯度的概念。

### 梯度与方向导数

给定一个多元函数

$$
y = f(\mathbf{x}) = f(x_1, x_2, \dots, x_n) \quad (\mathbf{x} \in \mathbb{R}^n)
$$

其梯度为 $\nabla f(\mathbf{x})$ 定义为

$$
\nabla f(\mathbf{x}) = \begin{bmatrix}
    \dfrac{y}{\partial x_1} \\
    \dfrac{y}{\partial x_2} \\
    \vdots \\
    \dfrac{y}{\partial x_n}
\end{bmatrix}
$$

简单来说，梯度即为以单位正交向量为基底，$y$ 对 $\mathbf{x}$ 各分量的导数的线性组合。对于多元函数而言，其梯度是一个和 $\mathbf{x}$ 同样维度的向量。

而方向导数是指函数在某一点处，在某一给定方向上的变化率，是一个标量。它定义为

$$
D_{\mathbf{v}}f(\mathbf{x}) = \nabla f(\mathbf{x})^{\top} \cdot \mathbf{v}
$$

### Jacobian 矩阵

对于一簇多元函数（也称为**向量函数**，即定义域和值域都是向量的集合的函数）

$$
\mathbf{y} = f(\mathbf{x}) = \begin{bmatrix}
    f_1(\mathbf{x}) \\
    f_2(\mathbf{x}) \\
    \vdots \\
    f_m(\mathbf{x})
\end{bmatrix}
\quad (\mathbf{x} \in \mathbb{R}^n, \mathbf{y} \in \mathbb{R}^m)
$$

其各个函数的梯度组合成一个矩阵，称为 Jacobian 矩阵，记为 $\mathbf{J}(\mathbf{x})$。它定义为

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

是一个 $m \times n$ 的矩阵，其中 $m$ 是输出的维度，$n$ 是输入的维度。

::: warning
**注意**

Jacobian 矩阵的维度是 $m \times n$，而不是 $n \times m$。这意味着，Jacobian 矩阵不能用来直接表示向量函数的导数和梯度——Jacobian 矩阵的**转置**才能表示向量函数的导数和梯度。

实际上，向量函数的求导运算是一种从函数到函数的映射。用形式化的语言表达就是

$$
\begin{aligned}
    \nabla: \mathbb{R}^{n} \to \mathbb{R}^{m} \longrightarrow \mathbb{R}^{n} \to \mathbb{R}^{n \times m}
\end{aligned}
$$
:::

### Hessian 矩阵

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

## 导数的链式求导法则

对于复合函数

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

不过，如果自变量是一个向量或者矩阵，那么由于矩阵乘法不满足交换律，于是就存在分母表达式和分子表达式两种形式。

### 分母表达式和分子表达式

这里的分子和分母指的是原微商式中的分子和分母，即 $\mathrm{d}f(x)$ 和 $\mathrm{d}x$。顾名思义，分母/分子表达式的含义就是先求含分母/分子的那一项，即

$$
\begin{aligned}
    \dfrac{\mathrm{d}f(x)}{\mathrm{d}x} &= \dfrac{\mathrm{d}f(x)}{\mathrm{d}f_n(x)} \cdot \dfrac{\mathrm{d}f_n(x)}{\mathrm{d}f_{n-1}(x)} \cdots \dfrac{\mathrm{d}f_2(x)}{\mathrm{d}f_1(x)} \\
    &= \dfrac{\mathrm{d}f_1(x)}{\mathrm{d}x} \cdot \dfrac{\mathrm{d}f_2(x)}{\mathrm{d}f_1(x)} \cdots \dfrac{\mathrm{d}f_n(x)}{\mathrm{d}f_{n-1}(x)} \\
\end{aligned}
$$

其中，$(1)$ 式是分子表达式，$(2)$ 是分母表达式。由此可见，分子表达式是先求外层函数，然后逐层深入求导；分母表达式是先求内层函数，然后逐层向外求导。

在深度学习中，为了方便，一般采用**分母表达式**来表示导数。稍后我们就会看到这种表达方式的方便之处。

## 多项式向量函数的导数

多项式向量函数是指，每个因变量 $y_1, y_2, \cdots, y_m$ 都是关于自变量 $x_1, x_2, \cdots, x_n$ 和常数的线性函数的函数。本小节主要讨论一次多项式和二次多项式向量函数的导数计算，只需要理解齐次式的导数计算即可。

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

注意到，$f: \mathbb{R}^n \rightarrow \mathbb{R}^m$ 是一个将向量从 $n$ 维映射到 $m$ 维的向量函数。所以，这里的 $\mathbf{W} \in \mathbb{R}^{m \times n}$，恰好是其 Jacobian 矩阵的转置。

::: info
**常用线性函数求导公式**

$$
\begin{aligned}
    \dfrac{\partial \mathbf{Wx}}{\partial \mathbf{x}} &= \mathbf{W}^{\top} \\
    \dfrac{\partial \mathbf{Wx}}{\partial \mathbf{W}} &= \mathbf{x}^{\top}
\end{aligned}
$$
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

## 常见神经网络层的导数计算

### 全连接层

一层全连接层的函数表达式为

$$
\mathbf{y} = \mathbf{W} \mathbf{x} + \mathbf{b}
\quad (\mathbf{x} \in \mathbb{R}^n, \mathbf{y} \in \mathbb{R}^m)
$$

它是一个典型的一次多项式向量函数，其导数为

$$
\dfrac{\mathrm{d}\mathbf{y}}{\mathrm{d}\mathbf{x}} = \mathbf{W}^{\top}
$$

一般地，全连接层的参数矩阵 $\mathbf{W}$ 是可学习的参数，需要通过梯度下降法来更新，就不可避免地需要对其求导数。显然

$$
\begin{aligned}
    \dfrac{\mathrm{d}\mathbf{y}}{\mathrm{d}\mathbf{W}} = \mathbf{x}^{\top}
\end{aligned}
$$

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

对于一簇多元函数 $\mathbf{y} = \mathrm{ReLU} (\mathbf{x})$，其 Jacobian 矩阵为

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

### 卷积层

> 待补充。

### 自注意力层

> 待补充。

### 归一化层

不论是 BatchNorm 还是 LayerNorm，其函数形式都相同，都是将任何特征分布转化为均值为 0，方差为 1 的特征分布。

$$
\mathbf{y} = \dfrac{\mathbf{x} - \mathbf{\mu}}{\sqrt{\sigma^2 + \varepsilon}} \cdot \gamma + \mathbf{\beta}
\quad (\mathbf{x} \in \mathbb{R}^n, \mathbf{y} \in \mathbb{R}^n)
$$

其中，$\gamma, \beta \in \mathbb{R}^n$ 是可学习的参数，都是

分子是用线性代数表示为

$$
\begin{aligned}
    \mathbf{x} - \mathbf{\mu}
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
\end{aligned} \tag{1}
$$

其中，$\mathbf{I}$ 是单位矩阵，$\mathbf{1}$ 是元素全为 1 的列向量。

分母的被开方数用线性代数表示为

$$
\begin{aligned}
    \sigma^2 + \varepsilon
    &= \left\| \mathbf{x} - \mathbf{\mu} \right\|_{2}^{2} + \varepsilon \\
    &= (\mathbf{x} - \mathbf{\mu})^{\top} (\mathbf{x} - \mathbf{\mu}) + \varepsilon \\
    &= \mathbf{x}^{\top} \left(\mathbf{I} - \dfrac{1}{n} \mathbf{1} \mathbf{1}^{\top} \right)^{\top} \left(\mathbf{I} - \dfrac{1}{n} \mathbf{1} \mathbf{1}^{\top} \right) \mathbf{x} + \varepsilon \\
    &= \mathbf{x}^{\top} \left(\mathbf{I} - \dfrac{1}{n} \mathbf{1} \mathbf{1}^{\top} \right) \left(\mathbf{I} - \dfrac{1}{n} \mathbf{1} \mathbf{1}^{\top} \right) \mathbf{x} + \varepsilon \\
    &= \mathbf{x}^{\top} \left(\mathbf{I} - \dfrac{2}{n} \mathbf{1} \mathbf{1}^{\top} + \dfrac{1}{n^2} \mathbf{1} \mathbf{1}^{\top} \mathbf{1} \mathbf{1}^{\top} \right) \mathbf{x} + \varepsilon \\
    &= \mathbf{x}^{\top} \left(\mathbf{I} - \dfrac{2}{n} \mathbf{1} \mathbf{1}^{\top} + \dfrac{1}{n} \mathbf{1} \mathbf{1}^{\top} \right) \mathbf{x} + \varepsilon \\
    &= \mathbf{x}^{\top} \left(\mathbf{I} - \dfrac{1}{n} \mathbf{1} \mathbf{1}^{\top} \right) \mathbf{x} + \varepsilon
\end{aligned} \tag{2}
$$

其结果其实是一个标量。

由 $(1), (2)$ 两式的结果可知，原函数解析式可化为

$$
\begin{aligned}
    \mathbf{y}
    &= \sqrt{\mathbf{I} - \dfrac{1}{n} \mathbf{1} \mathbf{1}^{\top}} \times \dfrac{\mathbf{x}}{\sqrt{\mathbf{x}^{\top} \mathbf{x} + \varepsilon}} \cdot \gamma + \beta
\end{aligned}
$$

因此，其 Jacobian 矩阵为

$$
\begin{aligned}
    \mathbf{J}(\mathbf{x})
    &= \sqrt{\mathbf{I} - \dfrac{1}{n} \mathbf{1} \mathbf{1}^{\top}} \times \left[ \dfrac{\mathbf{I}}{\mathbf{x}^{\top} \mathbf{x} + \varepsilon} \left(
        \sqrt{\mathbf{x}^{\top} \mathbf{x} + \varepsilon} - \dfrac{\mathbf{x}}{\sqrt{\mathbf{x}^{\top} \mathbf{x} + \varepsilon}}
    \right) \right] \times \mathrm{diag}(\gamma) \\
    &= \sqrt{\mathbf{I} - \dfrac{1}{n} \mathbf{1} \mathbf{1}^{\top}} \times \dfrac{(\mathbf{x}^{\top} \mathbf{x} + \varepsilon) \mathbf{1} - \mathbf{x}}{(\mathbf{x}^{\top} \mathbf{x} + \varepsilon)^{\dfrac{3}{2}}} \times \mathrm{diag}(\gamma)
\end{aligned}
$$

## 深度神经网络的导数计算

我们以 Feed Forward 网络为例，其网络结构为

![](29284454c24b3c926515969d87e91efa.svg "Feed Forward Network")

用解析式表示就是

$$
\left\{ \begin{aligned}
    & \ \mathbf{g} = \mathbf{W_{in}} \mathbf{x} + \mathbf{b_{in}} \\
    & \ \mathbf{h} = \mathrm{ReLU} (\mathbf{g}) \\
    & \ \mathbf{y} = \mathbf{W_{out}} \mathbf{h} + \mathbf{b_{out}}
\end{aligned} \right.
$$

反向传播算法是从后向前计算导数的。我们可以很容易算出 $\mathbf{y}$ 对参数矩阵 $\mathbf{W_{out}}$ 的导数为

$$
\begin{aligned}
    \dfrac{\mathrm{d} \mathbf{y}}{\mathrm{d} \mathbf{W_{out}}}
    &= \mathbf{h}
\end{aligned}
$$

在 DNN 训练过程中，中间状态是需要存储在显存中的。可以认为，这里的 $\mathbf{x}, \mathbf{h}, \mathbf{g}, \mathbf{y}$ 都是已知的。参数矩阵从后向前通过梯度下降算法进行更新，即先更新 $\mathbf{W_{out}}, \mathbf{b_{out}}$，再更新 $\mathbf{W_{in}}, \mathbf{b_{in}}$。

现在计算 $\mathbf{y}$ 对参数矩阵 $\mathbf{W_{in}}$ 的导数。由求导链式法则的分母表达式，有

$$
\begin{aligned}
    \dfrac{\mathrm{d} \mathbf{y}}{\mathrm{d} \mathbf{W_{in}}}
    &= \dfrac{\mathrm{d} \mathbf{g}}{\mathrm{d} \mathbf{W_{in}}} \times \dfrac{\mathrm{d} \mathbf{h}}{\mathrm{d} \mathbf{g}} \times \dfrac{\mathrm{d} \mathbf{y}}{\mathrm{d} \mathbf{h}} \\
    &= \mathbf{x} \times \mathrm{diag}(\mathbf{g} > 0) \times \mathbf{W_{out}}
\end{aligned}
$$

对偏置 $\mathbf{b_{in}}, \mathbf{b_{out}}$ 的求导是类似的，本文不再赘述。

### 小结

深度学习中的矩阵求导，主要是利用导数的链式法则，让输出对深度神经网络中的参数矩阵进行求导。在求导过程中，主要涉及两种情况：一是直接对参数矩阵求导，二是对输入中间状态进行求导。采用分母表达式进行求导，可以按照神经网络的顺序进行，较为方便和直观。
