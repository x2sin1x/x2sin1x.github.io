---
title: "广义不等式问题"
date: 2026-09-29T00:00:00+08:00
weight: 1060
---
# 广义不等式问题

本节说明障碍方法如何扩展到广义不等式问题。考虑问题

$$
\begin{aligned}
    \mathrm{minimize} \quad & f_0(x) \\
    \mathrm{subject\ to} \quad & f_i(x) \preceq_{K_i} 0, \quad i = 1, \cdots, m \\
    & Ax = b
\end{aligned}
$$

其中 $f_0: \mathbf{R}^n \rightarrow \mathbf{R}$ 凸，$f_i: \mathbf{R}^n \rightarrow \mathbf{R}^{k_i}$ 是 $K_i$-凸的，$K_i \subseteq \mathbf{R}^{k_i}$ 是正常锥。与标量情形一样，假设 $f_i$ 二阶连续可微，$A \in \mathbf{R}^{p \times n}$ 且 $\operatorname{rank} A = p$，问题可解。

该问题的 KKT 条件为

$$
\begin{aligned}
    & Ax^{\star} = b \\
    & f_i(x^{\star}) \preceq_{K_i} 0, \quad i = 1, \cdots, m \\
    & \lambda_i^{\star} \succeq_{K_i^{*}} 0, \quad i = 1, \cdots, m \\
    & \nabla f_0(x^{\star}) + \sum_{i=1}^m Df_i(x^{\star})^{\top}\lambda_i^{\star} + A^{\top}\nu^{\star} = 0 \\
    & \lambda_i^{\star\top} f_i(x^{\star}) = 0, \quad i = 1, \cdots, m
\end{aligned}
$$

其中 $Df_i(x^{\star}) \in \mathbf{R}^{k_i \times n}$ 是 $f_i$ 在 $x^{\star}$ 处的导数。假设问题严格可行，则 KKT 条件是 $x^{\star}$ 最优性的充要条件。

该方法的展开过程与标量约束的情形完全平行：一旦发展出适用于一般正常锥的对数函数的推广，就可以定义问题的对数障碍函数；从那一点开始，后面的展开与标量情形本质相同。特别地，中心路径、障碍方法与复杂度分析都非常相似。

## 对数障碍与中心路径

### 正常锥的广义对数

我们首先定义正常锥 $K \subseteq \mathbf{R}^q$ 的对数 $\log x$ 的类似物。称 $\psi: \mathbf{R}^q \rightarrow \mathbf{R}$ 为 $K$ 的**广义对数**&#8203;（generalized logarithm），如果：

- $\psi$ 是凹的、闭的、二阶连续可微的，$\operatorname{dom} \psi = \operatorname{int} K$，且对 $y \in \operatorname{int} K$ 有 $\nabla^2\psi(y) \prec 0$；
- 存在常数 $\theta > 0$，使得对所有 $y \succ_K 0$ 和所有 $s > 0$，有 $\psi(sy) = \psi(y) + \theta\log s$。

换言之，$\psi$ 沿 $K$ 内的任何射线表现得像对数。我们称常数 $\theta$ 为 $\psi$ 的**次数**&#8203;（degree）（因为 $\exp\psi$ 是 $\theta$ 次齐次函数）。注意广义对数在相差一个加性常数的意义下不唯一：若 $\psi$ 是 $K$ 的广义对数，则 $\psi + a$（$a \in \mathbf{R}$）也是。普通对数当然是 $\mathbf{R}_+$ 的广义对数。

我们将使用任何广义对数都满足的两个性质：若 $y \succ_K 0$，则

$$
\nabla\psi(y) \succ_{K^{*}} 0
$$

（这意味着 $\psi$ 是 $K$-递增的），以及

$$
y^{\top}\nabla\psi(y) = \theta
$$

第二个性质对 $\psi(sy) = \psi(y) + \theta\log s$ 关于 $s$ 求导立即可得；第一个性质的证明见教材习题 11.15。

