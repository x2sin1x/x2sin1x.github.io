---
title: "线性代数"
weight: 60
---

# 线性代数

## 值域和零空间

设矩阵 $A \in \mathbf{R}^{m \times n}$，$A$ 的**值域**是指 $\mathbf{R}^{m}$ 中能够写成 $A$ 的列向量的线性组合的所有向量的集合，即

$$
\begin{aligned}
\mathcal{R} (A) = \{Ax \mid x \in \mathbf{R}^{n} \}
\end{aligned}
$$

值域 $\mathcal{R} (A)$ 是 $\mathbf{R}^{m}$ 的子空间，它的维数是 $A$ 的**秩**，记作 $\operatorname{rank} A$。$A$ 的秩一定不会大于 $m$ 和 $n$ 的较小值。当 $\operatorname{rank} A = \min \{m, n\}$ 时，称 $A$ 为**满秩**矩阵。

$A$ 的**零空间**（或**核**）是指被 $A$ 映射成零的所有向量 $x$ 的集合，即

$$
\begin{aligned}
\mathcal{N}(A) = \{x \mid Ax=0\}
\end{aligned}
$$

### 正交补

$$
\begin{aligned}
\mathcal{V}^{\bot} = \{x \mid \forall z \in \mathcal{V}, z^{\top}x=0\}
\end{aligned}
$$

有如下结论恒成立：

$$
\begin{aligned}
\mathcal{V}^{\bot\bot} = \mathcal{V}
\end{aligned}
$$

### $A$ 导出的正交分解

$$
\begin{aligned}
\mathcal{N}(A) = \mathcal{R}(A^{\top})^{\bot}
\end{aligned}
$$

## 对称特征值分解

设 $A$ 为 $n$ 阶实对称矩阵，则 $A$ 可以因式分解为

$$
\begin{aligned}
A = Q \Lambda Q^{\top}
\end{aligned}
$$

其中 $Q \in \mathbf{R}^{n \times n}$ 是正交矩阵，满足 $Q^{\top}Q = I$，而 $\Lambda = \operatorname{diag}(\lambda_1, \cdots, \lambda_n)$。实数 $\lambda_i$ 是 $A$ 的**特征值**，是**特征多项式** $\det(sI-A)$ 的根，$Q$ 的列向量构成 $A$ 的一组正交**特征向量**。

通常我们将特征值按从大到小排序，用 $\lambda_{i}(A)$ 表示第 $i$ 大特征值。最大特征值记作 $\lambda_{1}(A) = \lambda_{max}(A)$，最小特征值记作 $\lambda_{n}(A) = \lambda_{min}(A)$。

特征值具有如下性质：

$$
\begin{aligned}
\det A &= \prod_{i=1}^{n} \lambda_i \\
\operatorname{tr} A &= \sum_{i=1}^{n} \lambda_i
\end{aligned}
$$

### 矩阵不等式

$$
\begin{aligned}
\lambda_{\max}(A)=\sup_{x \neq 0} \dfrac{x^{\top} A x}{x^{\top} x}, \quad \lambda_{\min}(A)=\inf _{x \neq 0} \dfrac{x^{\top} A x}{x^{\top} x}
\end{aligned}
$$

特别地，对 $\forall x$，我们有

$$
\begin{aligned}
\lambda_{\min}(A)x^{\top}x \leqslant x^{\top}x \leqslant \lambda_{\max}(A)x^{\top}x
\end{aligned}
$$

### 正定矩阵

若矩阵 $A$ 对 $\forall x \ne 0$，有 $x^{\top}Ax > 0$ 成立，则称矩阵 $A$ **正定**，记作 $A \succ 0$。显然，$A \succ 0$ 的充要条件是 $\lambda_{\min}(A) > 0$。

同理，半正定（非负定）、负定、半负定（非正定）矩阵的定义类似。本文从略。

### 对称平方根

$$
\begin{aligned}
A^{1 / 2}=Q \operatorname{diag}\left(\lambda_{1}^{1 / 2}, \cdots, \lambda_{n}^{1 / 2}\right) Q^{\top}
\end{aligned}
$$

