---
title: "作业"
---

# 作业

## [跳跃游戏 II](https://leetcode-cn.com/problems/jump-game-ii/)

### 问题描述

给你一个非负整数数组 `nums`，你最初位于数组的第一个位置。

数组中的每个元素代表你在该位置可以跳跃的最大长度。

你的目标是使用最少的跳跃次数到达数组的最后一个位置。

假设你总是可以到达数组的最后一个位置。

### 方法一：反向查找出发位置

我们的目标是到达数组的最后一个位置，因此我们可以考虑最后一步跳跃前所在的位置，该位置通过跳跃能够到达最后一个位置。

如果有多个位置通过跳跃都能够到达最后一个位置，那么我们应该如何进行选择呢？直观上来看，我们可以“贪心”地选择距离最后一个位置最远的那个位置，也就是对应下标最小的那个位置。因此，我们可以从左到右遍历数组，选择第一个满足要求的位置。

找到最后一步跳跃前所在的位置之后，我们继续贪心地寻找倒数第二步跳跃前所在的位置，以此类推，直到找到数组的开始位置。

#### 算法代码

```cpp
int jump(vector<int> &nums) {
    int pos = nums.size() - 1; // 当前位置
    int step = 0;              // 统计步数
    while (pos > 0) {
        for (int i = 0; i < pos; ++i) {
            if (nums[i] + i >= pos) {
                // 说明位置 i 可以一步跳到当前位置
                pos = i;
                ++step;
                break;
            }
        }
    }
    return step;
}
```

#### 算法分析

- 时间复杂度：$O(n^2)$
- 空间复杂度：$O(1)$

### 方法二：正向查找可到达的最大位置

方法一虽然直观，但是时间复杂度比较高，有没有办法降低时间复杂度呢？

如果我们“贪心”地进行正向查找，每次找到可到达的最远位置，就可以在线性时间内得到最少的跳跃次数。

在具体的实现中，我们维护当前能够到达的最大下标位置，记为边界。我们从左到右遍历数组，到达边界时，更新边界并将跳跃次数增加 1。

在遍历数组时，我们不访问最后一个元素，这是因为在访问最后一个元素之前，我们的边界一定大于等于最后一个位置，否则就无法跳到最后一个位置了。如果访问最后一个元素，在边界正好为最后一个位置的情况下，我们会增加一次**不必要的跳跃次数**，因此我们不必访问最后一个元素。

#### 算法代码

```cpp
int jump(vector<int> &nums) {
    int len = nums.size();
    int end = 0;    // 上次可达最远位置，下次的起点
    int maxPos = 0; // 目前能跳到的最远位置
    int steps = 0;  // 跳跃次数
    for (int i = 0; i < len - 1; ++i) {
        maxPos = max(maxPos, i + nums[i]);
        if (i == end) {
            end = maxPos;
            ++steps;
        }
    }
    return steps;
}
```

#### 算法分析

- 时间复杂度：$O(n)$
- 空间复杂度：$O(1)$

## [无重叠区间](https://leetcode-cn.com/problems/non-overlapping-intervals/)

### 问题描述

给定一个区间的集合，找到需要移除区间的最小数量，使剩余区间互不重叠。

### 问题分析

本题的贪心思想和活动选择问题类似。

我们可以不断地寻找右端点在首个区间右端点左侧的新区间，将首个区间替换成该区间。那么当我们无法替换时，**首个区间就是所有可以选择的区间中右端点最小的那个区间**。因此我们将所有区间按照右端点从小到大进行排序，那么排完序之后的首个区间，就是我们选择的首个区间。

由于我们选择的是首个区间，因此在左侧不会有其它的区间，那么左端点在何处是不重要的，我们只要任意选择一个右端点最小的区间即可。

当确定了首个区间之后，所有与首个区间不重合的区间就组成了一个规模更小的子问题。由于我们已经在初始时将所有区间按照右端点排好序了，因此对于这个子问题，我们无需再次进行排序，只要找出其中**与首个区间不重合并且右端点最小的区间**即可。用相同的方法，我们可以依次确定后续的所有区间。

### 算法代码

```cpp
int eraseOverlapIntervals(vector<vector<int>> &intervals) {
    if (intervals.empty()) {
        return 0;
    }
    auto lambda = [](const vector<int> &a, const vector<int> &b) {
        return a[1] < b[1];
    }; // lambda 表达式：按右端点升序排列
    sort(intervals.begin(), intervals.end(), lambda);

    const int n = intervals.size();
    int right = intervals[0][1];
    int ans = 1;
    for (int i = 1; i < n; ++i) {
        if (intervals[i][0] >= right) {
            ++ans;
            right = intervals[i][1];
        }
    }
    return n - ans;
}
```

### 算法分析

- 时间复杂度：$O(n \log {n})$
- 空间复杂度：$O(\log {n})$

## [分发糖果](https://leetcode-cn.com/problems/candy/)

### 问题描述

`n` 个孩子站成一排。给你一个整数数组 `ratings` 表示每个孩子的评分。

你需要按照以下要求，给这些孩子分发糖果：

- 每个孩子至少分配到 1 个糖果。
- 相邻两个孩子评分更高的孩子会获得更多的糖果。

请你给每个孩子分发糖果，计算并返回需要准备的最少糖果数目。

### 问题分析

我们可以将**相邻的孩子中，评分高的孩子必须获得更多的糖果**这句话拆分为两个规则，分别处理。

- 左规则：当 $\textit{ratings}[i - 1] < \textit{ratings}[i]ratings[i−1]<ratings[i]$ 时，$i$ 号学生的糖果数量将比 $i - 1$ 号孩子的糖果数量多。
- 右规则：当 $\textit{ratings}[i] > \textit{ratings}[i + 1]ratings[i]>ratings[i+1]$ 时，$i$ 号学生的糖果数量将比 $i + 1$ 号孩子的糖果数量多。

我们遍历该数组两次，处理出每一个学生分别满足左规则或右规则时，最少需要被分得的糖果数量。每个人最终分得的糖果数量即为这两个数量的最大值。

### 算法代码

```cpp
int candy(vector<int> &ratings) {
    const int n = ratings.size();
    vector<int> left(n, 1); // 初始化时给每个孩子发一个糖果
    // 第一次遍历，满足左规则
    for (int i = 1; i < n; ++i) {
        if (ratings[i] > ratings[i - 1]) {
            // i 比 i-1 多一个糖果
            left[i] = left[i - 1] + 1;
        }
    }
    
    int right = 0, ret = 0;
    // 第二次遍历，满足右规则
    for (int i = n - 1; i >= 0; --i) {
        if (i < n - 1 && ratings[i] > ratings[i + 1]) {
            // i 比 i+1 多一个糖果
            right++;
        } else {
            right = 1;
        }
        ret += max(left[i], right); // 左规则右规则取最大
    }
    return ret;
}
```

### 算法分析

- 时间复杂度：$O(n)$
- 空间复杂度：$O(n)$
