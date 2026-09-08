---
title: "共轭函数"
weight: 240
---

# 共轭函数

## 定义

设函数 $f: \mathbf{R}^n \rightarrow \mathbf{R}$，其共轭函数 $f^{*}: \mathbf{R}^n \rightarrow \mathbf{R}$ 为

$$
f^{*}(y)=\sup _{x \in \operatorname{dom} f}\left(y^{\top} x-f(x)\right)
$$

### 几何意义

![](42ab18f4d6e33cabf67b80e910096099.png "共轭函数的几何意义")

共轭函数的几何意义如图所示。教材当中仅仅只是简略说明了这张图，但实际上这张图并不是特别容易理解。下面详细说明如何将这张图和共轭函数的定义结合起来理解。

首先，我们要明确的一点是，在共轭函数的定义中，自变量是 $y$，而不是 $x$，$x$ 应该当成常数或者参数。而在上面的函数图像中，自变量是 $x$，而不是 $y$，$y$ 应该当成常数或者参数。

因此，一元函数 $f(x)$ 的图像就可以画在平面直角坐标系中（图中蓝色曲线）。这里为了方便并且直观地说明，假设 $f: \mathbf{R} \rightarrow \mathbf{R}$。由于 $y$ 被当成常数，$yx$ 就是正比例函数，其图像是过原点的倾斜直线（图中上方虚线）。

因此，共轭函数的定义可以用自然语言描述为：直线（超平面）$y^{\top}x$ 与 $f(x)$ 函数值的最大差值，并且该差值的取值与 $y^{\top}$ 的取值一一对应——任意改变直线的斜率（超平面的方向向量），都有唯一确定的一个值与之对应。

显然，$f^{*}$ 是凸函数，这是因为它是在求一系列值的逐点上确界。而且，无论 $f$ 是否为凸函数，$f^{*}$ 都是凸函数。如果 $f$ 是凸函数，那么就没必要限制 $x \in \operatorname{dom} f$ 了。这是因为根据之前关于扩展值延伸的定义，对于 $x \notin \operatorname{dom} f$，$y^{\top}x - f(x) = -\infty$。

### 举例

#### 仿射函数

$$
f(x) = ax + b
$$

当且仅当 $y=a$ 时，$yx - ax - b = -b$ 有界。因此，仿射函数的共轭函数为

$$
f^{*}(y) = -b, \quad \operatorname{dom} f^{*} = \{a\}
$$

#### 负对数函数

$$
f(x) = -\log x, \quad \operatorname{dom} f = \mathbf{R}_{++}
$$

当 $y > 0$ 时，函数 $xy + \log x$ 无上界；当 $y < 0$ 时，在 $x = - \dfrac{1}{y}$ 处取最大值。因此，负对数函数的共轭函数为

$$
f^{*}(y) = -\log (-y) - 1, \quad \operatorname{dom} f^{*} = -\mathbf{R}_{++}
$$

#### 指数函数

$$
f(x) = e^x
$$

当 $y < 0$ 时，函数 $xy - e^x$ 无界；当 $y > 0$ 时，函数 $xy - e^x$ 在 $x = \ln y$ 处取最大值；当 $y = 0$ 时，$f^{*}(y) = \sup \{-e^x\} = 0$。因此，指数函数的共轭函数为

$$
f^{*}(y) = y \log y - y, \quad \operatorname{dom} f^{*} = \mathbf{R}_{+}
$$

#### 负熵函数

$$
f(x) = x \log x, \quad \operatorname{dom} f = \mathbf{R}_{+}
$$

对所有 $y$，函数 $xy - x \log x$ 关于 $x$ 在 $\mathbf{R}_{+}$ 上有上界，且在 $x = e^{y-1}$ 处取最大值。因此，负熵函数的共轭函数为

$$
f^{*}(y) = e^{y-1}
$$

#### 反比例函数

$$
f(x) = \dfrac{1}{x}, \quad \operatorname{dom} f = \mathbf{R}_{++}
$$

当 $y > 0$ 时，$yx - 1/x$ 无上界；当 $y = 0$ 时，函数有上确界 0；当 $y < 0$ 时，在 $x = (-y)^{1/2}$ 处达到上确界。因此，反比例函数的共轭函数为

$$
f^{*}(y) = -2 (-y)^{1/2}, \quad \operatorname{dom} f^{*} = \mathbf{R}_{+}
$$

#### 严格凸的二次函数

$$
f(x)=\dfrac{1}{2} x^{\top} Q x, \quad Q \in \mathbf{S}_{++}^{n}
$$

对所有的 $y$，关于 $x$ 的函数 $y^{\top} x-\dfrac{1}{2} x^{\top} Q x$ 都有上界并在 $x = Q^{-1}y$ 处达到上确界。因此

