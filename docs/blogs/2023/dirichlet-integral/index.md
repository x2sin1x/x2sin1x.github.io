---
title: "Dirichlet 积分"
description: "求解 Dirichlet 积分的三种方法：构造含参变量函数、化为二重积分与利用留数定理。"
---

# Dirichlet 积分

【问题】计算广义积分

$$
\int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x
$$

------

## 解法一：构造含参变量函数

记

$$
I = \int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x
$$

构造函数

$$
f(x) = \int_{0}^{+\infty} e^{-xt} \dfrac{\sin{t}}{t} \mathrm{d}t \quad (x \geqslant 0)
$$

则

$$
\begin{aligned}
    f(0) &= I
\end{aligned}
$$

同时，利用定积分的基本性质，可以证明

$$
\begin{aligned}
    0 &\leqslant \left|\int_{0}^{+\infty} e^{-xt} \dfrac{\sin{t}}{t} \mathrm{d}t \right| \\
    &\leqslant \int_{0}^{+\infty} e^{-xt} \left|\dfrac{\sin{t}}{t}\right| \mathrm{d}t \\
    &\leqslant \int_{0}^{+\infty} e^{-xt} \mathrm{d}t \\
    &= \dfrac{1}{x}
\end{aligned}
$$

::: info
**复变函数积分的特殊性质**

复变函数积分的性质几乎与第二类曲线积分的性质一致。这里做一个补充和总结。

设曲线 $C$ 的长度为 $L$，$f(z)$ 是有界的，且

$$
|f(z)| \leqslant M
$$

那么有如下不等式成立

$$
\begin{aligned}
    \left|
        \int_{C} f(z) \mathrm{d}z
    \right| &\leqslant \int_{C} |f(z)| \mathrm{d}s \\
    &\leqslant \int_{C} M \mathrm{d}s \\
    &\leqslant ML
\end{aligned}
$$
:::

所以，根据极限的两边夹定理，当 $x \rightarrow +\infty$ 时

$$
\begin{aligned}
    & \lim_{x \rightarrow +\infty} \left| f(x) \right| = 0 \\
    \Longrightarrow & \lim_{x \rightarrow +\infty} f(x) = 0
\end{aligned}
$$

::: info
**极限的两边夹定理**

设数列 $\{a_n\}, \{b_n\}$ 收敛，且当 $n \to \infty$ 时

$$
\lim_{n \to +\infty} a_n = \lim_{n \to +\infty} b_n = k
$$

若存在自然数 $N$，使得当 $n > N$ 时，数列 $\{c_n\}$ 满足

$$
a_n \leqslant c_n \leqslant b_n
$$

则数列 $\{c_n\}$ 收敛，且当 $n \to \infty$ 时

$$
\lim_{n \to +\infty} c_n = k
$$
:::

对函数 $f(x)$ 求一阶导数

$$
\begin{aligned}
    f'(x) &= \int_{0}^{+\infty} \dfrac{\partial e^{-xt}}{\partial x} \cdot \dfrac{\sin{t}}{t} \mathrm{d}t \\
    &= -t \int_{0}^{+\infty} e^{-xt} \dfrac{\sin{t}}{t} \mathrm{d}t \\
    &= - \int_{0}^{+\infty} e^{-xt} \sin{t} \mathrm{d}t
\end{aligned}
$$

然后我们令

$$
\Phi = - \int_{0}^{+\infty} e^{-xt} \sin{t} \mathrm{d}t
$$

应用两次分部积分法

$$
\begin{aligned}
    \Phi &= - \int_{0}^{+\infty} e^{-xt} \sin{t} \mathrm{d}t \\
    &= \dfrac{1}{x} \int_{0}^{+\infty} \sin{t} \mathrm{d} e^{-xt} \\
    &= \dfrac{1}{x} \left(
        e^{-xt} \sin{t} \Big|_{0}^{+\infty}
        - \int_{0}^{+\infty} e^{-xt} \mathrm{d} \sin{t}
    \right) \\
    &= \dfrac{1}{x^{2}} \int_{0}^{+\infty} \cos{t} \mathrm{d} e^{-xt} \\
    &= \dfrac{1}{x^{2}} \left(e^{-xt} \cos{t} \Big|_{0}^{+\infty} - \int_{0}^{+\infty} e^{-xt} \mathrm{d} \cos{t} \right) \\
    &= - \dfrac{1}{x^2} \left( 1 + \Phi \right)
