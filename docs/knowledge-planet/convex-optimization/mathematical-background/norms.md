---
inHomePost: false
title: "范数"
---

# 范数

## Euclid 范数

### 内积

$$
\begin{aligned}
\langle x, y\rangle=x^{\top} y=\sum_{i=1}^{n} x_{i} y_{i}
\end{aligned}
$$

### $\ell_2$-范数

$$
\begin{aligned}
\|x\|_2 = \left ( x^{\top}x \right ) ^{1/2} = \left ( x_1^2 + \dots + x_n^2 \right ) ^{1/2}
\end{aligned}
$$

### 夹角

$$
\begin{aligned}
\cos \left ( x,y \right ) = \dfrac{x^{\top}y}{\|x\|_2\|y\|_2} 
\end{aligned}
$$

若 $x^{\top}y=0$，称 $x$ 和 $y$ **正交**。

## Frobenius 范数

### 矩阵的标准内积

对于 $m \times n$ 的实矩阵 $X,Y \in \mathbf{R}^{m \times n}$，其标准内积为：

$$
\begin{aligned}
\langle X, Y\rangle = \operatorname{tr}\left(X^{\top} Y\right) = \sum_{i = 1}^{m} \sum_{j = 1}^{n} X_{i j} Y_{i j}
\end{aligned}
$$

特别地，若 $X,Y \in \mathbf{R}^{n \times n}$，则标准内积为：

$$
\begin{aligned}
    \langle X, Y \rangle &= \operatorname{tr}(XY) \\
    &= \sum_{i=1}^{n} \sum_{j=1}^{n} X_{ij} Y_{ij} \\
    &= \sum_{i=1}^{n} X_{ii} Y_{ii} + 2 \sum_{i < j} X_{ij} Y_{ij}
\end{aligned}
$$

### 矩阵的 Frobenius 范数

$$
\begin{aligned}
\|X\| _F = \left( \operatorname{tr} \left( X^{\top} X \right) \right) ^{1/2} = \left( \sum _{i=1} ^{m} \sum _{j=1} ^{n} X _{i j} ^{2} \right) ^{1/2}
\end{aligned}
$$

Frobenius 范数实际上就是将矩阵的系数按一定顺序排列后所生成的相应向量的 $\ell_2$-范数。

::: info
向量的 Euclid 范数和 $\ell_2$-范数是一回事，但是矩阵的 Frobenius 范数和 $\ell_2$-范数不是一回事。后文详述。
:::

## 范数

满足以下条件的函数 $f: \mathbf{R}^{n} \rightarrow \mathbf{R}$ 称为**范数**：

- $f$ 是非负的：对所有的 $x \in \mathbf{R}^{n}$，$f(x) \geqslant 0$ 成立；
- $f$ 是正定的：$f(x)=0$ 仅对 $x=0$ 成立；
- $f$ 是齐次的：对所有的 $x \in \mathbf{R}^{n}$ 和 $t \in \mathbf{R}$，$f(t x)=|t| f(x)$ 成立；
- $f$ 满足三角不等式：对所有的 $x, y \in \mathbf{R}^{n}$，$f(x+y) \leqslant f(x)+f(y)$ 成立。

范数是 $\mathbf{R}$ 上绝对值函数的推广。

### 距离

范数是对向量长度的度量，可以用两个向量 $x$ 和 $y$ 差的长度来度量它们之间的距离。

$$
\begin{aligned}
\operatorname{dist}(x, y)=\|x-y\|
\end{aligned}
$$

### 单位球

范数小于或等于 1 的所有向量的集合称为单位球。

$$
\begin{aligned}
\mathcal{B}=\left\{x \in \mathbf{R}^{n} \mid\|x\| \leqslant 1\right\}
\end{aligned}
$$

## 其他范数

### $\ell_1$-范数（绝对值之和）

$$
\begin{aligned}
\|x\| _1 = \left| x_1 \right| + \cdots + \left| x_n \right|
\end{aligned}
$$

### $\ell_{\infty}$-范数（Chebyshev 范数）

$$
\begin{aligned}
\|x\| _{\infty} = \max \{ \left| x_1 \right|, \cdots, \left| x_n \right| \}
\end{aligned}
$$

