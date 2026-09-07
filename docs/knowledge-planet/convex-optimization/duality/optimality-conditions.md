---
inHomePost: false
title: "最优性条件"
---

# 最优性条件

## 次优解认证和终止准则

如果能够找到一个对偶可行解 $(\lambda, \nu)$，就对原问题的最优值建立了一个下界：$p^{\star} \geqslant g(\lambda, \nu)$。因此，对偶可行点 $(\lambda, \nu)$ 为表达式 $p^{\star} \geqslant g(\lambda, \nu)$ 的成立提供了一个证明或认证。强对偶性意味着存在任意好的认证。

对偶可行点可以让我们在不知道 $p^{\star}$ 的确切值的情况下界定给定可行点的次优程度。事实上，如果 $x$ 是原问题的可行解且 $(\lambda, \nu)$ 对偶可行，那么

$$
f(x) - p^{\star} \leqslant f_0(x) - g(\lambda, \nu)
$$

特别地，上式说明了 $x$ 是 $\epsilon$- 次优，其中 $\epsilon = f_0(x) - g(\lambda, \nu)$。

定义原问题和对偶问题目标函数的差值

$$
f_0(x) - g(\lambda, \nu)
$$

为原问题可行解 $x$ 和对偶可行解 $(\lambda, \nu)$ 之间的对偶间隙。一对原对偶问题的可行点 $x, (\lambda, \nu)$ 将原问题（对偶问题）的最优值限制在一个区间上：

$$
p^{\star} \in\left[g(\lambda, \nu), f_0(x)\right], \quad d^{\star} \in\left[g(\lambda, \nu), f_0(x)\right]
$$

区间的长度即为上面定义的对偶间隙。

如果原对偶可行对 $x, (\lambda, \nu)$ 的对偶间隙为零，即 $f_0(x) = g(\lambda, \nu)$，那么 $x$ 是原问题的最优解且 $(\lambda, \nu)$ 是对偶问题的最优解。此时，我们可以认为 $(\lambda, \nu)$ 是证明 $x$ 为最优解的一个认证。（类似地，也可以认为 $x$ 是证明 $(\lambda, \nu)$ 为最优解的一个认证。）

上述现象可以用在优化算法中给出非启发式停止准则。即令对偶间隙小于给定精度 $\epsilon_{\mathrm{abs}}$，这能够保证当算法终止的时候，问题的解可以达到 $\epsilon_{\mathrm{abs}}$- 最优。

## 互补松驰性

设原问题和对偶问题的最优值都可以达到且相等（即强对偶性成立）。令 $x^{\star}$ 是原问题的最优解，$(\lambda^{\star}, \nu^{\star})$，这表明

$$
\begin{aligned}
f_0\left(x^{\star}\right) &=g\left(\lambda^{\star}, \nu^{\star}\right) \\
&=\inf_x \left(f_0(x)+\sum_{i=1}^{m} \lambda_i^{\star} f_i(x)+\sum_{i=1}^{p} \nu_i^{\star} h_i(x)\right) \\
& \leqslant f_0\left(x^{\star}\right)+\sum_{i=1}^{m} \lambda_i^{\star} f_i\left(x^{\star}\right)+\sum_{i=1}^{p} \nu_i^{\star} h_i\left(x^{\star}\right) \\
& \leqslant f_0\left(x^{\star}\right)
\end{aligned}
$$

第一个等式说明最优对偶间隙为零，第二个等式是对偶函数的定义。第三个不等式是根据 Lagrange 函数关于 $x$ 求下确界小于等于其在 $x = x^{\star}$ 处得到。最后一个不等式成立是因为