\end{aligned}
$$

解得

$$
\Phi = - \dfrac{1}{x^2 + 1}
$$

于是

$$
\begin{aligned}
    f'(x) &= - \int_{0}^{+\infty} e^{-xt} \sin{t} \mathrm{d}t \\
    &= - \dfrac{1}{x^2 + 1}
\end{aligned}
$$

等式两边同时积分，由牛顿-莱布尼兹公式得

$$
\begin{aligned}
    \int_{0}^{+\infty} f'(x) &= - \int_{0}^{+\infty} \dfrac{1}{x^2 + 1} \mathrm{d}x = - \arctan{x} \Big|_{0}^{+\infty} = -\dfrac{\pi}{2} \\
    &= \lim_{x \rightarrow +\infty} f(x) - f(0) = -I
\end{aligned}
$$

解得

$$
I = \dfrac{\pi}{2}
$$

## 解法二：化为二重积分

考虑如下广义积分

$$
\begin{aligned}
    \int_{0}^{+\infty} e^{-xy} \mathrm{d}y &= -\dfrac{1}{x} e^{-xy} \Big|_{0}^{+\infty} \\
    &= \dfrac{1}{x}
\end{aligned}
$$

将之代入原式得

$$
\begin{aligned}
    \int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x &= \int_{0}^{+\infty} \sin{x} \left( \int_{0}^{+\infty} e^{-xy} \mathrm{d}y \right) \mathrm{d}x \\
    &= \iint_{\mathbb{R}_{+}^{2}} \sin{x} e^{-xy} \mathrm{d}x \mathrm{d}y
\end{aligned} 
$$

化为二重积分后，交换积分次序，即先对 $x$ 积分

$$
\begin{aligned}
    \int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x &= \int_{0}^{+\infty} \left( \int_{0}^{+\infty} \sin{x} e^{-xy} \mathrm{d}x \right) \mathrm{d}y
\end{aligned} 
$$

由解法一的计算结果可知，上式可化简为

$$
\begin{aligned}
    \int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x &= \int_{0}^{+\infty} \dfrac{1}{y^2 + 1} \mathrm{d}y \\
    &= \arctan{x} \Big|_{0}^{+\infty} \\
    &= \dfrac{\pi}{2}
\end{aligned} 
$$

## 解法三：留数定理

::: info
**留数**

洛朗级数负幂项的系数

$$
\mathrm{Res}[f(z), a] = \dfrac{1}{2 \pi i} \oint_{z = a + \rho e^{i \theta}} f(z) \mathrm{d}z
$$
:::

::: info
**留数定理**

闭合回路积分等于所有孤立奇点的留数之和

$$
\oint_C f(z) \mathrm{d}z = 2 \pi i \sum_{i=1}^{n} \mathrm{Res}[f(z), z_i]
$$
:::

根据欧拉公式可知

$$
\begin{aligned}
    \sin{x} &= \dfrac{1}{2i}\left(e^{ix} - e^{-ix}\right)
\end{aligned}
$$

所以

$$
\begin{aligned}
    \int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x &= \dfrac{1}{2i} \int_{0}^{+\infty} \dfrac{e^{ix} - e^{-ix}}{x} \mathrm{d}x \\
    &= \dfrac{1}{2i} \int_{0}^{+\infty} \dfrac{e^{ix}}{x} \mathrm{d}x - \dfrac{1}{2i} \int_{0}^{-\infty} \dfrac{e^{-ix}}{-x} \mathrm{d}(-x) \\
    &= \dfrac{1}{2i} \int_{0}^{+\infty} \dfrac{e^{ix}}{x}  \mathrm{d}x + \dfrac{1}{2i} \int_{-\infty}^{0} \dfrac{e^{ix}}{x} \mathrm{d}x \\
    &= \dfrac{1}{2i} \int_{-\infty}^{+\infty} \dfrac{e^{ix}}{x} \mathrm{d}x
