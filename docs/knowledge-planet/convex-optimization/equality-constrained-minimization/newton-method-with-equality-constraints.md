---
title: "带等式约束的 Newton 方法"
date: 2026-09-29T00:00:00+08:00
weight: 920
---
# 带等式约束的 Newton 方法

本节描述 Newton 方法向等式约束问题的扩展。该方法与无约束的 Newton 方法几乎相同，只有两点差别：初始点必须是可行的（即 $x \in \operatorname{dom} f$ 且 $Ax = b$），并且 Newton 步的定义需要考虑等式约束。特别地，我们保证 Newton 步 $\Delta x_{\mathrm{nt}}$ 是一个**可行方向**&#8203;（feasible direction），即 $A\Delta x_{\mathrm{nt}} = 0$。

## Newton 步

### 通过二阶近似定义

为在**可行**点 $x$ 处导出等式约束问题

$$
\mathrm{minimize} \quad f(x) \quad \mathrm{subject\ to} \quad Ax = b
$$

的 Newton 步 $\Delta x_{\mathrm{nt}}$，用目标函数在 $x$ 附近的二阶 Taylor 近似代替目标函数，得到问题

$$
\mathrm{minimize} \quad \hat{f}(x + v) = f(x) + \nabla f(x)^{\top}v + (1/2)v^{\top}\nabla^2 f(x)v \quad \mathrm{subject\ to} \quad A(x + v) = b
$$

这是一个（凸的）等式约束二次极小化问题，可以解析求解。假设相应的 KKT 矩阵非奇异，我们定义该问题的解为 Newton 步 $\Delta x_{\mathrm{nt}}$。换言之，Newton 步 $\Delta x_{\mathrm{nt}}$ 是把目标函数换成二次近似后，为解出问题所需要加到 $x$ 上的一步。

由等式约束二次问题的分析可知，Newton 步 $\Delta x_{\mathrm{nt}}$ 由如下条件刻画：

$$
\begin{bmatrix}
    \nabla^2 f(x) & A^{\top} \\
    A & 0
\end{bmatrix}
\begin{bmatrix}
    \Delta x_{\mathrm{nt}} \\
    w
\end{bmatrix}
=
\begin{bmatrix}
    -\nabla f(x) \\
    0
\end{bmatrix}
$$

其中 $w$ 是该二次问题相应的最优对偶变量。与无约束情形一样，当 $f$ 恰为二次函数时，Newton 更新 $x + \Delta x_{\mathrm{nt}}$ 精确解出等式约束极小化问题，且 $w$ 就是原问题的最优对偶变量。这提示我们：当 $f$ 接近二次函数时，$x + \Delta x_{\mathrm{nt}}$ 应当是解 $x^{\star}$ 的很好估计，$w$ 应当是最优对偶变量 $\nu^{\star}$ 的很好估计。

### 线性化最优性条件的解

Newton 步 $\Delta x_{\mathrm{nt}}$ 与向量 $w$ 也可以解释为最优性条件

$$
Ax^{\star} = b, \quad \nabla f(x^{\star}) + A^{\top}\nu^{\star} = 0
$$

的线性化近似的解。将 $x + \Delta x_{\mathrm{nt}}$ 代入 $x^{\star}$、$w$ 代入 $\nu^{\star}$，并把第二式中的梯度项换成在 $x$ 附近的线性近似，得到

$$
A(x + \Delta x_{\mathrm{nt}}) = b, \quad \nabla f(x) + \nabla^2 f(x)\Delta x_{\mathrm{nt}} + A^{\top}w = 0
$$

利用 $Ax = b$，两式化为 $A\Delta x_{\mathrm{nt}} = 0$ 与 $\nabla^2 f(x)\Delta x_{\mathrm{nt}} + A^{\top}w = -\nabla f(x)$，这正是定义 Newton 步的那组方程。

### Newton 减量

等式约束问题的 **Newton 减量**&#8203;（Newton decrement）定义为

$$
\lambda(x) = \left(\Delta x_{\mathrm{nt}}^{\top}\nabla^2 f(x)\Delta x_{\mathrm{nt}}\right)^{1/2}
$$

这与无约束情形的表达式完全一样，各种解释也仍然成立。例如，$\lambda(x)$ 是 Newton 步在 Hessian 所确定的范数下的范数。设 $\hat{f}$ 为二阶 Taylor 近似，则

$$
f(x) - \inf\{\hat{f}(x + v) \mid A(x + v) = b\} = \lambda(x)^2/2
$$

