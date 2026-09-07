---
title: "等价的对偶问题"
---

# 等价的对偶问题

本小节的例子将说明，对一个问题进行简单的等价变形有可能得到非常不一样的对偶问题。

## 引入新的变量以及相应的等式约束

$$
\mathrm{minimize} \quad f_0(Ax+b)
$$

该问题的 Lagrange 对偶函数是常数 $p^{\star}$。即使强对偶性成立，但其 Lagrange 对偶问题没有什么意义和用途。

现在我们对原问题作等价变形

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(y) \\
    \mathrm{subject\ to} \quad & Ax+b = y
\end{aligned}
$$

我们引入了新的变量 $y$，并且增加了新的等式约束，将原来作为目标函数的复合函数拆开了。这样，变换之后的问题的 Lagrange 函数为

$$
L(x, y, \nu) = f_0(y) + \nu^{\top}(Ax+b-y)
$$

求解 Lagrange 对偶函数

$$
g(\nu) = b^{\top} \nu + \inf_y (f_0(y) - \nu^{\top} y) = b^{\top} - f_0^{\star}(\nu)
$$

于是对偶问题可以描述为

$$
\begin{aligned}
    \mathrm{minimize} \quad & b^{\top} \nu - f_0^{\star}(\nu) \\
    \mathrm{subject\ to} \quad & A^{\top} \nu = 0
\end{aligned}
$$

显然，变换后的问题的对偶问题要比原问题的对偶问题更有意义。

引入新的等式约束的思想同样可以用在约束函数上面。例如，考虑问题

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(A_0x + b_0) \\
    \mathrm{subject\ to} \quad & f_i(A_ix+ b_i) \leqslant 0, \quad i=1,\cdots,m
\end{aligned}
$$

其中 $A_i \in \mathbf{R}^{k_i \times n}$，函数 $f_i: \mathbf{R}^{k_i} \rightarrow \mathbf{R}$ 是凸函数。对 $i=0,\cdots,m$，引入新的变量 $y_i \in \mathbf{R}^{k_i}$，将原问题重新描述为

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(y_0) \\
    \mathrm{subject\ to} \quad & f_i(y_i) \leqslant 0, \quad i=1,\cdots,m \\
    \quad & A_ix + b_i = y_i, i=0,\cdots,m
\end{aligned}
$$

后面的步骤与之前类似，同样也是求解 Lagrange 对偶函数，并描述对偶问题。

## 变换目标函数

如果我们将目标函数 $f_0$ 替换为 $f_0$ 的增函数，得到的问题与原问题显然是等价的。但是，等价问题的对偶问题可能和原问题的对偶问题大不相同。

考虑最小范数问题

$$
\mathrm{minimize} \quad \| Ax-b \|
$$

我们将问题重新描述为

$$
\begin{aligned}
    \mathrm{minimize} \quad & \dfrac{1}{2} \| y \|^2 \\
    \mathrm{subject\ to} \quad & Ax-b = y
\end{aligned}
$$

## 隐式约束

接下来考虑一个简单的重新描述问题的方式，通过修改目标函数将约束包含到目标函数中，当约束被违背时，目标函数为无穷大。

考虑下列具有框约束的线性规划问题

$$
\begin{aligned}
    \mathrm{minimize} \quad & c^{\top}x \\
    \mathrm{subject\ to} \quad & Ax=b \\
    \quad & l \preceq x \preceq u
\end{aligned}
$$

原问题的对偶问题很容易就能够得到，但是特别复杂。我们换一种做法，将原问题重新描述为

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(x) \\
    \mathrm{subject\ to} \quad & Ax = b
\end{aligned}
$$

其中 $f_0(x)$ 定义为

$$
f_0(x) = \left\{\begin{matrix}
    c^{\top}x & l \preceq x \preceq u \\
    \infty & \text{otherwise}
\end{matrix}\right.
$$

这样一来新问题的对偶问题则是一个更为简单的无约束问题。
