---
title: Python 集合
weight: 40
---

# Python 集合

之前看到的列表和字符串都是一种有序序列，而集合 `set` 是一种无序的序列。

因为集合是无序的，所以当集合中存在两个同样的元素的时候，Python只会保存其中的一个（唯一性）；同时为了确保其中不包含同样的元素，集合中放入的元素只能是不可变的对象（确定性）。

## 集合生成

可以用 `set()` 函数来显示的生成空集合：


```python
a = set()
type(a)
```


    set

也可以使用一个列表来初始化一个集合：


```python
a = set([1, 2, 3, 1])
a
```


    {1, 2, 3}

集合会自动去除重复元素 `1`。

可以看到，集合中的元素是用大括号 `{}` 包含起来的，这意味着可以用 `{}` 的形式来创建集合：


```python
a = {1, 2, 3, 1}
a
```


    {1, 2, 3}

但是创建空集合的时候只能用 `set` 来创建，因为在 **Python** 中 `{}` 创建的是一个空的字典：


```python
s = {}
type(s)
```


    dict

## 集合操作

假设有这样两个集合：


```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
```

### 并

两个集合的并，返回包含两个集合所有元素的集合（去除重复）。

可以用方法 `a.union(b)` 或者操作 `a | b` 实现。


```python
a.union(b)
```


    {1, 2, 3, 4, 5, 6}


```python
b.union(a)
```


    {1, 2, 3, 4, 5, 6}


```python
a | b
```


    {1, 2, 3, 4, 5, 6}

### 交

两个集合的交，返回包含两个集合共有元素的集合。

可以用方法 `a.intersection(b)` 或者操作 `a & b` 实现。


```python
a.intersection(b)
```


    {3, 4}


```python
b.intersection(a)
```


    {3, 4}


```python
a & b
```


    {3, 4}

### 差

`a` 和 `b` 的差集，返回只在 `a` 不在 `b` 的元素组成的集合。

可以用方法 `a.difference(b)` 或者操作 `a - b` 实现。


```python
a.difference(b)
```


    {1, 2}


```python
a - b
```


    {1, 2}

注意，`a - b` 与 `b - a` 并不一样，`b - a` 返回的是返回 `b` 不在 `a` 的元素组成的集合：


```python
b.difference(a)
```


    {5, 6}


```python
b - a 
```


    {5, 6}

### 对称差

`a` 和 `b` 的对称差集，返回在 `a` 或在 `b` 中，但是不同时在 `a` 和 `b` 中的元素组成的集合。

可以用方法 `a.symmetric_difference(b)` 或者操作 `a ^ b` 实现（异或操作符）。


```python
a.symmetric_difference(b)
```


    {1, 2, 5, 6}


```python
b.symmetric_difference(a)
```


    {1, 2, 5, 6}


```python
a ^ b
```


    {1, 2, 5, 6}

### 包含关系

假设现在有这样两个集合：


```python
a = {1, 2, 3}
b = {1, 2}
```

要判断 `b` 是不是 `a` 的子集，可以用 `b.issubset(a)` 方法，或者更简单的用操作 `b <= a`：


```python
b.issubset(a)
```


    True


```python
b <= a
```


    True

与之对应，也可以用 `a.issuperset(b)` 或者 `a >= b` 来判断：


```python
a.issuperset(b)
```


    True


```python
a >= b
```


    True

方法只能用来测试子集，但是操作符可以用来判断真子集：


```python
a <= a
```


    True

自己不是自己的真子集：


```python
a < a
```


    False

**注意：**

许多集合操作都有两个版本，即普通的返回副本的版本和以 `update` 结尾的会修改调用方法集合的版本。

例如，求交集的方法 `intersection` 也有上述类似的版本 `intersection_update`：


```python
print('a =', a)
print('b =', b)
a.intersection_update(b)
print('now a =', a)
```

    a = {1, 2, 3}
    b = {1, 2}
    now a = {1, 2}


## 集合方法

### add 方法向集合添加单个元素

跟列表的 `append` 方法类似，用来向集合添加单个元素。

`s.add(a)` 将元素 `a` 加入集合 `s` 中。


```python
t = {1, 2, 3}
t.add(5)
t
```


    {1, 2, 3, 5}

如果添加的是已有元素，集合不改变：


```python
t.add(3)
t
```


    {1, 2, 3, 5}

### update 方法向集合添加多个元素

跟列表的 `extend` 方法类似，用来向集合添加多个元素。

`s.update(seq)` 将 `seq` 中的元素添加到 `s` 中。


```python
t.update([5, 6, 7])
t
```


    {1, 2, 3, 5, 6, 7}

### remove 方法移除单个元素

`s.remove(ob)` 从集合 `s` 中移除元素 `ob`，如果不存在会报错。


```python
t.remove(1)
t
```


    {2, 3, 5, 6, 7}

### pop 方法弹出元素

由于集合没有顺序，不能像列表一样按照位置弹出元素，所以 `pop` 方法删除并返回集合中任意一个元素，如果集合中没有元素会报错。


```python
t.pop()
```


    2

### discard 方法

作用与 `remove` 一样，但是当元素在集合中不存在的时候不会报错。


```python
t.discard(3)
t
```


    {5, 6, 7}
