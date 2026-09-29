---
title: "等式约束优化问题"
date: 2026-09-29T00:00:00+08:00
weight: 910
---
# 等式约束优化问题

本章描述求解带等式约束的凸优化问题的方法：

$$
\begin{aligned}
    \mathrm{minimize} \quad & f(x) \\
    \mathrm{subject\ to} \quad & Ax = b
\end{aligned}
$$

其中 $f: \mathbf{R}^n \rightarrow \mathbf{R}$ 凸且二阶连续可微，$A \in \mathbf{R}^{p \times n}$ 且 $\operatorname{rank} A = p < n$（即等式约束的个数少于变量个数，且约束相互独立）。假设最优解 $x^{\star}$ 存在，记最优值 $p^{\star} = \inf\{f(x) \mid Ax = b\} = f(x^{\star})$。

回顾一下，点 $x^{\star} \in \operatorname{dom} f$ 是上述问题的最优点，当且仅当存在 $\nu^{\star} \in \mathbf{R}^p$ 使

$$
Ax^{\star} = b, \quad \nabla f(x^{\star}) + A^{\top}\nu^{\star} = 0
$$

因此，求解等式约束优化问题等价于求解上述 **KKT 方程组**——它是关于 $n + p$ 个变量 $x^{\star}, \nu^{\star}$ 的 $n + p$ 个方程。第一组方程 $Ax^{\star} = b$ 称为**原始可行性方程**&#8203;（primal feasibility equations），是线性的；第二组方程 $\nabla f(x^{\star}) + A^{\top}\nu^{\star} = 0$ 称为**对偶可行性方程**&#8203;（dual feasibility equations），一般是非线性的。与无约束优化一样，只有少数问题可以解析求解这些最优性条件，最重要的特殊情形是 $f$ 为二次函数的情形。

任何等式约束问题都可以通过消去等式约束化为等价的无约束问题，然后用第 9 章的方法求解；另一种方法是求解对偶问题（假设对偶函数二阶可微），再由对偶解恢复原问题的解。本章的大部分内容致力于将 Newton 方法直接扩展到含等式约束的情形。在很多情形下，这些方法优于把等式约束问题化为无约束问题的方法。原因之一是问题的结构（例如稀疏性）常会在消去约束（或构造对偶）时被破坏，而直接处理等式约束的方法可以利用问题结构。另一个原因是概念上的：直接处理等式约束的方法可以看作直接求解最优性条件（KKT 方程）的方法。

## 等式约束凸二次极小化

考虑等式约束凸二次极小化问题

$$
\begin{aligned}
    \mathrm{minimize} \quad & f(x) = (1/2)x^{\top}Px + q^{\top}x + r \\
    \mathrm{subject\ to} \quad & Ax = b
\end{aligned}
$$

其中 $P \in \mathbf{S}^n_{+}$，$A \in \mathbf{R}^{p \times n}$。该问题本身很重要，同时它也是把 Newton 方法扩展到等式约束问题的基础。

此时最优性条件为 $Ax^{\star} = b$，$Px^{\star} + q + A^{\top}\nu^{\star} = 0$，即

$$
\begin{bmatrix}
    P & A^{\top} \\
    A & 0
\end{bmatrix}
\begin{bmatrix}
    x^{\star} \\
    \nu^{\star}
\end{bmatrix}
=
\begin{bmatrix}
    -q \\
    b
\end{bmatrix}
$$

这个关于 $x^{\star}, \nu^{\star}$ 的 $n + p$ 阶线性方程组称为等式约束二次优化问题的 **KKT 系统**&#8203;（KKT system），系数矩阵称为 **KKT 矩阵**&#8203;。

当 KKT 矩阵非奇异时，存在唯一的最优原始—对偶对 $(x^{\star}, \nu^{\star})$。若 KKT 矩阵奇异但 KKT 系统可解，则任何解都给出一个最优对；若 KKT 系统不可解，则二次优化问题下无界或不可行——此时存在 $v \in \mathbf{R}^n$、$w \in \mathbf{R}^p$ 满足 $Pv + A^{\top}w = 0$，$Av = 0$，$-q^{\top}v + b^{\top}w > 0$，沿方向 $x = \hat{x} + tv$ 目标函数无界下降。

### KKT 矩阵的非奇异性

在 $P \in \mathbf{S}^n_{+}$、$\operatorname{rank} A = p < n$ 的假设下，以下条件与 KKT 矩阵的非奇异性等价：

- $\mathcal{N}(P) \cap \mathcal{N}(A) = \{0\}$，即 $P$ 与 $A$ 没有非平凡的公共零空间；
- $Ax = 0$，$x \neq 0 \implies x^{\top}Px > 0$，即 $P$ 在 $A$ 的零空间上正定；
- $F^{\top}PF \succ 0$，其中 $F \in \mathbf{R}^{n \times (n-p)}$ 是值域为 $\mathcal{N}(A)$ 的矩阵。

作为重要的特殊情形，当 $P \succ 0$ 时 KKT 矩阵必然非奇异。

## 消去等式约束

