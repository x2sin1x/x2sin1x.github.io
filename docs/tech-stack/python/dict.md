---
title: Python 字典
date: '2021-01-01'
weight: 30
---
# Python 字典

字典 `dictionary`，在一些编程语言中也称为 `hash` 或 `map`，是一种由键值对组成的数据结构。

## 基本操作

### 空字典

**Python** 使用 `{}` 或者 `dict()` 来创建一个空的字典：


```python
a = {}
type(a)
```


    dict


```python
a = dict()
type(a)
```


    dict

有了dict之后，可以用索引键值的方法向其中添加元素，也可以通过索引来查看元素的值：

### 插入键值


```python
a["one"] = "this is number 1"
a["two"] = "this is number 2"
a
```


    {'one': 'this is number 1', 'two': 'this is number 2'}

### 查看键值


```python
a['one']
```


    'this is number 1'

### 更新键值


```python
a["one"] = "this is number 1, too"
a
```


    {'one': 'this is number 1, too', 'two': 'this is number 2'}

### 初始化字典

可以看到，Python使用`key: value`这样的结构来表示字典中的元素结构，事实上，可以直接使用这样的结构来初始化一个字典：


```python
b = {'one': 'this is number 1', 'two': 'this is number 2'}
b['one']
```


    'this is number 1'

### 字典没有顺序

当我们 `print` 一个字典时，**Python** 并不一定按照插入键值的先后顺序进行显示,因为字典中的键本身不一定是有序的。


```python
print(a)
```

    {'one': 'this is number 1, too', 'two': 'this is number 2'}

```python
print(b)
```

    {'one': 'this is number 1', 'two': 'this is number 2'}


因此，**Python**中不能用支持用数字索引按顺序查看字典中的值，而且数字本身也有可能成为键值，这样会引起混淆：

### 键必须是不可变的类型

出于hash的目的，Python中要求这些键值对的**键**必须是**不可变**的，而值可以是任意的Python对象。

一个表示近义词的字典：


```python
synonyms = {}
synonyms['mutable'] = ['changeable', 'variable', 'varying', 'fluctuating',
                       'shifting', 'inconsistent', 'unpredictable', 'inconstant',
                       'fickle', 'uneven', 'unstable', 'protean']
synonyms['immutable'] = ['fixed', 'set', 'rigid', 'inflexible', 
                         'permanent', 'established', 'carved in stone']
synonyms
```


    {'mutable': ['changeable',
      'variable',
      'varying',
      'fluctuating',
      'shifting',
      'inconsistent',
      'unpredictable',
      'inconstant',
      'fickle',
      'uneven',
      'unstable',
      'protean'],
     'immutable': ['fixed',
      'set',
      'rigid',
      'inflexible',
      'permanent',
      'established',
      'carved in stone']}

另一个例子：


```python
# 定义四个字典
e1 = {'mag': 0.05, 'width': 20}
e2 = {'mag': 0.04, 'width': 25}
e3 = {'mag': 0.05, 'width': 80}
e4 = {'mag': 0.03, 'width': 30}
# 以字典作为值传入新的字典
events = {500: e1, 760: e2, 3001: e3, 4180: e4}
events
```


    {500: {'mag': 0.05, 'width': 20},
     760: {'mag': 0.04, 'width': 25},
     3001: {'mag': 0.05, 'width': 80},
     4180: {'mag': 0.03, 'width': 30}}

键（或者值）的数据类型可以不同：


```python
people = [
    {'first': 'Sam', 'last': 'Malone', 'name': 35},
    {'first': 'Woody', 'last': 'Boyd', 'name': 21},
    {'first': 'Norm', 'last': 'Peterson', 'name': 34},
    {'first': 'Diane', 'last': 'Chambers', 'name': 33}
]
people
```


    [{'first': 'Sam', 'last': 'Malone', 'name': 35},
     {'first': 'Woody', 'last': 'Boyd', 'name': 21},
     {'first': 'Norm', 'last': 'Peterson', 'name': 34},
     {'first': 'Diane', 'last': 'Chambers', 'name': 33}]

