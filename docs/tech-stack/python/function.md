---
inHomePost: false
title: Python 函数
---

# Python 函数

## 定义函数

函数 `function`，通常接受输入参数，并有返回值。

它负责完成某项特定任务，而且相较于其他代码，具备相对的独立性。


```python
def add(x, y):
    """Add two numbers"""
    a = x + y
    return a
```

函数通常有一下几个特征：
- 使用 `def` 关键词来定义一个函数。
- `def` 后面是函数的名称，括号中是函数的参数，不同的参数用 `,` 隔开，`def foo():` 的形式是必须要有的，参数可以为空；
- 使用缩进来划分函数的内容；
- `docstring` 用 `"""` 包含的字符串，用来解释函数的用途，可省略；
- `return` 返回特定的值，如果省略，返回 `None`。

## 使用函数

使用函数时，只需要将参数换成特定的值传给函数。

**Python** 并没有限定参数的类型，因此可以使用不同的参数类型：


```python
add(2, 3)
```


    5


```python
add('foo', 'bar')
```


    'foobar'

传入参数时，**Python** 提供了两种选项，第一种是上面使用的按照位置传入参数，另一种则是使用关键词模式，显式地指定参数的值：


```python
add(x=2, y=3)
```


    5


```python
add(y="foo", x="bar")
```


    'barfoo'

可以混合这两种模式：


```python
add(2, y=3)
```


    5

## 设定参数默认值

可以在函数定义的时候给参数设定默认值，例如：


```python
def quad(x, a=1, b=0, c=0):
    return a*x**2 + b*x + c
```

可以省略有默认值的参数：


```python
quad(2.0)
```


    4.0

可以修改参数的默认值：


```python
quad(2.0, b=3)
```


    10.0

这里混合了位置和指定两种参数传入方式，第二个 2 是传给 `a` 的：


```python
quad(2.0, 2, c=4)
```


    12.0

## 接收不定参数

使用如下方法，可以使函数接受不定数目的参数：


```python
def add(x, *args):
    total = x
    for arg in args:
        total += arg
    return total
```

这里，`*args` 表示参数数目不定，可以看成一个元组，把第一个参数后面的参数当作元组中的元素。


```python
add(1, 2, 3, 4)
```


    10


```python
add(1, 2)
```


    3

这样定义的函数不能使用关键词传入参数，要使用关键词，可以这样：


```python
def add(x, **kwargs):
    total = x
    for arg, value in kwargs.items():
        print("adding", arg)
        total += value
    return total
```

这里，`**kwargs` 表示参数数目不定，相当于一个字典，关键词和值对应于键值对。


```python
add(10, y=11, z=12, w=13)
```

    adding y
    adding z
    adding w
    


    46

再看这个例子，可以接收任意数目的位置参数和键值对参数：


```python
def foo(*args, **kwargs):
    print('args =', args)
    print('kwargs =', kwargs)
```

不过要按顺序传入参数，先传入位置参数 `args`，再传入关键词参数 `kwargs`。


```python
foo(2, 3, x='bar', z=10)
```

    args = (2, 3)
    kwargs = {'x': 'bar', 'z': 10}
    

## 返回多个值

函数可以返回多个值：


```python
from math import atan2

def to_polar(x, y):
    r = (x**2 + y**2) ** 0.5
    theta = atan2(y, x)
    return r, theta
```

事实上，**Python**将返回的两个值变成了元组：


```python
to_polar(3, 4)
```


    (5.0, 0.9272952180016122)

因为这个元组中有两个值，所以可以使用下面的方法给两个值赋值：


```python
r, theta = to_polar(3, 4)
r, theta
```


    (5.0, 0.9272952180016122)

事实上，不仅仅返回值可以用元组表示，也可以将参数用元组以这种方式传入：


```python
def add(x, y):
    """Add two numbers"""
    a = x + y
    return a
    
z = (2, 3)
add(*z)
```


    5

这里的 `*` 必不可少。

事实上，还可以通过字典传入参数来执行函数：


```python
def add(x, y):
    """Add two numbers"""
    a = x + y
    return a

w = {'x': 2, 'y': 3}
add(**w)
```


    5

同理，这里的 `**` 必不可少。

## map 方法生成序列

可以通过 `map` 的方式利用函数来生成序列：


```python
def sqr(x): 
    return x ** 2

a = [2, 3, 4]
list(map(sqr, a))
```


    [4, 9, 16]

`map(aFun, aSeq)` 将函数 `aFun` 应用到序列 `aSeq` 上的每一个元素上，返回一个列表，不管这个序列原来是什么类型。

事实上，根据函数参数的多少，`map` 可以接受多组序列，将其对应的元素作为参数传入函数：


```python
def add(x, y): 
    return x + y

a = (2, 3, 4)
b = [10, 5, 3]
list(map(add, a, b))
```


    [12, 8, 7]
