---
title: "内点法"
date: 2021-11-07T17:27:25+08:00
weight: 1000
---
# 内点法

## 本章目录

- [不等式约束极小化问题](/knowledge-planet/convex-optimization/interior-point-methods/inequality-constrained-minimization-problems/)
- [对数障碍函数与中心路径](/knowledge-planet/convex-optimization/interior-point-methods/logarithmic-barrier-and-central-path/)
- [障碍方法](/knowledge-planet/convex-optimization/interior-point-methods/barrier-method/)
- [可行性与阶段 I 方法](/knowledge-planet/convex-optimization/interior-point-methods/feasibility-and-phase-i-methods/)
- [基于自和谐的复杂度分析](/knowledge-planet/convex-optimization/interior-point-methods/complexity-analysis-via-self-concordance/)
- [广义不等式问题](/knowledge-planet/convex-optimization/interior-point-methods/problems-with-generalized-inequalities/)

## 本章涉及到的数学符号

| 符号                                   | 含义                                                          |
| -------------------------------------- | ------------------------------------------------------------- |
| $\phi$                                 | 对数障碍函数 $-\sum_{i=1}^m \log(-f_i(x))$                    |
| $x^{\star}(t)$                         | 中心路径上的中心点（$tf_0 + \phi$ 在 $Ax = b$ 下的极小点）    |
| $\lambda^{\star}(t)$, $\nu^{\star}(t)$ | 中心点 $x^{\star}(t)$ 对应的对偶可行点                        |
| $m/t$                                  | 中心点的对偶间隙（标量不等式情形）                            |
| $\mu$                                  | 障碍方法中 $t$ 每次外层迭代的更新因子（$\mu > 1$）            |
| $t^{(0)}$                              | 参数 $t$ 的初始值                                             |
| $\hat{I}_{-}(u) = -(1/t)\log(-u)$      | 示性函数 $I_{-}$ 的对数障碍近似                               |
| $I_{-}$                                | 非正实数的示性函数                                            |
| $\theta$                               | 广义对数的次数（各锥次数之和）                                |
| $\psi$                                 | 正常锥的广义对数（$\bar{\psi}$ 为对偶对数）                   |
| $\preceq_K$, $\succ_{K^{*}}$           | 由正常锥 $K$ 导出的广义不等式（对偶锥广义不等式）             |
| $\bar{p}^{\star}$                      | 阶段 I 问题的最优值                                           |
| $F$, $G$, $R$                          | 最大约束违反量 / 梯度范数上界 / 可行集半径先验上界            |
| $\gamma$, $c$                          | Newton 复杂度界中的常数（只依赖回溯参数与终止容许误差）       |
