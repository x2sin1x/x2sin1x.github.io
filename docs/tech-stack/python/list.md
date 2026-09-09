---
title: Python 列表
date: '2021-01-01'
weight: 10
---
# Python 列表

## 创建列表

在 **Python** 中，列表 `list` 是一个有序的序列。

列表用一对 `[]` 生成，中间的元素用 `,` 隔开，其中的元素不需要是同一类型，同时列表的长度也不固定。


```python
l = [1, 2.0, 'hello']
l
```


    [1, 2.0, 'hello']


```python
empty_list = []
empty_list
```


    []

空列表可以用 `[]` 或者 `list()` 生成：


```python
empty_list = list()
empty_list
```


    []

列表可以通过其他数据类型强制转换得到，例如元组：


```python
t = (1, 2, 3)
list(t)
```


    [1, 2, 3]

## 列表操作

与字符串类似，列表也支持以下的操作：

### 长度

用 `len` 查看列表长度：


```python
len(l)
```


    3

### 加法和乘法

列表加法，相当于将两个列表按顺序连接：


```python
a = [1, 2, 3]
b = [3.2, 'hello']
a + b
```


    [1, 2, 3, 3.2, 'hello']

列表与整数相乘，相当于将列表重复相加：


```python
l * 2
```


    [1, 2.0, 'hello', 1, 2.0, 'hello']

### 索引和切片

列表和字符串一样可以通过索引和分片来查看它的元素。

索引：


```python
a = [10, 11, 12, 13, 14]
a[0]
```


    10

反向索引：


```python
a[-1]
```


    14

分片：


```python
a[2:-1]
```


    [12, 13]

与字符串不同的是，列表的元素可以通过索引来修改：


```python
a = [10, 11, 12, 13, 14]
a[0] = 100
a
```


    [100, 11, 12, 13, 14]

这种赋值也适用于分片，例如，将列表的第2，3两个元素换掉：


```python
a[1:3] = [1, 2]
a
```


    [100, 1, 2, 13, 14]

事实上，对于连续的分片（即步长为 1），**Python** 采用的是整段替换的方法，两者的元素个数并不需要相同，例如，将 `[11,12]` 替换为 `[1, 2, 3, 4]`：


```python
a = [10, 11, 12, 13, 14]
a[1:3] = [1, 2, 3, 4]
a
```


    [10, 1, 2, 3, 4, 13, 14]

这意味着，可以用这种方法来删除列表中一个连续的分片：


```python
a = [10, 1, 2, 11, 12]
a[1:3] = []
a
```


    [10, 11, 12]

对于不连续（间隔 `step` 不为 1）的片段进行修改时，两者的元素数目必须一致：


```python
a = [10, 11, 12, 13, 14]
a[::2] = [1, 2, 3]
a
```


    [1, 11, 2, 13, 3]

### 删除元素

**Python** 提供了删除列表中元素的方法 `del`。

删除列表中的第一个元素：


```python
a = [1002, 'a', 'b', 'c']
del a[0]
a
```


    ['a', 'b', 'c']

删除第二到最后一个元素：


```python
a = [1002, 'a', 'b', 'c']
del a[1:]
a
```


    [1002]

删除间隔的元素：


```python
a = ['a', 1, 'b', 2, 'c']
del a[::2]
a
```


    [1, 2]

### 测试从属关系

用 `in` 来看某个元素是否在某个序列（不仅仅是列表）中，用 `not in` 来判断是否不在某个序列中。


```python
a = [10, 11, 12, 13, 14]
10 in a, 11 not in a
```


    (True, False)

也可以作用于字符串：


```python
s = 'hello world'
'he' in s, 'world' not in s
```


    (True, False)

列表中可以包含各种对象，甚至可以包含列表：


```python
a = [10, 'eleven', [12, 13]]
a[2]
```


    [12, 13]

`a[2]` 是列表，可以对它再进行索引：


```python
a[2][1]
```


    13

## 列表方法

### 不改变列表的方法

#### 列表中某个元素个数 count

`l.count(ob)` 返回列表中元素 `ob` 出现的次数。


```python
a = [11, 12, 13, 12, 11]
a.count(11)
```


    2

#### 列表中某个元素位置 index

`l.index(ob)` 返回列表中元素 `ob` 第一次出现的索引位置，如果 `ob` 不在 `l` 中会报错。


```python
a.index(12)
```


    1

### 改变列表的方法

#### 向列表添加单个元素

`l.append(ob)` 将元素 `ob` 添加到列表 `l` 的最后。


```python
a = [10, 11, 12]
a.append(11)
a
```


    [10, 11, 12, 11]

`append` 每次只添加一个元素，并不会因为这个元素是序列而将其展开：


```python
a.append([11, 12])
a
```


    [10, 11, 12, 11, [11, 12]]

#### 向列表添加序列

`l.extend(lst)` 将序列 `lst` 的元素依次添加到列表 `l` 的最后，作用相当于 `l += lst`。


```python
a = [10, 11, 12, 11]
a.extend([1, 2])
a
```


    [10, 11, 12, 11, 1, 2]

#### 插入元素

`l.insert(idx, ob)` 在索引 `idx` 处插入 `ob`，之后的元素依次后移。