$$
f^{*}(y)=\dfrac{1}{2} y^{\top} Q^{-1} y
$$

这是一个很好的性质，严格凸的二次函数求共轭函数只需要求其二次型矩阵的逆矩阵即可。

#### 对数-行列式

$$
f(X) = \log \det X^{-1}, \quad X \in \mathbf{S}_{++}^{n}
$$

其共轭函数定义为

$$
\begin{aligned}
f^{*}(Y) &= \sup _{X \succ 0} \{ \operatorname{tr}(Y X)+\log \det X \} \\
&= \log \det (-Y)^{-1} - n, \quad \operatorname{dom} f^{*} = -\mathbf{S}^{n}_{++}
\end{aligned}
$$

#### 指数和的对数函数

$$
f(x) = \log (\sum_{i=1}^{n} e^{x_i})
$$

其共轭函数的推到稍微有些复杂，这里直接给出结果。

$$
f^{*}(y)=\left\{\begin{array}{ll}
\sum_{i=1}^{n} y_{i} \log y_{i} & y \succeq 0 \wedge \mathbf{1}^{\top} y=1 \\
\infty & \text { otherwise }
\end{array}\right.
$$

也就是说，指数和的对数函数的共轭函数是概率单纯形内的负熵函数。

#### 范数

我们知道，$\mathbf{R}^n$ 上的范数 $\|\cdot\|$ 的对偶范数为 $\|\cdot\|_{*}$。$f(x) = \|x\|$ 的共轭函数为

$$
f^{*}(y) = \left \{\begin{array}{ll}
0 & \|y\|_{*} \leqslant 1 \\
\infty & \text { otherwise }
\end{array}\right.
$$

## 基本性质

### Fenchel 不等式

$$
f(x)+f^{*}(y) \geqslant x^{\top} y
$$

如果 $f$ 可微，上式亦可称为 Young 不等式。

令 $f(x) = \dfrac{1}{2} x^{\top}Qx$，其中 $Q \in \mathbf{S}_{++}$，利用 Fenchel 不等式，我们可以如下结论：

$$
x^{\top}y \leqslant \dfrac{1}{2} x^{\top}Qx + \dfrac{1}{2} y^{\top}Q^{-1}y
$$

### 共轭的共轭

我们学过的很多概念当中都包含“共轭”，例如共轭根式、共轭复数等。实际上“共轭”包含了“成对出现”这么一层意思。因此，共轭函数也有类似的性质。

$$
f^{**} = f
$$

上述等式要求函数 $f$ 是凸的而且闭的。

### Legendre 变换

可微函数 $f$ 的共轭函数亦称为函数 $f$ 的 Legendre 变换。

设函数 $f$ 是凸函数且可微，其定义域为 $\operatorname{dom} f = \mathbf{R}^n$，使 $y^{\top}x - f(x)$ 取最大的 $x^{*}$ 满足 $y = \nabla f(x^{*})$，并且若 $x^{*}$ 满足 $y = \nabla f(x^{*})$，$y^{\top}x - f(x)$ 在 $x^{*}$ 处取最大值（二者等价）。因此，我们可以得到

$$
f^{*}(y)=x^{* \top} \nabla f\left(x^{*}\right)-f\left(x^{*}\right)
$$

有了这个结论，给定任意 $y$，我们可以求解梯度方程 $y = \nabla f(z)$，从而得到 $y$ 处的共轭函数 $f^{*}(y)$。

我们也可以换一个角度理解。$\forall z \in \mathbf{R}^n$，令 $y = \nabla f(z)$，则

$$
f^{*}(y)=z^{\top} \nabla f\left(z\right)-f\left(z\right)
$$

### 伸缩变换和复合仿射变换

设 $a > 0$，$b \in \mathbf{R}$，则伸缩变换及其共轭函数为

$$
\begin{aligned}
    g(x) &= a f(x) + b \\
    g^{*}(y) &= a f^{*}(y / a)-b
\end{aligned}
$$

设 $A \in \mathbf{R}^{n \times n}$ 非奇异，$b \in \mathbf{R}^n$，则复合仿射变换及其共轭函数为

$$
\begin{aligned}
    g(x) &= f(Ax + b) \\
    g^{*}(y) &= f^{*}\left(A^{-\top} y\right)-b^{\top} A^{-\top} y
\end{aligned}
$$

其定义域为 $\operatorname{dom} g^{*} = A^{\top} \operatorname{dom} f^{*}$。

### 独立函数的和

设函数 $f_1$ 和 $f_2$ 都是凸函数，它们的独立函数

$$
f(u, v) = f_1(u) + f_2(v)
$$

的共轭函数为

$$
f^{*}(w, z) = f_1^{*}(w) + f_2^{*}(z)
$$

也就是说，独立凸函数的和的共轭函数是各个凸函数的共轭函数的和。
