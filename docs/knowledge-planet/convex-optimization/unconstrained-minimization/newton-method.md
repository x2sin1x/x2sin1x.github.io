---
title: "Newton 方法"
date: 2026-09-29T00:00:00+08:00
weight: 850
---
# Newton 方法

## Newton 步

设 $x \in \operatorname{dom} f$，向量

$$
\Delta x_{\mathrm{nt}} = -\nabla^2 f(x)^{-1}\nabla f(x)
$$

称为 $f$ 在 $x$ 处的 **Newton 步**&#8203;（Newton step）。由于 $\nabla^2 f(x)$ 正定，除非 $\nabla f(x) = 0$，总有

$$
\nabla f(x)^{\top}\Delta x_{\mathrm{nt}} = -\nabla f(x)^{\top}\nabla^2 f(x)^{-1}\nabla f(x) < 0
$$

因此 Newton 步是下降方向（除非 $x$ 已最优）。Newton 步可以从多个角度解释和引出。

### 二阶近似的极小点

$f$ 在 $x$ 处的二阶 Taylor 近似（或模型）为

$$
\hat{f}(x + v) = f(x) + \nabla f(x)^{\top}v + \frac{1}{2}v^{\top}\nabla^2 f(x)v
$$

它是 $v$ 的凸二次函数，在 $v = \Delta x_{\mathrm{nt}}$ 处取极小。因此 Newton 步 $\Delta x_{\mathrm{nt}}$ 正是使二阶近似最小的点所需要加上的一步。由此可以获得一些直觉：如果 $f$ 是二次函数，那么 $x + \Delta x_{\mathrm{nt}}$ 就是 $f$ 的精确极小点；如果 $f$ 接近二次函数，那么 $x + \Delta x_{\mathrm{nt}}$ 应当是极小点 $x^{\star}$ 的很好估计。由于 $f$ 二阶可微，当 $x$ 接近 $x^{\star}$ 时二次模型非常准确，因此 $x + \Delta x_{\mathrm{nt}}$ 应该是 $x^{\star}$ 的很好估计——这一直觉是正确的。

### Hessian 范数下的最速下降方向

Newton 步也是 $x$ 处由 Hessian 定义的二次范数

$$
\|u\|_{\nabla^2 f(x)} = (u^{\top}\nabla^2 f(x)u)^{1/2}
$$

下的最速下降方向。这提供了 Newton 步为何是好的搜索方向的另一种解释：回忆最速下降方法在二次范数 $\|\cdot\|_P$ 下、当坐标变换后的 Hessian 条件数很小时收敛很快，而 $x^{\star}$ 附近最好的选择是 $P = \nabla^2 f(x^{\star})$；当 $x$ 接近 $x^{\star}$ 时 $\nabla^2 f(x) \approx \nabla^2 f(x^{\star})$，这解释了为什么 Newton 步是非常好的搜索方向。

> **待配图**&#8203;：对应教材图 9.17 —— 某凸函数的等高线、椭圆体 $\{x + v \mid v^{\top}\nabla^2 f(x)v \leqslant 1\}$、负梯度方向以及 Hessian 范数下的（归一化）最速下降方向。

### 线性化最优性条件的解

将最优性条件 $\nabla f(x^{\star}) = 0$ 在 $x$ 附近线性化：

$$
\nabla f(x + v) \approx \nabla f(x) + \nabla^2 f(x)v = 0
$$

这是关于 $v$ 的线性方程，其解为 $v = \Delta x_{\mathrm{nt}}$。所以 Newton 步正是使线性化的最优性条件成立所需加上的一步。当 $n = 1$（即 $f: \mathbf{R} \rightarrow \mathbf{R}$）时这个解释特别简单：解 $x^{\star}$ 由 $f'(x^{\star}) = 0$ 刻画，即 $f'$（单调递增）的零点；给定当前近似 $x$，对 $f'$ 作一阶 Taylor 近似，该仿射近似的零点就是 $x + \Delta x_{\mathrm{nt}}$。

> **待配图**&#8203;：对应教材图 9.16 与图 9.18 —— 左：函数 $f$ 与其二阶近似 $\hat{f}$，Newton 步 $\Delta x_{\mathrm{nt}}$ 把 $x$ 加上后得到 $\hat{f}$ 的极小点；右：导数 $f'$ 及其线性近似 $\hat{f}'$，Newton 步是 $\hat{f}'$ 的零点与 $x$ 之差。