### $\ell_p$-范数

$$
\begin{aligned}
\|x\| _p = \left( \left| x_1 \right| ^p + \cdots + \left| x_n \right| ^p \right) ^{1/p}
\end{aligned}
$$

取 $p=1$ 就得到 $\ell_1$-范数，取 $p=2$ 就得到 $\ell_2$-范数。$p \rightarrow \infty$ 时的极限就是 $\ell_{\infty}$-范数。

### $P$- 二次范数

$$
\begin{aligned}
\|x\| _{P}=\left(x^{\top} P x\right)^{1 / 2}=\left\|P^{1 / 2} x\right\| _{2}
\end{aligned}
$$

二次范数的单位球是椭圆（反之, 如果一个范数的单位球是椭圆, 该范数就是二次范数）。

## 范数的等价性

对所有的 $x \in \mathbf{R}^{n}$，存在正常数 $\alpha$ 和 $\beta$，使得：

$$
\begin{aligned}
\alpha\|x\| _{\mathrm{a}} \leqslant \|x\| _{\mathrm{b}} \leqslant \beta \|x\| _{\mathrm{a}}
\end{aligned}
$$

据此可以证明，$\mathbf{R}^{n}$ 上任何范数可以在 $\sqrt{n}$ 倍的范围内被二次范数一致逼近。

$$
\begin{aligned}
\|x\| _{P} \leqslant\|x\| \leqslant \sqrt{n}\|x\| _{P}
\end{aligned}
$$

## 算子范数

假设 $\| \cdot \| _{\mathrm{a}}$ 和 $\|\cdot\| _{\mathrm{b}}$ 分别是 $\mathbf{R}^{m}$ 和 $\mathbf{R}^{n}$ 上的范数。对于 $X \in \mathbf{R}^{m \times n}$，我们定义由范数 $\|\cdot\| _{\mathrm{a}}$ 和 $\|\cdot\| _{\mathrm{b}}$ 导出的**算子范数**。

$$
\begin{aligned}
\|X\| _{\mathrm{a}, \mathrm{b}}=\sup \{\|X u\| _{\mathrm{a}} \mid \|u\| _{\mathrm{b}} \leqslant 1\}
\end{aligned}
$$

### 矩阵的 $\ell_2$-范数

当 $\|\cdot\| _{\mathrm{a}}$ 和 $\|\cdot\| _{\mathrm{b}}$ 都是 Euclid 范数时，$X$ 的算子范数是它的**最大奇异值**。

$$
\begin{aligned}
\|X\|_{2}=\sigma _{\max }(X)=\left(\lambda _{\max }\left(X^{\top} X\right)\right)^{1 / 2}
\end{aligned}
$$

### 最大行和范数和最大列和范数

由 $\mathbf{R}^{m}$ 和 $\mathbf{R}^{n}$ 上的 $\ell_{\infty}$-范数导出的范数，被称为最大行和范数：

$$
\begin{aligned}
\|X\| _{\infty}=\sup \{\|X u\| _{\infty} \mid\|u\| _{\infty} \leqslant 1\}=\max _{i=1, \cdots, m} \sum _{j=1}^{n}\left|X _{i j}\right|
\end{aligned}
$$

而由 $\mathbf{R}^{m}$ 和 $\mathbf{R}^{n}$ 上的 $\ell_{1}$-范数导出的范数，被称为最大列和范数：

$$
\begin{aligned}
\|X\| _{\infty}=\max _{j=1, \cdots, n} \sum _{i=1}^{m}\left|X _{i j}\right|
\end{aligned}
$$

## 对偶范数

$$
\begin{aligned}
\|z\|_{*}=\sup \{z^{\top} x \mid \|x\| \leqslant 1\}
\end{aligned}
$$

关于对偶范数，有如下结论恒成立：

$$
\begin{aligned}
z^{\top}x \leqslant \|x\| \|z\|
\end{aligned}
$$

Euclid 范数的对偶还是 Euclid 范数，$\ell_1$-范数和 $\ell_{\infty}$-范数互为对偶。
