---
title: "最速下降方法"
date: 2026-09-29T00:00:00+08:00
weight: 840
---
# 最速下降方法

设 $f(x + v)$ 在 $x$ 附近的一阶 Taylor 近似为

$$
f(x + v) \approx \hat{f}(x + v) = f(x) + \nabla f(x)^{\top}v
$$

右端第二项 $\nabla f(x)^{\top}v$ 是 $f$ 在 $x$ 处沿方向 $v$ 的**方向导数**&#8203;（directional derivative），给出了小步 $v$ 引起的 $f$ 的近似变化。若方向导数为负，则 $v$ 是下降方向。

我们希望选取 $v$ 使方向导数尽可能负。由于 $\nabla f(x)^{\top}v$ 关于 $v$ 是线性的，取很大的 $v$ 就可以使其任意负（只要 $v$ 是下降方向），因此必须限制 $v$ 的大小（或按其长度归一化）。设 $\|\cdot\|$ 是 $\mathbf{R}^n$ 上的任意范数，定义**归一化最速下降方向**&#8203;（normalized steepest descent direction）（关于范数 $\|\cdot\|$）：

$$
\Delta x_{\mathrm{nsd}} = \operatorname{argmin}\{\nabla f(x)^{\top}v \mid \|v\| = 1\}
$$

（之所以说“一个”最速下降方向，是因为极小点可能不唯一。）归一化最速下降方向是单位范数的步进中使 $f$ 的线性近似下降最大的方向。几何上，它等价地定义为

$$
\Delta x_{\mathrm{nsd}} = \operatorname{argmin}\{\nabla f(x)^{\top}v \mid \|v\| \leqslant 1\}
$$

即在 $\|\cdot\|$ 的单位球内沿 $-\nabla f(x)$ 方向延伸最远的方向。

把归一化最速下降方向按特定方式缩放，还可以得到**未归一化**的最速下降步：

$$
\Delta x_{\mathrm{sd}} = \|\nabla f(x)\|_{*}\,\Delta x_{\mathrm{nsd}}
$$

其中 $\|\cdot\|_{*}$ 为对偶范数。对最速下降步有 $\nabla f(x)^{\top}\Delta x_{\mathrm{sd}} = -\|\nabla f(x)\|_*^2$。&#8203;**最速下降方法**&#8203;（steepest descent method）以最速下降方向为搜索方向。

**算法 9.4（最速下降方法）** 给定初始点 $x \in \operatorname{dom} f$。

1. 计算最速下降方向 $\Delta x_{\mathrm{sd}}$。
2. **直线搜索**&#8203;：通过回溯或精确直线搜索选取 $t$。
3. 更新：$x := x + t\Delta x_{\mathrm{sd}}$。

重复上述步骤直至满足终止准则。

当采用精确直线搜索时，搜索方向中的尺度因子没有影响，因此使用归一化或未归一化的方向均可。

## 欧氏范数与二次范数的最速下降

### 欧氏范数

若取 $\|\cdot\|$ 为欧氏范数，则最速下降方向就是负梯度方向 $\Delta x_{\mathrm{sd}} = -\nabla f(x)$，即欧氏范数下的最速下降方法与梯度下降方法完全一致。

### 二次范数

考虑二次范数

$$
\|z\|_P = (z^{\top}Pz)^{1/2} = \|P^{1/2}z\|_2
$$

其中 $P \in \mathbf{S}^n_{++}$。归一化最速下降方向为

$$
\Delta x_{\mathrm{nsd}} = -\left(\nabla f(x)^{\top}P^{-1}\nabla f(x)\right)^{-1/2} P^{-1}\nabla f(x)
$$

对偶范数为 $\|z\|_{*} = \|P^{-1/2}z\|_2$，因此关于 $\|\cdot\|_P$ 的最速下降步为

$$
\Delta x_{\mathrm{sd}} = -P^{-1}\nabla f(x)
$$

> **待配图**&#8203;：对应教材图 9.9 —— 二次范数下的归一化最速下降方向。图中椭圆是平移到点 $x$ 处的范数单位球，$\Delta x_{\mathrm{nsd}}$ 是停留在椭圆内、沿 $-\nabla f(x)$ 方向延伸最远的方向。

### 通过坐标变换来理解