**例子：非负象限**&#8203;。$\psi(x) = \sum_{i=1}^n \log x_i$ 是 $\mathbf{R}^n_+$ 的广义对数，次数为 $n$。对 $x \succ 0$，$\nabla\psi(x) = (1/x_1, \cdots, 1/x_n)$，故 $\nabla\psi(x) \succ 0$，且 $x^{\top}\nabla\psi(x) = n$。

**例子：二阶锥**&#8203;。函数

$$
\psi(x) = \log\left(x_{n+1}^2 - \sum_{i=1}^n x_i^2\right)
$$

是二阶锥

$$
K = \left\{x \in \mathbf{R}^{n+1} \,\middle|\, \left(\sum_{i=1}^n x_i^2\right)^{1/2} \leqslant x_{n+1}\right\}
$$

的广义对数，次数为 2。$\psi$ 在 $\operatorname{int} K$ 内点 $x$ 处的梯度为

$$
\frac{\partial\psi(x)}{\partial x_j} = \frac{-2x_j}{x_{n+1}^2 - \sum_{i=1}^n x_i^2}\ (j = 1, \cdots, n), \quad \frac{\partial\psi(x)}{\partial x_{n+1}} = \frac{2x_{n+1}}{x_{n+1}^2 - \sum_{i=1}^n x_i^2}
$$

恒等式 $\nabla\psi(x) \in \operatorname{int} K^{*} = \operatorname{int} K$ 与 $x^{\top}\nabla\psi(x) = 2$ 容易验证。

**例子：半正定锥**&#8203;。$\psi(X) = \log\det X$ 是 $\mathbf{S}^p_+$ 的广义对数。次数为 $p$，因为 $\log\det(sX) = \log\det X + p\log s$（$s > 0$）。$\psi$ 在 $X \in \mathbf{S}^p_{++}$ 处的梯度为 $\nabla\psi(X) = X^{-1}$，因此 $\nabla\psi(X) = X^{-1} \succ 0$，且 $X$ 与 $\nabla\psi(X)$ 的内积为 $\operatorname{tr}(XX^{-1}) = p$。

### 广义不等式的对数障碍函数

回到广义不等式问题。设 $\psi_1, \cdots, \psi_m$ 分别是锥 $K_1, \cdots, K_m$ 的广义对数，次数为 $\theta_1, \cdots, \theta_m$。定义问题的**对数障碍函数**为

$$
\phi(x) = -\sum_{i=1}^m \psi_i(-f_i(x)), \quad \operatorname{dom}\phi = \{x \mid f_i(x) \prec_{K_i} 0,\ i = 1, \cdots, m\}
$$

$\phi$ 的凸性来自：$\psi_i$ 是 $K_i$-递增的，而 $f_i$ 是 $K_i$-凸的（见凸函数一章的复合规则）。

### 中心路径

下一步定义问题的中心路径。定义中心点 $x^{\star}(t)$（$t \geqslant 0$）为 $tf_0 + \phi$ 在约束 $Ax = b$ 下的极小点，即问题

$$
\mathrm{minimize} \quad tf_0(x) - \sum_{i=1}^m \psi_i(-f_i(x)) \quad \mathrm{subject\ to} \quad Ax = b
$$

的解（假设极小点存在且唯一）。中心点由最优性条件

$$
t\nabla f_0(x) + \nabla\phi(x) + A^{\top}\nu = t\nabla f_0(x) + \sum_{i=1}^m Df_i(x)^{\top}\nabla\psi_i(-f_i(x)) + A^{\top}\nu = 0
$$

刻画（对某个 $\nu \in \mathbf{R}^p$，$Df_i(x)$ 为 $f_i$ 在 $x$ 处的导数）。

### 中心路径上的对偶点

与标量情形一样，中心路径上的点给出原问题的对偶可行点。对 $i = 1, \cdots, m$，定义

