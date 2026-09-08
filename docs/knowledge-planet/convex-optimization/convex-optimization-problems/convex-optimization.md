---
title: "凸优化"
weight: 320
---

# 凸优化

## 凸优化问题的标准形式

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(x) \\
    \mathrm{subject\ to} \quad & f_i(x) \leqslant 0, \quad i = 1, \cdots, m \\
    & a_i^{\top}x = b_i, \quad i = 1, \cdots, p
\end{aligned}
$$

其中 $f_0, \cdots, f_m$ 是凸函数。相较于一般的优化问题而言，凸优化问题还需要满足如下条件：

- 目标函数是凸函数
- 不等式约束是凸的
- 等式约束 $h_i(x) = a_i^{\top}x - b_i$ 是仿射函数

凸优化问题的可行域也是凸的。因此，在凸优化问题中，我们最小化凸集上的凸目标函数。

同理，如果函数 $f_0$ 是拟凸函数而不是凸函数，则称该问题是一个（标准形式的）拟凸优化问题。

### 凹最大化问题

若目标函数 $f_0$ 是凹函数，则称最大化问题

$$
\begin{aligned}
    \mathrm{maximize} \quad & f_0(x) \\
    \mathrm{subject\ to} \quad & f_i(x) \leqslant 0, \quad i = 1, \cdots, m \\
    & a_i^{\top}x = b_i, \quad i = 1, \cdots, p
\end{aligned}
$$

凸优化问题。这是因为凹最大化问题可以转化为极小化 $-f_0$ 得以求解。

### 凸优化问题的抽象形式

考虑 $\mathbf{R}^2$ 上的问题

$$
\begin{aligned}
\mathrm{maximize} \quad & f_{0}(x)=x_{1}^{2}+x_{2}^{2} \\
\mathrm{subject\ to} \quad & f_{1}(x) = \dfrac{x_{1}}{1+x_{2}^{2}} \leqslant 0 \\
& h_{1}(x)=\left(x_{1}+x_{2}\right)^{2}=0
\end{aligned}
$$

根据凸优化的定义，它不是一个凸优化问题。因为等式约束 $h_1$ 不是仿射函数，并且不等式约束 $f_1$ 也不是凸函数。不过，该问题的可行域却是凸集

$$
\{ x \mid x_1 \leqslant 0, x_1 + x_2 = 0 \}
$$

从客观上讲，我们最小化了凸集上的凸函数。那么为什么根据凸优化的定义，它不是一个凸优化问题呢？

上述问题其实和下面的问题等价

$$
\begin{aligned}
\mathrm{maximize} \quad & f_0(x)=x_1^2+x_2^2 \\
\mathrm{subject\ to} \quad & \tilde{f}_1(x) = x_1 \leqslant 0 \\
& \tilde{h}_1(x)=x_1+x_2=0
\end{aligned}
$$

显然该问题是一个凸优化问题。我们称原问题是一个抽象的凸优化问题，即凡是在凸集上最小化凸函数的问题都可以被称为抽象的凸优化问题。但是，我们不讨论这类问题，还是需要用凸不等式和线性等式来进行约束。

## 局部最优解和全局最优解

凸优化问题的一个基本性质是，任何局部最优点一定是全局最优点。从几何上看，如果点 $x$ 是凸优化问题的最优解，那么 $-\nabla f_0(x)$ 定义了 $X$ 在 $x$ 处的一个支撑超平面。

## 可微目标函数的最优性准则

设凸优化问题的目标函数 $f_0$ 是可微的，那么 $\forall x, y \in \operatorname{dom} f_0$

$$
f_0(y) \geqslant f_0(x) + \nabla f_0(x)^{\top} (y-x)
$$

设 $X$ 表示可行域，即

$$
\begin{aligned}
    X = \{ x \mid f_i(x) & \leqslant 0, i=1,\cdots,m, \\
    h_i(x) &= 0, i=1,\cdots,p \}
\end{aligned}
$$

那么 $x$ 是最优的当且仅当

$$
\forall y \in X, \quad \nabla f_0(x)^{\top} (y-x) \geqslant 0
$$

这意味着 $-\nabla f_0(x)$ 定义了 $x$ 处可行域的支撑超平面。

### 最优性条件的证明

> 本文从略

### 无约束凸优化问题

对于无约束凸优化问题，$x$ 是最优解的充要条件是

$$
\nabla f_0(x) = 0
$$

这就是我们非常熟悉的利用导数等于零来求极值的方法。

无约束二次优化是一个很好的例子，考虑 $\mathbf{R}^n$ 上的目标函数

$$
f_0(x) = \dfrac{1}{2} x^{\top}Px + q^{\top} + r
$$

其中 $P \in \mathbf{S}^n_+$。$x$ 是 $f_0$ 的极小值的充要条件是

$$
\nabla f_0(x) = Px + q = 0
$$

上面的线性方程组的解决定了无约束二次优化的最优解。根据非齐次线性方程组 $Px = -q$ 的解的三种情况，可以得到如下结论：

- 原问题无最优解（线性方程组无解）
- 原问题有唯一最优解（线性方程组有唯一解）
- 原问题有无穷多个最优解（线性方程组有无穷多组解）

### 只含等式约束的问题

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(x) \\
    \mathrm{subject\ to} \quad & Ax = b
\end{aligned}
$$

这样，可行域也是仿射的。于是可行解 $x$ 的最优性条件为：对任意满足 $Ay = b$ 的 $y$，

$$
\nabla f_0(x)^{\top}(y-x) \geqslant 0
$$

