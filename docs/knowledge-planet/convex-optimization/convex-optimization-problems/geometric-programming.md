---
title: "几何规划"
date: 2022-03-29T10:57:25+08:00
weight: 350
---
# 几何规划

本小节描述的几何规划问题在自然形式中并不是凸的，但是可以通过变量变换，以及目标函数和约束函数的变换转化成凸优化问题。

## 单项式和正项式

定义函数 $f: \mathbf{R}^n \rightarrow \mathbf{R}$，$\operatorname{dom} f = \mathbf{R}^n_{++}$，则单项式定义为

$$
f(x) = c x_1^{a_1} x_2^{a_2} \cdots x_n^{a_n}
$$

其中 $c > 0$，$a_i \in \mathbf{R}$。这里的单项式和过去在中学里学习的单项式的概念其实是类似的，只是定义更加严格，要确保其函数值为正。

有了单项式的定义，我们就可以定义多项式了。由于我们的单项式都是正的，多项式在这里被称为正项式

$$
f(x) = \sum_{k=1}^K c_k x_1^{a_{1k}} x_2^{a_{2k}} \cdots x_n^{a_{nk}}
$$

这个正项式有 $K$ 个项，其中 $c_k > 0$。

单项式对数乘和除都是封闭的，正项式对加法、数乘和非负的伸缩变换都是封闭的。正项式和单项式相乘，结果仍然是一个正项式；类似地，正项式除以单项式，结果仍然是一个正项式。这些和我们在中学里学到的完全一样。

## 几何规划

几何规划（Geometric Program, GP）是定义在单项式和正项式上的优化问题，如下

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(x) \\
    \mathrm{subject\ to} \quad & f_i(x) \leqslant 1, \quad i = 1,\cdots,m \\
    \quad & h_i(x) = 1, \quad i = 1,\cdots,p
\end{aligned}
$$

其中 $f_0, \cdots, f_m$ 都是正项式，$h_1, \cdots, h_p$ 都是单项式。几何规划问题的定义域是 $\mathcal{D} = \mathbf{R}^n_{++}$，约束 $x \succ 0$ 是隐式的。


### 几何规划的推广

如果几何规划问题的不等式约束是 $f(x) \leqslant h(x)$，我们可以在不等式两边同除以 $h(x)$，得到

$$
\dfrac{f(x)}{h(x)} \leqslant 1
$$

根据上述性质，不等号左边的函数仍然是一个正项式，仍然满足几何规划问题的定义。

类似地，如果几何规划问题的等式约束是 $h_1(x) = h_2(x)$，我们同样也可以在等式两边同除以 $h_2(x)$，得到

$$
\dfrac{h_1(x)}{h_2(x)} = 1
$$

根据上述性质，不等号左边的函数仍然是一个单项式，仍然满足几何规划问题的定义。

下面是一个例子：

$$
\begin{aligned}
    \mathrm{maximize} \quad & \dfrac{x}{y} \\
    \mathrm{subject\ to} \quad & 2 \leqslant x \leqslant 3 \\
    \quad & x^2 + \dfrac{3y}{z} \leqslant \sqrt{y} \\
    \quad & \dfrac{x}{y} = z^2
\end{aligned}
$$

使用上述推广，原问题可以化为标准的几何规划形式

$$
\begin{aligned}
    \mathrm{minimize} \quad & x^{-1} y \\
    \mathrm{subject\ to} \quad & 2 x^{-1} \leqslant 1 \\
    \quad & \dfrac{1}{3} x \leqslant 1 \\
    \quad & x^2 y^{-1/2} + 3 y^{1/2} z^{-1} \leqslant 1 \\
    \quad & x y^{-1} z^{-2} = 1
\end{aligned}
$$

## 凸形式的几何规划

一般来说，几何规划问题不是凸优化问题，但是可以通过变量变换以及目标函数和约束函数的变换将之转化为凸优化问题。

我们定义新的变量 $y_i = \log x_i$，则 $x_i = e^{y_i}$。于是，目标函数可化为

$$
\begin{aligned}
    f(x) &= \sum_{k=1}^K c_k x_1^{a_{1k}} x_2^{a_{2k}} \cdots x_n^{a_{nk}} \\
    &= \sum_{k=1}^K c_k e^{a_{1k} y_1} e^{a_{2k} y_2} \cdots e^{a_{nk} y_n} \\
    &= \sum_{k=1}^K e^{a_k^{\top} y + b_k}
\end{aligned}
$$

其中，$a_k = (a_{1k}, \cdots, a_{nk})$，$b_k = \log c_k$。于是，原问题可化为

$$
\begin{aligned}
    \mathrm{minimize} \quad & \sum_{k=1}^{K_0} e^{a_{0k}^{\top} y+b_{0k}} \\
    \mathrm{subject\ to} \quad & \sum_{k=1}^K e^{a_{ik}^{\top} y+b_{ik}} \leqslant 1, \quad i=1, \cdots, m \\
    \quad & e^{g_i^{\top} y+h_i}=1, \quad i=1, \cdots, p
\end{aligned}
$$

现在我们通过取对数的方法来变换目标函数和约束函数，得到

$$
\begin{aligned}
    \mathrm{minimize} \quad & \tilde{f} _0(y) = \log (\sum _{k=1}^{K_0} e^{a _{0k}^{\top} y+b _{0k}}) \\
    \mathrm{subject\ to} \quad & \tilde{f} _i(y) = \log (\sum _{k=1}^K e^{a _{ik}^{\top} y+b _{ik}}) \leqslant 1, \quad i=1, \cdots, m \\
    \quad & \tilde{h}_i(y) = g_i^{\top} y+h_i=1, \quad i=1, \cdots, p
\end{aligned}
$$

其中 $\tilde{f}_i$ 是凸的，$\tilde{h}_i$ 是仿射的，因此上面的问题是凸优化问题，并且称之为凸形式的几何规划。

如果正项式的目标函数和约束函数都只有一个项，则凸形式的几何规划就退化为（一般的）线性规划。因此，我们可以认为几何规划是线性规划的一个推广。
