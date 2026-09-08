---
title: "广义不等式约束"
weight: 360
---

# 广义不等式约束

我们知道，引入广义不等式后，可以对标准形式的凸优化问题做如下推广：

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(x) \\
    \mathrm{subject\ to} \quad & f_i(x) \preceq _{K_i} 0, \quad i=1,\cdots,m \\
    \quad & Ax = b
\end{aligned}
$$

一般凸优化问题的许多结论适用于具有广义不等式的问题，例如：

- 可行域、任意下水平集和最优集都是凸的。
- 任意局部最优解都是全局最优的。
- 可微函数 $f_0$ 最优性条件成立。

## 锥形式问题

具有广义不等式的最简单的凸优化问题是锥形式问题（或称为锥规划），它有线性目标函数和一个不等式约束函数，且该函数是仿射的（因此是 $K$- 凸的）：

$$
\begin{aligned}
    \mathrm{minimize} \quad & c^{\top}x \\
    \mathrm{subject\ to} \quad & Fx + g \preceq_K 0 \\
    \quad & Ax = b
\end{aligned}
$$

当 $K$ 是非负象限时，锥形式问题退化为线性规划。我们可以将锥形式问题视为线性规划的推广，其中的分量不等式被替换为广义不等式。

下面是锥形式问题的标准形式

$$
\begin{aligned}
    \mathrm{minimize} \quad & c^{\top}x \\
    \mathrm{subject\ to} \quad & x \succeq_K 0 \\
    \quad & Ax = b
\end{aligned}
$$

而下面则是不等式形式的锥形式问题

$$
\begin{aligned}
    \mathrm{minimize} \quad & c^{\top}x \\
    \mathrm{subject\ to} \quad & Fx + g \preceq_K 0
\end{aligned}
$$

## 半定规划

当 $K$ 是 $k$ 阶半正定锥时，即 $K \in \mathbf{S}^k_+$，相应的的锥形式问题被称为半定规划（Semidefinite Program, SDP），并且具有如下形式

$$
\begin{aligned}
    \mathrm{minimize} \quad & c^{\top} x \\
    \mathrm{subject\ to} \quad & x_{1} F_{1}+\cdots+x_{n} F_{n}+G \preceq 0 \\
    \quad & A x=b
\end{aligned}
$$

其中 $G, F_1, \cdots, F_n \in \mathbf{S}^k$，并且 $A \in \mathbf{R}^{p \times n}$。这里的不等式是一个矩阵线性不等式。

如果这些矩阵都是对角矩阵，则上式等价于 $n$ 个线性不等式，于是 SDP 问题简化为线性规划问题。

### 标准和不等式形式的半定规划

标准形式的 SDP 具有对变量 $X \in \mathbf{S}^n$ 的线性等式约束和（矩阵）非负约束：

$$
\begin{aligned}
    \mathrm{minimize} \quad & \operatorname{tr}(C X) \\
    \mathrm{subject\ to} \quad & \operatorname{tr}(A_{i} X)=b_{i}, \quad i=1, \cdots, p \\
    \quad & X \succeq 0,
\end{aligned}
$$

其中 $C, A_1, \cdots, A_P \in \mathbf{S}^n$。

如图不等式形式的 LP，不等式形式的 SDP 不含有等式约束但具有一个 LMI：

$$
\begin{aligned}
    \mathrm{minimize} \quad & c^{\top}x \\
    \mathrm{subject\ to} \quad & x_1 A_1 + \cdots + x_n A_n \preceq B
\end{aligned}
$$

### 多 LMI 与线性不等式

对于具有线性目标，等式、不等式约束及多个 LMI 约束的问题

$$
\begin{aligned}
    \mathrm{minimize} \quad & c^{\top}x \\
    \mathrm{subject\ to} \quad & F^{(i)}(x) = x_1 F_1^{(i)} + \cdots + x_n F_n^{(i)} + G^{(i)} \preceq 0, \quad i=1,\cdots,K \\
    \quad & Gx \preceq h,
    \quad & Ax = b
\end{aligned}
$$

仍然经常称其为 SDP。从单个 LMI 和线性不等式可以构造具有达到对角块的 LMI，从而可以很容易地将该问题转化为一个 SDP

$$
\begin{aligned}
    \mathrm{minimize} \quad & c^{\top}x \\
    \mathrm{subject\ to} \quad & \operatorname{diag}(G x-h, F^{(1)}(x), \cdots, F^{(K)}(x)) \preceq 0 \\
    \quad & Ax = b
\end{aligned}
$$

## 举例

### 二阶锥规划

SOCP 可以表示为锥形式问题

$$
\begin{aligned}
    \mathrm{minimize} \quad & c^{\top}x \\
    \mathrm{subject\ to} \quad & -(A_i x+b_i, c_i^{\top} x+d_i) \preceq_{K_i} 0, \quad i=1, \cdots, m \\
    \quad & Fx = g
\end{aligned}
$$

其中

$$
K_{i}=\left\{(y, t) \in \mathbf{R}^{n_i+1} \mid \|y\|_2 \leqslant t\right\}
$$

即 $\mathbf{R}^{n_i+1}$ 中的二阶锥。
