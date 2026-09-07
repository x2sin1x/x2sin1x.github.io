---
title: "函数"
---

# 函数

## 连续

如果对 $\forall \epsilon > 0$，$\exists \delta$ 满足

$$
\begin{aligned}
y \in \operatorname{dom} f, \quad\|y-x\| _{2} \leqslant \delta \Longrightarrow\|f(y)-f(x)\| _{2} \leqslant \epsilon
\end{aligned}
$$

则称函数 $f: \mathbf{R}^n \rightarrow \mathbf{R}^m$ 在 $x \in \operatorname{dom} f$ 处**连续**。

::: info
$\operatorname{dom} f$ 表示函数 $f: \mathbf{R}^n \rightarrow \mathbf{R}^m$ 的**前域**。根据离散数学的相关知识，$f$ 是笛卡尔积 $\mathbf{R}^n \times \mathbf{R}^m$ 的子集，其前域（定义域）是 $\mathbf{R}^n$ 的子集。
:::

可以用极限来描述函数的连续性：

$$
\begin{aligned}
\lim _{i \rightarrow \infty} f\left(x _{i}\right)=f\left(\lim _{i \rightarrow \infty} x _{i}\right)
\end{aligned}
$$

函数连续是指它在定义域上每个点都连续。

## 闭函数

对于函数 $f: \mathbf{R}^n \rightarrow \mathbf{R}$，如果对 $\forall \alpha \in \mathbf{R}$，集合 $\{x \in \operatorname{dom} f \mid f(x) \leqslant \alpha\}$ 是闭集，则称函数 $f$ 是**闭函数**。

对于连续函数 $f: \mathbf{R}^n \rightarrow \mathbf{R}$，如果 $\operatorname{dom} f$ 是闭集，那么 $f$ 是闭函数；如果 $\operatorname{dom} f$ 是开集，那么 $f$ 是闭函数的充要条件是 $f$ 将沿着任何收敛于 $\operatorname{dom} f$ 的边界点的序列趋于 $\infty$。

来看 $\mathbf{R} \rightarrow \mathbf{R}$ 上的一些简单例子：

$$
f = x \log{x} \quad \operatorname{dom}f = (0, +\infty)
$$

而

$$
\begin{aligned}
\lim _{x \rightarrow 0^{+}} x \log{x} = 0 \neq \infty
\end{aligned}
$$

因此不是闭函数。

再比如

$$
f = \log{x} \quad \operatorname{dom}f = (0, +\infty)
$$

而

$$
\begin{aligned}
\lim _{x \rightarrow 0^{+}} \log{x} = -\infty
\end{aligned}
$$

且

$$
\begin{aligned}
\lim _{x \rightarrow +\infty} \log{x} = +\infty
\end{aligned}
$$

因此是闭函数。
