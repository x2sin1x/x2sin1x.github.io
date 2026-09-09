---
title: "作业"
date: 2021-11-03T21:23:15+08:00
---
# 作业

## [不同路径 II](https://leetcode-cn.com/problems/unique-paths-ii/)

### 问题描述

一个机器人位于一个 $m \times n$ 网格的左上角，他每次只能向下或者向右移动一步。机器人试图达到网格的右下角。

现在考虑网格中有障碍物。那么从左上角到右下角将会有多少条不同的路径？

### 问题分析

我们记 $dp[i, j]$ 为从 $(0, 0)$ 到 $(i, j)$ 的路径总数，$ob[i, j]$ 表示 $(i, j)$ 处有无障碍物（有障碍物则值为 1）。根据题目的规则，只能向下和向右走。因此从 $(0, 0)$ 到 $(i, j)$ 的路径总数等于从 $(0, 0)$ 到 $(i - 1, j)$ 和 $(i, j - 1)$ 两点坐标路径总数之和，即原问题可以由子问题递推得到。要注意这里要考虑到障碍物的问题，如果 $(i, j)$ 处是障碍物，则没有任何路径。于是可以得到下面的状态转移方程：

$$
\begin{aligned}
dp[i, j] = \left\{\begin{matrix}
 0 & ob[i, j] = 1 \\
 dp[i - 1, j] + dp[i, j - 1] & ob[i, j] = 0
\end{matrix}\right.
\end{aligned}
$$

### 算法代码

```cpp
int uniquePathsWithObstacles(vector<vector<int>> &obstacleGrid)
{
    const int m = obstacleGrid.size();
    const int n = obstacleGrid[0].size();
    // dp[i][j] 表示从坐标 (0, 0) 到 (i, j) 的路径数
    vector<vector<int>> dp(m, vector<int>(n, 0));
    dp[0][0] = 1; // 初始化
    for (int i = 0; i < m; i++)
    {
        for (int j = 0; j < n; j++)
        {
            if (obstacleGrid[i][j] == 1)
            {
                // 遇到障碍物直接置零
                dp[i][j] = 0;
            }
            else
            {
                // 否则统计右边和下面一共有多少条路径
                if (i - 1 >= 0)
                {
                    dp[i][j] += dp[i - 1][j];
                }
                if (j - 1 >= 0)
                {
                    dp[i][j] += dp[i][j - 1];
                }
            }
        }
    }
    return dp[m - 1][n - 1];
}
```

### 算法分析

- 时间复杂度：$O(mn)$
- 空间复杂度：$O(mn)$

## [打家劫舍 II](https://leetcode-cn.com/problems/house-robber-ii/)

### 问题描述

你是一个专业的小偷，计划偷窃沿街的房屋，每间房内都藏有一定的现金。这个地方所有的房屋都**围成一圈**，这意味着第一个房屋和最后一个房屋是紧挨着的。同时，相邻的房屋装有相互连通的防盗系统，如果两间相邻的房屋在同一晚上被小偷闯入，系统会自动报警。

给定一个代表每个房屋存放金额的非负整数数组，计算你**在不触动警报装置的情况下**，今晚能够偷窃到的最高金额。

### 问题分析

本题和[打家劫舍](https://leetcode-cn.com/problems/house-robber/)的区别是房屋是环形的，也就是说不能够同时偷第一家和最后一家。因此需要对原问题稍作分解，分解为偷第 1 到第 $n - 1$ 家和偷第 2 到第 $n$ 家，取这两个子问题的最大值即可。

对于每个子问题，我们记 $w[i]$ 表示第 $i$ 家存放的金额，$dp[i]$ 表示偷第 1 家到第 $i$ 家的最大总金额。很显然 $dp[i]$ 的值即为第一家的金额。依题意，多考虑偷一家，会存在如下两种情况：

- 如果当前这家没偷，那么可以偷下一家，上一家及其之前偷的金额可以汇总。
- 如果偷了当前这家，那么不可以偷下一家，当前偷得的金额还是和上一次偷完一样。

这两种情况取最大即可得到最优方案，如此递推算下去即可求解得到最终结果。因此，状态转移方程为：

$$
\begin{aligned}
dp[i] = \max \{dp[i - 2] + w[i], dp[i - 1]\}
\end{aligned}
$$

### 算法代码

```cpp
int rob(vector<int> &nums)
{
    const int n = nums.size();
    vector<int> dp1(n, 0); // 偷第一家而不偷最后一家
    vector<int> dp2(n, 0); // 偷最后一家而不偷第一家
    if (n == 1)
    {
        // 只有一家
        return nums[0];
    }
    // 初始化
    dp1[0] = nums[0];
    if (n > 1)
    {
        dp1[1] = max(nums[0], nums[1]);
        dp2[1] = nums[1];
    }
    if (n > 2)
    {
        dp2[2] = max(nums[1], nums[2]);
    }
    for (int i = 2; i < n - 1; ++i)
    {
        dp1[i] = max(dp1[i - 2] + nums[i], dp1[i - 1]);
    }
    for (int i = 3; i < n; ++i)
    {
        dp2[i] = max(dp2[i - 2] + nums[i], dp2[i - 1]);
    }
    return max(dp1[n - 2], dp2[n - 1]);
}
```

### 算法分析

- 时间复杂度：$O(n)$
- 空间复杂度：$O(n)$

## [不同的子序列](https://leetcode-cn.com/problems/distinct-subsequences/)

### 问题描述

给定一个字符串 $s$ 和一个字符串 $t$，计算在 $s$ 的子序列中 $t$ 出现的个数。

字符串的一个**子序列**是指，通过删除一些（也可以不删除）字符且不干扰剩余字符相对位置所组成的新字符串。（例如，"ACE" 是 "ABCDE" 的一个子序列，而 "AEC" 不是）

题目数据保证答案符合 32 位带符号整数范围。

### 问题分析

本题和[最长公共子序列](https://leetcode-cn.com/problems/longest-common-subsequence/)类似。我们记 $dp[i, j]$ 表示 $s$ 的子串 $s[:i]$ 的子序列中 $t$ 的子串 $t[:j]$ 出现的个数。下面是两种简单情况：

- 如果 $j = 0$，即 $t[:j]$ 是空串，是任意字符串的子序列。应当设置 $dp[i, j] = 1$。
- 如果 $i < j$，说明 $t[:j]$ 比 $s[:i]$ 还长，$t[:j]$ 不可能是 $s[:i]$ 的子序列。

原问题与子问题存在如下两种关系：

- 如果之前对应位不能匹配，即 $s[i - 1] \ne t[j - 1]$，那么问题和 $dp[i - 1, j]$ 相当。因为 $t[:j]$ 删除掉倒数第二个字符 $t[j - 1]$ 后，可能会出现在 $s[:i - 1]$ 的子序列中。
- 如果之前的对应位能够匹配，即 $s[i - 1] = t[j - 1]$，那么原问题分解为如下两种情况之和：
    + 认为 $s[i - 1]$ 和 $t[j - 1]$ 匹配，这个时候需要考察 $dp[i - 1, j - 1]$ 和 $dp[i - 1, j]$。
    + 认为 $s[i - 1]$ 和 $t[j - 1]$ 不匹配，这个时候只需要考察 $dp[i - 1, j]$。

那么本题的状态转移方程为：

$$
\begin{aligned}
dp[i, j] = \left\{\begin{matrix}
 dp[i - 1, j] & s[i - 1] \ne t[j - 1] \\ 
 dp(i - 1, j - 1) + dp[i - 1, j] & s[i - 1] = t[j - 1]
\end{matrix}\right.
\end{aligned}
$$

### 算法代码

```cpp
int numDistinct(string s, string t)
{
    const int m = s.size(), n = t.size();
    // dp[i][j] 表示 s 的子串 s[:i] 的子序列中 t 的子串 t[:j] 出现的个数
    vector<vector<long long>> dp(m + 1, vector<long long>(n + 1, 0)); // 运算过程中可能溢出
    for (int i = 0; i <= m; ++i)
    {
        for (int j = 0; j <= n; ++j)
        {
            if (j == 0)
            {
                // t[:j] 为空串，是任意字符串的子序列
                dp[i][j] = 1;
            }
            else if (i < j)
            {
                // t[:j] 比 s[:i] 还长，不可能是 s[:i] 的子序列
                dp[i][j] = 0;
            }
            else if (i > 0 && j > 0)
            {
                // 只有当 t[:j] 不比 s[:i] 长才有可能在 s[:i] 的子序列中出现
                if (s[i - 1] != t[j - 1])
                {
                    // 如果之前对应位不能匹配，那问题和 s[:i - 1] 的子序列是否有 t[:j] 相当
                    // 因为 t[:j] 删除掉倒数第二个字符 t[j - 1] 后，可能会出现在 s[:i - 1] 的子序列中
                    dp[i][j] = dp[i - 1][j];
                }
                else
                {
                    // dp[i - 1][j - 1] 表示匹配 s[i] 和 t[j]
                    // dp[i - 1][j] 表示不匹配 s[i] 和 t[j]
                    // 最终子序列的出现的次数应为二者之和
                    dp[i][j] = dp[i - 1][j - 1] % 0x7fffffff + dp[i - 1][j] % 0x7fffffff;
                    // 虽然题目保证最终结果不会溢出，但中间结果还是会溢出，忽略高 32 位
                }
            }
        }
    }
    return dp[m][n];
}
```

### 算法分析

- 时间复杂度：$O(mn)$
- 空间复杂度：$O(mn)$