最速下降方向 $\Delta x_{\mathrm{sd}} = -P^{-1}\nabla f(x)$ 有一个有趣解释：它是对原问题做坐标变换 $\bar{u} = P^{1/2}u$ 后，在新变量 $\bar{x}$ 上应用梯度方法得到的搜索方向。在此变换下 $\|u\|_P = \|\bar{u}\|_2$，原问题等价于极小化

$$
\bar{f}(\bar{u}) = f(P^{-1/2}\bar{u})
$$

对 $\bar{f}$ 应用梯度方法，搜索方向 $\Delta\bar{x} = -\nabla\bar{f}(\bar{x}) = -P^{-1/2}\nabla f(x)$ 对应于原变量 $x$ 下的方向 $-P^{-1}\nabla f(x)$。换言之，二次范数 $\|\cdot\|_P$ 下的最速下降方法可以看作变换 $\bar{x} = P^{1/2}x$ 之后的梯度方法。

## $\ell_1$ 范数的最速下降

对 $\ell_1$ 范数，归一化最速下降方向

$$
\Delta x_{\mathrm{nsd}} = \operatorname{argmin}\{\nabla f(x)^{\top}v \mid \|v\|_1 \leqslant 1\}
$$

有一个简单的刻画。设 $i$ 是使 $\|\nabla f(x)\|_{\infty} = |(\nabla f(x))_i|$ 成立的任一下标，则可取

$$
\Delta x_{\mathrm{nsd}} = -\operatorname{sign}\left(\frac{\partial f(x)}{\partial x_i}\right) e_i
$$

其中 $e_i$ 为第 $i$ 个标准基向量。相应的未归一化最速下降步为

$$
\Delta x_{\mathrm{sd}} = \Delta x_{\mathrm{nsd}}\,\|\nabla f(x)\|_{\infty} = -\frac{\partial f(x)}{\partial x_i}e_i
$$

因此 $\ell_1$ 范数下的归一化最速下降方向总可以选为某个标准基向量（或其负方向）：它是使 $f$ 的近似下降最大的坐标轴方向。

$\ell_1$ 范数的最速下降算法有一个非常自然的解释：每次迭代选取 $\nabla f(x)$ 中绝对值最大的一个分量，然后按其符号减小或增大 $x$ 的相应分量。由于每次只更新变量 $x$ 的一个分量，该算法有时称为**坐标下降**&#8203;（coordinate descent）算法。这可以极大地简化、甚至使直线搜索变得平凡。

### 例子：Frobenius 范数缩放

考虑无约束几何规划（凸形式）

$$
\mathrm{minimize} \quad f(x) = \log\left(\sum_{i,j=1}^n M_{ij}^2 e^{x_i - x_j}\right)
$$

（它来自矩阵的 Frobenius 范数缩放问题，变量 $x_i = 2\log d_i$。）这个问题很容易逐分量最小化：固定除 $x_k$ 以外的所有分量，可写 $f(x) = \log(\alpha_k + \beta_k e^{-x_k} + \gamma_k e^{x_k})$，其中

$$
\alpha_k = M_{kk}^2 + \sum_{i,j \neq k} M_{ij}^2 e^{x_i - x_j}, \quad \beta_k = \sum_{i \neq k} M_{ik}^2 e^{x_i}, \quad \gamma_k = \sum_{j \neq k} M_{kj}^2 e^{-x_j}
$$

$f$ 关于 $x_k$ 的最小值在 $x_k = \log(\beta_k/\gamma_k)/2$ 处取得，因此精确直线搜索可以用一个解析公式完成。$\ell_1$ 最速下降算法（带精确直线搜索）就是重复以下步骤：

1. 计算梯度 $(\nabla f(x))_i = (-\beta_i e^{-x_i} + \gamma_i e^{x_i})/(\alpha_i + \beta_i e^{-x_i} + \gamma_i e^{x_i})$，$i = 1, \cdots, n$。
2. 选取 $\nabla f(x)$ 中绝对值最大的分量 $k$：$|\nabla f(x)|_k = \|\nabla f(x)\|_{\infty}$。
3. 极小化 $f$ 关于标量 $x_k$：令 $x_k = \log(\beta_k/\gamma_k)/2$。

## 收敛性分析

可以把梯度方法在回溯直线搜索下的收敛分析推广到任意范数下的最速下降方法。任何范数都可以用欧氏范数来界定，即存在常数 $\gamma, \tilde{\gamma} \in (0, 1]$ 使

$$
\|x\| \geqslant \gamma\|x\|_2, \quad \|x\|_{*} \geqslant \tilde{\gamma}\|x\|_2
$$

