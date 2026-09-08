---
title: "广义不等式的单调性和凸性"
weight: 270
---

# 广义不等式的单调性和凸性

现在我们考虑广义的单调性和凸性，采用广义不等式，而不是前面几节中讨论的 $R$ 上的顺序。

## 广义不等式的单调性

设 $K \subseteq \mathbf{R}^n$ 是一个正常锥，其相应的广义不等式为 $\\preceq_{K}$。定义函数 $f: \mathbf{R}^n \rightarrow \mathbf{R}$，若

$$
x \preceq_{K} y \Longrightarrow f(x) \leqslant f(y)
$$

则称函数 $f$ $K$- 非减。若

$$
x \preceq_{K} y \wedge x \ne y \Longrightarrow f(x) < f(y)
$$

则称函数 $f$ $K$- 增。类似地，可以定义 $K$- 非增和 $K$- 减函数。

### 举例

向量单调函数 $f: \mathbf{R}^n \rightarrow \mathbf{R}$ 在 $\mathbf{R}^n_+$ 上非减，当且仅当

$$
\forall x, y \in \operatorname{dom} f, \quad x_1 \leqslant y_1, \cdots, x_n \leqslant y_n \Longrightarrow f(x) \leqslant f(y)
$$

矩阵单调函数 $f: \mathbf{S}^n \rightarrow \mathbf{R}$ 如果在半正定锥内函数是单调的，那么函数 $f$ 矩阵单调。例如：

- 函数 $\operatorname{tr}(WX)$，其中 $W \in \mathbf{S}^n$。当 $W \succeq 0$ 时，函数是矩阵非减的；当 $W \succ 0$ 时，函数是矩阵增的。（同理可以推出矩阵非增和矩阵减。）
- 函数 $\operatorname{tr}(X^{-1})$ 在 $\mathbf{S}^n_{++}$ 上矩阵减。
- 函数 $\det X$ 在 $\mathbf{S}^n_{++}$ 上矩阵增，在 $\mathbf{S}^n_+$ 上矩阵非减。

### 单调性的梯度条件

考虑可微函数 $f$，其定义域为凸集，它是 $K$- 非减的，当且仅当对 $\forall x \in \operatorname{dom} f$ 有

$$
\nabla f(x) \succeq_{K^{*}} 0
$$

同理，对于严格的 $K$- 增情况，我们有

$$
\nabla f(x) \succ_{K^{*}} 0
$$

但反过来不一定正确。

## 广义不等式的凸性

设 $K \subseteq \mathbf{R}^m$ 为正常锥，相应的广义不等式为 $\preceq_{K}$。如果对于任意的 $x, y$，以及 $0 \leqslant \theta \leqslant 1$，有

$$
f(\theta x+(1-\theta) y) \preceq_{K} \theta f(x)+(1-\theta) f(y)
$$

则称函数 $f$ 是 $K$- 凸的。如果对于任意的 $x, y \wedge x \ne y$，以及 $0 < \theta < 1$，有

$$
f(\theta x+(1-\theta) y) \prec_{K} \theta f(x)+(1-\theta) f(y)
$$

则称函数 $f$ 是严格 $K$- 凸的。

### 举例

关于分量不等式的凸性和矩阵凸性，其结论与上述的类似。这里给出一些具有矩阵凸性函数的例子：

- 函数 $f(X) = XX^{\top}$，其中 $X \in \mathbf{R}^{n \times m}$，是矩阵凸的。
- 当 $1 \leqslant p \leqslant 2$ 或 $-1 \leqslant p \leqslant 0$ 时，函数 $X^p$ 在 $\mathbf{S}^n_{++}$ 上是矩阵凸的；当 $0 \leqslant p \leqslant 1$ 时，函数是矩阵凹的。

凸函数的很多结论都可以扩展到 $K$- 凸函数。

### $K$- 凸的对偶刻画

函数 $f$ 是 $K$- 凸的，当且仅当对任意的 $\omega \succeq_{K^{*}} 0$，（实值）函数 $\omega^{\top}f$ 是凸的。

函数 $f$ 是严格 $K$- 凸的，当且仅当对任意非零向量 $\omega \succeq_{K^{*}} 0$，函数 $\omega^{\top}f$ 是严格凸的。

### 可微的 $K$- 凸函数

可微函数 $f$ 是 $K$- 凸的，当且仅当其定义域是凸集，且对 $\forall x, y \in \operatorname{dom} f$ 有

$$
f(y) \succeq_{K} f(x)+D f(x)(y-x)
$$

类似地，可以得到严格 $K$- 凸的等价条件：对 $\forall x, y \in \operatorname{dom} f \wedge x \ne y$ 有

$$
f(y) \succ_{K} f(x)+D f(x)(y-x)
$$

### 复合定理

函数复合暴露凸性的很多结论都可以推广到 $K$- 凸的情形。详见[保凸运算](/knowledge-planet/convex-optimization/convex-functions/operations-that-preserve-convexity)一节。