\end{aligned}
$$

构造复变函数

$$
f(z) = \dfrac{e^{iz}}{z}
$$

它有一个孤立奇点 $z_0=0$。由留数定理得

$$
\begin{aligned}
    \int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x &= \dfrac{1}{2i} \int_{-\infty}^{+\infty} \dfrac{e^{ix}}{x} \mathrm{d}x \\
    &= \dfrac{1}{2i} \cdot i \pi \mathrm{Res}[f(z), z_0] \\
    &= \dfrac{\pi}{2} \mathrm{Res}[f(z), z_0]
\end{aligned}
$$

注意到此处在运用留数定理时，被积函数是定义在实数域上的。实轴上的奇点具有对称性，积分路径（即实轴）的上半部分和下半部分对积分的贡献是相等的。因此，在应用留数定理时只需考虑上半复平面的情况即可。

$$
\begin{aligned}
    \int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x &= \dfrac{\pi}{2} \mathrm{Res}[f(z), z_0] \\
    &= \dfrac{\pi}{2} \cdot \dfrac{1}{2 \pi i} \oint_{|z|=\varepsilon} f(z) \mathrm{d}z \\
    &= \dfrac{1}{4i} \oint_{|z|=\varepsilon} \dfrac{e^{iz}}{z} \mathrm{d}z
\end{aligned}
$$

其中，$\varepsilon > 0$ 是一个任意小的常数。所以曲线积分的路径是一个半径为 $\varepsilon$ 的圆。

作变量变换 $z = iz$，相当于将复平面顺时针旋转了 90°。但是这并没有改变曲线积分的路径，即

$$
\begin{aligned}
    |z| &= \varepsilon \\
    \Longleftrightarrow |iz| &= \varepsilon
\end{aligned}
$$

下面来计算这个环路上的积分

$$
\begin{aligned}
    \oint_{|z|=\varepsilon} \dfrac{e^{iz}}{z} \mathrm{d}z &= \oint_{|z|=\varepsilon} \dfrac{e^{iz}}{iz} \mathrm{d}(iz) \\
    &= \oint_{|z|=\varepsilon} \dfrac{e^{z}}{z} \mathrm{d}z \\
    &= \oint_{|z|=\varepsilon} \dfrac{1}{z} \left( \sum_{n=0}^{\infty} \dfrac{z^n}{n!} \right) \mathrm{d}z \\
    &= \oint_{|z|=\varepsilon} \left( \dfrac{1}{z} + \sum_{n=1}^{\infty} \dfrac{z^{n-1}}{n!} \right) \mathrm{d}z \\
    &= \oint_{|z|=\varepsilon} \dfrac{1}{z} \mathrm{d}z + \oint_{|z|=\varepsilon} \sum_{n=1}^{\infty} \dfrac{z^{n-1}}{n!} \mathrm{d}z
\end{aligned}
$$

由柯西积分定理可知，如果环路所围成的区域是单连通区域，即没有孤立奇点，那么积分结果为零。这意味着

$$
\begin{aligned}
    \oint_{|z|=\varepsilon} \sum_{n=1}^{\infty} \dfrac{z^{n-1}}{n!} \mathrm{d}z &= 0
\end{aligned}
$$

那么，下面只需求解

$$
\begin{aligned}
    \oint_{|z|=\varepsilon} \dfrac{1}{z} \mathrm{d}z
\end{aligned}
$$

作变量变换 $z = e^{i \theta}$，得到

$$
\begin{aligned}
    \oint_{|z|=\varepsilon} \dfrac{1}{z} \mathrm{d}z &= \int_{0}^{2 \pi} \dfrac{1}{e^{i \theta}} \mathrm{d}(e^{i \theta}) \\
    &= i \int_{0}^{2 \pi} \mathrm{d}\theta \\
    &= 2 \pi i
\end{aligned}
$$

于是

$$
\begin{aligned}
    \int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x &= \dfrac{1}{4i} \oint_{|z|=\varepsilon} \dfrac{e^{iz}}{z} \mathrm{d}z \\
    &= \dfrac{1}{4i} \cdot 2 \pi i \\
    &= \dfrac{\pi}{2}