### 使用 dict 初始化字典

除了通常的定义方式，还可以通过 `dict()` 强制类型转换来生成字典：


```python
inventory = dict(
    [('foozelator', 123),
     ('frombicator', 18), 
     ('spatzleblock', 34), 
     ('snitzelhogen', 23)
    ])
inventory
```


    {'foozelator': 123, 'frombicator': 18, 'spatzleblock': 34, 'snitzelhogen': 23}

利用索引直接更新键值对：


```python
inventory['frombicator'] += 1
inventory
```


    {'foozelator': 123, 'frombicator': 19, 'spatzleblock': 34, 'snitzelhogen': 23}

### 适合做键的类型

在不可变类型中，整数和字符串是字典中最常用的类型；而浮点数通常不推荐用来做键，因为浮点数存在精度问题。

有时候，也可以使用元组作为键值，例如，可以用元组做键来表示从第一个城市飞往第二个城市航班数的多少：


```python
connections = {}
connections[('New York', 'Seattle')] = 100
connections[('Austin', 'New York')] = 200
connections[('New York', 'Austin')] = 400
```

元组是有序的，因此`('New York', 'Austin')`和`('Austin', 'New York')`是两个不同的键：


```python
connections[('Austin', 'New York')], connections[('New York', 'Austin')]
```


    (200, 400)

## 字典方法

### get 方法返回键值

`d.get(key, default = None)` 返回字典中键 `key` 对应的值，如果没有这个键，返回 `default` 指定的值（默认是 `None`）。


```python
a = {}
a["one"] = "this is number 1"
a["two"] = "this is number 2"
```

使用 `get` 方法：


```python
a.get("three")
```

指定默认值参数：


```python
a.get("three", "undefined")
```


    'undefined'

### pop 方法删除元素

`d.pop(key, default = None)` 删除并返回字典中键 `key` 对应的值，如果没有这个键，返回 `default` 指定的值（默认是 `None`）。


```python
a
```


    {'one': 'this is number 1', 'two': 'this is number 2'}

弹出并返回值：


```python
a.pop("two")
```


    'this is number 2'


```python
a
```


    {'one': 'this is number 1'}

弹出不存在的键值：


```python
a.pop("two", 'not exist')
```


    'not exist'

与列表一样，`del` 函数可以用来删除字典中特定的键值对，例如：


```python
del a["one"]
a
```


    {}

### update 方法更新字典

`d.update(newd)` 将字典 `newd` 中的内容更新到 `d` 中去。


```python
person = {}
person['first'] = "Jmes"
person['last'] = "Maxwell"
person['born'] = 1831
person
```


    {'first': 'Jmes', 'last': 'Maxwell', 'born': 1831}

把 `first` 改成 `James`，同时插入 `middle` 的值 `Clerk`：


```python
person_modifications = {'first': 'James', 'middle': 'Clerk'}
person.update(person_modifications)
person
```


    {'first': 'James', 'last': 'Maxwell', 'born': 1831, 'middle': 'Clerk'}

### in 查询字典中是否有该键


```python
barn = {'cows': 1, 'dogs': 5, 'cats': 3}
```

`in` 可以用来判断字典中是否有某个特定的键：


```python
'chickens' in barn
```


    False


```python
'cows' in barn
```


    True

## 遍历字典

- `d.keys()`：返回一个由所有键组成的列表；
- `d.values()`：返回一个由所有值组成的列表；
- `d.items()`：返回一个由所有键值对元组组成的列表；


```python
d = {'Name': 'Runoob', 'Age': 7, 'Class': 'First'}
```

常常与 `for` 循环结合使用：


```python
for key in d.keys():
    print('Key:', key)
```

    Key: Name
    Key: Age
    Key: Class

```python
for value in d.values():
    print('Value:',value)
```

    Value: Runoob
    Value: 7
    Value: First

```python
for key, value in d.items():
    print('Key:', key)
    print('Value:', value)
```

    Key: Name
    Value: Runoob
    Key: Age
    Value: 7
    Key: Class
    Value: First
