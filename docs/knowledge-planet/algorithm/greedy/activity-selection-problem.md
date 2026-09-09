---
title: "活动选择"
date: 2021-11-07T15:14:56+08:00
weight: 310
---
# 活动选择

## 问题描述

### 形式化描述

输入：

- $n$ 个活动组成的集合 $S = \{ a_1, a_2, \cdots, a_n \}$- 每个活动 $a_i$ 的开始时间 $s_i$ 和结束时间 $f_i$

输出：

- 活动集合 $S$ 的子集 $S'$

优化目标：

$$
\begin{aligned}
\max \left | S' \right |
\end{aligned}
$$

约束条件：

$$
\begin{aligned}
\mathbf{s.t.} \forall a_i, a_j \in S', s_i \geqslant f_j \vee s_j \geqslant f_i
\end{aligned}
$$

## 问题分析

我们可以很容易想到如下策略：

1. 最短活动优先
2. 最早开始活动优先
3. 最早结束活动优先

上面三种策略到底哪一种正确呢？还是都不正确？

### 最短活动优先

![](活动选择1.png)

### 最早开始活动优先

![](活动选择2.png)

### 最早结束活动优先

因为选择最早结束的活动，可以给后面的活动留更大的选择空间。然而这只是我们的直观感受，这是否可以保证最优解？需要证明。

#### 证明

先证明问题具有最优子结构性质，用反证法。再证明贪心选择性：

- 设贪心最优解 $A$ 也按结束时间递增排序，设其第一个活动为 $k$，第二个活动为 $j$。
- 若 $k=1$，显然成立。
- 若 $k \ne 1$，由于 $A$ 中的活动相容，有 $f_k \leqslant s_j$。由于 $f_1 \leqslant f_k$，因此可以用活动 1 代替活动 $k$。

## 算法代码

```cpp
void activitySelection(vector<pair<int, int>> &activities) {
    // lambda表达式：按结束时间排序，若相同则按最早开始时间排序
    auto lambda = [](const pair<int, int> &a1,
                     const pair<int, int> &a2) {
        return a1.second < a2.second;
    };
    sort(activities.begin(), activities.end(), lambda);
    auto iter = activities.begin();
    while (iter != activities.end()) {
        // 删除所有与iter所指活动时间冲突的活动
        for (auto it = iter + 1; it != activities.end();) {
            if (it->first < iter->second) {
                it = activities.erase(it); // erase函数返回删除后的下一个元素的迭代器
            } else {
                ++it;
            }
        }
        ++iter;
    }
}
```
