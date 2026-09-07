---
title: "钢条切割"
---

# 钢条切割

## 问题描述

给定长度为 $n$ 的一段钢条，以及一个价格表 $p$。这个价格表中标明了长度为 $l$ 的价格，其中 $l$ 为整数，取值范围为 $[0,n]$。

求一组切割方案，使得钢条的价格尽可能高。

## 问题分析

令 $r[n]$ 为长度为 $n$ 英寸的钢条的最大收益，则状态转移方程为

$$
\begin{aligned}
r[n] = \max_{1 \leqslant i \leqslant n}{p[i] + r[n-i]}
\end{aligned}
$$

## 算法代码

```cpp
void rodCutting(const vector<int> &p) {
    // 初始化
    const int length = p.size();
    vector<int> r(length + 1, 0);   // r[i]表示切割长度为i的钢条可得最大总收益
    vector<int> rec(length + 1, 0); // rec[i]记录长度为i的钢条的最优切割方案

    // 动态规划
    for (int j = 1; j <= length; ++j) {
        r[j] = p[j];
        rec[j] = j;
        for (int i = 1; i <= j - 1; ++i) {
            if (p[i] + r[j - i] > r[j]) {
                r[j] = p[i] + r[j - i];
                rec[j] = i;
            }
        }
    }
    // 输出结果
    int n = length;
    cout << "最优价格：" << r[n] << endl;
    cout << "切割方式：" << endl;
    while (n > 0) {
        cout << rec[n] << ' ';
        n = n - rec[n];
    }
}
```

## 算法分析

- 时间复杂度：$O(n^2)$
- 空间复杂度：$O(n)$
