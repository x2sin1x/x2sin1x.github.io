---
inHomePost: false
title: "导数"
---

# 导数

## 导数

设函数 $f: \mathbf{R}^{n} \rightarrow \mathbf{R}^{m}$，$x \in \operatorname{int} \operatorname{dom} f$。如果存在矩阵 $Df(x) \in \mathbf{R}^{m \times n}$，满足

$$
\begin{aligned}
\lim _{z \in \operatorname{dom} f, z \neq x, z \rightarrow x} \dfrac{\|f(z)-f(x)-D f(x)(z-x)\| _{2}}{\|z-x\| _{2}}=0
\end{aligned}
$$

则称函数 $f$ **可微**，并称 $Df(x)$ 为 $f$ 在 $x$ 处的**导数**（或 **Jacobian** 矩阵）。

我们将 $z$ 的仿射函数

$$
\begin{aligned}
f(x) + Df(x)(z-x)
\end{aligned}
$$

称为 $f$ 在 $x$ 处（或附近）的**一次逼近**。当 $z$ 接近 $x$ 时，该仿射函数非常接近 $f$。

$Df(x)$ 可以通过计算偏导数的方式求得：

$$
\begin{aligned}
D f(x) _{ij}=\dfrac{\partial f _{i}(x)}{\partial x _{j}}, \quad i=1, \cdots, m, \quad j=1, \cdots, n
\end{aligned}
$$

## 梯度

$$
\begin{aligned}
\nabla f(x)=D f(x)^{\top}
\end{aligned}
$$

**梯度**是一个列向量，它的分量是 $f$ 的偏导数。

$$
\begin{aligned}
\nabla f(x) _{i}=\dfrac{\partial f(x)}{\partial x _{i}}, \quad i=1, \cdots, n
\end{aligned}
$$

## 链式规则

设复合函数 $h(x) = g(f(x))$，则

$$
\begin{aligned}
\nabla h(x) &= g'(f(x))f(x) \\
&= \nabla g(f(x))^{\top} f(x)
\end{aligned}
$$

### 仿射函数

设仿射函数 $g(x) = f(Ax+b)$，其中 $f: \mathbf{R}^{n} \rightarrow \mathbf{R}^{m}$，$A \in \mathbf{R}^{n \times p}$，$b \in \mathbf{R}^{n}$，则 $g: \mathbf{R}^{p} \rightarrow \mathbf{R}^{m}$。当 $f$ 是实函数时（即 $m=1$），仿射函数 $g$ 的梯度公式为：

$$
\begin{aligned}
\nabla g(x) = A^{\top} \nabla f(Ax+b)
\end{aligned}
$$

::: info
**仿射**

从 $\mathbf{R}^{n}$ 到 $\mathbf{R}^{m}$ 的映射 $x \rightarrow Ax+b$ 称为**仿射变换**。当 $m=1$ 时，称上述仿射变换为**仿射函数**。若仿射函数的 $b=0$，则称之为**线性函数**。
:::

### 方向导数

设 $f: \mathbf{R}^{n} \rightarrow \mathbf{R}^{m}$，$x, v \in \mathbf{R}^{n}$。定义函数 $\tilde{f} = f(x+tv)$。（粗略地说，$\tilde{f}$ 是将 $f$ 限制在直线 $\{x+tv \mid t \in \mathbf{R}\}$ 上的函数。）则

$$
\begin{aligned}
D \tilde{f}(t)=\tilde{f}^{\prime}(t)=\nabla f(x+t v)^{\top} v
\end{aligned}
$$

并称标量 $\tilde{f}^{\prime}(0)$ 为函数 $f$ 在 $x$ 处沿方向 $v$ 的**方向导数**。

## 二阶导数

设函数 $f: \mathbf{R}^{n} \rightarrow \mathbf{R}$，$x \in \operatorname{int} \operatorname{dom} f$。那么 $f$ 在 $x$ 处的二阶导数（或 **Hessian** 矩阵）为

$$
\begin{aligned}
\nabla^{2} f(x) _{ij}=\dfrac{\partial^{2} f(x)}{\partial x _{i} \partial x _{j}}, \quad i=1, \cdots, n, \quad j=1, \cdots, n
\end{aligned}
$$

函数 $f$ 在（或接近）$x$ 处以 $z$ 为变量的**二次逼近**为

$$
\begin{aligned}
\widehat{f}(z)=f(x)+\nabla f(x)^{\top}(z-x)+\dfrac{1}{2}(z-x)^{\top} \nabla^{2} f(x)(z-x)
\end{aligned}
$$

## 二阶导数的链式规则

### 标量复合函数

设 $f: \mathbf{R}^{n} \rightarrow \mathbf{R}$，$g: \mathbf{R} \rightarrow \mathbf{R}$，$h(x)=g(f(x))$。我们有

$$
\begin{aligned}
\nabla^{2} h(x)=g^{\prime}(f(x)) \nabla^{2} f(x)+g^{\prime \prime}(f(x)) \nabla f(x) \nabla f(x)^{\top}
\end{aligned}
$$

### 复合仿射函数

设 $f: \mathbf{R}^{n} \rightarrow \mathbf{R}$，$A \in \mathbf{R}^{n \times m}$，$b \in \mathbf{R}^{n}$，定义 $g: \mathbf{R}^{m} \rightarrow \mathbf{R}$ 为 $g(x) = f(Ax+b)$。我们有

$$
\begin{aligned}
\nabla^{2} g(x)=A^{\top} \nabla^{2} f(Ax+b) A
\end{aligned}
$$