与无约束情形完全一样：$\lambda(x)^2/2$ 给出了基于 $x$ 处二次模型的 $f(x) - p^{\star}$ 的估计，而且 $\lambda(x)$（或 $\lambda(x)^2$ 的某个倍数）可以作为一个好的终止准则的基础。

Newton 减量同样出现在直线搜索中，因为 $f$ 沿 $\Delta x_{\mathrm{nt}}$ 方向的方向导数为

$$
\left.\frac{d}{dt}f(x + t\Delta x_{\mathrm{nt}})\right|_{t=0} = \nabla f(x)^{\top}\Delta x_{\mathrm{nt}} = -\lambda(x)^2
$$

### 可行下降方向

设 $Ax = b$。若 $v \in \mathbf{R}^n$ 满足 $Av = 0$，则称 $v$ 为**可行方向**——此时形如 $x + tv$ 的点都可行。若对小的 $t > 0$ 有 $f(x + tv) < f(x)$，则称 $v$ 为 $f$ 在 $x$ 处的**下降方向**&#8203;。

Newton 步总是一个可行下降方向（除非 $x$ 已最优，此时 $\Delta x_{\mathrm{nt}} = 0$）：定义 Newton 步的第二组方程 $A\Delta x_{\mathrm{nt}} = 0$ 表明它是可行方向，而方向导数 $\nabla f(x)^{\top}\Delta x_{\mathrm{nt}} = -\lambda(x)^2$ 表明它是下降方向。

### 仿射不变性

与无约束情形一样，等式约束问题的 Newton 步与 Newton 减量都是仿射不变的。设 $T \in \mathbf{R}^{n \times n}$ 非奇异，$\bar{f}(y) = f(Ty)$，约束 $Ax = b$ 变为 $ATy = b$。对问题 $\mathrm{minimize}\ \bar{f}(y)\ \mathrm{s.t.}\ ATy = b$ 写出其 Newton 步方程并与 $x = Ty$ 处的 Newton 步方程比较，可得

$$
T\Delta y_{\mathrm{nt}} = \Delta x_{\mathrm{nt}} \quad (\text{且 } w = \bar{w})
$$

即 $y$ 与 $x$ 处的 Newton 步通过同一坐标变换相联系。

## 带等式约束的 Newton 方法

**算法 10.1（等式约束极小化的 Newton 方法）** 给定初始点 $x \in \operatorname{dom} f$ 且 $Ax = b$，容许误差 $\epsilon > 0$。

1. 计算 Newton 步与减量 $\Delta x_{\mathrm{nt}}$，$\lambda(x)$。
2. **终止准则**&#8203;：若 $\lambda^2/2 \leqslant \epsilon$ 则退出。
3. **直线搜索**&#8203;：用回溯直线搜索选取步长 $t$。
4. 更新：$x := x + t\Delta x_{\mathrm{nt}}$。

该方法是一种**可行下降方法**&#8203;（feasible descent method）：所有迭代点都可行，且 $f(x^{(k+1)}) < f(x^{(k)})$（除非 $x^{(k)}$ 已最优）。Newton 方法要求 KKT 矩阵在每个迭代点处可逆。

## Newton 方法与消去法

可以证明：对等式约束问题应用带等式约束的 Newton 方法，其迭代点与应用 Newton 方法求解约简问题 $\mathrm{minimize}\ \tilde{f}(z) = f(Fz + \hat{x})$ 所得的迭代点完全一致（其中 $F$ 满足 $\mathcal{R}(F) = \mathcal{N}(A)$、$\operatorname{rank} F = n - p$，$\hat{x}$ 满足 $A\hat{x} = b$）。

约简目标函数的梯度与 Hessian 为

$$
\nabla\tilde{f}(z) = F^{\top}\nabla f(x), \quad \nabla^2\tilde{f}(z) = F^{\top}\nabla^2 f(x)F, \quad x = Fz + \hat{x}
$$

由此可知：等式约束问题的 Newton 步有定义（即 KKT 矩阵可逆）当且仅当约简问题的 Newton 步有定义（即 $\nabla^2\tilde{f}(z)$ 可逆）。约简问题的 Newton 步为

$$
\Delta z_{\mathrm{nt}} = -(F^{\top}\nabla^2 f(x)F)^{-1}F^{\top}\nabla f(x)
$$

它对应于原问题的方向 $F\Delta z_{\mathrm{nt}} = -F(F^{\top}\nabla^2 f(x)F)^{-1}F^{\top}\nabla f(x)$。可以验证（取 $\Delta x_{\mathrm{nt}} = F\Delta z_{\mathrm{nt}}$，$w = -(AA^{\top})^{-1}A(\nabla f(x) + \nabla^2 f(x)\Delta x_{\mathrm{nt}})$）这正是原问题由 KKT 方程定义的 Newton 方向。