$$
\lambda_i^{\star}(t) = \frac{1}{t}\nabla\psi_i(-f_i(x^{\star}(t)))
$$

并令 $\nu^{\star}(t) = \nu/t$（$\nu$ 为中心性条件中的对偶变量）。可以证明 $\lambda_1^{\star}(t), \cdots, \lambda_m^{\star}(t)$ 连同 $\nu^{\star}(t)$ 对原问题对偶可行。

首先，由广义对数的单调性性质，$\lambda_i^{\star}(t) \succ_{K_i^{*}} 0$。其次，由中心性条件可知 Lagrange 函数

$$
L(x, \lambda^{\star}(t), \nu^{\star}(t)) = f_0(x) + \sum_{i=1}^m \lambda_i^{\star}(t)^{\top}f_i(x) + \nu^{\star}(t)^{\top}(Ax - b)
$$

在 $x = x^{\star}(t)$ 处取极小，因此对偶函数值为

$$
g(\lambda^{\star}(t), \nu^{\star}(t)) = f_0(x^{\star}(t)) + \sum_{i=1}^m \lambda_i^{\star}(t)^{\top}f_i(x^{\star}(t)) + \nu^{\star}(t)^{\top}(Ax^{\star}(t) - b) = f_0(x^{\star}(t)) - \frac{1}{t}\sum_{i=1}^m \theta_i
$$

最后一行利用了 $y^{\top}\nabla\psi_i(y) = \theta_i$（$y \succ_{K_i} 0$），从而

$$
\lambda_i^{\star}(t)^{\top}f_i(x^{\star}(t)) = -\theta_i/t, \quad i = 1, \cdots, m
$$

于是若定义

$$
\theta = \sum_{i=1}^m \theta_i
$$

则原始可行点 $x^{\star}(t)$ 与对偶可行点 $(\lambda^{\star}(t), \nu^{\star}(t))$ 的对偶间隙为 $\theta/t$。这与标量情形一样，只是用 $\theta$（各锥广义对数的次数之和）代替了 $m$（不等式个数）。

**例子：二阶锥规划**&#8203;。考虑变量 $x \in \mathbf{R}^n$ 的 SOCP：

$$
\mathrm{minimize} \quad f^{\top}x \quad \mathrm{subject\ to} \quad \|A_ix + b_i\|_2 \leqslant c_i^{\top}x + d_i, \quad i = 1, \cdots, m
$$

（$A_i \in \mathbf{R}^{n_i \times n}$）。如上所述，$\psi(y) = \log(y_{p+1}^2 - \sum_{i=1}^p y_i^2)$ 是 $\mathbf{R}^{p+1}$ 中二阶锥的广义对数，次数为 2，因此相应的对数障碍函数为

$$
\phi(x) = -\sum_{i=1}^m \log\left((c_i^{\top}x + d_i)^2 - \|A_ix + b_i\|_2^2\right), \quad \operatorname{dom}\phi = \{x \mid \|A_ix + b_i\|_2 < c_i^{\top}x + d_i,\ i = 1, \cdots, m\}
$$

中心路径上的最优性条件为 $tf + \nabla\phi(x^{\star}(t)) = 0$，由此可得

$$
z_i^{\star}(t) = -\frac{2}{t\alpha_i}(A_ix^{\star}(t) + b_i), \quad w_i^{\star}(t) = \frac{2}{t\alpha_i}(c_i^{\top}x^{\star}(t) + d_i), \quad i = 1, \cdots, m
$$

（其中 $\alpha_i = (c_i^{\top}x^{\star}(t) + d_i)^2 - \|A_ix^{\star}(t) + b_i\|_2^2$）在对偶问题

$$
\mathrm{maximize} \quad -\sum_{i=1}^m (b_i^{\top}z_i + d_iw_i) \quad \mathrm{subject\ to} \quad \sum_{i=1}^m (A_i^{\top}z_i + c_iw_i) = f, \quad \|z_i\|_2 \leqslant w_i,\ i = 1, \cdots, m
$$

