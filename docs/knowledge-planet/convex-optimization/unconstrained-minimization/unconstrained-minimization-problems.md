---
title: "无约束优化问题"
date: 2026-09-29T00:00:00+08:00
weight: 810
---
# 无约束优化问题

本章讨论求解无约束优化问题的方法，问题形式为

$$
\mathrm{minimize} \quad f(x)
$$

其中 $f: \mathbf{R}^n \rightarrow \mathbf{R}$ 是凸的且二阶连续可微（这意味着 $\operatorname{dom} f$ 是开集）。我们假设问题是可解的，即存在最优点 $x^{\star}$（更准确地说，本章后面的假设将保证 $x^{\star}$ 存在且唯一），记最优值为 $p^{\star} = \inf_x f(x) = f(x^{\star})$。

由于 $f$ 可微且凸，点 $x^{\star}$ 为最优点的充要条件是

$$
\nabla f(x^{\star}) = 0
$$

因此，求解无约束优化问题等价于寻找上述最优性方程的解，这是一个包含 $n$ 个未知变量 $x_1, \cdots, x_n$ 的 $n$ 元方程组。只有极少数特殊情形可以通过解析求解最优性方程得到问题的解，一般情形必须采用迭代算法求解。所谓迭代算法，是指计算点列 $x^{(0)}, x^{(1)}, \cdots \in \operatorname{dom} f$ 且满足当 $k \rightarrow \infty$ 时 $f(x^{(k)}) \rightarrow p^{\star}$ 的算法，这样的点列称为问题的**极小化序列**&#8203;。当 $f(x^{(k)}) - p^{\star} \leqslant \epsilon$（$\epsilon > 0$ 为给定容许误差）时终止算法。

## 初始点和下水平集

本章描述的方法都要求一个合适的初始点 $x^{(0)}$。初始点必须属于 $\operatorname{dom} f$，并且下水平集

$$
S = \{x \in \operatorname{dom} f \mid f(x) \leqslant f(x^{(0)})\}
$$

必须是闭集。如果函数 $f$ 是闭的，即其所有下水平集都是闭集，那么该条件对任意 $x^{(0)} \in \operatorname{dom} f$ 都成立。$\operatorname{dom} f = \mathbf{R}^n$ 的连续函数是闭函数，所以当 $\operatorname{dom} f = \mathbf{R}^n$ 时，任意 $x^{(0)}$ 都满足初始下水平集条件。另一类重要的闭函数是定义域为开集、且当 $x$ 逼近 $\operatorname{bd}\operatorname{dom} f$ 时 $f(x)$ 趋于无穷的连续函数。

## 例子

### 二次最小化与最小二乘

一般形式的凸二次最小化问题为

$$
\mathrm{minimize} \quad (1/2)x^{\top}Px + q^{\top}x + r
$$

其中 $P \in \mathbf{S}^n_{+}$，$q \in \mathbf{R}^n$，$r \in \mathbf{R}$。该问题可以通过最优性条件 $Px^{\star} + q = 0$（一个线性方程组）求解。当 $P \succ 0$ 时存在唯一解 $x^{\star} = -P^{-1}q$；当 $P$ 不正定时，$Px^{\star} = -q$ 的任何解都是最优的，而如果 $Px^{\star} = -q$ 无解，则问题下无界。

二次最小化问题的一个重要特例是最小二乘问题

$$
\mathrm{minimize} \quad \|Ax - b\|_2^2 = x^{\top}(A^{\top}A)x - 2(A^{\top}b)^{\top}x + b^{\top}b
$$

其最优性条件 $A^{\top}Ax^{\star} = A^{\top}b$ 称为最小二乘问题的**正规方程**&#8203;（normal equations）。我们能够解析求解二次最小化问题是 Newton 方法的基础。

### 无约束几何规划

凸形式的（无约束）几何规划

$$
\mathrm{minimize} \quad f(x) = \log\left(\sum_{i=1}^m \exp(a_i^{\top}x + b_i)\right)
$$

其最优性条件为

$$
\nabla f(x^{\star}) = \frac{1}{\sum_{j=1}^m \exp(a_j^{\top}x^{\star} + b_j)} \sum_{i=1}^m \exp(a_i^{\top}x^{\star} + b_i)\, a_i = 0
$$

