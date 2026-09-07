---
title: "大整数乘法"
---

# 大整数乘法

## 问题描述

$n$ 位二进制整数 $X$ 和 $Y$ 相乘，通常算法时间复杂度为 $O(n^2)$。是否存在分治算法可以降低时间复杂度？

## 问题分析

设 $X$ 和 $Y$ 是 $n$ 位整数，将 $X$ 分为 $n/2$ 位的两部分（高 $n/2$ 位的 $A$ 和低 $n/2$ 位的 $B$），将 $Y$ 分为 $n/2$ 位的两部分（高 $n/2$ 位的 $C$ 和低 $n/2$ 位的 $D$）。则 $X \times Y$ 可以表示为：

$$
\begin{aligned}
XY &= (A \cdot 2^{n/2} + B)(C \cdot 2^{n/2} + D) \\
&= AC \cdot 2^n + (AD + BC) \cdot 2^{n/2} + BD \\
&= AC \cdot 2^n + ((A+B)(C+D) - AC - BD) \cdot 2^{n/2} + BD
\end{aligned}
$$

需要计算的子问题包括 $AC$、$BD$、$(A+B)(C+D)$。其中 $(A+B)(C+D)$ 中的加法运算的时间复杂度取决于问题规模，即数字位数 $n$。因此可以得到如下递推式：

$$
\begin{aligned}
T(n) = 3 T\left( \dfrac{n}{2} \right) + \Theta(n)
\end{aligned}
$$

可以解得时间复杂度为：

$$
\begin{aligned}
T(n) = \Theta\left(n^{\log _{2}{3}}\right)
\end{aligned}
$$
