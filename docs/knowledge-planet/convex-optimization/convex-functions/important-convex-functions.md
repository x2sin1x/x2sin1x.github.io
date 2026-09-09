---
title: "重要凸函数"
date: 2021-12-07T11:37:41+08:00
weight: 220
---
# 重要凸函数

## 基本初等函数

- 指数函数：对任意 $a \in \mathbf{R}$，函数 $f(x) = e^{ax}$ 在 $\mathbf{R}$ 上是凸的。
- 对数函数：函数 $f(x) = \log{x}$ 在 $\mathbf{R} _{++}$ 上是凸函数。
- 幂函数：当 $a \geqslant 1$ 或 $a \leqslant 0$ 时，$f(x) = x^a$ 在 $\mathbf{R} _{++}$ 上是凸函数；当 $0 \leqslant a \leqslant 1$，函数 $x^a$ 在 $\mathbf{R} _{++}$ 上是凹函数。

## 复合函数

### 负熵

函数 $f(x) = x \log{x}$ 在其定义域上是凸函数。其定义域为 $\mathbf{R} _{++}$，但也可以定义在 $\mathbf{R} _+$ 上（$f(0) = 0$），这是因为

$$
\begin{aligned}
    \lim _{x \rightarrow 0^{+}} x \log{x} &= \lim _{x \rightarrow 0^{+}} \dfrac{\log{x}}{1/x}  \\
    &= \lim _{x \rightarrow 0^{+}} \dfrac{1/x}{-1/x^2} \\
    &= 0
\end{aligned}
$$

函数 $f$ 的导数和二阶导数为

$$
f^{\prime}(x) = \log{x} + 1, \quad f^{\prime \prime}(x) = \dfrac{1}{x} > 0
$$

### 范数

$\mathbf{R}^n$ 上的任意范数均为凸函数。

### 二次-线性分式函数

二元函数 $f(x,y) = \dfrac{x^2}{y}$ 是凸函数，其定义域为

$$
\operatorname{dom} f = \mathbf{R} \times \mathbf{R} _{++} = \{ (x, y) \in \mathbf{R} ^2 \mid y > 0 \}
$$

![](083668ee8e05363e5194f9c2671d419b.png)

### 指数和的对数

函数 $f(x) = \log{(e^{x_1} + \cdots + e^{x_n})}$ 在 $\mathbf{R}^n$ 上是凸函数。

下面是函数 $f(x) = \log{(e^x + e^y)}$ 的图像。

![](96083f11deb407c668e7f5a77af7fd66.png)

### 几何平均数

几何平均数函数 $f(x)=\left(\prod_{i=1}^{n} x_{i}\right)^{1 / n}$ 在定义域 $\operatorname{dom} f=\mathbf{R}_{++}^{n}$ 上是凹函数。

## 分段函数

### 绝对值幂函数

当 $p \geqslant 1$ 时，函数 $|x|^p$ 在 $\mathbf{R}$ 上是凸函数。

### 最大值

最大值函数是凸函数是很显然的。

## 证明

判断上述函数的凸性可以通过多种途径。可以直接验证一阶条件是否成立，亦可以验证其 Hessian 矩阵是否半正定，或者可以将函数转换到与其定义域相交的任意直线上，通过得到的单变量函数判断原函数的凸性。