中严格可行。与 $x^{\star}(t)$ 和 $(z^{\star}(t), w^{\star}(t))$ 相关联的对偶间隙为

$$
\sum_{i=1}^m \left((A_ix^{\star}(t) + b_i)^{\top}z_i^{\star}(t) + (c_i^{\top}x^{\star}(t) + d_i)w_i^{\star}(t)\right) = \frac{2m}{t}
$$

与一般公式 $\theta/t$ 一致（$\theta_i = 2$）。

**例子：不等式形式的半定规划**&#8203;。考虑变量 $x \in \mathbf{R}^n$ 的 SDP：

$$
\mathrm{minimize} \quad c^{\top}x \quad \mathrm{subject\ to} \quad F(x) = x_1F_1 + \cdots + x_nF_n + G \preceq 0
$$

（$G, F_1, \cdots, F_n \in \mathbf{S}^p$）。其对偶问题为

$$
\mathrm{maximize} \quad \operatorname{tr}(GZ) \quad \mathrm{subject\ to} \quad \operatorname{tr}(F_iZ) + c_i = 0,\ i = 1, \cdots, n, \quad Z \succeq 0
$$

用 $\log\det X$ 作为半正定锥的广义对数，原始问题的对数障碍函数为 $\phi(x) = \log\det(-F(x)^{-1})$（$\operatorname{dom}\phi = \{x \mid F(x) \prec 0\}$）。对严格可行的 $x$，$\phi$ 的梯度为

$$
\frac{\partial\phi(x)}{\partial x_i} = \operatorname{tr}(-F(x)^{-1}F_i), \quad i = 1, \cdots, n
$$

由此得到刻画中心点的最优性条件：

$$
tc_i + \operatorname{tr}(-F(x^{\star}(t))^{-1}F_i) = 0, \quad i = 1, \cdots, n
$$

因此矩阵

$$
Z^{\star}(t) = \frac{1}{t}(-F(x^{\star}(t)))^{-1}
$$

严格对偶可行，与 $x^{\star}(t)$ 和 $Z^{\star}(t)$ 相关联的对偶间隙为 $p/t$。

## 障碍方法

我们已经看到中心路径的关键性质如何推广到广义不等式问题：

- 计算中心路径上的一点即在等式约束下极小化一个二阶可微的凸函数（可以用 Newton 方法完成）。
- 与中心点 $x^{\star}(t)$ 相关联的对偶可行点 $(\lambda^{\star}(t), \nu^{\star}(t))$ 的对偶间隙为 $\theta/t$。特别地，$x^{\star}(t)$ 至多 $\theta/t$-次优。

这意味着可以按完全相同的方式（与标量情形的障碍方法一样）求解广义不等式问题。从 $x^{\star}(t^{(0)})$ 出发计算对偶间隙为 $\epsilon$ 的中心点所需的外层迭代（中心点步）次数等于

$$
\left\lceil \frac{\log(\theta/(t^{(0)}\epsilon))}{\log\mu} \right\rceil
$$

外加一次初始中心点步。与标量情形结果的唯一差别是 $\theta$ 代替了 $m$。

**阶段 I 与可行性问题**&#8203;：阶段 I 方法可以直接推广到广义不等式问题。给定 $K_i$-正的向量 $e_i \succ_{K_i} 0$，为判定等式与广义不等式组

$$
f_1(x) \preceq_{K_1} 0,\ \cdots,\ f_L(x) \preceq_{K_m} 0, \quad Ax = b
$$

的可行性，求解问题

$$
\mathrm{minimize} \quad s \quad \mathrm{subject\ to} \quad f_i(x) \preceq_{K_i} se_i,\ i = 1, \cdots, m, \quad Ax = b
$$

