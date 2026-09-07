---
inHomePost: false
title: "哈夫曼编码"
---

# 哈夫曼编码

## 问题描述

前缀码：编码的任意前缀不是其他编码。

问题：如何求得编码后二进制串总长最短的前缀码？

### 形式化定义

输入：

- 字符数 $n$ 以及各个字符的频数 $F = \langle f_1, f_2, \cdots, f_n \rangle$

输出：

- 解析结果唯一的二进制编码方案 $C = \langle c_1, c_2, \cdots, c_n \rangle$

优化目标：

$$
\min \sum_{i=1}^{n}{\left | c_i \right | f_i}
$$

其中 $c_i$ 为字符 $i$ 的编码二进制串长度。

## 问题分析

我们可以很容易想到如下策略：

1. 优先处理高频字符
2. 优先处理低频字符

上述两种策略到底哪种是最优方案呢？会不会还有其他更优的方案？

实际上，优先处理低频字符是最优的方案。为什么呢？我们首先来看看带权路径长度的概念。

## 带权路径长度

假设二叉树中每个叶子结点有一个权值 $w_i$，到根的路径长度为 $l_i$，其他结点权值为 0。则有 $n$ 个叶子结点的树的带权路径长度为

$$
\begin{aligned}
WPL = \sum_{i=0}^{n-1} w_i l_i
\end{aligned}
$$

## Huffman 树

带权路径长度达到最小的二叉树即为 Huffman 树。在 Huffman 树中，权值越大的结点离根越近。

### 构造 Huffman 树

首先构造 $n$ 棵二叉树的森林 $F = \{ T_1, T_2, \cdots, T_n \}$，每棵二叉树 $T_i$ 只有一个带权值为 $w_i$ 的根结点。然后重复以下步骤，直到只剩一棵树为止：

1. 在 $F$ 中选两棵根结点权值最小的二叉树，作为左右子树构造一棵新的二叉树，新树的根结点权值等于其左右子树根结点权值之和。
2. 在 $F$ 中删除这两棵二叉树。
3. 把新构造的二叉树加入 $F$。

## 算法代码

### 结点定义

```cpp
struct HuffmanNode
{
    int freq; // 频数
    char ch;  // 字符，如果是非叶子结点则为空
    struct HuffmanNode *left;
    struct HuffmanNode *right;
};
```

### 初始化 Huffman 树

```cpp
struct HuffmanNode *initHuffmanTree(map<char, int> &F, vector<struct HuffmanNode> &treeNode)
{
    const int chNum = F.size();
    auto p = F.begin();
    for (int i = 0; i < chNum && p != F.end(); ++i, ++p)
    {
        treeNode[i].ch = p->first;
        treeNode[i].freq = p->second;
        treeNode[i].left = treeNode[i].right = nullptr;
    }
    auto begin = treeNode.begin(), end = begin + chNum;
    while (end != treeNode.end())
    {
        auto lambda = [](struct HuffmanNode &n1,
                         struct HuffmanNode &n2) { return n1.freq < n2.freq; };
        sort(begin, end, lambda);
        end->ch = '\0';
        end->freq = begin->freq + (begin + 1)->freq;
        end->left = &(*begin);
        end->right = &(*(begin + 1));
        begin += 2;
        ++end;
    }
    return &treeNode.at(treeNode.size() - 1);
}
```

### 先序遍历

```cpp
void LDR(HuffmanNode *p,
         string &code,
         map<char, string> &encodeTable)
{
    if (!p->left && !p->right)
    {
        encodeTable[p->ch] = code;
        return;
    }
    if (p->left)
    {
        code.push_back('0');
        LDR(p->left, code, encodeTable);
        code.pop_back();
    }
    if (p->right)
    {
        code.push_back('1');
        LDR(p->right, code, encodeTable);
        code.pop_back();
    }
}
```

### 编码

```cpp
map<char, string> encode(struct HuffmanNode *root)
{
    map<char, string> encodeTable;
    string code = "";
    LDR(root, code, encodeTable);
    return encodeTable;
}
```

### 主调函数

```cpp
int main()
{
    map<char, int> F = {
        {'a', 45},
        {'b', 13},
        {'c', 12},
        {'d', 16},
        {'e', 9},
        {'f', 5}};
    vector<struct HuffmanNode> node(F.size() * 2 - 1);
    auto ans = encode(initHuffmanTree(F, node));
    for (auto &i : ans)
    {
        cout << i.first << ": " << i.second << endl;
    }
}
```