一般没有解析解，必须采用迭代算法。此问题的定义域为 $\mathbf{R}^n$，因此任何点都可以选作初始点。

### 线性不等式的解析中心

考虑问题

$$
\mathrm{minimize} \quad f(x) = -\sum_{i=1}^m \log(b_i - a_i^{\top}x)
$$

其中 $f$ 的定义域为开集 $\operatorname{dom} f = \{x \mid a_i^{\top}x < b_i,\ i=1,\cdots,m\}$。目标函数 $f$ 称为不等式 $a_i^{\top}x \leqslant b_i$ 的**对数障碍**&#8203;（logarithmic barrier），问题的解（如果存在）称为这些不等式的**解析中心**&#8203;（analytic center）。初始点必须满足严格不等式 $a_i^{\top}x^{(0)} < b_i$。由于 $f$ 是闭函数，任何满足严格不等式的点的下水平集都是闭集。

### 线性矩阵不等式的解析中心

一个密切相关的问题是

$$
\mathrm{minimize} \quad f(x) = \log \det F(x)^{-1}
$$

其中 $F: \mathbf{R}^n \rightarrow \mathbf{S}^p$ 是仿射的，即 $F(x) = F_0 + x_1 F_1 + \cdots + x_n F_n$，$F_i \in \mathbf{S}^p$。$f$ 的定义域为 $\operatorname{dom} f = \{x \mid F(x) \succ 0\}$。目标函数称为线性矩阵不等式 $F(x) \succeq 0$ 的对数障碍，其解称为该线性矩阵不等式的解析中心。初始点必须满足严格线性矩阵不等式 $F(x^{(0)}) \succ 0$。

## 强凸性及其推论

在本章的大部分内容中（除了自和谐一节），我们假设目标函数在 $S$ 上是**强凸**的，即存在 $m > 0$ 使得

$$
\nabla^2 f(x) \succeq mI
$$

对所有 $x \in S$ 成立。强凸性有许多重要推论。对 $x, y \in S$，有

$$
f(y) = f(x) + \nabla f(x)^{\top}(y - x) + \frac{1}{2}(y - x)^{\top}\nabla^2 f(z)(y - x)
$$

其中 $z$ 为线段 $[x, y]$ 上的某点。由强凸性假设，上式最后一项至少为 $(m/2)\|y - x\|_2^2$，因此对 $S$ 中所有 $x$ 和 $y$ 都有下述不等式：

$$
f(y) \geqslant f(x) + \nabla f(x)^{\top}(y - x) + \frac{m}{2}\|y - x\|_2^2
$$

当 $m = 0$ 时就退化为刻画凸性的基本不等式；当 $m > 0$ 时，它给出了比凸性本身更好的下界。

### 次优性条件

上述不等式可以用 $\|\nabla f(x)\|_2$ 来估计点 $x$ 的次优程度 $f(x) - p^{\star}$。其右端是 $y$ 的凸二次函数（固定 $x$），令关于 $y$ 的梯度为零可得 $\tilde{y} = x - (1/m)\nabla f(x)$ 使其最小，因此

$$
f(y) \geqslant f(x) - \frac{1}{2m}\|\nabla f(x)\|_2^2
$$

由于此式对任意 $y \in S$ 成立，我们得到

$$
p^{\star} \geqslant f(x) - \frac{1}{2m}\|\nabla f(x)\|_2^2
$$

这个不等式说明：若梯度在一点处很小，则该点几乎最优。它也可解释为推广了最优性条件的**次优性条件**&#8203;：

$$
\|\nabla f(x)\|_2 \leqslant (2m\epsilon)^{1/2} \implies f(x) - p^{\star} \leqslant \epsilon
$$

类似地还可以用 $\|\nabla f(x)\|_2$ 给出 $x$ 与最优点 $x^{\star}$ 的距离上界：

$$
\|x - x^{\star}\|_2 \leqslant \frac{2}{m}\|\nabla f(x)\|_2
$$

由此可知最优点 $x^{\star}$ 是唯一的。

### Hessian 的上界

强凸性意味着下水平集 $S$ 有界，因此 $\nabla^2 f(x)$ 的最大特征值（它是 $x$ 的连续函数）在 $S$ 上有上界，即存在常数 $M$ 使得

$$
\nabla^2 f(x) \preceq MI
$$

对所有 $x \in S$ 成立。这个上界意味着对任意 $x, y \in S$，