### Newton 步的仿射不变性

Newton 步的一个重要特征是它不依赖于线性（或仿射）坐标变换。设 $T \in \mathbf{R}^{n \times n}$ 非奇异，定义 $\bar{f}(y) = f(Ty)$，则

$$
\nabla \bar{f}(y) = T^{\top}\nabla f(x), \quad \nabla^2 \bar{f}(y) = T^{\top}\nabla^2 f(x)T
$$

其中 $x = Ty$。$\bar{f}$ 在 $y$ 处的 Newton 步为

$$
\Delta y_{\mathrm{nt}} = -\left(T^{\top}\nabla^2 f(x)T\right)^{-1} T^{\top}\nabla f(x) = T^{-1}\Delta x_{\mathrm{nt}}
$$

即 $\bar{f}$ 与 $f$ 的 Newton 步通过同一个线性变换相联系：$x + \Delta x_{\mathrm{nt}} = T(y + \Delta y_{\mathrm{nt}})$。

## Newton 减量

量

$$
\lambda(x) = \left(\nabla f(x)^{\top}\nabla^2 f(x)^{-1}\nabla f(x)\right)^{1/2}
$$

称为 $x$ 处的 **Newton 减量**&#8203;（Newton decrement）。它在 Newton 方法的分析中起着重要作用，也可用作终止准则。Newton 减量与量 $f(x) - \inf_y \hat{f}(y)$（$\hat{f}$ 为 $f$ 在 $x$ 处的二阶近似）的关系是

$$
f(x) - \inf_y \hat{f}(y) = f(x) - \hat{f}(x + \Delta x_{\mathrm{nt}}) = \frac{\lambda(x)^2}{2}
$$

即 $\lambda^2/2$ 是基于 $x$ 处二次近似的 $f(x) - p^{\star}$ 的估计。

Newton 减量也可以表示为

$$
\lambda(x) = \left(\Delta x_{\mathrm{nt}}^{\top}\nabla^2 f(x)\Delta x_{\mathrm{nt}}\right)^{1/2}
$$

这说明 $\lambda$ 是 Newton 步在 Hessian 定义的二次范数下的范数。Newton 减量还出现在回溯直线搜索中，因为

$$
\nabla f(x)^{\top}\Delta x_{\mathrm{nt}} = -\lambda(x)^2
$$

它可以解释为 $f$ 在 $x$ 处沿 Newton 步方向的方向导数。最后，与 Newton 步一样，Newton 减量也是仿射不变的：$\bar{f}(y) = f(Ty)$（$T$ 非奇异）在 $y$ 处的 Newton 减量与 $f$ 在 $x = Ty$ 处的相等。

## Newton 方法

下面的算法有时称为**阻尼**&#8203;（damped）Newton 方法或**受保护**&#8203;（guarded）Newton 方法，以区别于使用固定步长 $t = 1$ 的**纯**&#8203;（pure）Newton 方法。

**算法 9.5（Newton 方法）** 给定初始点 $x \in \operatorname{dom} f$，容许误差 $\epsilon > 0$。

1. 计算 Newton 步与减量：$\Delta x_{\mathrm{nt}} := -\nabla^2 f(x)^{-1}\nabla f(x)$；$\lambda^2 := \nabla f(x)^{\top}\nabla^2 f(x)^{-1}\nabla f(x)$。
2. **终止准则**&#8203;：若 $\lambda^2/2 \leqslant \epsilon$ 则退出。
3. **直线搜索**&#8203;：用回溯直线搜索选取步长 $t$。
4. 更新：$x := x + t\Delta x_{\mathrm{nt}}$。

这与一般下降方法基本相同，只是用 Newton 步作搜索方向，且终止准则在计算搜索方向之后（而不是更新之后）检查。

## 收敛性分析

假设 $f$ 二阶连续可微且强凸（常数 $m$，即 $\nabla^2 f(x) \succeq mI$，$x \in S$），从而也存在 $M > 0$ 使 $\nabla^2 f(x) \preceq MI$。此外假设 $f$ 的 Hessian 在 $S$ 上 Lipschitz 连续（常数 $L$）：

$$
\|\nabla^2 f(x) - \nabla^2 f(y)\|_2 \leqslant L\|x - y\|_2
$$

$L$ 可以理解为对 $f$ 三阶导数的界（二次函数时 $L = 0$），衡量了 $f$ 能被二次模型近似的好坏，可以预期它在 Newton 方法的性能中起关键作用。