```python
a = [10, 11, 12, 13, 11]
# 在索引 3 插入 'a'
a.insert(3, 'a')
a
```


    [10, 11, 12, 'a', 13, 11]

#### 移除元素

`l.remove(ob)` 会将列表中第一个出现的 `ob` 删除，如果 `ob` 不在 `l` 中会报错。


```python
a = [10, 11, 12, 13, 11]
# 移除了第一个 11
a.remove(11)
a
```


    [10, 12, 13, 11]

#### 弹出元素

`l.pop(idx)` 会将索引 `idx` 处的元素删除，并返回这个元素。


```python
a = [10, 11, 12, 13, 11]
a.pop(2)
```


    12

#### 列表排序

`l.sort()` 会将列表中的元素按照一定的规则排序：


```python
a = [10, 1, 11, 13, 11, 2]
a.sort()
a
```


    [1, 2, 10, 11, 11, 13]

也可以降序排列：


```python
a.sort(reverse=True)
a
```


    [13, 11, 11, 10, 2, 1]

如果不想改变原来列表中的值，可以使用`sorted`函数：


```python
a = [10, 1, 11, 13, 11, 2]
b = sorted(a)
print('a =', a)
print('b =', b)
```

    a = [10, 1, 11, 13, 11, 2]
    b = [1, 2, 10, 11, 11, 13]
    

还可以利用 `lambda` 表达式对一些复杂的数据类型进行排序，例如下面的例子是按照年龄排序：


```python
data_list = [
    {'Name': 'ABC', 'Age': 17},
    {'Name': 'DEF', 'Age': 19},
    {'Name': 'GHI', 'Age': 16},
    {'Name': 'JKL', 'Age': 18}
]

sorted(data_list, key=lambda x:x['Age'])
```


    [{'Name': 'GHI', 'Age': 16},
     {'Name': 'ABC', 'Age': 17},
     {'Name': 'JKL', 'Age': 18},
     {'Name': 'DEF', 'Age': 19}]

甚至可以对具有多个属性的对象进行主次关键字排序：


```python
import operator

class Student:
    def __init__(self, name, age, grade):
        self.name = name
        self.age = age
        self.grade = grade
        
    def __str__(self):
        return 'Name: {}, Age: {}, Grade: {}'.format(self.name, \
                                                    self.age, self.grade)
```

定义比较函数，先按成绩排序再按年龄排序：


```python
cmpfun = operator.attrgetter('grade', 'age')
```

验证结果：


```python
student_list = [
    Student('ABC', 17, 90),
    Student('DEF', 19, 85),
    Student('GHI', 16, 90),
    Student('JKL', 18, 95)
]

student_list.sort(key=cmpfun)
for i in student_list:
    print(i)
```

    Name: DEF, Age: 19, Grade: 85
    Name: GHI, Age: 16, Grade: 90
    Name: ABC, Age: 17, Grade: 90
    Name: JKL, Age: 18, Grade: 95
    

#### 列表反向

`l.reverse()` 会将列表中的元素从后向前排列。


```python
a = [1, 2, 3, 4, 5, 6]
a.reverse()
a
```


    [6, 5, 4, 3, 2, 1]

如果不想改变原来列表中的值，可以使用切片的方法：


```python
a = [1, 2, 3, 4, 5, 6]
b = a[::-1]
print('a =', a)
print('b =', b)
```

    a = [1, 2, 3, 4, 5, 6]
    b = [6, 5, 4, 3, 2, 1]
    

## 列表推导式

循环可以用来生成列表：


```python
values = [10, 21, 4, 7, 12]
squares = []
for x in values:
    squares.append(x**2)
squares
```


    [100, 441, 16, 49, 144]

列表推导式可以使用更简单的方法来创建这个列表：


```python
values = [10, 21, 4, 7, 12]
squares = [x**2 for x in values]
squares
```


    [100, 441, 16, 49, 144]

还可以在列表推导式中加入条件进行筛选。例如在上面的例子中，假如只想保留列表中不大于 10 的数的平方：


```python
values = [10, 21, 4, 7, 12]
squares = [x**2 for x in values if x <= 10]
squares
```


    [100, 16, 49]

也可以使用推导式生成集合和字典：


```python
square_set = {x**2 for x in values if x <= 10}
square_set
```


    {16, 49, 100}


```python
square_dict = {x: x**2 for x in values if x <= 10}
square_dict
```


    {10: 100, 4: 16, 7: 49}

再如，计算上面例子中生成的列表中所有元素的和：


```python
total = sum([x**2 for x in values if x <= 10])
total
```


    165

但是，**Python** 会生成这个列表，然后在将它放到垃圾回收机制中（因为没有变量指向它），这毫无疑问是种浪费。

为了解决这种问题，与 `xrange()` 类似，**Python** 使用产生式表达式来解决这个问题：


```python
total = sum(x**2 for x in values if x <= 10)
total
```


    165

与上面相比，只是去掉了括号，但这里并不会一次性的生成这个列表。


```python
x = range(1000000)
```

比较一下两者的用时：


```python
%timeit total = sum([i**2 for i in x])
```

    268 ms ± 717 µs per loop (mean ± std. dev. of 7 runs, 1 loop each)
    


```python
%timeit total = sum(i**2 for i in x)
```

    259 ms ± 53.9 µs per loop (mean ± std. dev. of 7 runs, 1 loop each)
