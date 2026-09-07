---
title: "作业"
---

# 作业

## [搜索二维矩阵 II](https://leetcode-cn.com/problems/search-a-2d-matrix-ii/)

### 问题描述

编写一个高效的算法来搜索 $m \times n$ 矩阵 `matrix` 中的一个目标值 `target`。该矩阵具有以下特性：

- 每行的元素从左到右升序排列。
- 每列的元素从上到下升序排列。

### 问题分析

可以巧妙地利用矩阵的有序性，使用分治算法来求解。首先从右上角开始，判断：

- 如果 `target` 和当前元素相等，则找到，算法返回 `true`。
- 如果 `target` 比当前元素小，说明 `target` 只可能在当前列的左半边矩阵中。递归调用即可。
- 如果 `target` 比当前元素大，说明 `target` 只可能在当前行的下半部矩阵中。递归调用即可。

注意递归调用前做判断防止越界。

### 算法代码

**递归函数**

```cpp
bool recSearchMatrix(vector<vector<int>> &matrix, const int m, const int n, int row, int col, int target)
/*
 * @param matrix: 矩阵
 * @param m: 行数
 * @param n: 列数
 * @param row: 当前行
 * @param col: 当前列
 * @param target: 目标值
*/
{
    // 找到 target
    if (target == matrix[row][col])
    {
        return true;
    }
    // 小于 target 则在左半边矩阵当中找
    else if (target < matrix[row][col] && col > 0)
    {
        return recSearchMatrix(matrix, m, n, row, col - 1, target);
    }
    // 大于 target 则在下半部矩阵当中找
    else if (row + 1 < m)
    {
        return recSearchMatrix(matrix, m, n, row + 1, col, target);
    }
    // 找不到 target
    else
    {
        return false;
    }
}
```

**主调函数**

```cpp
bool searchMatrix(vector<vector<int>> &matrix, int target)
{
    const int m = matrix.size();
    const int n = matrix[0].size();
    // 从右上角开始递归搜索
    return recSearchMatrix(matrix, m, n, 0, n - 1, target);
}
```

### 算法分析

- 时间复杂度：$O(m+n)$
- 空间复杂度：$O(1)$

## [前 k 个高频元素](https://leetcode-cn.com/problems/top-k-frequent-elements/)

### 问题描述

给你一个整数数组 `nums` 和一个整数 `k`，请你返回其中出现频率前 `k` 高的元素。你可以按任意顺序返回答案。

### 问题分析

