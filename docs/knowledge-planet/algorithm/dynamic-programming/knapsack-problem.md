---
title: "0-1背包问题"
date: 2021-10-16T20:58:05+08:00
weight: 260
---
# 0-1背包问题

## 问题描述

超市允许顾客带一个有限容量的包选购商品，要求在有限的容量下选购价值总额最高的商品。

### 形式化定义

输入：

- 由 $n$ 个商品组成的集合 $O$，每种商品有容量 $v$ 和价格 $p$ 两个属性，分别表示体积和价格。
- 背包容量 $C$。

输出：

- 一个商品子集 $S \subseteq O$。

优化目标：

$$
\begin{aligned}
\max \sum_{i \in S} {p_i}
\end{aligned}
$$

约束条件：

$$
\begin{aligned}
\mathbf{s.t.} \sum_{i \in S} {v_i \leqslant C}
\end{aligned}
$$

## 问题分析

### 直观策略

1. 将商品价格由高到低排序，优先挑选价格高的商品。
2. 将商品体积由小到大排序，优先挑选体积小的商品。
3. 将商品按价值与体积的比由高到低排序，优先挑选比值高的商品。

然而，上述三种策略归根结底都是一种**贪心**策略。我们无法证明在这个问题上，贪心策略可以获得最优解。而且事实也充分说明，本题用贪心策略并不能得到最优解。

### 蛮力枚举：递归求解

![](0-1背包问题.png)

从递归树可以看出，采用分治法蛮力求解的过程中会产生大量的重复子问题，时间复杂度高达 $2^n$。

### 动态规划

设 $P[i,c]$ 表示在前 $i$ 个商品中做出选择，背包容量为 $c$ 时的最优解。则原始问题即求解 $P[n,C]$。

现在我们考察 $P[i,c]$，它由如下两个子问题决定：

- 选够商品 $i$，则购买金额为前 $i-1$ 件商品以及商品 $i$ 的价格之和。
- 不选购商品 $i$，则购买金额为前 $i-1$ 件商品的价格之和。

最终，这两个子问题取最大值，即

$$
\begin{aligned}
P[i,c] = \max \left \{ P[i-1,c-v_i] + p_i, P[i-1,c] \right \}
\end{aligned}
$$

## 算法代码

### 商品类定义

```cpp
struct Goods
{
    int price;  // 价格
    int volume; // 体积
};
```

### 蛮力递归

```cpp
int KnapsackSR(const vector<struct Goods> &goods, int i, int c)
{
    if (c < 0)
    { // 超出容量限制
        return 0x80000000;  // 负无穷大
    }
    if (i <= 0)
    { // 所有商品已决策完成
        return 0;
    }
    int pS = KnapsackSR(goods, i - 1, c - goods[i - 1].volume) + goods[i - 1].price; // 选择商品i
    int pDS = KnapsackSR(goods, i - 1, c);                                           // 不选商品i
    return pS > pDS ? pS : pDS;
}
```

### 动态规划

```cpp
void KnapsackDP(const vector<struct Goods> &goods, int c) {
    auto n = goods.size(); // 商品个数
    // p[i][c] 表示在前 i 个商品中做出选择，背包容量为 c 时的最优解
    vector<vector<int>> p(n + 1, vector<int>(c + 1, 0));
    // rec[i][c] 表示最优解是否包含商品 i，用于记录决策过程方便回溯
    vector<vector<bool>> rec(n + 1, vector<bool>(n + 1, 0));

    for (int i = 1; i <= n; ++i) {
        for (int j = 1; j <= c; ++j) {
            if (j - goods[i - 1].volume < 0) {
                // 超出背包容积
                p[i][j] = p[i - 1][j];
                rec[i][j] = false;
            } else {
                int pS = p[i - 1][j - goods[i - 1].volume] + goods[i - 1].price;
                int pSD = p[i - 1][j];
                p[i][j] = pS > pSD ? pS : pSD; // 总价值取最大
                rec[i][j] = pS > pSD;          // 选否
            }
        }
    }

    cout << "递推解法：" << p[n][c] << endl;
    for (int i = n, j = c; i >= 1; --i) {
        if (rec[i][j]) {
            cout << "选" << i << "号商品" << endl;
            j -= goods[i - 1].volume;
        }
    }
}
```

## 算法分析

### 蛮力递归

- 时间复杂度：$O(2^n)$
- 空间复杂度：$O(1)$

### 动态规划

- 时间复杂度：$O(n^2)$
- 空间复杂度：$O(n^2)$
