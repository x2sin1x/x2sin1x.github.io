---
title: "对数凹函数和对数凸函数"
---

# 对数凹函数和对数凸函数

## 定义

如果对所有的 $x \in \operatorname{dom} f$ 有 $f(x) > 0$ 且 $\log f$ 是凹函数，则称函数 $f$ 是**对数凹函数**。如果 $\log f$ 是凸函数，则称函数 $f$ 是**对数凸函数**。

因此，函数 $f$ 是对数凸的，等价于函数 $1/f$ 是对数凹的。

对数凹凸性可以不借助对数直接表达。考虑函数 $f: \mathbf{R}^n \rightarrow \mathbf{R}$，其定义域是凸集，且对于 $\forall x \in \operatorname{dom} f$ 有 $f(x) > 0$，则函数是对数凹的，当且仅当对 $\forall x, y \in \operatorname{dom} f$，$0 \leqslant \theta \leqslant 1$，有

$$
f(\theta x+(1-\theta) y) \geqslant f(x)^{\theta} f(y)^{1-\theta}
$$

特别地，若令 $\theta = \dfrac{1}{2}$，则可以得到如下结论：对数凹函数在两点中间的函数值不小于这两点函数的几何平均值，即

$$
f(\dfrac{x + y}{2}) \geqslant \sqrt{f(x)f(y)}
$$

根据函数复合规则，我们知道如果函数 $h$ 是凸函数，则函数 $e^h$ 是凸函数，因此对数凸函数是凸函数。类似地，非负凹函数是对数凹函数。此外，由于对数函数是单调增函数，所以对数凸函数是拟凸函数，对数凹函数是拟凹函数。

### 举例

- 仿射函数 $f(x) = a^{\top}x + b$ 在 $\{ x \mid a^{\top}x + b > 0 \}$ 上是对数凹函数。

- 幂函数 $f(x) = x^a$ 在 $\mathbf{R}_{++}$ 上当 $a \leqslant 0$ 时是对数凸函数，当 $a \geqslant 0$ 时是对数凹函数。

- 指数函数 $f(x) = e^{ax}$ 既是对数凸函数也是对数凹函数。

- Gauss 概率密度函数的累积分布函数是对数凹函数。

$$
\Phi(x)=\dfrac{1}{\sqrt{2 \pi}} \int_{-\infty}^{x} e^{-u^{2} / 2} \mathrm{d} u
$$

- $\Gamma$ 函数在 $[1, +\infty)$ 上是对数凸函数。

$$
\Gamma(x)=\int_{0}^{\infty} u^{x-1} e^{-u} \mathrm{d} u
$$

- 行列式 $\det X$ 在 $\mathbf{S}^n _{++}$ 上是对数凹函数。

- 行列式与迹之比 $\det X / \operatorname{tr} X$ 在 $\mathbf{S}^n _{++}$ 上是对数凹函数。

## 相关性质

### 二次可微的对数凸/凹函数

假设函数 $f$ 是二次可微的，并且 $\operatorname{dom} f$ 是凸的，那么

$$
\nabla^{2} \log f(x)=\dfrac{1}{f(x)} \nabla^{2} f(x)-\dfrac{1}{f(x)^{2}} \nabla f(x) \nabla f(x)^{\top}
$$

因此，判断函数 $f$ 的对数凹凸性，只需要分别令二阶导数大于零（凸）和小于零（凹），即

$$
\begin{aligned}
f(x) \nabla^{2} f(x) \succeq \nabla f(x) \nabla f(x)^{\top} \\
f(x) \nabla^{2} f(x) \preceq \nabla f(x) \nabla f(x)^{\top}
\end{aligned}
$$

### 乘积、求和与积分

乘积运算能够保持函数的对数凸性，这是因为对数运算和加法运算是能够保持函数的凸性。

$$
\begin{aligned}
    h(x) &= f(x)g(x) \\
    \log h(x) &= \log f(x) + \log g(x)
\end{aligned}
$$

然而，求和运算并不能够绝对保证函数的对数凸性。对数凹函数的和一般不是对数凹函数，而对数凸函数的和仍然是对数凸函数。

因此，对数凸函数的积分也是对数凸函数。例如，非负函数 $p(x)$ 的 Laplace 变换：

$$
P(z)=\int p(x) e^{-z^{\top} x} \mathrm{d} x
$$

### 对数凹函数的积分

对数凹函数的积分仍然是对数凹函数需要满足如下条件：如果函数 $f: \mathbf{R}^n \times \mathbf{R}^m \rightarrow \mathbf{R}$ 是对数凹函数，那么

$$
g(x) = \int f(x, y) \mathrm{d} y
$$

是对数凹函数（此时是在 $\mathbf{R}^m$ 上求积分）。

这个结论具有重要意义。它可以用来证明对数凹性对卷积运算也是封闭的，即如果函数 $f$ 和 $g$ 在 $\mathbf{R}^m$ 上是对数凹函数，则它们的卷积

$$
(f * g)(x)=\int f(x-y) g(y) \mathbf{d} y
$$

仍然是对数凹函数。这是因为：1. 乘积是保对数凹凸性的；2. 对数凹函数的积分仍然是对数凹函数。

设 $C \subseteq \mathbf{R}^n$ 是凸集，$w$ 是 $\mathbf{R}^n$ 上的随机向量，设其具有对数凹性的概率密度函数 $p$，则函数

$$
\begin{aligned}
    f(x) &= \operatorname{prob} (x + w \in C) \\
    &= \int g(x + w)f(w) \mathrm{d} w
\end{aligned}
$$

是 $x$ 的对数凹函数，其中 $g$ 定义为

$$
g(u)=\left\{\begin{array}{ll}
1 & u \in C \\
0 & u \notin C
\end{array}\right.
$$
