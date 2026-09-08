---
title: "择一定理"
weight: 480
---

# 择一定理

## 通过对偶函数建立弱择一性

对约束系统的定义如下

$$
\begin{aligned}
    f_i(x) & \leqslant 0, \quad i=1,\cdots,m \\
    h_i(x) & = 0, \quad i=1,\cdots,p
\end{aligned}
$$

考虑不等式和等式约束的系统的可行性，即求解如下优化问题

$$
\begin{aligned}
    \mathrm{minimize} \quad & 0 \\
    \mathrm{subject\ to} \quad & f_i(x) \leqslant 0, \quad i=1,\cdots,m \\
    \quad & h_i(x) = 0, \quad i=1,\cdots,p
\end{aligned}
$$

此问题的最优值显然只有两种情况：

- $p^{\star} = 0$：约束是可行的。
- $p^{\star} = \infty$：约束是不可行的。

### 对偶函数

$$
g(\lambda, \nu)=\inf_{x \in \mathcal{D}}\left(\sum_{i=1}^{m} \lambda_{i} f_{i}(x)+\sum_{i=1}^{p} \nu_{i} h_{i}(x)\right)
$$

同理，对偶问题的最优值同样也只有两种情况：

- $d^{\star} = \infty$：$\lambda \succeq 0, g(\lambda, \nu) > 0$ 可行。
- $d^{\star} = 0$：$\lambda \succeq 0, g(\lambda, \nu) > 0$ 不可行。

也就是说，原问题和对偶问题关于约束是否可行的情况正好相反。事实上，可以将不等式

$$
\begin{aligned}
    \lambda & \succeq 0 \\
    g(\lambda, \nu) & > 0
\end{aligned}
$$

看作是系统不可行的证明或认证。

如果两个不等式（等式）系统至多有一个可行，则称之为**弱择一**的。无论不等式是否是凸的，上述结论都成立；此外，择一不等式系统总是凸的。

### 严格不等式

同样可以分析具有严格不等式系统的可行性，我们得到择一不等式系统如下

$$
\begin{aligned}
    \lambda & \succeq 0 \\
    \lambda & \ne 0 \\
    g(\lambda, \nu) & \geqslant 0
\end{aligned}
$$

## 强择一

当原不等式系统是凸的，即函数 $f_i$ 是凸函数，$h_i$ 是仿射函数，且某些类型的约束准则成立是，那么上述描述的弱择一的两个系统是**强择一**的，即恰有一个系统可行。换而言之，两个不等式系统中的任意一个可行，当且仅当另一个不可行。

不等式系统可以描述为

$$
\begin{aligned}
    f_i(x) & \leqslant 0, \quad i=1,\cdots,m \\
    Ax &= b
\end{aligned}
$$

### 严格不等式

严格不等式系统的强择一还需要满足：存在一点 $x \in \operatorname{relint} \mathcal{D}$ 使得 $Ax=b$。

我们可以通过考虑相关的优化问题得到上述结论，即

$$
\begin{aligned}
    \mathrm{minimize} \quad & s \\
    \mathrm{subject\ to} \quad & f_i(x) - s \leqslant 0, \quad i=1,\cdots,m \\
    \quad & Ax = b
\end{aligned}
$$

优化变量为 $x, s$，定义域为 $\mathcal{D} \times \mathbf{R}$。当且仅当严格不等式系统有解时，上述优化问题的最优值 $p^{\star} < 0$。

其对偶函数为

$$
\inf_{x \in \mathcal{D}, s}\left(s+\sum_{i=1}^{m} \lambda_{i}\left(f_{i}(x)-s\right)+\nu^{\top}(A x-b)\right)=\left\{\begin{array}{ll}
g(\lambda, \nu) & \mathbf{1}^{\top} \lambda=1 \\
-\infty & \text {otherwise}
\end{array}\right.
$$

因此其对偶问题可以描述为

$$
\begin{aligned}
    \mathrm{maximize} \quad & g(\lambda, \nu) \\
    \mathrm{subject\ to} \quad & \lambda \succeq 0, \quad \mathbf{1}^{\top} \lambda = 1
\end{aligned}
$$

该问题满足 Slater 条件，即 $d^{\star} = p^{\star}$。

### 非严格不等式

下面考虑非严格不等式系统

$$
\begin{aligned}
    f_i(x) & \leqslant 0, \quad i=1,\cdots,m \\ 
    Ax &= b
\end{aligned}
$$

以及其择一系统

$$
\begin{aligned}
    \lambda & \succeq 0 \\
    g(\lambda, \nu) & > 0
\end{aligned}
$$

强择一成立的条件和严格不等式系统类似。

## 举例

### 线性不等式

考虑具有线性不等式 $Ax \preceq b$ 的系统。它的对偶函数为

$$
g(\lambda)=\inf _{x} \lambda^{\top}(A x-b)=\left\{\begin{array}{ll}
-b^{\top} \lambda & A^{\top} \lambda=0 \\
-\infty & \text {otherwise}
\end{array}\right.
$$

因此，其择一不等式系统为

$$
\begin{aligned}
    \lambda & \succeq 0 \\
    A^{\top} \lambda & = 0 \\
    b^{\top} \lambda & < 0
\end{aligned}
$$

这两个系统是强择一的。

### Farkas 引理

Farkas 引理描述了一对强择一系统，它们是由严格和非严格线性不等式组成的混合系统。不等式系统

$$
\begin{aligned}
    Ax & \preceq 0 \\
    c^{\top}x & < 0
\end{aligned}
$$

其中 $A \in \mathbf{R}^{m \times n}, c \in \mathbf{R}^n$，以及不等式系统

$$
\begin{aligned}
    A^{\top}y + c &= 0 \\
    y & \succeq 0
\end{aligned}
$$

是强择一的。
