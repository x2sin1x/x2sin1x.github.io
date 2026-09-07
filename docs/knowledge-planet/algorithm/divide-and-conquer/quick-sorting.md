---
inHomePost: false
title: "快速排序"
---

# 快速排序

## 基本思想

- **Partition**：任取一元素 `x` 为基准，小于 `x` 的元素放在 `x` 左边，大于等于 `x` 的元素放在 `x` 右边。
- 对左、右部分递归执行上一步骤直至只有一个元素。

## 算法代码

```cpp
void quickSort(int *arr, int begin, int end)
{
    if (end - begin <= 1) // 递归终止条件
    {
        return;
    }
    int i = begin, j = end - 1, key = arr[begin]; // 首元素视为基准
    while (i < j)
    {
        for (; i < j && arr[j] >= key; --j)
            ; // 先从右向左扫描，将小于基准的元素填入左边的坑中
        if (i < j)
        {
            arr[i++] = arr[j];
        }
        for (; i < j && arr[i] <= key; ++i)
            ; // 再从左向右扫描，将大于基准的元素填入右边的坑中
        if (i < j)
        {
            arr[j--] = arr[i];
        }
    }
    arr[i] = key; // 最后将大小居中的数回填
    quickSort(arr, begin, i);
    quickSort(arr, i + 1, end);
}
```

## 算法分析

每一趟执行 Partition 时，需要遍历数组一遍，并且将原问题分成两个快速排序的子问题。因此时间复杂度为

$$
\begin{aligned}
T(n) &= 2 T \left( \dfrac{n}{2} \right) + O(n) \\
&= O(n \log {n})
\end{aligned}
$$

### 最好情况

在最好情况下，每次划分对一个记录定位后，该记录的左侧子序列与右侧子序列的长度相同。因此

$$
\begin{aligned}
T(n) \leqslant 2 T \left( \dfrac{n}{2} \right) + n = O(n \log {n})
\end{aligned}
$$

### 最坏情况

在最坏情况下，待排序记录序列正序或逆序。每次划分只得到一个比上一次划分少一个记录的子序列，另一个子序列为空。此时，必须经过 $n-1$ 次递归调用才能把所有记录定位，而且第 $i$ 趟划分需要经过 $n-i$ 次关键码的比较才能找到第 $i$ 个记录的基准位置。因此，总的比较次数为：

$$
\begin{aligned}
\sum_{i=1}^{n-1} (n-i) = \dfrac{n(n-1)}{2} = O(n^2)
\end{aligned}
$$

时间复杂度为

$$
\begin{aligned}
T(n) = T \left( n-1 \right) + O(n)
\end{aligned}
$$

### 小结

- 快速排序算法的性能取决于划分的对称性。
- 基于比较的排序方法，最好的算法不会好于 $O(n \log {n})$，因为比较搜索树中 $2^h \geqslant n!$，从而 $h \geqslant n \log {n}$。

## 改进的快速排序

在快速排序算法的每一步中，当数组还没有被划分时，可以在数组 `arr` 中随机选出一个元素作为划分基准。这样可以使划分基准的选择是随机的，从而可以期望划
分是较对称的。