求解等式约束问题的一种一般方法是消去等式约束，然后用无约束极小化方法求解。先找到参数化仿射可行集的矩阵 $F \in \mathbf{R}^{n \times (n-p)}$ 和向量 $\hat{x} \in \mathbf{R}^n$：

$$
\{x \mid Ax = b\} = \{Fz + \hat{x} \mid z \in \mathbf{R}^{n-p}\}
$$

其中 $\hat{x}$ 可取 $Ax = b$ 的任一特解，$F$ 是任一值域为 $\mathcal{N}(A)$ 的矩阵。然后构造**约简问题**&#8203;（reduced problem）或称**消去后的问题**&#8203;（eliminated problem）：

$$
\mathrm{minimize} \quad \tilde{f}(z) = f(Fz + \hat{x})
$$

这是以 $z \in \mathbf{R}^{n-p}$ 为变量的无约束问题。由其解 $z^{\star}$ 可得原问题的解 $x^{\star} = Fz^{\star} + \hat{x}$，同时可以构造最优对偶变量

$$
\nu^{\star} = -(AA^{\top})^{-1}A\nabla f(x^{\star})
$$

（验证上式满足对偶可行性条件时用到 $F^{\top}\nabla f(x^{\star}) = \nabla\tilde{f}(z^{\star}) = 0$ 和 $AF = 0$。）

### 例子：带资源约束的最优分配

考虑问题

$$
\mathrm{minimize} \quad \sum_{i=1}^n f_i(x_i) \quad \mathrm{subject\ to} \quad \sum_{i=1}^n x_i = b
$$

其中 $f_i: \mathbf{R} \rightarrow \mathbf{R}$ 凸且二阶可微。该问题可解释为：将总量为 $b$ 的单一资源（预算）最优地分配给 $n$ 个相互独立的活动。消去 $x_n$（例如）即用参数化 $x_n = b - x_1 - \cdots - x_{n-1}$，对应于 $\hat{x} = be_n$，$F = [\,I;\ -\mathbf{1}^{\top}\,]$；约简问题为

$$
\mathrm{minimize} \quad f_n(b - x_1 - \cdots - x_{n-1}) + \sum_{i=1}^{n-1} f_i(x_i)
$$

### 消去矩阵的选择

消去矩阵 $F$ 有很多可能的选择：任何值域为 $\mathcal{N}(A)$ 的 $n \times (n-p)$ 矩阵都可以。若 $F$ 是一个合适的消去矩阵而 $T$ 非奇异，则 $\tilde{F} = FT$ 同样合适；反之，任意两个合适的消去矩阵之间总相差一个非奇异变换。用 $F$ 消去约束时求解 $\mathrm{minimize}\ f(Fz + \hat{x})$，用 $\tilde{F}$ 时求解的问题与之等价，只是做了变量替换 $z = T\tilde{z}$。换言之，改变消去矩阵相当于改变约简问题中的变量。

## 通过对偶求解等式约束问题

另一种方法是先求解对偶问题，再恢复最优原始变量 $x^{\star}$。问题的对偶函数为

$$
g(\nu) = -b^{\top}\nu + \inf_x (f(x) + \nu^{\top}Ax) = -b^{\top}\nu - f^{*}(-A^{\top}\nu)
$$

其中 $f^{*}$ 是 $f$ 的共轭函数，因此对偶问题为

$$
\mathrm{maximize} \quad -b^{\top}\nu - f^{*}(-A^{\top}\nu)
$$

由于假设存在最优点，问题是严格可行的，Slater 条件成立，因此强对偶成立且对偶最优可以达到，即存在 $\nu^{\star}$ 使 $g(\nu^{\star}) = p^{\star}$。

若对偶函数 $g$ 二阶可微，则可以用第 9 章的无约束极小化方法极大化 $g$（一般地，即使 $f$ 二阶可微，$g$ 也未必二阶可微）。求得最优对偶变量 $\nu^{\star}$ 之后，再由它重构最优原始解 $x^{\star}$（这一步并非总是直接的）。

### 例子：等式约束解析中心

考虑问题

$$
\mathrm{minimize} \quad f(x) = -\sum_{i=1}^n \log x_i \quad \mathrm{subject\ to} \quad Ax = b
$$

（隐含约束 $x \succ 0$，$A \in \mathbf{R}^{p \times n}$。）利用

$$
f^{*}(y) = \sum_{i=1}^n (-1 - \log(-y_i)) = -n - \sum_{i=1}^n \log(-y_i)
$$

（$\operatorname{dom} f^{*} = -\mathbf{R}^n_{++}$），对偶问题为

$$
\mathrm{maximize} \quad g(\nu) = -b^{\top}\nu + n + \sum_{i=1}^n \log(A^{\top}\nu)_i
$$

（隐含约束 $A^{\top}\nu \succ 0$）。这里可以容易地求解对偶可行性方程，即找到极小化 $L(x, \nu)$ 的 $x$：

$$
\nabla f(x) + A^{\top}\nu = -(1/x_1, \cdots, 1/x_n) + A^{\top}\nu = 0 \implies x_i(\nu) = 1/(A^{\top}\nu)_i
$$

因此求解等式约束解析中心问题，可以先求解（无约束的）对偶问题，再由上式恢复原问题的最优解。
