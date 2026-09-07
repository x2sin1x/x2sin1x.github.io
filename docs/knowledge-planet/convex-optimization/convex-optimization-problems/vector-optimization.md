---
title: "向量优化"
---

# 向量优化

## 广义和凸的向量优化问题

我们将广义的向量优化问题表示为

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(x) \text{（关于} K \text{）}\\
    \mathrm{subject\ to} \quad & f_i(x) \leqslant 0, \quad i=1,\cdots,m \\
    \quad & h_i(x) = 0, \quad i=1,\cdots,p
\end{aligned}
$$

这里 $x \in \mathbf{R}^n$ 为优化变量，$K \subseteq \mathbf{R}^q$ 为正常锥，$f_0: \mathbf{R}^n \rightarrow \mathbf{R}^q$ 为目标函数，$f_i: \mathbf{R}^n \rightarrow \mathbf{R}$ 为不等式约束函数，$h_i: \mathbf{R}^n \rightarrow \mathbf{R}$ 为等式约束函数。与标准的优化问题相比，唯一区别在于目标函数在 $\mathbf{R}^q$ 中取值，并且问题说明中含有用来比较目标值的正常锥 $K$。

如果上述函数中的目标函数 $f_0$ 是 $K$- 凸的，不等式约束函数 $f_1, \cdots, f_m$ 是凸的并且等式约束函数 $h_1, \cdots, h_p$ 是仿射的，那么就称该问题为凸向量优化问题。

## 最优解与值

下面我们考虑可行点的目标值的集合

$$
\begin{aligned}
    \mathcal{O} = \{f_{0}(x) \mid \exists x \in \mathcal{D}, f_i(x) & \leqslant 0, i=1, \cdots, m, \\
    h_i(x) &= 0, i=1, \cdots, p \} \subseteq \mathbf{R}^q
\end{aligned}
$$

它被称为可达目标值集合。如果这个集合有最小元，即有可行解 $x$ 使得对于所有可行的 $y$ 都有 $f_0(x) \preceq_K f_0(y)$，那么我们称 $x$ 是最优解，并且称 $f_0(x)$ 为该问题的最优值。（当向量优化问题有最优解时，该值唯一。）

点 $x^{\star}$ 是最优的，当且仅当它是可行的，并且

$$
\mathcal{O} \subseteq f_0(x^{\star}) + K
$$

### 几何意义

![](455f3f54b7dc5d4a7a0f58156d1779fb.png)

深色的部分表示目标值在 $\mathbf{R}^2$ 上的向量优化问题的可达目标值集合 $\mathcal{O}$，其中锥为 $K = \mathbf{R}^2_+$。在这个例子中，标有 $f_0(x^{\star})$ 的点为问题的最优值，$x^{\star}$ 为一个最优解。目标值 $f_0(x^{\star})$ 与其他任意可达值 $f_0(y)$ 均可比，并且比 $f_0(y)$ 更好或相等。（这里的“好”和“相等”表示在其下、其左。）

浅色的区域为 $f_0(x^{\star}) + K$，它是所有 $z \in \mathbf{R}^2$ 的集合，对应目标值比 $f_0(x^{\star})$ 差（或相等）。

## Pareto 最优解与值

现在，我们考虑可达目标值集合不含最小元的情况，因此问题不含有最优解和最优值。

如果 $f_0(x)$ 是可达集合 $\mathcal{O}$ 的极小元，我们称可行解 $x$ 为 Pareto 最优的（或有效的）。在这种情况下下，我们称 $f_0(x)$ 为向量优化问题的一个 Pareto 最优值。因此，点 $x$ 是 Pareto 最优的，如果它是可行的并且

$$
\forall y, \quad f_0(y) \preceq_K f_0(x) \Longrightarrow f_0(y) = f_0(x)
$$

换言之，任何比 $x$ 好或相等的可行解 $y$（即 $f_0(y) \preceq_K f_0(x)$）均与 $x$ 有完全相同的目标值。

### 几何意义

点 $x$ 是 Pareto 最优的，当且仅当它是可行的，并且

$$
(f_(0) - K) \cap \mathcal{O} = \{ f_0(x) \}
$$

集合 $f_(0) - K$ 可以解释为比 $f_0(x)$ 好或相等的值的集合。因此，上述条件说明了唯一比 $f_0(x)$ 好或相等的可达值就是 $f_0(x)$ 本身。如下图所示：

![](/missing-assets/77cce906e3ca.svg)