### 收敛证明的思路

可以证明存在满足 $0 < \eta \leqslant m^2/L$ 的 $\eta$ 和 $\gamma > 0$，使得：

- 若 $\|\nabla f(x^{(k)})\|_2 \geqslant \eta$，则 $f(x^{(k+1)}) - f(x^{(k)}) \leqslant -\gamma$；
- 若 $\|\nabla f(x^{(k)})\|_2 < \eta$，则回溯直线搜索选择 $t^{(k)} = 1$，且

$$
\frac{L}{2m^2}\|\nabla f(x^{(k+1)})\|_2^2 \leqslant \left(\frac{L}{2m^2}\|\nabla f(x^{(k)})\|_2^2\right)^2
$$

分析第二个条件：一旦它对第 $k$ 次迭代成立，由 $\eta \leqslant m^2/L$ 可知它对之后的每次迭代都成立，即此后算法总取全步长 $t = 1$，且递归应用可得

$$
f(x^{(l)}) - p^{\star} \leqslant \frac{1}{2m}\|\nabla f(x^{(l)})\|_2^2 \leqslant \frac{2m^3}{L^2}\left(\frac{1}{2}\right)^{2(l-k)+1}
$$

这说明第二条件成立后收敛极其迅速，这一现象称为**二次收敛**&#8203;（quadratic convergence）：大致地说，在足够多次迭代之后，每次迭代会使正确数字的位数翻倍。

Newton 方法的迭代自然分为两个阶段。第二阶段（条件 $\|\nabla f(x)\|_2 \leqslant \eta$ 成立之后）称为**二次收敛阶段**&#8203;；第一阶段称为**阻尼 Newton 阶段**&#8203;（damped Newton phase），因为算法可能选取小于 1 的步长。（二次收敛阶段也称为**纯 Newton 阶段**&#8203;，因为此时总取步长 $t = 1$。）

### 复杂度估计

阻尼 Newton 阶段中 $f$ 每次迭代至少下降 $\gamma$，因此其迭代次数不超过 $(f(x^{(0)}) - p^{\star})/\gamma$。二次收敛阶段由上面的不等式可知，至多

$$
\log_2 \log_2(\epsilon_0/\epsilon)
$$

次迭代（其中 $\epsilon_0 = 2m^3/L^2$）即可使 $f(x) - p^{\star} \leqslant \epsilon$。因此总迭代次数的上界为

$$
\frac{f(x^{(0)}) - p^{\star}}{\gamma} + \log_2 \log_2(\epsilon_0/\epsilon)
$$

其中 $\log_2 \log_2(\epsilon_0/\epsilon)$ 随要求的精度 $\epsilon$ 增长极慢，实际上可以视为常数（比如五或六；六次二次收敛阶段的迭代即可达到约 $5 \cdot 10^{-20}\,\epsilon_0$ 的精度）。于是可以（不太严格地）说，极小化 $f$ 所需的 Newton 迭代次数不超过

$$
\frac{f(x^{(0)}) - p^{\star}}{\gamma} + 6
$$

更精确的表述是：该式是计算极好近似解所需迭代次数的界。

### 阻尼 Newton 阶段

设 $\|\nabla f(x)\|_2 \geqslant \eta$。由 Hessian 上界及 $\lambda(x)^2 \geqslant m\|\Delta x_{\mathrm{nt}}\|_2^2$ 可得

$$
f(x + t\Delta x_{\mathrm{nt}}) \leqslant f(x) - t\lambda(x)^2 + \frac{M}{2m}t^2\lambda(x)^2
$$

步长 $\hat{t} = m/M$ 满足直线搜索的终止条件，因此直线搜索返回的步长 $t \geqslant \beta m/M$，目标函数的下降量满足

$$
f(x^{+}) - f(x) \leqslant -\alpha t\lambda(x)^2 \leqslant -\alpha\beta\frac{m}{M^2}\eta^2
$$

（利用 $\lambda(x)^2 = \nabla f(x)^{\top}\nabla^2 f(x)^{-1}\nabla f(x) \geqslant (1/M)\|\nabla f(x)\|_2^2$。）于是第一条性质成立，且

$$
\gamma = \alpha\beta\eta^2\frac{m}{M^2}
$$

### 二次收敛阶段

设 $\|\nabla f(x)\|_2 < \eta$。利用 Hessian 的 Lipschitz 条件，对 $\tilde{f}(t) = f(x + t\Delta x_{\mathrm{nt}})$ 有

