---
title: "Lagrange 对偶问题"
weight: 420
---

# Lagrange 对偶问题

## 定义

Lagrange 对偶函数实际上给出了优化问题最优值的下界。也就是说，对于一对给定的 $\lambda$ 和 $\nu$，就有一个确定的下界值相对应。那么，一个自然的问题是：Lagrange 对偶函数的最优下界是什么？即如下的一个优化问题

$$
\begin{aligned}
    \mathrm{maximize} \quad & g(\lambda, \nu) \\
    \mathrm{subject\ to} \quad & \lambda \succeq 0
\end{aligned}
$$

该问题被称为 Lagrange 对偶问题。称解 $(\lambda^{\star}, \nu^{\star})$ 为对偶最优解或者最优 Lagrange 乘子。

Lagrange 对偶问题是一个凸优化问题，这是因为极大化的目标函数是凹函数，且约束集合是凸集。因此，对偶问题的凸性和原问题是否是凸优化问题无关。

## 显式表达对偶约束

下面我们以标准形式线性规划的 Lagrange 对偶为例，说明如何显式表达对偶约束。

$$
\begin{aligned}
    \mathrm{minimize} \quad & c^{\top}x \\
    \mathrm{subject\ to} \quad & Ax = b \\
    \quad & x \succeq 0
\end{aligned}
$$

其 Lagrange 对偶函数为

$$
g(\lambda, \nu) = \left\{
    \begin{matrix}
        -b^{\top} \nu & A^{\top} \nu - \lambda + c = 0 \\
        -\infty & \text{其他情况}
    \end{matrix}
\right.
$$

严格来讲,标准形式线性规划的对偶问题是在满足约束 $\lambda \succeq 0$ 的条件下极大化对偶函数

$$
\begin{aligned}
    \mathrm{maximize} \quad & g(\lambda, \nu) \\
    \mathrm{subject\ to} \quad & \lambda \succeq 0
\end{aligned}
$$

当且仅当 $A^{\top} \nu - \lambda + c = 0$ 时对偶函数 $g$ 有界。我们看看可以通过将此“隐含”的等式约束“显式”化来得到一个等价的问题

$$
\begin{aligned}
    \mathrm{maximize} \quad & -b^{\top} \nu \\
    \mathrm{subject\ to} \quad & A^{\top} \nu - \lambda + c = 0 \\
    \quad & \lambda \succeq 0
\end{aligned}
$$

进一步地，这个问题可以描述为

$$
\begin{aligned}
    \mathrm{maximize} \quad & -b^{\top} \nu \\
    \mathrm{subject\ to} \quad & A^{\top} \nu + c \succeq 0 \\
\end{aligned}
$$

这是一个不等式形式的线性规划。

## 弱对偶性

Lagrange 对偶问题的最优值用 $d^{\star}$ 表示，这是通过 Lagrange 函数得到的原问题最优值 $p^{\star}$ 的最好下界。特别地，我们有下面虽然简单但是非常重要的不等式

$$
d^{\star} \leqslant p^{\star}
$$

即使原问题不是凸问题，上述表达式亦成立。这个性质称为**弱对偶性**。

定义差值 $p^{\star} - d^{\star}$ 是原问题的最优对偶间隙。

当原问题很难求解时，弱对偶不等式可以给出原问题最优值的一个下界，这是因为对偶问题总是凸问题，而且在很多情况下都可以进行有效的求解得到 $d^{\star}$。

## 强对偶性和 Slater 约束准则

如果对偶间隙为零，即

$$
p^{\star} = d^{\star}
$$

那么**强对偶性**成立。这说明从 Lagrange 对偶函数得到的最好下界是紧的。

如果原问题是凸优化问题，那么强对偶性通常（但不总是）成立。这意味着还需要满足一些额外条件，这些条件被称为约束准则。一个简单的约束准则是 Slater 条件：存在一点 $x \in \operatorname{relint} \mathcal{D}$ 使得

$$
f_i(x) < 0, \quad i=1,\cdots,m, \quad Ax = b
$$

满足上述条件的点被称为**严格可行**，这是因为不等式约束严格成立。Slater 定理说明，当 Slater 条件成立（且原问题是凸问题）时，强对偶性成立。

## 举例

### 线性方程组的最小二乘解

再次考虑问题

$$
\begin{aligned}
    \mathrm{minimize} \quad & x^{\top}x \\
    \mathrm{subject\ to} \quad & Ax = b
\end{aligned}
$$

其相应的对偶问题为

$$
\mathrm{maximize} \quad -\dfrac{1}{4} \nu^{\top} AA^{\top} \nu - b^{\top} \nu
$$

它是一个凹二次函数的无约束极大化问题。Slater 条件此时即是原问题的可行性条件。

### 线性规划的 Lagrange 对偶

对于任意线性规划问题，只要原问题可行，强对偶性都成立。

### 二次约束二次规划的 Lagrange 对偶

考虑 QCQP，根据 Slater 条件，当二次不等式约束严格成立时，则强对偶成立。
