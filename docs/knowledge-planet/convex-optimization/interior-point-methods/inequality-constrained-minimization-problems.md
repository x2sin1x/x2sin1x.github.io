---
title: "不等式约束极小化问题"
date: 2026-09-29T00:00:00+08:00
weight: 1010
---
# 不等式约束极小化问题

本章讨论用**内点方法**&#8203;（interior-point methods）求解带不等式约束的凸优化问题：

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(x) \\
    \mathrm{subject\ to} \quad & f_i(x) \leqslant 0, \quad i = 1, \cdots, m \\
    & Ax = b
\end{aligned}
$$

其中 $f_0, \cdots, f_m: \mathbf{R}^n \rightarrow \mathbf{R}$ 凸且二阶连续可微，$A \in \mathbf{R}^{p \times n}$ 且 $\operatorname{rank} A = p < n$。假设问题可解，即最优解 $x^{\star}$ 存在，最优值 $p^{\star} = f_0(x^{\star})$。

我们还假设问题是严格可行的，即存在 $x \in \mathcal{D}$（各函数定义域的交集）满足 $Ax = b$ 且 $f_i(x) < 0$（$i = 1, \cdots, m$）。这意味着 Slater 约束条件成立，因此存在对偶最优 $\lambda^{\star} \in \mathbf{R}^m$，$\nu^{\star} \in \mathbf{R}^p$，它们与 $x^{\star}$ 一起满足 KKT 条件：

$$
\begin{aligned}
    & Ax^{\star} = b, \quad f_i(x^{\star}) \leqslant 0, \quad i = 1, \cdots, m \\
    & \lambda^{\star} \succeq 0 \\
    & \nabla f_0(x^{\star}) + \sum_{i=1}^m \lambda_i^{\star}\nabla f_i(x^{\star}) + A^{\top}\nu^{\star} = 0 \\
    & \lambda_i^{\star} f_i(x^{\star}) = 0, \quad i = 1, \cdots, m
\end{aligned}
$$

内点方法通过把 Newton 方法应用于一系列等式约束问题，或应用于 KKT 条件的一系列修正形式，来求解上述问题（或其 KKT 条件）。我们重点讨论一个特殊的内点算法——**障碍方法**&#8203;（barrier method），并给出它的收敛性证明与复杂度分析；同时也描述一个简单的**原始—对偶内点方法**&#8203;（primal-dual interior-point method），但不做分析。

可以把内点方法看作凸优化算法层级中的又一级：带线性等式约束的二次问题是最低层——它的 KKT 条件是一组线性方程，可以解析求解；Newton 方法是下一层——它可以看作把带线性等式约束的二阶可微目标问题化为一系列带线性等式约束的二次问题求解的技术；内点方法构成再下一层——它们把带线性等式和不等式约束的优化问题化为一系列带线性等式约束的问题求解。

## 例子

很多问题本身已经具备上述形式，且目标和约束函数二阶可微。显然的例子有 LP、QP、QCQP 以及凸形式的 GP；另一个例子是线性不等式约束的熵最大化问题：

$$
\mathrm{minimize} \quad \sum_{i=1}^n x_i\log x_i \quad \mathrm{subject\ to} \quad Fx \preceq g, \quad Ax = b
$$

定义域 $\mathcal{D} = \mathbf{R}^n_{++}$。

许多其他问题不具有上述所需形式（目标与约束函数二阶可微），但可以改写成该形式。我们已经见过很多这样的例子，例如把（目标函数不可微的）无约束凸分段线性极小化问题

$$
\mathrm{minimize} \quad \max_{i=1,\cdots,m} (a_i^{\top}x + b_i)
$$

改写为 LP

$$
\mathrm{minimize} \quad t \quad \mathrm{subject\ to} \quad a_i^{\top}x + b_i \leqslant t,\ i = 1, \cdots, m
$$

（后者的目标与约束函数二阶可微）。

其他一些凸优化问题（例如 SOCP 与 SDP）不容易改写成所需形式，但可以通过把内点方法推广到广义不等式问题来处理。
