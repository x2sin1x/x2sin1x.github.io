---
title: "最长公共子序列"
weight: 230
---

# 最长公共子序列

## 问题描述

子序列：将当前序列去掉零个或多个元素所得序列。

公共子序列：同时满足是两个序列的子序列的序列。

最长公共子序列问题：求解两个序列的公共子序列，使得它尽可能长。

### 形式化定义

输入：

- 序列 $X = \langle x_1, x_2, \cdots, x_n \rangle$
- 序列 $Y = \langle y_1, y_2, \cdots, y_m \rangle$

输出：

- 公共子序列 $Z = \langle z_1, z_2, \cdots, z_l \rangle$

优化目标：

$$
\begin{aligned}
\max \left | Z \right |
\end{aligned}
$$

约束条件：

$$
\begin{aligned}
    \mathbf{s.t.} \langle z_{1}, z_{2}, \cdots, z_{l} \rangle = \langle x_{i_{1}}, x_{i_{2}}, \cdots, x_{i_{l}} \rangle = \langle y_{j_{1}}, y_{j_{2}}, \cdots, y_{j_{l}} \rangle \\
    \left({1} \leq {i}_{1}<{i}_{2}, \cdots, {i}_{l} \leq {n} ; {1} \leq {j}_{1}<{j}_{2}, \cdots, {j}_{l} \leq {m}\right)
\end{aligned}
$$

## 问题分析

令 $C[i,j]$ 表示 $X[1:i]$ 和 $Y[1:j]$ 的最长公共子序列长度，那么原始问题就是求解 $C[n,m]$。

下面我们来考察末尾字符，分为如下两大类情况：

### 情况一

![](最长公共子序列1.png)

如果 $x_i \ne y_j$，那么需要考察 $C[i,j-1]$ 和 $C[i-1,j]$ 两个子问题。并且当前问题的解是这两个子问题解的最大值，即如下的状态转移方程：

$$
\begin{aligned}
C[i,j] = \max \left \{ C[i-1,j], C[i,j-1] \right \}
\end{aligned}
$$

### 情况二

![](最长公共子序列2.png)

如果 $x_i = y_j$，那么既可以匹配这最后一对字符，也可以不匹配。这样一来，需要考察 $C[i-1,j-1]$、$C[i-1,j]$ 和 $C[i,j-1]$ 三个子问题。

**问题**：三个子问题是否都需要求解？

**分析**：

- $C[i-1,j]$ 比 $C[i-1,j-1]$ 至多大 1，即 $C[i-1,j] - C[i-1,j-1] \leqslant 1$。
- $C[i,j-1]$ 比 $C[i-1,j-1]$ 至多大 1，即 $C[i,j-1] - C[i-1,j-1] \leqslant 1$。

因此

$$
\begin{aligned}
C[i-1,j-1] + 1 \geqslant \max \left \{ C[i-1,j], C[i,j-1] \right \}
\end{aligned}
$$

故只需要考虑子问题 $C[i-1,j-1]$ 即可。于是状态转移方程为

$$
\begin{aligned}
C[i,j] = C[i-1,j-1] + 1
\end{aligned}
$$

### 小结

综上所述，状态转移方程为

$$
\begin{aligned}
C[i,j] = \left \{ \begin{matrix}
    \max \left \{ C[i-1,j], C[i,j-1] \right \} & (x_i=y_j) \\
    C[i-1,j-1] + 1 & (x_i \ne y_j)
\end{matrix}\right .
\end{aligned}
$$

## 算法代码

```cpp
string longestCommonSubsequence(const string &x, const string &y) {
    enum Drct {
        LU, // 向左上方回溯
        U,  // 向上方回溯
        L   // 向左边回溯
    };
    auto lengthX = x.size(), lengthY = y.size();
    // C[i,j] 表示 x[1..i] 和 y[1..j] 的最长公共子序列长度
    vector<vector<int>> C(lengthX + 1, vector<int>(lengthY + 1, 0));
    // rec[i,j] 是追踪数组，记录子问题来源
    vector<vector<Drct>> rec(lengthX + 1, vector<Drct>(lengthY + 1));

    for (int i = 1; i <= lengthX; ++i) {
        for (int j = 1; j <= lengthY; ++j) {
            if (x[i - 1] == y[j - 1]) {
                C[i][j] = C[i - 1][j - 1] + 1;
                rec[i][j] = LU;
            } else {
                C[i][j] = C[i - 1][j] > C[i][j - 1] ? C[i - 1][j] : C[i][j - 1];
                rec[i][j] = C[i - 1][j] > C[i][j - 1] ? U : L;
            }
        }
    }

    int maxLength = (lengthX < lengthY ? lengthX : lengthY) + 1;
    char *pStr = new char[maxLength];
    char *p = pStr + maxLength - 1;
    *p = '\0'; // 字符串末尾结束符

    // 根据追踪数组回溯最长公共子序列
    for (int i = lengthX, j = lengthY; i > 0 && j > 0;) {
        if (rec[i][j] == LU) {
            *(--p) = x[i - 1]; // LU 才说明 x[i]==y[j]，该字符是最长公共子序列的一部分
            --i;
            --j;
        } else if (rec[i][j] == L) {
            --j;
        } else if (rec[i][j] == U) {
            --i;
        }
    }

    return string(p);
}
```

## 算法分析

- 时间复杂度：$O(n^2)$
- 空间复杂度：$O(n^2)$
