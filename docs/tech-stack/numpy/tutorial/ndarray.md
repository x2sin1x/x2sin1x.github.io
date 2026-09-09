---
title: "NumPy ndarray 对象"
date: 2021-04-17T16:26:12+08:00
weight: 10
---
# NumPy ndarray 对象

```python
import numpy as np
```

## 创建数组

### 直接创建

使用当前内存的随机值创建指定形状的矩阵


```python
np.empty([3, 2], dtype=int)
```


    array([[0, 0],
           [0, 0],
           [0, 0]])

创建全 1 矩阵


```python
np.ones((3, 2), dtype=np.int)
```


    array([[1, 1],
           [1, 1],
           [1, 1]])

创建全 0 矩阵


```python
np.zeros((2, 3))
```


    array([[0., 0., 0.],
           [0., 0., 0.]])

用指定的值 `fill_value` 填充矩阵


```python
np.full((3, 3), fill_value=-1)
```


    array([[-1, -1, -1],
           [-1, -1, -1],
           [-1, -1, -1]])

创建单位矩阵


```python
np.eye(3)
```


    array([[1., 0., 0.],
           [0., 1., 0.],
           [0., 0., 1.]])

### 从指定范围创建

#### np.arange 创建序列

`np.arange` 类似 **Python** 标准库函数 `range`


```python
np.arange(10)
```


    array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

可以指定起始值，生成的数范围为左闭右开区间：


```python
np.arange(2, 10)
```


    array([2, 3, 4, 5, 6, 7, 8, 9])

可以指定步长：


```python
np.arange(2, 10, 2)
```


    array([2, 4, 6, 8])

可以指定数据类型：


```python
np.arange(10, dtype=np.float)
```


    array([0., 1., 2., 3., 4., 5., 6., 7., 8., 9.])

#### np.linspace 创建等差数列

`np.linspace` 创建一个由等差数列构成的一维数组


```python
np.linspace(start=0, stop=2*np.pi, num=12)
```


    array([0.        , 0.57119866, 1.14239733, 1.71359599, 2.28479466,
           2.85599332, 3.42719199, 3.99839065, 4.56958931, 5.14078798,
           5.71198664, 6.28318531])

默认情况下 `endpoint` 参数值为 `True`，表示包括右端点。值为 `False` 时则不包括右端点：


```python
np.linspace(0, 2*np.pi, 11, endpoint=False)
```


    array([0.        , 0.57119866, 1.14239733, 1.71359599, 2.28479466,
           2.85599332, 3.42719199, 3.99839065, 4.56958931, 5.14078798,
           5.71198664])

#### np.logspace 创建等比数列

`np.logspace` 和 `np.linspace` 类似，用于生成等比数列。参数 `base` 表示底数。


```python
np.logspace(start=0, stop=9, num=10, base=2)
```


    array([  1.,   2.,   4.,   8.,  16.,  32.,  64., 128., 256., 512.])

### 从已有数组创建

通过 **Python** 基本数据类型创建：


```python
np.array([0, 1, 2, 3])
```


    array([0, 1, 2, 3])


```python
np.array((-1, 1, -2, 2))
```


    array([-1,  1, -2,  2])


```python
np.array([[1, 2], [9, 8], (0.1, 0.2)])
```


    array([[1. , 2. ],
           [9. , 8. ],
           [0.1, 0.2]])

用 `np.asarray` 时不会在内存中拷贝副本，而是直接将 **Python** 基本数据类型转化为 `np.ndarray`


```python
A = [[1, 2, 3], [4, 5, 6]]
np.asarray(A)
```


    array([[1, 2, 3],
           [4, 5, 6]])

可以用参数 `order` 来指定数组在内存中存储是行优先 `C` 还是列优先 `F`：


```python
np.asarray(A, order='C'), np.asarray(A, order='F')
```


    (array([[1, 2, 3],
            [4, 5, 6]]),
     array([[1, 2, 3],
            [4, 5, 6]]))

根据已有 `np.ndarray` 的形状生成形状相同的矩阵：


```python
A = np.array([[1, 2], [3, 4], [5, 6]])
np.zeros_like(A), np.ones_like(A), np.full_like(A, 2)
```


    (array([[0, 0],
            [0, 0],
            [0, 0]]),
     array([[1, 1],
            [1, 1],
            [1, 1]]),
     array([[2, 2],
            [2, 2],
            [2, 2]]))

接受 `buffer` 输入参数，以流的形式读入转化成 `np.ndarray` 对象：


```python
s = b'Hello World'
np.frombuffer(s, dtype='S1')
```


    array([b'H', b'e', b'l', b'l', b'o', b' ', b'W', b'o', b'r', b'l', b'd'],
          dtype='|S1')

从可迭代对象中建立 `np.ndarray` 对象，返回一维 `np.ndarray` 数组：


```python
l = range(5)
it = iter(l)
np.fromiter(it, dtype=float)
```


    array([0., 1., 2., 3., 4.])

## ndarray 对象的方法

返回原矩阵重置形状的副本：


```python
A = np.arange(6)
B = A.reshape(3, 2)
A, B
```


    (array([0, 1, 2, 3, 4, 5]),
     array([[0, 1],
            [2, 3],
            [4, 5]]))

直接重置形状而不返回任何值：


```python
A = np.arange(6)
A.resize(2, 3)
A
```


    array([[0, 1, 2],
           [3, 4, 5]])

返回原矩阵“拉直”后的副本：


```python
A = np.zeros((2, 2, 3), dtype=np.int32)
B = A.flatten()
A, B
```


    (array([[[0, 0, 0],
             [0, 0, 0]],
     
            [[0, 0, 0],
             [0, 0, 0]]]),
     array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))

返回原矩阵中每个元素强制类型转换后的副本：


```python
A = np.arange(6)
B = A.astype(np.float32)
A, B
```


    (array([0, 1, 2, 3, 4, 5]), array([0., 1., 2., 3., 4., 5.], dtype=float32))

## ndarray 对象的属性


```python
A = np.empty((2, 3, 2), dtype=np.complex)
```

秩，即轴的数量或维度的数量（非矩阵的秩）


```python
A.ndim
```


    3

形状


```python
A.shape
```


    (2, 3, 2)

元素个数，即形状元组各个分量之积


```python
A.size
```


    12

数据类型


```python
A.dtype
```


    dtype('complex128')

每个元素所占字节数


```python
A.itemsize
```


    16

取实部和虚部


```python
A.real, A.imag
```


    (array([[[6.79038653e-313, 2.37663529e-312],
             [2.05833592e-312, 8.48798317e-313],
             [1.40051722e-312, 1.37929726e-312]],
     
            [[2.46151512e-312, 8.48798317e-313],
             [2.16443571e-312, 2.46151512e-312],
             [2.12199579e-313, 1.40051722e-312]]]),
     array([[[6.79038653e-313, 2.05833592e-312],
             [2.18565567e-312, 8.70018275e-313],
             [1.29441743e-312, 2.05833592e-312]],
     
            [[2.37663529e-312, 2.37663529e-312],
             [2.35541533e-312, 1.06099790e-312],
             [9.33678148e-313, 2.18568966e-312]]]))

内存信息


```python
A.flags
```


      C_CONTIGUOUS : True
      F_CONTIGUOUS : False
      OWNDATA : True
      WRITEABLE : True
      ALIGNED : True
      WRITEBACKIFCOPY : False
      UPDATEIFCOPY : False