\end{aligned}
$$

## 解法四：柯西积分定理

由解法三可知

$$
\begin{aligned}
    \int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x &= \dfrac{1}{2i} \int_{-\infty}^{+\infty} \dfrac{e^{ix}}{x} \mathrm{d}x \\
    &= \dfrac{1}{2i} \left( \int_{-\infty}^{0} \dfrac{e^{ix}}{x} \mathrm{d}x + \int_{0}^{+\infty} \dfrac{e^{ix}}{x} \mathrm{d}x \right)
\end{aligned}
$$

定义复变函数

$$
\begin{aligned}
    f(z) = \dfrac{e^{iz}}{z}
\end{aligned}
$$

为了挖掉 $f(z)$ 的孤立奇点 $z_0=0$，定义 $f(z)$ 的积分路径 $C$ 为

$$
\begin{aligned}
    C_{R}: |z| &= R, \arg z \in [0, \pi] \\
    C_{r}: |z| &= r, \arg z \in [0, \pi] \\
    Im(z) &= 0, |z| \in [r, R]
\end{aligned}
$$

所构成的正向闭曲线，如下图所示

![](1b319f1fa1348412c7d42b1457abe38d.png)

由柯西积分定理得

$$
\begin{aligned}
    \oint_{C} \dfrac{e^{iz}}{z} \mathrm{d}z &=
    \int_{C_{R}} \dfrac{e^{iz}}{z} \mathrm{d}z +
    \int_{-R}^{-r} \dfrac{e^{ix}}{x} \mathrm{d}x +
    \int_{C_{r}} \dfrac{e^{iz}}{z} \mathrm{d}z +
    \int_{r}^{R} \dfrac{e^{ix}}{x} \mathrm{d}x \\
    &= 0
\end{aligned}
$$

那么

$$
\begin{aligned}
    \int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x &=
    \dfrac{1}{2i} \lim_{\substack{r \to 0 \\ R \to +\infty}} \left(
        \int_{-R}^{-r} \dfrac{e^{ix}}{x} \mathrm{d}x + 
        \int_{r}^{R} \dfrac{e^{ix}}{x} \mathrm{d}x
    \right) \\
    &= -\dfrac{1}{2i} \left(
        \lim_{R \to +\infty} \int_{C_{R}} \dfrac{e^{iz}}{z} \mathrm{d}z +
        \lim_{r \to 0} \int_{C_{r}} \dfrac{e^{iz}}{z} \mathrm{d}z
    \right)
\end{aligned} \tag{*}
$$

下面分别计算这两个曲线积分。首先计算外环路径上的积分

$$
\begin{aligned}
    \int_{C_{R}} \dfrac{e^{iz}}{z} \mathrm{d}z &\leqslant \int_{C_{R}} \dfrac{\left|e^{iz}\right|}{|z|} \mathrm{d}s \\
    &= \dfrac{1}{R} \int_{C_{R}} \left|e^{ix-y}\right| \mathrm{d}s \\
    &= \dfrac{1}{R} \int_{C_{R}} e^{-y} \mathrm{d}s \\
    &= \int_{0}^{\pi} e^{-R \sin{\theta}} \mathrm{d}\theta \\
    &= 2 \int_{0}^{\dfrac{\pi}{2}} e^{-R \sin{\theta}} \mathrm{d}\theta \\
    &\leqslant 2 \int_{0}^{\dfrac{\pi}{2}} e^{-\dfrac{2R}{\pi} \theta} \mathrm{d}\theta \\
    &= -\dfrac{\pi}{R} e^{-\dfrac{2R}{\pi} \theta} \Big|_0^{\dfrac{\pi}{2}} \\
    &= \dfrac{\pi}{R} \left(1 - e^{-R} \right)
\end{aligned}
$$

这里进行了两次放大。第一次是利用积分的基本性质（保号性的推论），第二次是将曲线简化为割线。具体来说，对于 $\theta \in [0, \dfrac{\pi}{2}]$

$$
\sin{\theta} \geqslant \dfrac{2}{\pi} \theta
$$

