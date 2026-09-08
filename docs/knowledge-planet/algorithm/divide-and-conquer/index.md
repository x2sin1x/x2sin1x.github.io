---
title: "分治算法"
weight: 100
---

# 分治算法

## 分治算法的一般步骤

### 建立递归方程

- **Divide**：整个问题划分为多个子问题
- **Conquer**：求解各子问题（递归调用子问题的算法）
- **Combine**：合并子问题的解, 形成原始问题的解

### 递归方程求解

采用 Master 定理。

## 二分搜索

针对有序顺序表，已知左指针 `left = 0`，右指针 `right = n-1`。计算 `mid = (left + right) / 2`，比较 `mid` 和待查找元素 `x` 的大小关系：

- 若相等，则成功找到，返回下标；
- 若 `x` 更大，则在右半部分继续找；
- 若 `x` 更小，则在左半部分继续找。

最终如果出现了 `left > right`，则搜索失败，返回 `-1`。

### 二分搜索变式

假设按照升序排序的数组在预先未知的某个点上进行了旋转，例如 `a = [4, 5, 6, 7, 1, 2, 3]`。应该如何设计算法？

- [LeetCode Link](https://leetcode-cn.com/problems/search-in-rotated-sorted-array/)

对于有序数组，可以使用二分查找的方法查找元素。

但是这道题中，数组本身不是有序的，进行旋转后只保证了数组的局部是有序的，这还能进行二分查找吗？答案是可以的。

可以发现的是，我们将数组从中间分开成左右两部分的时候，一定有一部分的数组是有序的。拿示例来看，我们从 `6` 这个位置分开以后数组变成了 `[4, 5, 6]` 和 `[7, 0, 1, 2]` 两个部分，其中左边 `[4, 5, 6]` 这个部分的数组是有序的，其他也是如此。

这启示我们可以在常规二分查找的时候查看当前 `mid` 为分割位置分割出来的两个部分 `[l, mid]` 和 `[mid + 1, r]` 哪个部分是有序的，并根据有序的那个部分确定我们该如何改变二分查找的上下界，因为我们能够根据有序的那部分判断出 target 在不在这个部分：

- 如果 `[l, mid - 1]` 是有序数组，且 `target` 的大小满足 `[nums[l], nums[mid])`，则我们应该将搜索范围缩小至 `[l, mid - 1]`，否则在 `[mid + 1, r]` 中寻找。
- 如果 `[mid, r]` 是有序数组，且 `target` 的大小满足 `(nums[mid + 1], nums[r]]`，则我们应该将搜索范围缩小至 `[mid + 1, r]`，否则在 `[l, mid - 1]` 中寻找。

#### 算法代码

```cpp
class Solution {
public:
    int search(vector<int> &nums, int target) {
        int n = (int)nums.size();
        if (!n) {
            return -1;
        }
        if (n == 1) {
            return nums[0] == target ? 0 : -1;
        }
        int l = 0, r = n - 1;
        while (l <= r) {
            int mid = (l + r) / 2;
            if (nums[mid] == target)
                return mid;
            if (nums[0] <= nums[mid]) {
                // [0, mid] 有序
                if (nums[0] <= target && target < nums[mid]) {
                    r = mid - 1;
                } else {
                    l = mid + 1;
                }
            } else {
                // [mid + 1, n - 1] 有序
                if (nums[mid] < target && target <= nums[n - 1]) {
                    l = mid + 1;
                } else {
                    r = mid - 1;
                }
            }
        }
        return -1;
    }
};
```

## 分治算法经典问题

## 小结

### 平衡

平衡与分治法是密切相关的，甚至是不可分的。

在使用分治法和递归时，要尽量把问题分成规模相等，或至少是规模相近的子问题，即**平衡**。
