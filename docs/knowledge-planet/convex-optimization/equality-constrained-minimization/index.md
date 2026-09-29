---
title: "等式约束优化"
date: 2021-11-07T17:26:20+08:00
weight: 900
---
# 等式约束优化

## 本章目录

- [等式约束优化问题](/knowledge-planet/convex-optimization/equality-constrained-minimization/equality-constrained-minimization-problems/)
- [带等式约束的 Newton 方法](/knowledge-planet/convex-optimization/equality-constrained-minimization/newton-method-with-equality-constraints/)
- [不可行初始点的 Newton 方法](/knowledge-planet/convex-optimization/equality-constrained-minimization/infeasible-start-newton-method/)
- [实现](/knowledge-planet/convex-optimization/equality-constrained-minimization/implementation/)

## 本章涉及到的数学符号

| 符号                                    | 含义                                                         |
| --------------------------------------- | ------------------------------------------------------------ |
| $Ax = b$                                | 线性等式约束（$A \in \mathbf{R}^{p \times n}$，$\operatorname{rank} A = p < n$） |
| $\nu$                                   | 等式约束的 Lagrange 乘子（对偶变量）                         |
| $\begin{bmatrix} P & A^{\top} \\ A & 0 \end{bmatrix}$ | KKT 矩阵                                       |
| $\Delta x_{\mathrm{nt}}$                | 等式约束问题的 Newton 步（可行方向，$A\Delta x_{\mathrm{nt}} = 0$） |
| $w$                                     | 二次近似问题相应的最优对偶变量                               |
| $\lambda(x)$                            | Newton 减量                                                  |
| $r_{\mathrm{dual}}$, $r_{\mathrm{pri}}$ | 对偶残差 / 原始残差                                          |
| $r(x, \nu)$                             | 原始—对偶残差向量                                            |
| $\Delta y_{\mathrm{pd}}$                | 原始—对偶 Newton 步                                          |
| $F$, $\hat{x}$                          | 消去等式约束的矩阵（$\mathcal{R}(F) = \mathcal{N}(A)$）与特解 |
| $\tilde{f}(z) = f(Fz + \hat{x})$        | 消去等式约束后的约简目标函数                                 |
| $S = -AH^{-1}A^{\top}$                  | Hessian $H$ 在 KKT 矩阵中的 Schur 补                         |
| $K$, $L$                                | KKT 矩阵的逆的界 / Hessian 的 Lipschitz 常数                 |