而根据被积函数的单调性，达到化曲为直、放大结果的目的。

所以当 $R \to +\infty$ 时

$$
\lim_{R \to +\infty} \int_{C_{R}} \dfrac{e^{iz}}{z} \mathrm{d}z = 0 \tag{1}
$$

下面继续计算内环路径上的积分。我们尝试将 $f(z)$ 展开成洛朗级数

$$
\begin{aligned}
    \int_{C_{r}} \dfrac{e^{iz}}{z} \mathrm{d}z &=
    \int_{C_{r}} \dfrac{1}{z} \sum_{n=0}^{\infty} \dfrac{i^{n}z^{n}}{n!} \mathrm{d}z \\
    &= \int_{C_{r}} \left( \dfrac{1}{z} + \sum_{n=1}^{\infty} \dfrac{i^{n}z^{n-1}}{n!} \right) \mathrm{d}z \\
    &= \int_{C_{r}} \dfrac{1}{z} \mathrm{d}z + \int_{C_{r}} \sum_{n=1}^{\infty} \dfrac{i^{n}z^{n-1}}{n!} \mathrm{d}z \\
    &= \int_{\pi}^{0} \dfrac{ire^{i \theta}}{re^{i \theta}} \mathrm{d}\theta + \int_{C_{r}} \sum_{n=1}^{\infty} \dfrac{i^{n}z^{n-1}}{n!} \mathrm{d}z \\
    &= \int_{C_{r}} \sum_{n=1}^{\infty} \dfrac{i^{n}z^{n-1}}{n!} \mathrm{d}z - i\pi
\end{aligned}
$$

由于被积函数中需要展开的部分只有指数函数，相当于是作了泰勒级数展开。

下面研究正幂项的积分，令

$$
\varphi(z) = \sum_{n=1}^{\infty} \dfrac{i^{n}z^{n-1}}{n!} \mathrm{d}z
$$

则

$$
\begin{aligned}
    \left| \int_{C_{r}} \varphi(z) \mathrm{d}z \right| &\leqslant \int_{C_{r}} \left| \varphi(z) \right| \mathrm{d}s \\
    &= \int_{C_{r}} \left| \sum_{n=1}^{\infty} \dfrac{i}{n} \cdot \dfrac{i^{n-1}z^{n-1}}{(n-1)!} \right| \mathrm{d}s \\
    &\leqslant \int_{C_{r}} \left| \sum_{n=1}^{\infty} \dfrac{i^{n-1}z^{n-1}}{(n-1)!}\right| \mathrm{d}s \\
    &= \int_{C_{r}} \left| e^{iz} \right| \mathrm{d}s \\
    &= r \int_{0}^{\pi} \mathrm{d}\theta \\
    &= \pi r
\end{aligned}
$$

这里一共进行了两次放大。第一次是利用积分的基本性质（保号性的推论），第二次是将求和的每一项都放大 $n$ 倍。

所以当 $r \to 0$ 时

$$
\begin{aligned}
    \lim_{r \to 0} \int_{C_{r}} \varphi(z) \mathrm{d}z &= 0
\end{aligned}
$$

于是

$$
\begin{aligned}
    \lim_{r \to 0} \int_{C_{r}} \dfrac{e^{iz}}{z} \mathrm{d}z
    &= \lim_{r \to 0} \int_{C_{r}} \sum_{n=1}^{\infty} \dfrac{i^{n}z^{n-1}}{n!} \mathrm{d}z - i\pi \\
    &= -i \pi
\end{aligned} \tag{2}
$$

将 (1), (2) 这两个积分的结果代入原式 (*)，得到

$$
\begin{aligned}
    \int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x
    &= -\dfrac{1}{2i} \left(
        \lim_{R \to +\infty} \int_{C_{R}} \dfrac{e^{iz}}{z} \mathrm{d}z
        + \lim_{r \to 0} \int_{C_{r}} \dfrac{e^{iz}}{z} \mathrm{d}z
    \right) \\
    &= \left(-\dfrac{1}{2i} \right) \cdot (-i \pi) \\
    &= \dfrac{\pi}{2}