$$
f(y) \leqslant f(x) + \nabla f(x)^{\top}(y - x) + \frac{M}{2}\|y - x\|_2^2
$$

对上式两端关于 $y$ 取极小，得到与 $p^{\star} \geqslant f(x) - \frac{1}{2m}\|\nabla f(x)\|_2^2$ 对应的结果：

$$
p^{\star} \leqslant f(x) - \frac{1}{2M}\|\nabla f(x)\|_2^2
$$

## 下水平集的条件数

由强凸性和 Hessian 上界可知，对所有 $x \in S$ 有 $mI \preceq \nabla^2 f(x) \preceq MI$。比值 $\kappa = M/m$ 是矩阵 $\nabla^2 f(x)$ 条件数（最大特征值与最小特征值之比）的上界。

凸集 $C$ 的**条件数**定义为

$$
\operatorname{cond}(C) = \frac{W_{\max}^2}{W_{\min}^2}
$$

其中 $W_{\min}$ 和 $W_{\max}$ 分别是 $C$ 在所有单位方向 $q$ 上的最小宽度与最大宽度。条件数刻画了集合的各向异性（或离心程度）：条件数接近 1 意味着集合近似球形；条件数很大则说明集合在某些方向上远宽于其他方向。例如椭圆体 $E = \{x \mid (x - x_0)^{\top}A^{-1}(x - x_0) \leqslant 1\}$（$A \in \mathbf{S}^n_{++}$）的条件数恰好等于矩阵 $A$ 的条件数 $\kappa(A)$。

若 $f$ 满足 $mI \preceq \nabla^2 f(x) \preceq MI$（$x \in S$），则对 $p^{\star} < \alpha \leqslant f(x^{(0)})$，$\alpha$-下水平集 $C_{\alpha} = \{x \mid f(x) \leqslant \alpha\}$ 夹在两个球之间：

$$
B_{\mathrm{inner}} \subseteq C_{\alpha} \subseteq B_{\mathrm{outer}}, \quad B_{\mathrm{inner}} = \{y \mid \|y - x^{\star}\|_2 \leqslant (2(\alpha - p^{\star})/M)^{1/2}\}, \quad B_{\mathrm{outer}} = \{y \mid \|y - x^{\star}\|_2 \leqslant (2(\alpha - p^{\star})/m)^{1/2}\}
$$

两个球的半径之比的平方给出了 $C_{\alpha}$ 条件数的上界：

$$
\operatorname{cond}(C_{\alpha}) \leqslant \frac{M}{m}
$$

另外，在 $x^{\star}$ 附近对 $f$ 作 Taylor 展开可知，当 $\alpha$ 接近 $p^{\star}$ 时，$C_{\alpha}$ 近似为中心在 $x^{\star}$ 的椭圆体，因此 $\lim_{\alpha \rightarrow p^{\star}} \operatorname{cond}(C_{\alpha}) = \kappa(\nabla^2 f(x^{\star}))$。我们将会看到，下水平集的条件数（以 $M/m$ 为上界）对某些常见的无约束极小化方法的效率有很强的影响。

## 强凸性常数

需要注意的是，常数 $m$ 和 $M$ 只在极少数情况下是已知的，因此上面的次优性条件不能作为实用的终止准则，只能视为**概念上的**终止准则：它表明如果 $f$ 在 $x$ 处的梯度足够小，那么 $f(x)$ 与 $p^{\star}$ 的差也很小。如果我们以 $\|\nabla f(x^{(k)})\|_2 \leqslant \eta$（$\eta$ 选得足够小，以极大概率小于 $(m\epsilon)^{1/2}$）作为终止条件，那么就有（极大概率）$f(x^{(k)}) - p^{\star} \leqslant \epsilon$。

本章后面给出的收敛性证明包含达到 $f(x^{(k)}) - p^{\star} \leqslant \epsilon$ 所需迭代次数的界，其中许多界都含有（通常未知的）常数 $m$ 和 $M$，因此上述评价同样适用。这些结果至少在概念上是有用的：它们保证了算法收敛，即使达到给定精度所需的迭代次数的界依赖于未知常数。

一个重要的例外是自和谐（self-concordance）函数：对这类特殊的凸函数，我们可以给出 Newton 方法的完整收敛分析，且不依赖任何未知常数。