仍假设 $f$ 在初始下水平集 $S$ 上强凸。Hessian 上界 $\nabla^2 f(x) \preceq MI$ 给出

$$
f(x + t\Delta x_{\mathrm{sd}}) \leqslant f(x) + t\nabla f(x)^{\top}\Delta x_{\mathrm{sd}} + \frac{M\|\Delta x_{\mathrm{sd}}\|_2^2}{2}t^2 \leqslant f(x) - t\|\nabla f(x)\|_*^2 + \frac{M}{2\gamma^2}t^2\|\nabla f(x)\|_*^2
$$

使该二次上界最小的步长 $\hat{t} = \gamma^2/M$ 满足回溯直线搜索的终止条件（因 $\alpha < 1/2$ 且 $\nabla f(x)^{\top}\Delta x_{\mathrm{sd}} = -\|\nabla f(x)\|_*^2$），因此直线搜索返回的步长满足 $t \geqslant \min\{1, \beta\gamma^2/M\}$，进而

$$
f(x^{+}) \leqslant f(x) - \alpha\tilde{\gamma}^2\min\{1, \beta\gamma^2/M\}\|\nabla f(x)\|_2^2
$$

两边减去 $p^{\star}$ 并利用强凸性下界，得

$$
f(x^{+}) - p^{\star} \leqslant c\,(f(x) - p^{\star}), \quad c = 1 - 2m\alpha\tilde{\gamma}^2\min\{1, \beta\gamma^2/M\} < 1
$$

因此

$$
f(x^{(k)}) - p^{\star} \leqslant c^k(f(x^{(0)}) - p^{\star})
$$

即与梯度方法完全一样的线性收敛。

## 讨论与例子

### 范数的选择

用于定义最速下降方向的范数对收敛速度有巨大影响。以二次 $P$-范数为例：二次范数下的最速下降方法等价于坐标变换 $\bar{x} = P^{1/2}x$ 之后的梯度方法，而梯度方法在（变换后的）下水平集条件数适中时表现良好、条件数很大时表现糟糕。因此选取 $P$ 的准则是：使 $f$ 的下水平集经 $P^{-1/2}$ 变换后条件数良好。例如，若已知最优点处 Hessian 的近似 $\hat{H}$，则非常好的选择是 $P = \hat{H}$，因为此时 $\bar{f}$ 在最优点的 Hessian 为 $\hat{H}^{-1/2}\nabla^2 f(x^{\star})\hat{H}^{-1/2} \approx I$，其条件数很小。

不用坐标变换也可以描述同一思想：说下水平集在变换 $\bar{x} = P^{1/2}x$ 后条件数低，等价于说椭圆体 $E = \{x \mid x^{\top}Px \leqslant 1\}$（在适当的缩放与平移后）很好地近似了下水平集的形状。

$P$ 对收敛率的影响可以从两个角度看待。乐观的观点是：对任何问题，总存在使最速下降方法表现得非常好的 $P$——当然，挑战在于找到这样的 $P$。悲观的观点是：对任何问题，也存在大量使最速下降表现很差的 $P$。总之，只有当我们能识别出使变换后问题条件数适中的矩阵 $P$ 时，最速下降方法才表现良好。

### 例子

仍考虑梯度下降一节中 $\mathbf{R}^2$ 的非二次问题，采用两个二次范数

$$
P_1 = \begin{bmatrix} 2 & 0 \\ 0 & 8 \end{bmatrix}, \quad P_2 = \begin{bmatrix} 8 & 0 \\ 0 & 2 \end{bmatrix}
$$

两者都用参数 $\alpha = 0.1$、$\beta = 0.7$ 的回溯直线搜索。实验表明范数的选择强烈影响收敛：对范数 $\|\cdot\|_{P_1}$，收敛略快于梯度方法；而对范数 $\|\cdot\|_{P_2}$，收敛则慢得多。原因可以从变换后的坐标下看出：与 $P_1$ 相关联的坐标变换使下水平集条件数适中，因此收敛快；与 $P_2$ 相关联的变换反而使下水平集条件数变差，收敛因而变慢。

> **待配图**&#8203;：对应教材图 9.11、图 9.12、图 9.13 —— 两个二次范数下最速下降方法的迭代点与误差曲线；以及图 9.14、图 9.15 —— 坐标变换后两个问题的迭代点（一个降低、另一个提高了下水平集的条件数）。