\end{aligned}
$$

*附：闭曲线作图相关代码*

```python
import numpy as np
import matplotlib.pyplot as plt

# 定义参数
R = 10.0  # 外半径
r = 1.0  # 内半径

# 生成参数 t
theta = np.linspace(0, np.pi, 100)  # 0到2π之间均匀分布的100个点
t1 = np.linspace(-R, -r, 50)  # -R到-r之间均匀分布的50个点
t2 = np.linspace(r, R, 50)  # r到R之间均匀分布的50个点

# 生成复数 z
z1 = r * np.exp(1j * theta)  # 内圆上的点
z2 = R * np.exp(1j * theta)  # 外圆上的点
z3 = t1  # 右侧线上的点
z4 = t2  # 左侧线上的点

p = np

# 绘制图形
plt.figure(figsize=(6, 6))  # 设置图形大小
plt.plot(np.real(z1), np.imag(z1), 'b')  # 绘制内圆弧
plt.plot(np.real(z2), np.imag(z2), 'r')  # 绘制外圆弧
plt.plot(np.real(z3), np.imag(z3), 'g')  # 绘制右侧线
plt.plot(np.real(z4), np.imag(z4), 'g')  # 绘制左侧线
plt.plot(0, 0, 'ko')  # 绘制奇点

# 绘制曲线方向
plt.plot(0, 10, 'r<')
plt.plot(0, 1, 'b>')
plt.plot(-5, 0, 'g>')
plt.plot(5, 0, 'g>')

plt.xlabel('Real')  # x轴标签
plt.ylabel('Imaginary')  # y轴标签
plt.title('Closed Curve')  # 图形标题
plt.grid(True)  # 显示网格
plt.axis('equal')  # 设置坐标轴比例相等
plt.show()  # 显示图形
```

## 解法五：傅里叶变换

考虑如下定积分

$$
\begin{aligned}
    \dfrac{1}{2\pi} \int_{-1}^{1} \pi e^{iwt} \mathrm{d}w
    &= \dfrac{1}{2it} e^{iwt} \Big|_{-1}^{1} \\
    &= \dfrac{1}{2it} \left(
        e^{it} - e^{-it}
    \right) \\
    &= \dfrac{\sin{t}}{t} 
\end{aligned}
$$

这是一个傅里叶逆变换的表达式，它充分地说明了频域内的信号

