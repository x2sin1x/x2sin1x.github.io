---
title: "鞍点解释"
date: 2022-04-04T14:56:28+08:00
weight: 440
---
# 鞍点解释

## 鞍点

沿用标准的原问题

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(x) \\
    \mathrm{subject\ to} \quad & f_i(x) \leqslant 0, \quad i=1,\cdots,m \\
    & h_i(x) = 0, \quad i=1,\cdots,p
\end{aligned}
$$

定义 Lagrange 函数 $L: \mathbf{R}^n \times \mathbf{R}^m \times \mathbf{R}^p \rightarrow \mathbf{R}$

$$
L(x, \lambda, \nu) = f_0(x) + \sum_{i=1}^{m} \lambda_i f_i(x) + \sum_{i=1}^{p} \nu_i h_i(x)
$$

其中 $\lambda \succeq 0$。称 $(x^{\star}, \lambda^{\star}, \nu^{\star})$ 是 $L$ 的**鞍点**，如果对所有的 $x, \lambda \succeq 0, \nu$ 都有

$$
L(x^{\star}, \lambda, \nu) \leqslant L(x^{\star}, \lambda^{\star}, \nu^{\star}) \leqslant L(x, \lambda^{\star}, \nu^{\star})
$$

即 $x^{\star}$ 极小化 $L(x, \lambda^{\star}, \nu^{\star})$，而 $(\lambda^{\star}, \nu^{\star})$ 极大化 $L(x^{\star}, \lambda, \nu)$：固定另外两组变量时，它分别表现为“谷底”和“峰顶”，形如马鞍，故称鞍点。

一组变量构成鞍点，当且仅当强对偶性成立且 $x^{\star}$、$(\lambda^{\star}, \nu^{\star})$ 分别是原问题和对偶问题的最优解。此时鞍点值为共同最优值 $p^{\star} = d^{\star}$，且互补松弛性成立。反之，若强对偶性不成立（或 $(\lambda^{\star}, \nu^{\star})$ 不可行），则鞍点不存在。

## max-min 与 min-max 不等式

对任意 $L$ 都有下述**max-min 不等式**

$$
\sup_{\lambda \succeq 0, \nu} \inf_{x} L(x, \lambda, \nu) \leqslant \inf_{x} \sup_{\lambda \succeq 0, \nu} L(x, \lambda, \nu)
$$

左边正是对偶最优值 $d^{\star}$（先对 $x$ 取下确界得到对偶函数，再对对偶变量取上确界）；右边是“先对偶后原”的最优值，它总不小于 $p^{\star}$（对每个 $x$，$\sup_{\lambda\succeq 0,\nu} L \geqslant p^{\star}$ 当 $x$ 可行时取等号）。因此 max-min 不等式是弱对偶性 $d^{\star} \leqslant p^{\star}$ 的另一种表达。

强对偶性成立时，不等式取等号，且左右两边的最优点 $(x^{\star}, \lambda^{\star}, \nu^{\star})$ 恰好构成 $L$ 的鞍点。

## 博弈解释

鞍点有一个自然的博弈论解释。把 $x$ 看作第一个参与人（“最小化者”）的策略，$(\lambda, \nu)$（$\lambda \succeq 0$）看作第二个参与人（“最大化者”）的策略，支付函数为 $L(x, \lambda, \nu)$：最小化者希望支付越小越好，最大化者希望支付越大越好。

- 若最大化者先固定 $(\lambda, \nu)$，最小化者的最优响应是 $\inf_x L(x, \lambda, \nu)$，即对偶函数 $g(\lambda, \nu)$；
- 若最小化者先固定 $x$，最大化者的最优响应是 $\sup_{\lambda \succeq 0, \nu} L(x, \lambda, \nu)$，当 $x$ 不可行时该值为 $+\infty$，因此理性地选择可行点。

max-min 不等式说明“后手占优”：知道对方策略的一方总不会吃亏。鞍点 $(x^{\star}, \lambda^{\star}, \nu^{\star})$ 就是这个两人零和博弈的均衡点：任何一方单方面偏离自己的均衡策略都不会获益。强对偶性成立，等价于该博弈存在均衡点（最优值由先手选择不影响结果）。
