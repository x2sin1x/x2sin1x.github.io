---
title: "自和谐"
date: 2026-09-29T00:00:00+08:00
weight: 860
---
# 自和谐

经典的 Newton 方法收敛分析（基于强凸性与 Hessian 的 Lipschitz 连续性）有两个主要缺点。第一个是实际层面的：所得的复杂度估计涉及三个常数 $m$、$M$ 和 $L$，而这些常数在实践中几乎总是未知的，因此迭代次数的上界几乎无法具体给出。当然，收敛分析本身在概念上仍然有用。第二个缺点是：尽管 Newton 方法本身是仿射不变的，经典分析却强烈依赖于坐标系——改变坐标会使 $m$、$M$ 和 $L$ 全部改变。因此，我们希望找到一种像 Newton 方法本身一样独立于仿射坐标变换的分析。

Nesterov 和 Nemirovski 发现了一个能够实现这一目标的简单而优雅的假设，并称之为**自和谐**&#8203;（self-concordance）。自和谐函数之所以重要，有以下几个原因：

- 其中包括许多在凸优化内点法中起重要作用的对数障碍函数。
- 对自和谐函数的 Newton 方法分析不依赖任何未知常数。
- 自和谐是仿射不变的性质：对自和谐函数做线性变换后得到的仍是自和谐函数，因此对 Newton 方法给出的复杂度估计独立于仿射坐标变换。

## 定义与例子

### $\mathbf{R}$ 上的自和谐函数

先考虑 $\mathbf{R}$ 上的函数。凸函数 $f: \mathbf{R} \rightarrow \mathbf{R}$ 称为**自和谐**的，如果

$$
|f'''(x)| \leqslant 2f''(x)^{3/2}
$$

对所有 $x \in \operatorname{dom} f$ 成立。线性函数与（凸）二次函数的三阶导数为零，显然是自和谐的。更多例子：

- **负对数**&#8203;：$f(x) = -\log x$ 是自和谐的。由 $f''(x) = 1/x^2$，$f'''(x) = -2/x^3$，可得 $|f'''(x)|/(2f''(x)^{3/2}) = 1$，定义不等式以等号成立。
- **负熵加负对数**&#8203;：$f(x) = x\log x - \log x$ 是自和谐的。由 $f''(x) = (x + 1)/x^2$，$f'''(x) = -(x + 2)/x^3$，可得 $|f'''(x)|/(2f''(x)^{3/2}) = (x + 2)/(2(x + 1)^{3/2})$，该函数在 $\mathbf{R}_+$ 上的最大值为 1（在 $x = 0$ 处取得）。单独的负熵函数**不是**自和谐的。

关于定义中的常数 2，需要作一点说明：这个常数只是为方便而选的，目的是简化后面的公式；任何其他正常数都可以。若凸函数满足 $|f'''(x)| \leqslant kf''(x)^{3/2}$（$k$ 为某正常数），则 $\tilde{f}(x) = (k^2/4)f(x)$ 满足标准自和谐不等式。因此重要的是：函数的三阶导数被其二阶导数的 3/2 次幂的某个倍数控制，通过适当地缩放总可以把倍数化为 2。

另一个简单计算揭示了自和谐为何重要——它是仿射不变的：定义 $\tilde{f}(y) = f(ay + b)$（$a \neq 0$），代入 $\tilde{f}''(y) = a^2f''(x)$ 与 $\tilde{f}'''(y) = a^3f'''(x)$（$x = ay + b$），即可验证 $\tilde{f}$ 自和谐当且仅当 $f$ 自和谐。粗略地说，自和谐条件是一种以仿射坐标变换不变的方式限制三阶导数的途径。

### $\mathbf{R}^n$ 上的自和谐函数

对 $n > 1$ 的情形，若函数 $f: \mathbf{R}^n \rightarrow \mathbf{R}$ 沿定义域中的每条直线都是自和谐的，即对所有 $x \in \operatorname{dom} f$ 和所有 $v$，函数 $\tilde{f}(t) = f(x + tv)$ 关于 $t$ 自和谐，则称 $f$ 是自和谐的。