$$
F(w) = \left\{ \begin{array}{ll}
    \pi, & -1 \leqslant w \leqslant 1 \\
    0, & \mathrm{else}
\end{array} \right.
$$

在时域内对应的信号就是被积函数 $f(t)$，即

$$
\begin{aligned}
    F(w)
    &= \mathscr{F}(f(t)) \\
    &= \int_{-\infty}^{+\infty} f(t) e^{-iwt} \mathrm{d}t \\
    &= \int_{-1}^{1} \dfrac{\sin{t}}{t} e^{-iwt} \mathrm{d}t \\
    &= \pi
\end{aligned}
$$

令 $w=0$，得到

$$
\begin{aligned}
    F(0)
    &= \int_{-\infty}^{+\infty} \dfrac{\sin{t}}{t} \mathrm{d}t \\
    &= \pi
\end{aligned}
$$

又因为 $f(x)$ 是偶函数，所以

$$
\begin{aligned}
    \int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x
    &= \dfrac{1}{2} \int_{-\infty}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x \\
    &= \dfrac{\pi}{2}
\end{aligned}
$$

## 解法六：拉普拉斯变换

构造一个以 $t$ 为变量的函数 $f(t)$

$$
\begin{aligned}
    f(t) = \int_{0}^{+\infty} \dfrac{\sin{tx}}{x} \mathrm{d}x \quad (t > 0)
\end{aligned}
$$

则原式的值即为 $f(1)$。对 $f(t)$ 作拉普拉斯变换得

$$
\begin{aligned}
    F(s) = \mathscr{L}(f(t))
    &= \int_{0}^{+\infty} \left(
        \int_{0}^{+\infty} \dfrac{\sin{tx}}{x} \mathrm{d}x
    \right) e^{-st} \mathrm{d}t \\
    &= \iint_{\mathbb{R}_{+}^{2}} \dfrac{\sin{tx}}{x} e^{-st} \mathrm{d}x \mathrm{d}t \\
    &= \int_{0}^{+\infty} \dfrac{1}{x} \left(
         \int_{0}^{+\infty} \sin{tx} e^{-st} \mathrm{d}t 
    \right) \mathrm{d}x
\end{aligned}
$$

交换二重积分的积分次序后，使用两次分部积分法计算内层积分

$$
\begin{aligned}
    I &= \int_{0}^{+\infty} \sin{tx} e^{-st} \mathrm{d}t \\
    &= -\dfrac{1}{s} \int_{0}^{+\infty} \sin{tx} \mathrm{d} e^{-st} \\
    &= -\dfrac{1}{s} \left(
        \sin{tx} e^{-st} \Big|_{0}^{+\infty} - x \int_{0}^{+\infty} \cos{tx} e^{-st} \mathrm{d}t
    \right) \\
    &= \dfrac{x}{s} \int_{0}^{+\infty} \cos{tx} e^{-st} \mathrm{d}t \\
    &= -\dfrac{x}{s^2} \int_{0}^{+\infty} \cos{tx}  \mathrm{d} e^{-st} \\
    &= -\dfrac{x}{s^2} \left(
        \cos{tx} e^{-st} \Big|_{0}^{+\infty} + x \int_{0}^{+\infty} \sin{tx} e^{-st} \mathrm{d}t
    \right) \\
    &= -\dfrac{x}{s^2} \left(xI - 1\right)
\end{aligned}
$$

解得

$$
\begin{aligned}
    I = \dfrac{x}{x^2 + s^2}
\end{aligned}
$$

代入原式得

$$
\begin{aligned}
    F(s) &= \int_{0}^{+\infty} \dfrac{1}{x} \cdot \dfrac{x}{x^2 + s^2} \mathrm{d}x \\
    &= \dfrac{1}{s} \int_{0}^{+\infty} \dfrac{1}{\left(\dfrac{x}{s}\right)^{2} + 1} \mathrm{d} \dfrac{x}{s} \\
    &= \dfrac{1}{s} \arctan(\dfrac{x}{s}) \Big|_{0}^{+\infty} \\
    &= \dfrac{\pi}{2s}
\end{aligned}
$$

于是，再将 $F(s)$ 作拉普拉斯逆变换得

$$
\begin{aligned}
    f(t) &= \mathscr{L}^{-1}(F(s)) \\
    &= \dfrac{\pi}{2} \mathscr{L}^{-1}(\dfrac{1}{s}) \\
    &= \dfrac{\pi}{2} \cdot \dfrac{1}{4\pi j} \int_{\beta-j\infty}^{\beta+j\infty} \dfrac{e^{-st}}{s} \mathrm{d}s
\end{aligned}
$$

查阅拉普拉斯变换对可知

$$
\begin{aligned}
    \dfrac{1}{s} \longleftrightarrow u(t)
\end{aligned}
$$

其中 $u(t)$ 是单位阶跃函数

$$
u(t) = \left\{\begin{array}{rr}
    0, & t < 0 \\
    1, & t > 0
\end{array}
\right.
$$

所以 $f(t)$ 的表达式为

$$
\begin{aligned}
    f(t) &= \dfrac{\pi}{2} \mathscr{L}^{-1}(\dfrac{1}{s}) \\
    &= \left\{ \begin{array}{rr}
        0, & t < 0 \\
        \dfrac{\pi}{2}, & t > 0
    \end{array} \right.
\end{aligned}
$$

于是

$$
\begin{aligned}
    \int_{0}^{+\infty} \dfrac{\sin{x}}{x} \mathrm{d}x
    = f(1) = \dfrac{\pi}{2}
\end{aligned}
$$

特别地，我们通过拉普拉斯逆变换的方法发现，对于任意的 $n > 0$，有

$$
\begin{aligned}
    \int_{0}^{+\infty} \dfrac{\sin{nx}}{x} \mathrm{d}x
    = \dfrac{\pi}{2}
\end{aligned}
$$
