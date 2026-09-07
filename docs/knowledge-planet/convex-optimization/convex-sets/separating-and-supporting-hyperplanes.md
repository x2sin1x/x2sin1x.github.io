---
inHomePost: false
title: "分离与支撑超平面"
---

# 分离与支撑超平面

## 超平面分离定理

设两个凸集 $C \cap D = \emptyset$，那么 $\exists a \ne 0, b$ 使得对 $\forall x \in C$ 有 $a^{\top}x \leqslant b$，对 $\forall x \in D$ 有 $a^{\top}x \geqslant b$。称超平面 $\{x \mid a^{\top}x = b\}$ 为凸集 $C$ 和 $D$ 的**分离超平面**，如图所示：

![](6995c45258793cf9a9f9363897d1aa05.png "分离超平面")

*注：*

- 严格分离：即超平面分离定理中的等号不成立。
- 超平面分离定理的逆命题：不成立。

## 支撑超平面

设 $C \subseteq \mathbf{R}^{n}$ 而 $x_0$ 是其边界 $\operatorname{bd} C$ 上的一点。如果 $a \ne 0$，并且对 $\forall x \in C$ 有 $a^{\top} x = a^{\top} x_0$，那么称超平面 $\{x \mid a^{\top} x = a^{\top} x_0\}$ 为集合 $C$ 在点 $x_0$ 处的**支撑超平面**。从几何上看，超平面 $\{x \mid a^{\top} x = a^{\top} x_0\}$ 与 $C$ 相切于点 $x_0$，半空间 $\{x \mid a^{\top} x \leqslant a^{\top} x_0\}$ 包含 $C$，如图所示：

![](9c96fb3ceb496450e27af1b98586faa3.png "支撑超平面")
