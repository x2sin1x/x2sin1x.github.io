---
inHomePost: false
title: "重要凸集"
---

# 重要凸集

## 一些简单的凸集

- 空集 $\emptyset$、任意一点（单点集）$\{x_0\}$、全空间 $\mathbf{R}^{n}$ 都是 $\mathbf{R}^{n}$ 的仿射（自然也是凸的）子集。
- 任意直线是仿射的。如果直线通过零点，则是子空间，因此，也是凸锥。
- 一条线段是凸的，但不是仿射的（除非退化为一个点）。
- 一条射线是凸的，但不是仿射的。如果射线的基点是零点，则它是凸锥。
- 任意子空间是仿射的、凸锥（自然是凸的）。

## 超平面与半空间

超平面是具有如下形式的集合

$$
\begin{aligned}
\{x \mid a^{\top}x=b\}
\end{aligned}
$$

其中 $a \in \mathbf{R}^{n}$，$a \ne 0$ 且 $b \in \mathbf{R}$。超平面是关于 $x$ 的非平凡线性方程的解空间（因此是一个仿射集合）。几何上，$\{x \mid a^{\top}x=b\}$ 可以看作是法线方向为 $a$ 的超平面，而常数 $b$ 决定了这个平面从原点的偏移。下面给出的是超平面的点向式方程：

$$
\begin{aligned}
\{x \mid a^{\top}(x - x_0) = 0\}
\end{aligned}
$$

一个超平面将全空间 $\mathbf{R}^{n}$ 划分为两个半空间。（闭的）半空间是具有如下形式的集合：

$$
\begin{aligned}
\{x \mid a^{\top}x \leqslant b\}
\end{aligned}
$$

半空间是凸的，但不是仿射的。

## Euclid 球和椭球

$\mathbf{R}^{n}$ 中的空间 Euclid 球（或简称为球）具有如下形式：

$$
\begin{aligned}
B(x_c, r) = \{x \mid \|x - x_c\| _2 \leqslant r\}
\end{aligned}
$$

其中向量 $x_c$ 是球心，标量 $r > 0$ 是半径。Euclid 还有另一种常见的表达式为：

$$
\begin{aligned}
B(x_c, r) = \{x_c + ru \mid \|u\| _2 \leqslant 1\}
\end{aligned}
$$

和 Euclid 球类似的还有椭球，它们具有如下形式：

$$
\begin{aligned}
\mathcal{E} = \{x | (x - x_c)^{\top} P^{-1} (x - x_c) \leqslant 1\}
\end{aligned}
$$

其中 $P = P^{\top} \succ 0$，即 $P$ 是对称正定矩阵。向量 $x_c$ 为椭球的中心，矩阵 $P$ 决定了椭球从 $x_c$ 向各个方向扩展的幅度。$\mathcal{E}$ 的半轴长度为 $\sqrt{\lambda_i}$，这里的 $\lambda_i$ 为 $P$ 的特征值。

椭球另一个常用的表示形式是

$$
\begin{aligned}
\mathcal{E} = \{x_c + Au \mid \|u\| _2 \leqslant 1\}
\end{aligned}
$$

## 范数球和范数锥

范数锥是集合

$$
\begin{aligned}
C = \{(x, t) \mid \|x\| \leqslant t\} \in \mathbf{R}^{n+1}
\end{aligned}
$$

显然，它是一个凸锥。

## 多面体

多面体被定义为有限个线性等式和不等式的解集

$$
\begin{aligned}
\mathcal{P} = \{x \mid a_i^{\top}x \leqslant b_i, i=1,\cdots,m, c_j^{\top}x = d_j, j=1,\cdots,p\}
\end{aligned}
$$

因此，多面体是有限个半空间和超平面的交集。仿射集合（例如子空间、超平面、直线）、射线、线段和半空间都是多面体。显而易见，多面体是凸集。

多面体可以使用紧凑表达式来表示

$$
\begin{aligned}
\mathcal{P} = \{x \mid Ax \preceq b, Cx = d\}
\end{aligned}
$$

### 单纯形

单纯形是一类重要的多面体。设 $k+1$ 个点 $v_0, \cdots, v_k \in \mathbf{R}^{n}$ 仿射独立，即 $v_1-v_0, \cdots, v_k-v_0$ 线性独立，那么这些点决定了一个单纯形状

$$
\begin{aligned}
C = \operatorname{conv}\{v_0, \cdots, v_k\} = \{\theta_0v_0 + \cdots + \theta_kv_k \mid \theta \succeq 0, \mathbf{1}^{\top}\theta=1\}
\end{aligned}
$$

其中 $\mathbf{1}$ 表示所有分量均为 1 的向量。这个单纯形的仿射维数为 $k$，因而也称为 $\mathbf{R}^{n}$ 空间的 $k$ 维单纯形。

一维空间中的单纯形是一条线段，二维空间中的单纯形是一个三角形，三维空间中的单纯形是一个四面体

### 多面体的凸包描述

有限集合 $\{v_1, \cdots, v_k\}$ 的凸包是

$$
\begin{aligned}
\operatorname{conv}\{v_1, \cdots, v_k\} = \{\theta_1v_1 + \cdots + \theta_kv_k \mid \theta \succeq 0, \mathbf{1}^{\top} \theta = 1\}
\end{aligned}
$$

它表示 $k-1$ 维空间中由 $k$ 个顶点组成的有界多面体。

## 半正定锥

设 $\mathbf{S}^n$ 表示 $n$ 阶对称矩阵的集合，即

$$
\begin{aligned}
\mathbf{S}^n = \{X \in \mathbf{R}^{n \times n} \mid X = X^{\top}\}
\end{aligned}
$$

这是一个维数为 $n(n+1)/2$ 的向量空间。我们用 $\mathbf{S}_+^n$ 表示对称半正定矩阵的集合

$$
\begin{aligned}
\mathbf{S}_+^n = \{X \in \mathbf{S}^{n} \mid X \succeq 0\}
\end{aligned}
$$

用 $\mathbf{S}_{++}^n$ 表示对称正定矩阵的集合

$$
\begin{aligned}
\mathbf{S}_{++}^n = \{X \in \mathbf{S}^{n} \mid X \succ 0\}
\end{aligned}
$$

集合 $\mathbf{S}_+^n$ 是一个凸锥，称为半正定锥。例如 $\mathbf{S}^2$ 上的半正定锥

$$
\begin{aligned}
X=\left[\begin{array}{ll}
x & y \\
y & z
\end{array}\right] \in \mathbf{S}_{+}^{2} \Longleftrightarrow 
\left\{\begin{matrix}
x \geqslant 0 \\
z \geqslant 0 \\
x z \geqslant y^{2}
\end{matrix}\right.
\end{aligned}
$$