类似地，约简问题在 $z$ 处的 Newton 减量 $\tilde{\lambda}(z)$ 与原问题在 $x$ 处的 Newton 减量相等：

$$
\tilde{\lambda}(z)^2 = \Delta z_{\mathrm{nt}}^{\top}F^{\top}\nabla^2 f(x)F\Delta z_{\mathrm{nt}} = \Delta x_{\mathrm{nt}}^{\top}\nabla^2 f(x)\Delta x_{\mathrm{nt}} = \lambda(x)^2
$$

## 收敛性分析

既然带等式约束的 Newton 方法与对消去后的问题应用 Newton 方法完全相同，无约束 Newton 方法收敛性的一切结论都直接转移到等式约束的情形：一旦 $x^{(k)}$ 接近 $x^{\star}$，收敛极其迅速，只需几次迭代即可达到很高精度。

### 假设

- 下水平集 $S = \{x \mid x \in \operatorname{dom} f,\ f(x) \leqslant f(x^{(0)}),\ Ax = b\}$ 是闭集（当 $f$ 是闭函数时成立）。
- 在 $S$ 上，$\nabla^2 f(x) \preceq MI$，且

$$
\left\|\begin{bmatrix}
    \nabla^2 f(x) & A^{\top} \\
    A & 0
\end{bmatrix}^{-1}\right\|_2 \leqslant K
$$

即 KKT 矩阵的逆在 $S$ 上有界（当然，为了 Newton 步在 $S$ 的每点有定义，其逆必须存在）。
- 对 $x, \tilde{x} \in S$，$\nabla^2 f$ 满足 Lipschitz 条件 $\|\nabla^2 f(x) - \nabla^2 f(\tilde{x})\|_2 \leqslant L\|x - \tilde{x}\|_2$。

**KKT 矩阵有界逆假设**&#8203;：条件“KKT 矩阵的逆有界”扮演了标准 Newton 方法分析中强凸性假设的角色。当没有等式约束时，该条件退化为 $\|\nabla^2 f(x)^{-1}\|_2 \leqslant K$（取 $K = 1/m$ 即强凸性）；带等式约束时，条件不如“最小特征值有正下界”那么简单：由于 KKT 矩阵是对称的，该条件即其 $n$ 个正特征值与 $p$ 个负特征值都有界远离零。

### 通过消去问题进行分析

上述假设意味着：消去后的目标函数 $\tilde{f}$ 及相应的初始点满足无约束 Newton 方法收敛分析所需的全部条件（常数 $\tilde{m}$、$\tilde{M}$、$\tilde{L}$ 不同）。因此，带等式约束的 Newton 方法收敛于 $x^{\star}$（以及 $\nu^{\star}$）。

其中最关键（也稍显微妙）的一环是：KKT 矩阵有界逆条件加上 Hessian 上界 $\nabla^2 f(x) \preceq MI$，可以推出 $\nabla^2\tilde{f}(z) \succeq m\tilde{I}$（某正常数 $m$）。具体地，可以证明该不等式对

$$
m = \frac{\sigma_{\min}(F)^2}{K^2M}
$$

成立（$F$ 满秩，故 $m > 0$）。证明采用反证法：若 $F^{\top}HF \not\succeq mI$（$H = \nabla^2 f(x)$），则存在 $\|u\|_2 = 1$ 使 $u^{\top}F^{\top}HFu < m$，即 $\|H^{1/2}Fu\|_2 < m^{1/2}$；利用 $AF = 0$ 构造 KKT 矩阵与向量 $(Fu, 0)$ 的乘积，可得

$$
\left\|\begin{bmatrix}
    H & A^{\top} \\
    A & 0
\end{bmatrix}^{-1}\right\|_2 \geqslant \frac{\|Fu\|_2}{\|HFu\|_2} > \frac{\sigma_{\min}(F)}{M^{1/2}m^{1/2}} = K
$$

与假设矛盾。

### 自和谐函数的收敛分析

若 $f$ 自和谐，则 $\tilde{f}(z) = f(Fz + \hat{x})$ 也自和谐。因此若 $f$ 自和谐，等式约束 Newton 方法具有与无约束情形完全相同的复杂度估计：达到精度 $\epsilon$ 所需的迭代次数不超过

$$
\frac{20 - 8\alpha}{\alpha\beta(1 - 2\alpha)^2}\left(f(x^{(0)}) - p^{\star}\right) + \log_2 \log_2(1/\epsilon)
$$

其中 $\alpha$、$\beta$ 为回溯参数。