## 自和谐函数的运算

**缩放与求和**&#8203;：若 $f$ 自和谐且 $a \geqslant 1$，则 $af$ 自和谐。若 $f_1, f_2$ 自和谐，则 $f_1 + f_2$ 自和谐（证明只需考虑一维情形，利用 $|f_1''' + f_2'''| \leqslant |f_1'''| + |f_2'''| \leqslant 2(f_1''^{3/2} + f_2''^{3/2}) \leqslant 2(f_1'' + f_2'')^{3/2}$）。

**与仿射函数复合**&#8203;：若 $f: \mathbf{R}^n \rightarrow \mathbf{R}$ 自和谐，$A \in \mathbf{R}^{n \times m}$，$b \in \mathbf{R}^n$，则 $f(Ax + b)$ 自和谐。

- **例：线性不等式的对数障碍**&#8203;。$f(x) = -\sum_{i=1}^m \log(b_i - a_i^{\top}x)$（$\operatorname{dom} f = \{x \mid a_i^{\top}x < b_i\}$）自和谐：每一项都是 $-\log y$ 与仿射函数 $y = b_i - a_i^{\top}x$ 的复合，因此自和谐，其和也自和谐。
- **例：对数行列式**&#8203;。$f(X) = -\log\det X$ 在 $\mathbf{S}^n_{++}$ 上自和谐。沿方向 $V$ 考虑 $\tilde{f}(t) = -\log\det(X + tV) = -\log\det X - \sum_{i=1}^n \log(1 + t\lambda_i)$（$\lambda_i$ 为 $X^{-1/2}VX^{-1/2}$ 的特征值），每一项都是 $t$ 的自和谐函数，故其和自和谐。
- **例：凹二次函数的对数**&#8203;。$f(x) = -\log(x^{\top}Px + q^{\top}x + r)$（$P \in -\mathbf{S}^n_+$）在其定义域上自和谐（一维情形可分解为 $-\log(-p) - \log(x - a) - \log(b - x)$）。

**与对数复合**&#8203;：设 $g: \mathbf{R} \rightarrow \mathbf{R}$ 是凸函数，$\operatorname{dom} g = \mathbf{R}_{++}$，且满足

