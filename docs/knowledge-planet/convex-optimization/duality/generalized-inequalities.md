---
title: "广义不等式"
date: 2022-04-08T15:12:16+08:00
weight: 490
---
# 广义不等式

本章讲授的 Lagrange 对偶理论可以推广至具有广义不等式约束的问题中，即

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(x) \\
    \mathrm{subject\ to} \quad & f_i(x) \preceq_{K_i} 0, \quad i=1,\cdots,m \\
    \quad & h_i(x) = 0, \quad i=1,\cdots,p
\end{aligned}
$$

其中 $K_i \subseteq \mathbf{R}^{k_i}$ 是正常锥（闭、凸、尖且有非空内部），并约定

$$
u \preceq_{K_i} v \quad \Longleftrightarrow \quad v-u \in K_i.
$$

因此，约束 $f_i(x) \preceq_{K_i} 0$ 等价于 $-f_i(x) \in K_i$。本节推导广义不等式对应的乘子约束，并用半定规划说明如何构造对偶问题。

## 对偶锥与 Lagrange 对偶函数

锥 $K$ 的对偶锥定义为

$$
K^* = \{z \mid z^{\top}u \geqslant 0,\ \forall u \in K\}.
$$

若 $f_i(x) \preceq_{K_i} 0$，则 $-f_i(x) \in K_i$。对任意 $\lambda_i \in K_i^*$，由对偶锥定义可得 $\lambda_i^{\top}f_i(x) \leqslant 0$。所以广义不等式的 Lagrange 乘子必须满足 $\lambda_i \in K_i^*$。

令 $h(x)=(h_1(x),\ldots,h_p(x))$，Lagrange 函数和对偶函数分别为

$$
\begin{aligned}
L(x,\lambda,\nu)
&= f_0(x)+\sum_{i=1}^{m}\lambda_i^{\top}f_i(x)+\nu^{\top}h(x),\\
g(\lambda,\nu)
&=\inf_{x\in D} L(x,\lambda,\nu),
\end{aligned}
$$

其中 $D$ 是原问题的定义域。对任意原问题可行点 $\tilde{x}$ 及满足 $\lambda_i\in K_i^*$ 的乘子，等式约束项为零，广义不等式项非正，因此

$$
g(\lambda,\nu) \leqslant L(\tilde{x},\lambda,\nu) \leqslant f_0(\tilde{x}).
$$

对所有原问题可行点取下确界，便得到弱对偶关系 $g(\lambda,\nu)\leqslant p^*$。相应的 Lagrange 对偶问题为

$$
\begin{aligned}
\mathrm{maximize}\quad & g(\lambda,\nu) \\
\mathrm{subject\ to}\quad & \lambda_i \in K_i^*,\quad i=1,\ldots,m.
\end{aligned}
$$

记其最优值为 $d^*$，则始终有 $d^*\leqslant p^*$。这与普通不等式对偶的结构相同，区别在于标量乘子的非负约束被对偶锥约束取代。

## Slater 条件与强对偶

考虑等式约束为仿射形式 $Ax=b$ 的问题。假设 $f_0$ 为凸函数，每个 $f_i$ 关于锥 $K_i$ 凸，并且存在 $x$ 满足

$$
x\in\operatorname{relint}D,\qquad Ax=b,\qquad f_i(x)\prec_{K_i}0,\quad i=1,\ldots,m,
$$

其中 $u\prec_K v$ 表示 $v-u\in\operatorname{int}K$。这就是广义 Slater 条件。若满足该条件且原问题最优值有限，则强对偶成立，且对偶最优值能够取到。对半定锥 $\mathbf{S}_+^k$，严格不等式表示矩阵负定；对二阶锥，则表示 $-f_i(x)$ 严格位于锥内部。关于向量值函数的锥凸性，另见[广义不等式下的凸性](/knowledge-planet/convex-optimization/convex-functions/convexity-with-respect-to-generalized-inequalities/)。

## 例子：半定规划的对偶

考虑半定规划

$$
\begin{aligned}
\mathrm{minimize}\quad & c^{\top}x \\
\mathrm{subject\ to}\quad & F(x)=\sum_{i=1}^{n}x_iF_i+G\preceq 0,
\end{aligned}
$$

其中 $F_i,G\in\mathbf{S}^k$，约束锥为半正定锥 $\mathbf{S}_+^k$。该锥关于矩阵内积 $\langle X,Y\rangle=\operatorname{tr}(XY)$ 自对偶，因此乘子是满足 $Z\succeq0$ 的对称矩阵。Lagrange 函数为

$$
\begin{aligned}
L(x,Z)
&=c^{\top}x+\operatorname{tr}(F(x)Z)\\
&=\sum_{i=1}^{n}x_i\bigl(c_i+\operatorname{tr}(F_iZ)\bigr)
  +\operatorname{tr}(GZ).
\end{aligned}
$$

对自由变量 $x$ 取下确界：只要某个 $c_i+\operatorname{tr}(F_iZ)\ne0$，Lagrange 函数就沿相应方向无界，故 $g(Z)=-\infty$；若这些系数全为零，则 $g(Z)=\operatorname{tr}(GZ)$。于是对偶问题为

$$
\begin{aligned}
\mathrm{maximize}\quad & \operatorname{tr}(GZ) \\
\mathrm{subject\ to}\quad & \operatorname{tr}(F_iZ)+c_i=0,\quad i=1,\ldots,n,\\
& Z\succeq0.
\end{aligned}
$$

只要原问题可行，任意对偶可行矩阵 $Z$ 都给出原问题最优值的一个下界；若进一步满足适当的广义 Slater 条件，则原始和对偶最优值相等。关于半定规划的建模形式和其他例子，另见[广义不等式约束](/knowledge-planet/convex-optimization/convex-optimization-problems/generalized-inequality-constraints/)。