右上角的部分是目标值在 $\mathbf{R}^2$ 上的向量优化问题的可达目标值集合 $\mathcal{O}$，其中锥为 $K = \mathbf{R}^2_+$。这个问题不含有最优解或最优值，但确实有 Pareto 最优解集。在 $O$ 的左下边界上，黄色的点左边和绿色的点右边两部分为 Pareto 最优解集的对应值。$x^{\mathrm{po}}$ 是一个 Pareto 最优解，$f_0(x^{\mathrm{po}})$ 是一个 Pareto 最优值。

浅色阴影区域是 $f_0(x^{\mathrm{po}}) - K$，即所有对应值比 $f_0(x^{\mathrm{po}})$ 好（或相等）的 $z \in \mathbf{R}^2$。

一个向量优化问题可以有很多 Pareto 最优值（和解）。Pareto 最优值的集合记为 $\mathcal{P}$，它满足

$$
\mathcal{P} \subseteq \mathcal{O} \cap \operatorname{bd} \mathcal{O}
$$

## 标量化

标量化是寻找向量优化问题 Pareto 最优解的标准技术。选择任意 $\lambda \succ _{K^*} 0$，即任意在对偶广义不等式中为正的向量，考虑标量优化问题

$$
\begin{aligned}
    \mathrm{minimize} \quad & \lambda^{\top} f_0(x) \\
    \mathrm{subject\ to} \quad & f_i(x) \leqslant 0, \quad i=1,\cdots,m \\
    \quad & h_i(x) = 0, \quad i=1,\cdots,p      
\end{aligned}
$$

并令 $x$ 为最优解。那么，$x$ 对于向量优化问题是 Pareto 最优的。利用表量化，我们可以通过求解普通的标量优化问题，寻找任意向量优化问题的 Pareto 最优解。权向量 $\lambda$ 是一个自由参数，但必须满足 $\lambda \succ _{K^*} 0$。通过改变 $\lambda$，我们（有可能）得到向量优化问题的不同的 Pareto 最优解。如下图所示：

![](/missing-assets/766492c09f1d.svg)

图中的 $\mathcal{O}$ 为与锥 $K = \mathbf{R}^2_+$ 相应的向量优化函数的可达值集合。图中显示了三个 Pareto 最优值 $f_0(x_1), f_0(x_2), f_0(x_3)$。前两个值可以通过标量化得到（图中红点），而值 $f_0(x_3)$ 是最优的，但不能通过标量化找到（图中绿点）。

### 凸向量优化问题的标量化

与向量优化问题类似，凸向量优化问题也可以通过求解凸标量优化问题找到凸向量优化问题的 Pareto 最优解。

此外，凸向量优化问题还有一个逆命题成立，对于每一个 Pareto 最优解 $x^{\mathrm{po}}$，有非零 $\lambda \succeq _{K^*} 0$ 使得 $x^{\mathrm{po}}$ 是标量化问题的解。（即能够找到所有的 Pareto 最优解。）

## 多准则优化

当向量优化函数关于锥 $K = \mathbf{R}^q_+$ 时，它称为多准则或多目标优化问题。$f_0$ 的分量，即 $F_1,\cdots,F_q$，可以解释为 $q$ 个不同的标量目标，每一个都希望被极小化。凸多目标优化的定义类似。

因为多目标优化问题是向量优化问题，所以上述所有结论均适用。尽管如此，对于多目标优化问题的解释，我们还可以更加具体一些：

- 如果 $x$ 可行，则称 $F_i(x)$ 为依据第 $i$ 个目标的得分或价值。
- 如果 $x$ 和 $y$ 都可行：
  - $F_i(x) \leqslant F_i(y)$ 意味着在第 $i$ 个目标上 $x$ 至少与 $y$ 一样好。
  - 对于 $i=1,\cdots,q$ 都有 $F_i(x) \leqslant F_i(y)$，并且对于至少一个 $j$，有 $F_j(x) < F_j(y)$，则称 $x$ 比 $y$ 更优，或 $x$ 支配 $y$。

在多目标优化问题中，最优解 $x^{\star}$ 满足：对于可行的 $y$ 都有

$$
F_{i}(x^{\star}) \leqslant F_{i}(y), \quad i=1, \cdots, q
$$

换言之，$x^{\star}$ 同时是下述所有 $j=1,\cdots,q$ 标量优化问题的最优解

$$
\begin{aligned}
    \mathrm{minimize} \quad & F_j(x) \\
    \mathrm{subject\ to} \quad & f_i(x) \leqslant 0, \quad i=1,\cdots,m \\
    \quad & h_i(x) = 0, \quad i=1,\cdots,p
\end{aligned}
$$

当最优解存在时，我们称目标是非竞争的，因为不需要再目标间做出折中；每个目标函数都能达到忽略其他约束时的最小值。