变量为 $x$ 与 $s \in \mathbf{R}$。其最优值 $\bar{p}^{\star}$ 判定等式与广义不等式组的可行性，方式与普通不等式完全一样。当 $\bar{p}^{\star}$ 为正时，任何目标为正的对偶可行点都给出证明该等式与广义不等式组不可行的 alternative（备选解）。

## 例子

### 一个小型 SOCP

求解 SOCP

$$
\mathrm{minimize} \quad f^{\top}x \quad \mathrm{subject\ to} \quad \|A_ix + b_i\|_2 \leqslant c_i^{\top}x + d_i, \quad i = 1, \cdots, m
$$

其中 $x \in \mathbf{R}^{50}$，$m = 50$，$A_i \in \mathbf{R}^{5 \times 50}$。问题实例随机生成，严格原始与对偶可行，$p^{\star} = 1$。初始点在中心路径上，对偶间隙 100。

用障碍函数 $\phi(x) = -\sum_{i=1}^m \log\left((c_i^{\top}x + d_i)^2 - \|A_ix + b_i\|_2^2\right)$ 求解；中心点问题用 Newton 方法（参数与前面例子相同：$\alpha = 0.01$，$\beta = 0.5$，终止准则 $\lambda(x)^2/2 \leqslant 10^{-5}$）。对偶间隙随累计 Newton 步数的曲线与 LP、GP 的非常相似：每次中心点步所需 Newton 步数近似为常数，对偶间隙近似线性收敛。$\mu$ 至少为 10 左右时，$\mu$ 的取值对总步数影响不大；与 LP 和 GP 一样，$\mu$ 取 10 到 100 的合理值时总 Newton 步数约 30。

> **待配图**&#8203;：对应教材图 11.15 与图 11.16 —— 小 SOCP 的对偶间隙随累计 Newton 步数的曲线，以及总 Newton 步数随 $\mu$ 变化的折中曲线。

### 一个小型 SDP

下一个例子是 SDP

$$
\mathrm{minimize} \quad c^{\top}x \quad \mathrm{subject\ to} \quad \sum_{i=1}^n x_iF_i + G \preceq 0
$$

变量 $x \in \mathbf{R}^{100}$，$F_i \in \mathbf{S}^{100}$，$G \in \mathbf{S}^{100}$（实例随机生成，严格原始与对偶可行，$p^{\star} = 1$）。初始点在中心路径上，对偶间隙 100。应用带对数障碍函数

$$
\phi(x) = -\log\det\left(-\sum_{i=1}^n x_iF_i - G\right)
$$

的障碍方法。$\mu = 2, 50, 150$ 三种取值下的进展曲线与 LP、GP、SOCP 的非常相似；同样，只要 $\mu$ 不太小，参数 $\mu$ 对效率的影响就很小。

> **待配图**&#8203;：对应教材图 11.17 与图 11.18 —— 小 SDP 的对偶间隙曲线与 $\mu$ 折中曲线。

### 一族 SDP

考察障碍方法性能随问题维数的变化，考虑形如

$$
\mathrm{minimize} \quad \mathbf{1}^{\top}x \quad \mathrm{subject\ to} \quad A + \operatorname{diag}(x) \succeq 0
$$

的一族 SDP（变量 $x \in \mathbf{R}^n$，$A \in \mathbf{S}^n$ 随机生成并归一化为谱范数 1）。算法参数：$\mu = 20$，中心点步用 $\alpha = 0.01$、$\beta = 0.5$ 与终止准则 $\lambda(x)^2/2 \leqslant 10^{-5}$；初始点在中心路径上（$t^{(0)} = 1$，间隙 $n$）；终止于初始对偶间隙缩小 8000 倍（即三次外层迭代）。

$n = 50$、$n = 500$、$n = 1000$ 三个实例的曲线与 LP 的非常相似。对 20 个 $n$ 值（从 10 到 1000）各 100 个实例共 2000 个问题的统计表明：所需 Newton 步数随问题维数增大 100 倍只从约 20 增长到约 26——与 LP 的情形非常相像。