本题与[数组中的第 k 个最大元素](https://leetcode-cn.com/problems/kth-largest-element-in-an-array/)有诸多相似之处。不论是求前 `k` 个，还是第 `k` 个，其思想都是类似的。

与之不同的是，本题是要找高频元素，排序的对象不是元素本身，而是元素的频率。因此，首先需要建立起元素和与之对应频率的哈希表。这只需要对数组遍历一遍即可，时间复杂度为 $O(n)$。那么接下来就相当于找前 `k` 个最大元素了，这里提供如下几种思路。

#### 最大堆

最大堆即根结点最大的完全二叉树。我们将频率数组看作是完全二叉树，每次循环将之调整为最大堆，弹出根结点。这样循环 `k` 次就可以得到前 `k` 个频率最高的元素了。

这个方法比较简单，也很容易想到。时间复杂度是 $O(k\log{n})$。

#### 最小堆

最小堆即根结点最小的完全二叉树。和最大堆略有不同的是，我们将频率数组存入一个空完全二叉树中，每次插入一个数值-频率键值对，并将之调整为最小堆。我们构造的最小堆的大小不能超过 `k`，因为我们只需要找前 `k` 个频率最高的元素即可。如果插入时发现堆的大小已经达到 `k`，则需要判断当前插入元素的频率和堆顶元素的频率的大小关系：

- 如果堆顶元素的频率更大，那么不插入当前元素。
- 如果堆顶元素的频率更小，那么弹出堆顶元素，插入当前元素。

如此遍历一次频率数组后，就建立起了大小为 `k` 的最小堆，堆中的所有元素都是我们需要的结果。

最小堆的方法比最大堆更巧妙，时间复杂度更低，为 $O(k\log{k})$。

#### 快速排序

快速排序有一个很大的特点是，每一趟排序完以后，基准两边的元素都是比基准大（或小）的，也就是相对有序的。基于此，可以结合分治的思想将找前 `k` 个元素的问题归结到某个子问题当中。

我们将频率数组用快速排序降序排序一趟后，基准左边的数值都比基准大，基准右边的数值都比基准小。因此前 `k` 个元素只存在如下两种情况：

- `k` 的值小于基准以及基准左边的所有元素数量的和，说明前 `k` 个元素在由基准以及基准左边的所有元素构成的新的数组中。
- `k` 的值大于基准以及基准左边的所有元素数量的和，说明基准以及基准左边的所有元素肯定被包含在前 `k` 个元素之中，剩下的元素在由基准右边的所有元素构成的新的数组中。

如此递归下去就可以找到前 `k` 个频率最高的元素。

### 算法代码

#### 最小堆

**主调函数**

```cpp
vector<int> topKFrequent(vector<int> &nums, int k)
{
    unordered_map<int, int> hash;
    // 初始化哈希表，键为数值，值为频率
    for (const int &n : nums)
    {
        ++hash[n];
    }
    priority_queue<pair<int, int>, vector<pair<int, int>>, decltype(&cmpFrequent)> heap(cmpFrequent);
    // 不断插入元素，并调整为最小堆
    for (const auto &h : hash)
    {
        if (heap.size() < k)
        {
            heap.emplace(h);
        }
        // 只调整前 k 个元素
        else if (heap.top().second < h.second)
        {
            heap.pop(); // 频率太小，直接弹出
            heap.emplace(h);
        }
    }
    // 最后只剩下频率较高的前 k 个元素
    vector<int> ans;
    while (!heap.empty())
    {
        ans.push_back(heap.top().first);
        heap.pop();
    }
    return ans;
}
```

**谓词**

该谓词是用于给优先队列（堆）模板 `priority_queue` 提供自定义数据类型的比较方法参数。本题比较的是元素的频率，即键值对中的值 `second`。另外，`priority_queue` 默认建立最大堆，要建立最小堆则把比较的不等号改变方向即可。

```cpp
// 比较频率，由于建立最小堆，谓词应为 x.value > y.value
static bool cmpFrequent(pair<int, int> &x, pair<int, int> &y)
{
    return x.second > y.second;
}
```

#### 快速排序

**主调函数**

```cpp
vector<int> topKFrequent(vector<int> &nums, int k)
{
    srand(time(NULL));
    unordered_map<int, int> hash;
    // 初始化哈希表，键为数值，值为频率
    for (auto &n : nums)
    {
        hash[n]++;
    }
    // 哈希表存入容器中
    vector<pair<int, int>> values;
    for (auto &kv : hash)
    {
        values.push_back(kv);
    }
    vector<int> ans;
    quickSort(values, 0, values.size(), ans, k);
    return ans;
}
```

**快速排序**

```cpp
void quickSort(vector<pair<int, int>> &v, int start, int end, vector<int> &ans, int k)
/*
 * @param v: 哈希表，统计频率
 * @param start: 左闭
 * @param end: 右开
 * @param ans: 保存前 k 个高频元素的容器
 *
*/
{
    if (end - start <= 1)
    {
        return;
    }
    int picked = rand() % (end - start) + start; // 随机挑选某一个位置作为基准
    swap(v[picked], v[start]);                   // 将基准放到首位
    int pivot = v[start].second; // 基准的频率
    int index = start; // 最终指向基准的位置
    for (int i = start + 1; i < end; i++)
    {
        // 频率高的元素换到左边
        if (v[i].second >= pivot)
        {
            swap(v[index + 1], v[i]);
            index++;
        }
    }
    // 如下交换后，index 左边的元素都比 index 大，右边的元素都比 index 小
    swap(v[start], v[index]);
    // 只需要找前 k 个元素，在部分有序的情况下判断是不是只需要在左边找
    if (k <= index - start)
    {
        quickSort(v, start, index, ans, k);
    }
    else
    {
        // 将已知的高频元素（左边+基准）都存入结果中
        for (int i = start; i <= index; i++)
        {
            ans.push_back(v[i].first);
        }
        // 到右边找，问题规模减小，变为找前 k - (index - start + 1) 高频的元素
        if (k > index - start + 1)
        {
            quickSort(v, index + 1, end, ans, k - (index - start + 1));
        }
    }
}
```

### 算法分析

|   方法   |  时间复杂度   | 空间复杂度 |
| :------: | :-----------: | :--------: |
|  最大堆  | $O(k\log{n})$ |   $O(n)$   |
|  最小堆  | $O(k\log{k})$ |  $O(n+k)$  |
| 快速排序 |    $O(n)$     |   $O(n)$   |

## [数组中的逆序对](https://leetcode-cn.com/problems/shu-zu-zhong-de-ni-xu-dui-lcof/)

### 问题描述

在数组中的两个数字，如果前面一个数字大于后面的数字，则这两个数字组成一个逆序对。输入一个数组，求出这个数组中的逆序对的总数。

### 问题分析

本题是归并排序的一个典型应用。归并排序的思想就是分治，想要排好整个数组的顺序，首先子数组有序。如此将数组不断划分下去，最后形成一个个大小为 1 的数组。我们认为大小为 1 的数组是有序的。然后我们合并子问题解，可以利用合并有序数组（链表）的算法，使用 3 个指针即可。如此合并下去最终得到原始问题解。

那么求逆序对和归并排序有什么关系呢？是因为我们在合并有序数组时，非常容易就能够判断存在多少对逆序对。只要左指针指向的数比右指针指向的数大，那么至少可以判断左边数组剩下的所有数都比右指针指向的数大，也就找到了若干对逆序对。如此循环下去可以得到两个子数组所合并成的新的数组的逆序对数。

### 算法代码

**主调函数**

```cpp
int reversePairs(vector<int> &nums)
{
    vector<int> temp(nums.size());
    return countInver(nums, 0, nums.size(), temp);
}
```

**合并有序数组**

一边合并一边统计逆序对数。

```cpp
int mergeCount(vector<int> &nums, int begin, int mid, int end, vector<int> &temp)
{
    int i = begin, j = mid, k = 0, count = 0;
    // 合并有序数组
    while (i < mid && j < end)
    {
        if (nums[i] <= nums[j])
        {
            temp[k++] = nums[i++];
        }
        else
        {
            // 左边有元素比右边大，说明存在逆序对，且左边剩余的元素个数就等于逆序对数
            temp[k++] = nums[j++];
            count += mid - i;
        }
    }
    while (i < mid)
    {
        temp[k++] = nums[i++];
    }
    while (j < end)
    {
        temp[k++] = nums[j++];
    }
    // 排序结果回填
    for (int i = 0; i < end - begin; ++i)
    {
        nums[begin + i] = temp[i];
    }
    return count;
}
```

**归并排序**

归并排序递归算法。

```cpp
int countInver(vector<int> &nums, int begin, int end, vector<int> &temp)
{
    if (end - begin <= 1)
    {
        return 0;
    }
    int mid = (begin + end) / 2;
    int countLeft = countInver(nums, begin, mid, temp);
    int countRight = countInver(nums, mid, end, temp);
    int countBoth = mergeCount(nums, begin, mid, end, temp);
    return countLeft + countRight + countBoth;
}
```

### 算法分析

- 时间复杂度：$O(n\log{n})$
- 空间复杂度：$O(n)$
