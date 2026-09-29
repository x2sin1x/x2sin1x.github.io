---
title: "无约束优化"
date: 2021-11-07T17:25:01+08:00
weight: 800
---
# 无约束优化

## 本章目录

- [无约束优化问题](/knowledge-planet/convex-optimization/unconstrained-minimization/unconstrained-minimization-problems/)
- [下降方法](/knowledge-planet/convex-optimization/unconstrained-minimization/descent-methods/)
- [梯度下降方法](/knowledge-planet/convex-optimization/unconstrained-minimization/gradient-descent-methods/)
- [最速下降方法](/knowledge-planet/convex-optimization/unconstrained-minimization/steepest-descent-methods/)
- [Newton 方法](/knowledge-planet/convex-optimization/unconstrained-minimization/newton-method/)
- [自和谐](/knowledge-planet/convex-optimization/unconstrained-minimization/self-concordance/)

## 本章涉及到的数学符号

| 符号                                   | 含义                                                       |
| -------------------------------------- | ---------------------------------------------------------- |
| $x^{(k)}$                              | 第 $k$ 次迭代点                                            |
| $\Delta x$                             | 步进（搜索方向）                                           |
| $t^{(k)}$                              | 第 $k$ 次迭代的步长                                        |
| $x^{+}$                                | 下一个迭代点 $x + t\Delta x$                               |
| $\tilde{f}(t) = f(x + t\Delta x)$      | $f$ 沿直线（射线）的限制函数                               |
| $S$                                    | 初始点处的下水平集                                         |
| $m$, $M$                               | Hessian 下界与上界常数：$mI \preceq \nabla^2 f(x) \preceq MI$ |
| $\kappa = M/m$                         | 下水平集（Hessian）条件数的上界                            |
| $\operatorname{cond}(C)$               | 凸集 $C$ 的条件数（最大宽度与最小宽度之比的平方）          |
| $\Delta x_{\mathrm{nt}}$               | Newton 步 $-\nabla^2 f(x)^{-1}\nabla f(x)$                 |
| $\lambda(x)$                           | Newton 减量                                                |
| $\|u\|_{\nabla^2 f(x)}$                | 由 Hessian 定义的二次范数                                  |
| $\Delta x_{\mathrm{nsd}}$, $\Delta x_{\mathrm{sd}}$ | 归一化 / 未归一化最速下降方向                 |
| $\|\cdot\|_{*}$                        | 范数 $\|\cdot\|$ 的对偶范数                                |
| $\|z\|_P$                              | 二次范数 $(z^{\top}Pz)^{1/2}$                              |
| $L$                                    | Hessian 的 Lipschitz 常数                                  |
| $\gamma$, $\eta$                       | 收敛分析中的常数（每步下降量下界 / 二次收敛阶段阈值）      |
