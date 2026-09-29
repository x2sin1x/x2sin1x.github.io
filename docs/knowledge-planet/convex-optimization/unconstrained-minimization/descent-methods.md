---
title: "下降方法"
date: 2026-09-29T00:00:00+08:00
weight: 820
---
# 下降方法

本章描述的算法产生极小化序列 $x^{(k)}$，$k = 1, 2, \cdots$：

$$
x^{(k+1)} = x^{(k)} + t^{(k)}\Delta x^{(k)}
$$

其中 $t^{(k)} > 0$（除非 $x^{(k)}$ 已经最优）。向量 $\Delta x^{(k)} \in \mathbf{R}^n$ 称为**步进**&#8203;（step）或**搜索方向**&#8203;（search direction）（尽管它不一定具有单位范数），$k = 0, 1, \cdots$ 表示迭代次数。标量 $t^{(k)} \geqslant 0$ 称为第 $k$ 次迭代的**步长**&#8203;（step size）或**步长长度**&#8203;（step length）（尽管它并不等于 $\|x^{(k+1)} - x^{(k)}\|$，除非 $\|\Delta x^{(k)}\| = 1$）。当我们只关注一次迭代时，常采用简化的记号 $x^{+} = x + t\Delta x$ 或 $x := x + t\Delta x$ 来代替 $x^{(k+1)} = x^{(k)} + t^{(k)}\Delta x^{(k)}$。

我们研究的所有方法都是**下降方法**&#8203;，即除 $x^{(k)}$ 已最优外，始终满足

$$
f(x^{(k+1)}) < f(x^{(k)})
$$

这意味着对所有 $k$ 都有 $x^{(k)} \in S$（初始下水平集），特别地 $x^{(k)} \in \operatorname{dom} f$。由凸性可知，若 $\nabla f(x^{(k)})^{\top}(y - x^{(k)}) \geqslant 0$，则 $f(y) \geqslant f(x^{(k)})$，因此下降方法中的搜索方向必须满足

$$
\nabla f(x^{(k)})^{\top}\Delta x^{(k)} < 0
$$

即它与负梯度方向成锐角。我们称这样的方向为 $f$ 在 $x^{(k)}$ 处的**下降方向**&#8203;（descent direction）。

## 一般下降方法

一般下降方法在如下两个步骤之间交替：确定一个下降方向 $\Delta x$，以及选择步长 $t$。

**算法 9.1（一般下降方法）** 给定初始点 $x \in \operatorname{dom} f$。

1. 确定下降方向 $\Delta x$。
2. **直线搜索**&#8203;（line search）：选择步长 $t > 0$。
3. 更新：$x := x + t\Delta x$。

重复上述步骤直至满足终止准则。

第 2 步称为**直线搜索**&#8203;，因为选择步长 $t$ 决定了下一点在直线 $\{x + t\Delta x \mid t \in \mathbf{R}_+\}$ 上的位置。实用的下降方法具有相同的总体结构，但组织方式可能不同：例如终止准则通常在计算下降方向 $\Delta x$ 的过程中或之后立即检查，其形式常为 $\|\nabla f(x)\|_2 \leqslant \eta$（$\eta$ 为很小的正数），这正是次优性条件所提示的。

## 精确直线搜索

实际中有时使用的一种直线搜索方法是**精确直线搜索**&#8203;（exact line search），即选取 $t$ 使 $f$ 沿射线 $\{x + t\Delta x \mid t \geqslant 0\}$ 最小：

$$
t = \operatorname{argmin}_{s \geqslant 0}\, f(x + s\Delta x)
$$

当该一维极小化问题的代价比计算搜索方向本身的代价小时，可以采用精确直线搜索。某些特殊情形下沿射线的极小点可以解析求出，其他情形也可以高效地数值求解。

## 回溯直线搜索

实践中使用的直线搜索大多数是**不精确的**&#8203;：步长的选取只是近似地最小化 $f$ 沿射线的取值，甚至只要求 $f$“足够”下降。一种非常简单且十分有效的不精确直线搜索称为**回溯直线搜索**&#8203;（backtracking line search），它依赖于两个常数 $\alpha$ 和 $\beta$：$0 < \alpha < 0.5$，$0 < \beta < 1$。

**算法 9.2（回溯直线搜索）** 给定 $f$ 在 $x \in \operatorname{dom} f$ 处的下降方向 $\Delta x$，$\alpha \in (0, 0.5)$，$\beta \in (0, 1)$。

令 $t := 1$。当 $f(x + t\Delta x) > f(x) + \alpha t\nabla f(x)^{\top}\Delta x$ 时，令 $t := \beta t$。

之所以称为回溯，是因为它从单位步长开始，然后按因子 $\beta$ 不断缩小 $t$，直到停止条件 $f(x + t\Delta x) \leqslant f(x) + \alpha t\nabla f(x)^{\top}\Delta x$ 成立。由于 $\Delta x$ 是下降方向，$\nabla f(x)^{\top}\Delta x < 0$，因此当 $t$ 足够小时

$$
f(x + t\Delta x) \approx f(x) + t\nabla f(x)^{\top}\Delta x < f(x) + \alpha t\nabla f(x)^{\top}\Delta x
$$

这表明回溯直线搜索最终必然终止。常数 $\alpha$ 可以解释为：我们接受线性外推所预测的 $f$ 下降量的一部分（比例 $\alpha$）。（要求 $\alpha < 0.5$ 的原因将在后面说明。）

回溯终止不等式 $f(x + t\Delta x) \leqslant f(x) + \alpha t\nabla f(x)^{\top}\Delta x$ 对某个区间 $(0, t_0]$ 中的所有 $t$ 都成立，因此回溯直线搜索终止时得到的步长满足

$$
t = 1 \quad \text{或者} \quad t \in (\beta t_0,\ t_0]
$$

第一种情形对应单位步长本身就满足回溯条件（即 $1 \leqslant t_0$）。特别地，回溯直线搜索得到的步长满足 $t \geqslant \min\{1, \beta t_0\}$。

当 $\operatorname{dom} f$ 不等于全空间 $\mathbf{R}^n$ 时，回溯条件需要仔细解释：按照 $f$ 在定义域之外取值为无穷的约定，不等式蕴含 $x + t\Delta x \in \operatorname{dom} f$。在实际实现中，首先将 $t$ 乘以 $\beta$ 直至 $x + t\Delta x \in \operatorname{dom} f$，然后才开始检查不等式。

参数 $\alpha$ 典型取值在 0.01 与 0.3 之间，即接受线性外推预测下降量的 1% 到 30%；参数 $\beta$ 常取 0.1（对应非常粗糙的搜索）到 0.8（对应较为精细的搜索）之间。

> **待配图**&#8203;：对应教材图 9.1 —— 回溯直线搜索示意图。曲线为 $f$ 沿直线方向的取值，下方虚线为线性外推 $f(x) + t\nabla f(x)^{\top}\Delta x$，上方虚线为斜率缩小 $\alpha$ 倍的直线 $f(x) + \alpha t\nabla f(x)^{\top}\Delta x$；回溯条件即要求 $f$ 位于上方虚线之下。