$$
\tilde{f}''(t) \leqslant \lambda(x)^2 + t\frac{L}{m^{3/2}}\lambda(x)^3
$$

积分两次并取 $t = 1$ 得

$$
f(x + \Delta x_{\mathrm{nt}}) \leqslant f(x) - \frac{1}{2}\lambda(x)^2 + \frac{L}{6m^{3/2}}\lambda(x)^3
$$

若 $\eta \leqslant 3(1 - 2\alpha)m^2/L$，则由强凸性 $\lambda(x) \leqslant 3(1 - 2\alpha)m^{3/2}/L$，代入上式可知单位步长 $t = 1$ 满足回溯直线搜索的充分下降条件。此外，由 Lipschitz 条件可证

$$
\|\nabla f(x^{+})\|_2 \leqslant \frac{L}{2m^2}\|\nabla f(x)\|_2^2
$$

即第二条性质。综上，当

$$
\eta = \min\{1, 3(1 - 2\alpha)\}\frac{m^2}{L}
$$

时算法选取单位步并满足二次收敛条件。总迭代次数的上界为

$$
6 + \frac{M^2L^2/m^5}{\alpha\beta(1 - 2\alpha)^2 \min\{1, 9(1 - 2\alpha)^2\}}\left(f(x^{(0)}) - p^{\star}\right)
$$

## 例子

### $\mathbf{R}^2$ 中的例子

对前文的非二次测试函数采用参数 $\alpha = 0.1$、$\beta = 0.7$ 的回溯直线搜索：Newton 方法只需五次迭代就达到很高精度，二次收敛十分明显——最后一步把误差从约 $10^{-5}$ 降到 $10^{-10}$。该方法之所以有效，是因为椭圆体 $\{x \mid \|x - x^{(k)}\|_{\nabla^2 f(x^{(k)})} \leqslant 1\}$ 很好地近似了下水平集的形状。

> **待配图**&#8203;：对应教材图 9.19 与图 9.20 —— $\mathbf{R}^2$ 例子中 Newton 方法的迭代点与相应椭圆体，以及误差随迭代次数的变化曲线。

### $\mathbf{R}^{100}$ 中的例子

对 $m = 500$、$n = 100$ 的对数障碍型问题，回溯直线搜索（$\alpha = 0.01$，$\beta = 0.5$）下八次迭代即达到很高精度，从第三次迭代起二次收敛就很明显。精确直线搜索只比回溯直线搜索快一次迭代——这也很典型：精确直线搜索通常只会给 Newton 方法带来很小的改进。步长曲线显示：经过两步阻尼步之后，回溯直线搜索总是取全步 $t = 1$。回溯参数 $\alpha$、$\beta$ 对 Newton 方法性能影响很小（$\beta$ 在 0.2 到 1 之间、$\alpha$ 在 0.005 到 0.5 之间变化时，迭代次数在 8 到 12 之间变化）。因此大多数实用实现采用较小的 $\alpha$（如 0.01）和较大的 $\beta$（如 0.5）。

> **待配图**&#8203;：对应教材图 9.21 与图 9.22 —— $\mathbf{R}^{100}$ 问题的误差曲线与步长曲线。

### $\mathbf{R}^{10000}$ 中的例子

考虑更大规模的问题

$$
\mathrm{minimize} \quad -\sum_{i=1}^n \log(1 - x_i^2) - \sum_{i=1}^m \log(b_i - a_i^{\top}x)
$$

其中 $m = 100000$，$n = 10000$（$a_i$ 为随机生成的稀疏向量）。参数 $\alpha = 0.01$、$\beta = 0.5$ 的回溯直线搜索下，性能与前面的例子非常相似：约 13 次迭代的初始线性收敛阶段之后是二次收敛阶段，再经过四五次迭代即达到很高精度。

> **待配图**&#8203;：对应教材图 9.23 —— $\mathbf{R}^{10000}$ 问题的误差曲线；即使对如此大规模的问题，Newton 方法也只需 18 次迭代即达到很高精度。

### Newton 方法的仿射不变性

