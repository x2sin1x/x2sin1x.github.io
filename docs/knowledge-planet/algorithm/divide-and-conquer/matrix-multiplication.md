---
title: "矩阵乘法"
---

# 矩阵乘法

## 问题描述

两个 $n \times n$ 的矩阵 $A$ 和 $B$ 相乘，通常算法时间复杂度为 $O(n^3)$。是否存在分治算法可以降低时间复杂度？

## 问题分析

将 $A$ 和 $B$ 分成 4 个大小为 $\dfrac{n}{2} \times \dfrac{n}{2}$ 的子矩阵相乘。

$$
\begin{array}{l}
{\left[\begin{array}{ll}
C_{11} & C_{12} \\
C_{21} & C_{22}
\end{array}\right]=\left[\begin{array}{ll}
A_{11} & A_{12} \\
A_{21} & A_{22}
\end{array}\right]\left[\begin{array}{ll}
B_{11} & B_{12} \\
B_{21} & B_{22}
\end{array}\right]}
\end{array}
$$

需要计算的子问题包括 8 个小矩阵乘法以及 4 个矩阵加法，时间复杂度为：

$$
\begin{aligned}
T(n) = 8 T\left( \dfrac{n}{2} \right) + \Theta(n^2)
\end{aligned}
$$

即使如此，计算得到的时间复杂度没有得到改善，仍为 $T(n^3)$。我们可令

$$
\begin{aligned}
    M_{1} &= A_{11}(B_{12} - B_{22}) \\
    M_{2} &= (A_{11} + A_{12})B_{22} \\
    M_{3} &= (A_{21} + A_{22})B_{11} \\
    M_{4} &= A_{22}(B_{21} - B_{11}) \\
    M_{5} &= (A_{11} + A_{22})(B_{11} + B_{22}) \\
    M_{6} &= (A_{12} - A_{22})(B_{21} + B_{22}) \\
    M_{7} &= (A_{11} - A_{21})(B_{11} + B_{12}) \\
\end{aligned}
$$

于是

$$
\begin{aligned}
    C_{11} = M_{5} + M_{4} - M_{2} + M_{6} \\
    C_{12} = M_{1} + M_{2} \\
    C_{21} = M_{3} + M_{4} \\
    C_{22} = M_{5} + M_{1} - M_{3} - M_{7}
\end{aligned}
$$

这样就把 8 个矩阵相乘转变成 7 个矩阵相乘，时间复杂度降低为

$$
\begin{aligned}
    T(n) &= 7 T\left( \dfrac{n}{2} \right) + \Theta(n^2) \\
    &= \Theta\left(n^{\log_{2}{7}}\right)
\end{aligned}
$$