都成立。由于 $x$ 是可行的，每个可行的 $y$ 都可以表示成直线参数方程的形式 $y=x+v$，其中 $v \in \mathcal{N}(A)$。因此，上式可以转化为

$$
\forall v \in \mathcal{N}(A), \quad \nabla f_0(x)^{\top}v \geqslant 0
$$

如果一个线性函数在其子空间上非负，则它在子空间上必恒等于零。因此，$\forall v \in \mathcal{N}(A)$，有 $\nabla f_0(x)^{\top}v = 0$，即

$$
\nabla f_0(x) \bot \mathcal{N}(A)
$$

利用导出正交分解的性质

$$
\mathcal{N}(A) = \mathcal{R}(A^{\top})^{\bot}
$$

可以将只含等式约束的凸优化问题表示为 $\nabla f_0(x) \in \mathcal{R}(A^{\top})$，即存在 $v \in \mathbf{R}^p$，使得

$$
\nabla f_0(x) + A^{\top}v = 0
$$

同时考虑 $Ax = b$ 要求（即要求 $x$ 可行），这是经典的 Lagrange 乘子最优性条件。

### 非负象限中的极小化

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(x) \\
    \mathrm{subject\ to} \quad & x \succeq 0
\end{aligned}
$$

其最优性条件可以表示为

$$
\begin{cases}
    \quad x \succeq 0 \\
    \quad \nabla f_0(x)\succeq 0 \\
    \quad x_i(\nabla f_0(x))_i = 0, \quad i=1,\cdots,n
\end{cases}
$$

## 等价的凸问题

在上一小节中，我们讨论了[等价问题](/knowledge-planet/convex-optimization/convex-optimization-problems/optimization-problems#等价问题)，意在说明经过一些变换之后问题等价。实际上，有一些变换不仅可以保证问题前后等价，还可以保持凸性。

### 消除等式约束

由于凸优化问题的等式约束都是线性等式 $Ax=b$，我们可以将之转化为非齐次线性方程组 $Ax=b$ 的一个特解 $x_0$ 和域为 $A$ 的零空间的矩阵 $F$ 来消除这些等式约束，从而得到关于 $z$ 的问题

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(Fz+x_0) \\
    \mathrm{subject\ to} \quad & f_i(Fz+x_0) \preceq 0
\end{aligned}
$$

### 引入等式约束

如果目标函数或约束函数具有 $f_i(A_ix+b_i)$ 的形式，其中 $A_i \in \mathbf{R}^{k_i \times n}$。我们可以引入新的变量 $y_i \in \mathbf{R}^{k_i}$，用 $f_i(y_i)$ 替换 $f_i(A_ix+b_i)$ 并添加线性等式约束 $y_i=A_ix+b_i$。

### 松弛变量

由于凸优化问题中的等式约束必须是仿射的，所以 $f_i$ 需为仿射的。换而言之，为线性不等式引入松弛变量保持问题的凸性不变。

### 上镜图问题形式

$$
\begin{aligned}
    \mathrm{minimize} \quad & t \\
    \mathrm{subject\ to} \quad & f_0(x) - t \leqslant 0 \\
    \quad & f_i(x) \leqslant 0, \quad i=1,\cdots,m \\
    \quad & a_i^{\top}x=b_i, \quad i=1,\cdots,p
\end{aligned}
$$

## 拟凸优化

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(x) \\
    \mathrm{subject\ to} \quad & f_i(x) \leqslant 0, \quad i = 1, \cdots, m \\
    & A^{\top}x = b 
\end{aligned}
$$

其中不等式约束函数 $f_1,\cdots,f_m$ 是凸的，而目标函数 $f_0$ 是拟凸的。拟凸约束函数可以等价的替换为凸约束函数，即具有相同的 0- 下水平集的凸函数。

这里探讨凸优化和拟凸优化本质上的不同，同时也将说明拟凸优化问题可以归结为求解一系列凸优化问题。

### 局部最优解与最优性条件

凸优化和拟凸优化之间最重要的区别在于，拟凸优化问题可以有非全局最优解。

![](0ed3da5493d6875598b33f9867210ee9.png)

如图所示的拟凸函数在 $x$ 是局部最优解，但却不是全局最优解。这个例子说明了在凸函数中的最优性条件 $f^{\prime}(x)=0$ 对拟凸函数并不成立，它仅仅是一个充分条件。

### 通过凸可行性问题求解拟凸优化问题

可以通过一族凸不等式来表示拟凸函数的下水平集，这是解决拟凸优化问题的一般方法。令 $\phi_t: \mathbf{R}^n \rightarrow \mathbf{R}$，$t \in \mathbf{R}$ 为满足

$$
f_0(x) \leqslant t \Longleftrightarrow \phi_t(x) \leqslant 0
$$

的一族非增凸函数。用 $p^{\star}$ 表示拟凸优化问题的最优值。如果可行性问题

$$
\begin{aligned}
    \mathrm{find} \quad & x \\
    \mathrm{subject\ to} \quad & \phi_t(x) \leqslant 0 \\
    \quad & f_i(x) \leqslant 0, \quad i=1,\cdots,m \\
    \quad & Ax=b
\end{aligned}
$$

是可行的，我们有 $p^{\star} \leqslant t$。反之，如果不可行，那么 $p^{\star} \geqslant t$。

按照上面的性质，我们可以得到一个解决拟凸优化问题的一个简单算法：使用二分法并在每步中求解凸可行性问题。我们设问题可行，并从已知包含最优解 $p^{\star}$ 的区间 $[l, u]$ 开始求解。然后在中点 $t = (l+u)/2$ 求解凸可行性问题，判断最优解是在区间的上半或下半部分，并据此更新区间。重复上述过程直到区间宽度足够小。
