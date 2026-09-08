---
title: Python 元组
weight: 20
---

# Python 元组

## 基本操作

与列表相似，元组 `tuple` 也是个有序序列，但是元组是不可变的，用 `()` 生成。


```python
t = (10, 11, 12, 13, 14)
t
```


    (10, 11, 12, 13, 14)

可以索引，切片：


```python
t[0]
```


    10


```python
t[1:3]
```


    (11, 12)

## 生成元组

由于 `()` 在表达式中被应用，只含有单个元素的元组容易和表达式混淆，所以采用下列方式定义只有一个元素的元组：


```python
a = (10,)
a, type(a)
```


    ((10,), tuple)


```python
a = (10)
a, type(a)
```


    (10, int)

将列表转换为元组：


```python
a = [10, 11, 12, 13, 14]
tuple(a)
```


    (10, 11, 12, 13, 14)

## 元组方法

由于元组是不可变的，所以只能有一些不可变的方法，例如计算元素个数 `count` 和元素位置 `index`，用法与列表一样。


```python
a.count(10)
```


    1


```python
a.index(12)
```


    2

## 元组与逗号表达式

**Python**中有将多个变量用逗号 `,` 隔开的语法，表示多组变量的赋值或返回。而如果将整个逗号表达式看作一个整体，它相当于一个元组类型的变量。例如有下列函数定义：


```python
def foo(l:list):
    """return min & max of a list"""
    return min(l), max(l)
```

使用下面的方法来调用此函数：


```python
l = list(range(10))
l_min, l_max = foo(l)

print('l_min =', l_min)
print('l_max =', l_max)
```

    l_min = 0
    l_max = 9


如果只使用一个变量接收 `foo` 函数的返回值：


```python
ans = foo(l)
ans  # tuple
```


    (0, 9)

如果只需要最大值而不需要最小值，可以使用占位符 `_`：


```python
_, l_max = foo(l)
l_max
```


    9