$$
|g'''(x)| \leqslant \frac{3g''(x)}{x}
$$

则 $f(x) = -\log(-g(x)) - \log x$ 在 $\{x \mid x > 0,\ g(x) < 0\}$ 上自和谐。该条件是齐次的且在加法下保持，所有（凸）二次函数都满足。满足条件的 $g$ 的例子有：$-x^p$（$0 < p \leqslant 1$）、$-\log x$、$x\log x$、$x^p$（$-1 \leqslant p \leqslant 0$）、$(ax + b)^2/x$ 等。由此可以证明如下函数的自和谐性：$-\log(y^2 - x^{\top}x)$（在 $\|x\|_2 < y$ 上）、$-2\log y - \log(y^{2/p} - x^2)$（$p \geqslant 1$）、$-\log y - \log(\log y - x)$（在 $e^x < y$ 上）等。

## 自和谐函数的性质

在经典分析中，我们用梯度范数来估计次优性；对严格凸的自和谐函数，可以用 Newton 减量

$$
\lambda(x) = \left(\nabla f(x)^{\top}\nabla^2 f(x)^{-1}\nabla f(x)\right)^{1/2}
$$

得到类似的估计（可以证明严格凸自和谐函数的 Hessian 处处正定）。与基于梯度范数的界不同，基于 Newton 减量的界不受仿射坐标变换影响。为后面引用，注意到 Newton 减量也可以表示为

$$
\lambda(x) = \sup_{v \neq 0} \frac{-v^{\top}\nabla f(x)}{(v^{\top}\nabla^2 f(x)v)^{1/2}}
$$

即对任意非零 $v$ 有

$$
\frac{-v^{\top}\nabla f(x)}{(v^{\top}\nabla^2 f(x)v)^{1/2}} \leqslant \lambda(x)
$$

等号在 $v = \Delta x_{\mathrm{nt}}$ 时成立。

### 二阶导数的上下界

设 $f: \mathbf{R} \rightarrow \mathbf{R}$ 严格凸且自和谐。自和谐不等式可以写成

$$
\left|\frac{d}{dt}f''(t)^{-1/2}\right| \leqslant 1
$$

从 0 到 $t$ 积分（设 $t \geqslant 0$ 且区间含于定义域），得 $-t \leqslant f''(t)^{-1/2} - f''(0)^{-1/2} \leqslant t$，从而得到 $f''(t)$ 的下界与上界：

$$
\frac{f''(0)}{(1 + tf''(0)^{1/2})^2} \leqslant f''(t) \leqslant \frac{f''(0)}{(1 - tf''(0)^{1/2})^2}
$$

下界对所有非负的 $t \in \operatorname{dom} f$ 都有效；上界在 $t \in \operatorname{dom} f$ 且 $0 \leqslant t < f''(0)^{-1/2}$ 时有效。

### 次优性的界

设 $f: \mathbf{R}^n \rightarrow \mathbf{R}$ 严格凸自和谐，$v$ 为任一下降方向（即 $v^{\top}\nabla f(x) < 0$，不必是 Newton 方向），定义 $\tilde{f}(t) = f(x + tv)$，则 $\tilde{f}$ 自和谐。对上述二阶导数下界积分两次，得到

$$
\tilde{f}(t) \geqslant \tilde{f}(0) + t\tilde{f}'(0) + t\tilde{f}''(0)^{1/2} - \log(1 + t\tilde{f}''(0)^{1/2})
$$

右端在 $\bar{t} = -\tilde{f}'(0)/(\tilde{f}''(0) + \tilde{f}''(0)^{1/2}\tilde{f}'(0))$ 处取最小，计算可得

$$
\inf_{t \geqslant 0} \tilde{f}(t) \geqslant \tilde{f}(0) - \tilde{f}'(0)\tilde{f}''(0)^{-1/2} + \log(1 + \tilde{f}'(0)\tilde{f}''(0)^{-1/2})
$$

结合 Newton 减量的变分表达式（$\lambda(x) \geqslant -\tilde{f}'(0)\tilde{f}''(0)^{-1/2}$，$v = \Delta x_{\mathrm{nt}}$ 时取等号），并利用 $u + \log(1 - u)$ 关于 $u$ 单调递减，得到对任意下降方向 $v$ 都成立的

$$
\inf_{t \geqslant 0}\tilde{f}(t) \geqslant \tilde{f}(0) + \lambda(x) + \log(1 - \lambda(x))
$$

因此当 $\lambda(x) < 1$ 时

$$
p^{\star} \geqslant f(x) + \lambda(x) + \log(1 - \lambda(x))
$$

函数 $-(\lambda + \log(1 - \lambda))$ 在 $\lambda$ 很小时近似为 $\lambda^2/2$，且在 $0 \leqslant \lambda \leqslant 0.68$ 上不超过 $\lambda^2$。于是有次优性界

$$
p^{\star} \geqslant f(x) - \lambda(x)^2 \quad (\lambda(x) \leqslant 0.68)
$$

回忆 $\lambda(x)^2/2$ 是基于二次模型的 $f(x) - p^{\star}$ 估计；上式说明对自和谐函数，把该估计加倍即可得到一个可证明的界。特别地，对自和谐函数可以使用终止准则

$$
\lambda(x)^2 \leqslant \epsilon \quad (\epsilon < 0.68^2)
$$

并保证退出时 $f(x) - p^{\star} \leqslant \epsilon$。

> **待配图**&#8203;：对应教材图 9.24 —— 实线为函数 $-(\lambda + \log(1 - \lambda))$（$\lambda$ 很小时近似 $\lambda^2/2$），虚线为 $\lambda^2$（在 $0 \leqslant \lambda \leqslant 0.68$ 上是上界）。

## 自和谐函数的 Newton 方法分析

现在对应用于严格凸自和谐函数的、带回溯直线搜索的 Newton 方法进行分析。假设已知初始点 $x^{(0)}$，下水平集 $S = \{x \mid f(x) \leqslant f(x^{(0)})\}$ 是闭集，且 $f$ 下有界（这意味着 $f$ 存在极小点 $x^{\star}$）。该分析与经典分析非常相似，只是以自和谐性代替强凸性和 Hessian 的 Lipschitz 条件，并以 Newton 减量代替梯度范数。可以证明存在只依赖于直线搜索参数 $\alpha$ 和 $\beta$ 的数 $\eta$ 和 $\gamma > 0$（$0 < \eta \leqslant 1/4$），使得：

- 若 $\lambda(x^{(k)}) > \eta$，则 $f(x^{(k+1)}) - f(x^{(k)}) \leqslant -\gamma$；
- 若 $\lambda(x^{(k)}) \leqslant \eta$，则回溯直线搜索选择 $t = 1$，且

$$
2\lambda(x^{(k+1)}) \leqslant \left(2\lambda(x^{(k)})\right)^2
$$

与经典分析一样，第二条件可以递归应用：对 $l \geqslant k$，有 $\lambda(x^{(l)}) \leqslant (1/2)^{2^{(l-k)}/2}$ 型的界，进而

$$
f(x^{(l)}) - p^{\star} \leqslant \lambda(x^{(l)})^2 \leqslant \left(\frac{1}{2}\right)^{2(l-k)+1}
$$

因此当 $l - k \geqslant \log_2\log_2(1/\epsilon)$ 时 $f(x^{(l)}) - p^{\star} \leqslant \epsilon$。第一条不等式意味着阻尼阶段至多需要 $(f(x^{(0)}) - p^{\star})/\gamma$ 步。所以，从 $x^{(0)}$ 出发达到精度 $f(x) - p^{\star} \leqslant \epsilon$ 所需的总迭代次数由下式界定：

$$
\frac{f(x^{(0)}) - p^{\star}}{\gamma} + \log_2 \log_2(1/\epsilon)
$$

这正是经典分析中相应界的自和谐版本。

### 阻尼 Newton 阶段

令 $\tilde{f}(t) = f(x + t\Delta x_{\mathrm{nt}})$，则 $\tilde{f}'(0) = -\lambda(x)^2$，$\tilde{f}''(0) = \lambda(x)^2$。对二阶导数上界积分两次可得（对 $0 \leqslant t < 1/\lambda(x)$ 有效）

$$
\tilde{f}(t) \leqslant \tilde{f}(0) - t\lambda(x)^2 - t\lambda(x) - \log(1 - t\lambda(x))
$$

利用它可以证明回溯直线搜索得到的步长总满足 $t \geqslant \beta/(1 + \lambda(x))$：点 $\hat{t} = 1/(1 + \lambda(x))$ 满足直线搜索终止条件（利用对 $x \geqslant 0$ 成立的不等式 $-x + \log(1 + x) + \frac{x^2}{2(1+x)} \leqslant 0$）。于是

$$
\tilde{f}(t) - \tilde{f}(0) \leqslant -\alpha\beta\frac{\lambda(x)^2}{1 + \lambda(x)}
$$

即第一条性质成立，且 $\gamma = \alpha\beta\eta^2/(1 + \eta)$。

### 二次收敛阶段

可以取 $\eta = (1 - 2\alpha)/4$（因 $0 < \alpha < 1/2$，它满足 $0 < \eta < 1/4$）：若 $\lambda(x^{(k)}) \leqslant (1 - 2\alpha)/4$，则回溯直线搜索接受单位步长，且第二条性质成立。事实上，上述 $\tilde{f}$ 的上界表明：单位步长 $t = 1$ 在 $\lambda(x) < 1$ 时产生定义域内的点；而当 $\lambda(x) \leqslant (1 - 2\alpha)/2$ 时 $\tilde{f}(1) \leqslant \tilde{f}(0) - \alpha\lambda(x)^2$，满足充分下降条件。至于 $\lambda$ 的递减，有如下事实（见教材习题 9.18）：若 $\lambda(x) < 1$ 且 $x^{+} = x - \nabla^2 f(x)^{-1}\nabla f(x)$，则

$$
\lambda(x^{+}) \leqslant \frac{\lambda(x)^2}{(1 - \lambda(x))^2}
$$

特别地，当 $\lambda(x) \leqslant 1/4$ 时 $\lambda(x^{+}) \leqslant 2\lambda(x)^2$，这就证明了 $\lambda(x^{(k)}) \leqslant \eta$ 时第二条性质成立。

### 最终复杂度界

综合起来，总迭代次数的界为

$$
\frac{20 - 8\alpha}{\alpha\beta(1 - 2\alpha)^2}\left(f(x^{(0)}) - p^{\star}\right) + \log_2 \log_2(1/\epsilon)
$$

这个表达式只依赖于直线搜索参数 $\alpha$、$\beta$ 和最终精度 $\epsilon$；其中与 $\epsilon$ 有关的一项可以放心地用常数 6 代替。对典型的 $\alpha$、$\beta$，缩放 $f(x^{(0)}) - p^{\star}$ 的常数是几百的量级：例如 $\alpha = 0.1$、$\beta = 0.8$ 时该常数为 375，取 $\epsilon = 10^{-10}$ 得到界

$$
375(f(x^{(0)}) - p^{\star}) + 6
$$

这个界相当保守，但确实刻画了 Newton 步数的（最坏情形）一般形式。更精细的分析（如 Nesterov 和 Nemirovski 的原始分析）给出类似形式的界，但缩放常数小得多。

## 讨论与数值例子

### 一族自和谐函数

把上界与实际迭代次数进行比较是有意义的。考虑问题族 $f(x) = -\sum_{i=1}^m \log(b_i - a_i^{\top}x)$（随机生成数据，剔除下无界的实例）。对每个实例先计算 $x^{\star}$，再沿随机方向取初始点使 $f(x^{(0)}) - p^{\star}$ 为 0 到 35 之间的给定值，然后用参数 $\alpha = 0.1$、$\beta = 0.8$、容许误差 $\epsilon = 10^{-10}$ 的 Newton 方法极小化。

150 个实例的结果显示：实际所需 Newton 步数远小于界 $375(f(x^{(0)}) - p^{\star}) + 6$。结果暗示存在形如相同、但常数小得多（约 1.5）的界。事实上，表达式

$$
f(x^{(0)}) - p^{\star} + 6
$$

作为所需 Newton 步数的粗略预测效果并不差（尽管它显然不是唯一因素）。还应指出，所研究的问题族不仅是自和谐的，而且是**极小自和谐**&#8203;（minimally self-concordant）的——即对 $\alpha < 1$，$\alpha f$ 不再自和谐——因此该界无法通过缩放 $f$ 来改进。（$f(x) = -20\log x$ 是一个自和谐但非极小自和谐的函数的例子，因为 $(1/20)f$ 也自和谐。）

> **待配图**&#8203;：对应教材图 9.25 —— 极小化自和谐函数所需的 Newton 迭代次数对 $f(x^{(0)}) - p^{\star}$ 的散点图（三个不同规模的问题族各 50 个实例）。

### 自和谐性的实际意义

我们已经看到，Newton 方法对强凸目标函数一般表现得非常好；经典分析可以给出复杂度界，但该界依赖几个几乎总是未知的常数。

对自和谐函数可以说得更多：我们有一个完全显式的、不依赖任何未知常数的复杂度界。实证研究表明该界可以大幅收紧，但其一般形式——一个较小的常数加上 $f(x^{(0)}) - p^{\star}$ 的某个倍数——至少粗略地预测了极小化一个（近似）极小自和谐函数所需的 Newton 步数。

自和谐函数在实践中是否比非自和谐函数更容易用 Newton 方法极小化，目前还不清楚（甚至不清楚如何把这句话表述得严谨）。目前可以说的是：自和谐函数是这样一类函数，对它们我们关于 Newton 方法复杂度所能说的，比非自和谐函数的情形多得多。
