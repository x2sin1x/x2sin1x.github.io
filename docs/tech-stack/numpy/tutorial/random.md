---
inHomePost: false
title: "NumPy 随机数函数"
---

# NumPy 随机数函数

```python
import numpy as np
```

## 生成随机矩阵

$3 \times 2$ 的服从 $[0, 1)$ 均匀分布的矩阵


```python
np.random.rand(3, 2)
```


    array([[0.03586754, 0.17938111],
           [0.28677757, 0.73396444],
           [0.4283936 , 0.11322565]])

如果对均匀分布的参数由要求，可以使用下面的函数生成范围为 $[low, high)$ 的矩阵


```python
np.random.uniform(low=1, high=2, size=(2, 3))
```


    array([[1.3865865 , 1.89435718, 1.35093917],
           [1.55512695, 1.55014588, 1.69716036]])

$2 \times 3$ 的服从标准正态分布矩阵


```python
np.random.randn(2, 3)
```


    array([[-0.48992602,  1.31041614,  0.37765003],
           [-0.41608239,  0.72038314,  0.11513688]])

如果对正态分布的参数有要求，可以使用下面的函数生成均值为 `loc`、标准差为 `scale` 的矩阵


```python
np.random.normal(loc=1, scale=1, size=(2, 2))
```


    array([[1.14519121, 1.65683431],
           [1.26922318, 1.55413937]])

产生服从泊松分布的 $3 \times 2$ 矩阵，其中参数 $λ=2$


```python
np.random.poisson(lam=2, size=(3, 2))
```


    array([[3, 1],
           [3, 1],
           [7, 1]])

生成形状为 $2 \times 3$ 的矩阵，其中每个元素的值为 $[1, 10)$ 的随机整数


```python
np.random.randint(low=1, high=10, size=(2, 3))
```


    array([[1, 9, 6],
           [1, 6, 2]])

## 随机运算与概率模型

初始化随机数种子


```python
np.random.seed(0)
```


```python
x = np.arange(9).reshape(3, 3)
x
```


    array([[0, 1, 2],
           [3, 4, 5],
           [6, 7, 8]])

对原矩阵的第 1 维随机排列，并且只能对第 1 维随机排列。


```python
np.random.shuffle(x)
np.random.permutation(x)
```


    array([[0, 1, 2],
           [6, 7, 8],
           [3, 4, 5]])

摸球模型

`x` 表示球的编号，`p` 表示摸到各个球的概率。


```python
x = np.array([1, 2, 3, 4])
p = [0.3, 0.2, 0.4, 0.1]
```

`choice` 函数模拟摸一次球


```python
np.random.choice(x, p=p)
```


    3

可以不指定概率分布 `p`，那么摸到每个球的概率是等可能的。


```python
np.random.choice(x)
```


    4

从 `x` 中随机抽取 6 个球，排成 $3 \times 2$ 矩阵：


```python
np.random.choice(x, size=(3, 2))
```


    array([[4, 2],
           [4, 2],
           [3, 1]])

可以无放回地抽取，默认是有放回：


```python
np.random.choice(x, size=(3, 1), replace=False)
```


    array([[2],
           [1],
           [3]])

进行伯努利试验，验证频率依概率收敛于概率：


```python
A = np.random.choice(x, size=(100, 100), p=p)
A1 = (A==1).astype(np.int32)  # 将 A 中值为 1 的元素置 1，下同
A2 = (A==2).astype(np.int32)
A3 = (A==3).astype(np.int32)
A4 = (A==4).astype(np.int32)
count1 = np.sum(np.sum(A1))
count2 = np.sum(np.sum(A2))
count3 = np.sum(np.sum(A3))
count4 = np.sum(np.sum(A4))
count1/A.size, count2/A.size, count3/A.size, count4/A.size
```


    (0.3058, 0.201, 0.3929, 0.1003)