平方根 $A^{1/2}$ 是矩阵方程 $X^2 = A$ 的唯一的对称半正定的解。

## 广义特征值分解

两个对称矩阵 $\left(A, B\right) \in \mathbf{S}^{n} \times \mathbf{S}^{n}$ 的广义特征值定义为多项式 $\det (sB - A)$ 的根。

## 奇异值分解

设 $A \in \mathbf{R}^{m \times n}$，$\operatorname{rank} A = r$，那么 $A$ 可以因式分解为

$$
\begin{aligned}
A = U \Sigma V^{\top}
\end{aligned}
$$

其中 $U \in \mathbf{R}^{m \times r}$ 满足 $U^{\top}U = I$，$V \in \mathbf{R}^{n \times r}$ 满足 $V^{\top}V = I$，而 $\Sigma = \operatorname{diag}(\sigma_1, \cdots, \sigma_r)$ 满足

$$
\begin{aligned}
\sigma_1 \geqslant \sigma_2 \geqslant \cdots \geqslant \sigma_r > 0
\end{aligned}
$$

称为 $A$ 的**奇异值分解**（SVD）。$U$ 的列向量称为 $A$ 的**左奇异向量**，$V$ 的列向量称为 $A$ 的**右奇异向量**，而 $\sigma_i$ 称为**奇异值**。奇异值分解可以写成

$$
\begin{aligned}
A=\sum_{i=1}^{r} \sigma_{i} u_{i} v_{i}^{\top}
\end{aligned}
$$

### 伪逆

设 $A = U \Sigma V^{\top}$ 为 $A \in \mathbf{m \times n}$ 的奇异值分解，$\operatorname{rank} A = r$，则 $A$ 的**伪逆**为

$$
\begin{aligned}
A^{\dagger}=V \Sigma^{-1} U^{\top} \in \mathbf{R}^{n \times m}
\end{aligned}
$$

伪逆可以用于求解最小二乘、最小范数、二次规划以及（Euclid）投影这些问题。

## Schur 补

考虑进行以下划分的矩阵 $X \in \mathbf{S}^{n}$

$$
\begin{aligned}
X = \left [ \begin{matrix}
 A & B \\
 B^{\top} & C
\end{matrix} \right ] 
\end{aligned}
$$

其中 $A \in \mathbf{S}^k$。如果 $\det A \ne 0$，矩阵

$$
\begin{aligned}
S = C - B^{\top}A^{-1}B
\end{aligned}
$$

被称为 $A$ 在 $X$ 中的 **Schur 补**。Schur 补出现于很多重要的公式和定理中，例如

$$
\begin{aligned}
\det X = \det A \det S
\end{aligned}
$$

### 分块矩阵求逆

考虑如下分块矩阵方程：

$$
\begin{aligned}
\left[\begin{array}{cc}
A & B \\
B^{\top} & C
\end{array}\right]\left[\begin{array}{l}
x \\
y
\end{array}\right]=\left[\begin{array}{l}
u \\
v
\end{array}\right]
\end{aligned}
$$

假设 $\det A \ne 0$。将方程中的 $x$ 消去，解得

$$
\begin{aligned}
y = S^{-1}\left(v - B^{\top}A^{-1}u\right)
\end{aligned}
$$

将 $y$ 代入原方程，解得

$$
\begin{aligned}
x=\left(A^{-1}+A^{-1} B S^{-1} B^{\top} A^{-1}\right) u-A^{-1} B S^{-1} v
\end{aligned}
$$

于是我们可以得到分块矩阵的求逆公式：

$$
\begin{aligned}
\left[\begin{array}{cc}
A & B \\
B^{\top} & C
\end{array}\right]^{-1}=\left[\begin{array}{cc}
A^{-1}+A^{-1} B S^{-1} B^{\top} A^{-1} & -A^{-1} B S^{-1} \\
-S^{-1} B^{\top} A^{-1} & S^{-1}
\end{array}\right]
\end{aligned}
$$