Newton 方法的一个非常重要的特征是它不依赖于线性（或仿射）坐标变换。设 $x^{(k)}$ 是对 $f$ 应用 Newton 方法得到的第 $k$ 个迭代点，$T$ 非奇异且 $\bar{f}(y) = f(Ty)$；若对 $\bar{f}$ 采用 Newton 方法（相同的回溯参数）并从 $y^{(0)} = T^{-1}x^{(0)}$ 出发，则对所有 $k$ 都有 $Ty^{(k)} = x^{(k)}$。换句话说，两个方法的迭代点通过同一坐标变换相联系，连终止准则也相同（Newton 减量是仿射不变的）。这与受坐标变换强烈影响的梯度（或最速下降）方法形成鲜明对比。

例如，对前文条件数随参数 $\gamma$ 变化的问题族，梯度方法在 $\gamma$ 小于 0.05 或大于 20 时慢到不可用；而 Newton 方法（$\alpha = 0.01$，$\beta = 0.5$）对 $10^{-10}$ 到 $10^{10}$ 之间的所有 $\gamma$ 都只需九次迭代（且达到更高的精度）。在实际实现中，由于有限精度算术，Newton 方法并非严格仿射不变，但条件数高达 $10^{10}$ 这样的量级也不会对实际实现造成不利影响。对梯度方法而言，可容忍的条件数范围要小得多。总之，坐标选择（或下水平集条件数）对梯度和最速下降方法是一阶问题，而对 Newton 方法只是二阶问题——它唯一的影响是计算 Newton 步所需的数值线性代数部分。

## 总结

与梯度和最速下降方法相比，Newton 方法有以下非常强的优点：

- 收敛一般很快，且在 $x^{\star}$ 附近是二次的。一旦进入二次收敛阶段，至多六次左右的迭代即可产生很高精度的解。
- Newton 方法是仿射不变的，对坐标选择和目标函数下水平集的条件数不敏感。
- Newton 方法对问题规模具有很好的伸缩性：它在 $\mathbf{R}^{10000}$ 问题上的表现与其在 $\mathbf{R}^{10}$ 问题上的表现相似，所需步数只有适度的增加。
- Newton 方法的良好性能不依赖于算法参数的选择；相比之下，最速下降方法中范数的选择对其性能起关键作用。

Newton 方法的主要缺点是形成和存储 Hessian 的代价，以及计算 Newton 步（需要求解一个线性方程组）的代价。许多情形下可以利用问题的结构显著降低计算 Newton 步的代价（见下文实现部分）。另一类替代算法是**拟 Newton**&#8203;（quasi-Newton）方法，它们形成搜索方向所需计算量更小，但保留了 Newton 方法的一些重要优点（如 $x^{\star}$ 附近的快速收敛）。

## 实现

### 直线搜索的预计算

最简单的直线搜索实现对每个 $t$ 都按通常方式计算 $f(x + t\Delta x)$。但在某些情形下，可以利用 $f$（以及精确直线搜索中的导数）要在射线 $\{x + t\Delta x \mid t \geqslant 0\}$ 上许多点处求值这一事实，通过一定的**预计算**降低总计算量。

设 $\tilde{f}(t) = f(x + t\Delta x)$。一个很一般的可加速情形是目标函数具有复合形式 $f(x) = \phi(Ax + b)$（$A \in \mathbf{R}^{p \times n}$，$\phi$ 容易求值，例如可分的）。此时先计算 $Ax + b$ 和 $A\Delta x$（代价 $4pn$ flops），再对每个 $t$ 用 $A(x + t\Delta x) + b = (Ax + b) + t(A\Delta x)$ 组装，总代价约 $4pn + 2kp$ flops，而简单方法需要 $2kpn$ flops（$k$ 为试探的 $t$ 的个数）。

一个更具体的例子是线性矩阵不等式的解析中心问题，即极小化 $\log\det F(x)^{-1}$（$F$ 仿射）。沿直线有

$$
\tilde{f}(t) = -\log\det(A + tB), \quad A = F(x),\ B = \Delta x_1 F_1 + \cdots + \Delta x_n F_n
$$

先对 $A$ 做 Cholesky 分解 $A = LL^{\top}$，可得

$$
\tilde{f}(t) = -\log\det A - \sum_{i=1}^p \log(1 + t\lambda_i)
$$

其中 $\lambda_i$ 是 $L^{-1}BL^{-\top}$ 的特征值。预计算之后，任意 $t$ 处的 $\tilde{f}(t)$（及其导数 $\tilde{f}'(t) = -\sum_{i=1}^p \lambda_i/(1 + t\lambda_i)$）都只需 $4p$ 次简单运算即可求值。当 $k$ 相对 $p(2n + (11/3)p)$ 较小时，整个直线搜索的代价与一次 $f$ 求值相当，节省可达 $k$ 的量级。