$$
\left\{
    \begin{matrix}
        \lambda_i^{\star} \geqslant 0, & i=1,\cdots,m \\
        f_i(x^{\star}) \leqslant 0, & i=1,\cdots,m \\
        h_i(x^{\star}) = 0, & i=1,\cdots,p
    \end{matrix}
\right.
$$

因此，在上面的式子链中，两个不等式取等号。

由此可以得出一些有意义的结论。其中一个特别重要的结论是

$$
\sum_{i=1}^m \lambda_i^{\star} f_i(x^{\star}) = 0
$$

事实上，求和项的每一项都非正，因此有

$$
\lambda_i^{\star} f_i(x^{\star}) = 0, \quad i=1,\cdots,m
$$

上述条件称为**互补松弛性**。它对任意原问题的最优解 $x^{\star}$ 以及对偶问题的最优解 $(\lambda^{\star}, \nu^{\star})$ 都成立（当强对偶性成立时）。我们可以将互补松弛性条件写成

$$
\lambda_i^{\star} > 0 \Longrightarrow f_i(x^{\star}) = 0
$$

或者等价地

$$
f_i(x^{\star}) < 0 \Longrightarrow \lambda_i^{\star} = 0
$$

互补松弛性条件说明了在最优点处，除了第 $i$ 个约束起作用的情况，最优 Lagrange 乘子的第 $i$ 项都为零。

## KKT 最优性条件

### 非凸问题的 KKT 条件

由于 $L(x, \lambda^{\star}, \nu^{\star})$ 关于 $x$ 求极小在 $x^{\star}$ 处取得最小值，因此函数在 $x^{\star}$ 处的导数必须为零，即

$$
\nabla f_{0}\left(x^{\star}\right)+\sum_{i=1}^{m} \lambda_{i}^{\star} \nabla f_{i}\left(x^{\star}\right)+\sum_{i=1}^{p} \nu_{i}^{\star} \nabla h_{i}\left(x^{\star}\right)=0
$$

因此，我们可以得到

$$
\begin{aligned}
    f_{i}\left(x^{\star}\right) &\leqslant 0, & i &=1, \cdots, m \\
    h_{i}\left(x^{\star}\right) &=0, & i &=1, \cdots, p \\
    \lambda_{i}^{\star} & \geqslant 0, & i &=1, \cdots, m \\
    \lambda_{i}^{\star} f_{i}\left(x^{\star}\right) &=0, & i &=1, \cdots, m \\
    \nabla f_{0}\left(x^{\star}\right)+\sum_{i=1}^{m} \lambda_{i}^{\star} \nabla f_{i}\left(x^{\star}\right)+\sum_{i=1}^{p} \nu_{i}^{\star} \nabla h_{i}    \left(x^{\star}\right) &=0 & &
\end{aligned}
$$

我们称上式为 **Karush-Kuhn-Tucker (KKT)** 条件。

总之，只要强对偶性成立，那么任何一对原问题的最优解和对偶问题的最优解必须满足 KKT 条件。

### 凸问题的 KKT 条件

$$
\begin{aligned}
    f_i(\tilde{x}) & \leqslant 0, & i &=1, \cdots, m \\
    h_i(\tilde{x}) &=0, & i &=1, \cdots, p \\
    \tilde{\lambda}\_i & \geqslant 0, & i &=1, \cdots, m \\
    \tilde{\lambda}\_i f_i(\tilde{x}) &=0, & i &=1, \cdots, m \\
    \nabla f_0(\tilde{x})+\sum_{i=1}^{m} \tilde{\lambda}\_i \nabla f_i(\tilde{x})+\sum_{i=1}^{p} \tilde{\nu}\_i \nabla h_i(\tilde{x}) &=0, & &
\end{aligned}
$$

从凸问题的 KKT 条件中，我们可以得出结论

$$
\begin{aligned}
    g(\tilde{\lambda}, \tilde{\nu}) &=L(\tilde{x}, \tilde{\lambda}, \tilde{\nu}) \\
    &=f_{0}(\tilde{x})+\sum_{i=1}^{m} \tilde{\lambda}\_{i} f\_{i}(\tilde{x})+\sum_{i=1}^{p} \tilde{\nu}\_{i} h_{i}(\tilde{x}) \\
    &=f_{0}(\tilde{x})
\end{aligned}
$$

推导过程的最后一步成立是因为 $h_i(\tilde{x}) = 0$ 以及 $\tilde{\lambda}_i f_i(\tilde{x}) = 0$。这说明原问题的解 $\tilde{x}$ 和对偶问题的解 $(\tilde{\lambda}, \tilde{\nu})$ 之间的对偶间隙为零，因此分别是原、对偶问题的最优解。总之，对目标函数和约束函数可微的任意凸优化问题，任意满足 KKT 条件的点分别是原、对偶问题的最优解，对偶间隙为零。

KKT 条件在优化领域有着重要作用。在一些特殊的情形下，是可以解析求解 KKT 条件的（因此可以求解优化问题）。更一般地，很多求解凸优化问题的方法可以认为或者理解为求解 KKT 条件的方法。

::: info
关于 KKT 条件的深入理解与分析，详见下一小节[深入理解 KKT 条件](/knowledge-planet/convex-optimization/duality/going-deeper-into-kkt)。
:::