> **待配图**&#8203;：对应教材图 11.19 与图 11.20 —— 三个不同维数 SDP 的对偶间隙曲线，以及平均 Newton 步数随 $n$ 的变化（含标准差误差条）。

## 基于自和谐的复杂度分析

本节把障碍方法（对普通不等式）的复杂度分析推广到广义不等式问题。外层迭代次数已经知道是

$$
\left\lceil \frac{\log(\theta/t^{(0)}\epsilon)}{\log\mu} \right\rceil
$$

外加一次初始中心点步。剩下的是估计每个中心点步所需的 Newton 步数，这要用到自和谐函数的 Newton 方法复杂度理论。为简单起见，不计初始中心点的代价。

做与标量情形相同的假设：$tf_0 + \phi$ 对所有 $t \geqslant t^{(0)}$ 闭且自和谐，且问题的下水平集有界。

**例子：二阶锥规划**&#8203;。函数

$$
-\psi(x) = -\log\left(x_{p+1}^2 - \sum_{i=1}^p x_i^2\right)
$$

自和谐（见自和谐一章的例子），因此 SOCP 的对数障碍函数满足闭性与自和谐性假设。

**例子：半定规划**&#8203;。用 $\log\det X$ 作为半正定锥的广义对数，自和谐假设对一般的半定规划成立。例如，对标准形式 SDP

$$
\mathrm{minimize} \quad \operatorname{tr}(CX) \quad \mathrm{subject\ to} \quad \operatorname{tr}(A_iX) = b_i,\ i = 1, \cdots, p, \quad X \succeq 0
$$

（变量 $X \in \mathbf{S}^n$），函数 $t^{(0)}\operatorname{tr}(CX) - \log\det X$ 对任意 $t^{(0)} \geqslant 0$ 都自和谐（且闭）。

与标量情形完全一样，可以证明

$$
\mu tf_0(x^{\star}(t)) + \phi(x^{\star}(t)) - \mu tf_0(x^{\star}(\mu t)) - \phi(x^{\star}(\mu t)) \leqslant \theta(\mu - 1 - \log\mu)
$$

因此当自和谐与有界下水平集条件成立时，每个中心点步所需 Newton 步数不超过

$$
\frac{\theta(\mu - 1 - \log\mu)}{\gamma} + c
$$

与普通不等式的障碍方法完全一样。一旦建立了这个基本界，广义不等式问题的复杂度分析与普通不等式情形完全相同，唯一的例外是：$\theta$（各锥的广义对数次数之和）代替了不等式个数。

### 对偶锥的广义对数

我们将用共轭函数证明上述界。设 $\psi$ 是正常锥 $K$ 的广义对数，次数为 $\theta$。（凸）函数 $-\psi$ 的共轭为

$$
(-\psi)^{*}(v) = \sup_u (v^{\top}u + \psi(u))
$$

该函数是凸的，定义域为 $-K^{*} = \{v \mid v \prec_{K^{*}} 0\}$。定义

$$
\bar{\psi}(v) = -(-\psi)^{*}(-v) = \inf_u (v^{\top}u - \psi(u)), \quad \operatorname{dom}\bar{\psi} = \operatorname{int} K^{*}
$$

$\bar{\psi}$ 是凹的，而且实际上是**对偶锥** $K^{*}$ 的广义对数，次数同为 $\theta$（见教材习题 11.17）。我们称 $\bar{\psi}$ 为与广义对数 $\psi$ 相关联的**对偶对数**&#8203;（dual logarithm）。

由上式可以得到不等式

$$
\bar{\psi}(v) + \psi(u) \leqslant u^{\top}v
$$

它对任意 $u \succ_K 0$、$v \succ_{K^{*}} 0$ 成立（这是广义对数版本的 Fenchel 不等式）。由此出发，仿照标量情形的推导（利用各中心点的对偶可行性以及对偶间隙 $\theta/t$ 的表达式），即可建立基本界并完成复杂度分析。