### 计算 Newton 步

计算 Newton 步 $\Delta x_{\mathrm{nt}}$ 首先要在 $x$ 处形成 Hessian $H = \nabla^2 f(x)$ 和梯度 $g = \nabla f(x)$，然后求解线性方程组 $H\Delta x_{\mathrm{nt}} = -g$。该方程组有时称为 **Newton 系统**&#8203;（Newton system），也称为**正规方程**&#8203;（normal equations）。虽然可以用一般的线性方程求解器，但更好的方法是利用 $H$ 的对称性与正定性：最常用的方法是对 $H$ 做 Cholesky 分解 $H = LL^{\top}$（$L$ 为下三角），然后通过前代与回代得到

$$
\Delta x_{\mathrm{nt}} = -L^{-\top}L^{-1}g = -H^{-1}g
$$

Newton 减量可由 $\lambda^2 = -\Delta x_{\mathrm{nt}}^{\top}g$ 或 $\lambda^2 = \|L^{-1}g\|_2^2 = \|w\|_2^2$ 计算（$w$ 为前代所得 $w = -L^{-1}g$）。若采用稠密 Cholesky 分解，代价为 $F + (1/3)n^3$ flops，其中 $F$ 是形成 $H$ 和 $g$ 的代价。经常可以通过利用 $H$ 的特殊结构（带状、稀疏等）更高效地求解 Newton 系统。

**带状结构**&#8203;：若 $H$ 是带宽为 $k$ 的带状矩阵（$H_{ij} = 0$，$|i - j| > k$），则可用带状 Cholesky 分解及带状前代回代，代价为 $F + nk^2$ flops（假设 $k \ll n$）。Hessian 带状意味着目标函数中每个变量 $x_i$ 只与 $2k + 1$ 个相邻变量非线性耦合，即 $f$ 具有**部分可分**&#8203;（partial separability）形式

$$
f(x) = \psi_1(x_1, \cdots, x_{k+1}) + \psi_2(x_2, \cdots, x_{k+2}) + \cdots + \psi_{n-k}(x_{n-k}, \cdots, x_n)
$$

例如 $f(x) = \psi_1(x_1, x_2) + \psi_2(x_2, x_3) + \cdots + \psi_{n-1}(x_{n-1}, x_n)$ 时 Hessian 是三对角的，求解 Newton 系统只需 $n$ 阶 flops（而不利用结构则需 $n^3$ 阶）。

**稀疏结构**&#8203;：更一般地，当目标函数可以表示为一些只依赖少数变量的函数之和、且每个变量只出现在其中少数几个函数中时，Hessian 是稀疏的。此时可用稀疏 Cholesky 分解计算置换矩阵 $P$ 和下三角矩阵 $L$ 使 $H = PLL^{\top}P^{\top}$，然后通过 $Lw = -P^{\top}g$ 与 $L^{\top}v = w$ 解出 $v$，最终 $\Delta x = Pv$。由于稀疏模式不随 $x$ 改变，确定好的置换矩阵 $P$ 的**符号分解**&#8203;（symbolic factorization）步骤只需进行一次。

**对角加低秩**&#8203;：若 Hessian 可以表示为对角矩阵加低秩（秩为 $p$）矩阵，即目标函数形如

$$
f(x) = \sum_{i=1}^n \psi_i(x_i) + \psi_0(Ax + b)
$$

其中 $A \in \mathbf{R}^{p \times n}$，则 Newton 系统 $H\Delta x_{\mathrm{nt}} = -g$ 中 $H = D + A^{\top}H_0A$（$D$ 为对角阵，$H_0 = \nabla^2\psi_0(Ax + b)$）。引入辅助变量 $w = L_0^{\top}A\Delta x_{\mathrm{nt}}$（$H_0 = L_0L_0^{\top}$ 为 $H_0$ 的 Cholesky 分解），通过消元化为 $p$ 阶线性方程组

$$
(I + L_0^{\top}AD^{-1}A^{\top}L_0)w = -L_0^{\top}AD^{-1}g
$$

求解后由 $\Delta x_{\mathrm{nt}} = -D^{-1}(A^{\top}L_0w + g)$ 得到 Newton 步。总代价约为 $2p^2n$ flops，当 $p \ll n$ 时远小于 $(1/3)n^3$。
