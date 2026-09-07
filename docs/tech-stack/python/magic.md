---
title: Python 魔法函数
---

# Python 魔法函数

**Python** 是面向对象编程语言，可以把 **Python** 里的基本数据类型和用户自定义的数据类型都看作是对象。对象除了可以调用它们自己的方法外，在 **Python** 中，还有一些全局的、不需要额外导包就可以被 **Python** 解释器调用的类似装饰器的函数，它们可以直接以对象为参数返回特定的值或者在某些特定的情况下实现特定的功能。这就是魔法函数 `magic method`，它们往往被一头一尾双下划线 `__<funcname>__` 包围。

## 打印信息与魔法函数

### \_\_str\_\_


```python
class StrUnavailable:
    pass
```

有时，当我们想要打印某个自定义对象时，如果直接用 `print` 方法，或者直接在 `ipython` 解释器中输出，会得到这样的输出结果：


```python
print(StrUnavailable())
```

    <__main__.StrUnavailable object at 0x061294A8>


当类没有实现 `__str__` 方法时，如果直接打印对象，**Python** 默认会输出其类名和地址。


```python
class StrAvaliable:
    def __str__(self):
        return "I'm a StrAvaliable object."
```

实现了 `__str__` 方法后，调用 `print` 方法可以直接输出 `__str__` 方法的返回值：


```python
print(StrAvaliable())
```

    I'm a StrAvaliable object.


同理，将之强制类型转换为 `str` 类型也可以得到一样的结果：


```python
str(StrAvaliable())
```


    "I'm a StrAvaliable object."

但是直接输入对象就无法输出相应值：


```python
StrAvaliable()
```


    <__main__.StrAvaliable at 0x6129be0>

### \_\_repr\_\_

**Python** 中，如果想要实现交互式的输入对象即可打印出指定信息的功能，可以在类中实现 `__repr__` 方法：


```python
class ReprAvaliable:
    def __repr__(self):
        return "I'm a ReprAvaliable object."
```


```python
ReprAvaliable()
```


    I'm a ReprAvaliable object.

如果用 `print` 打印，也可以输出指定信息：


```python
print(ReprAvaliable())
```

    I'm a ReprAvaliable object.


强制类型转换也没有问题：


```python
str(ReprAvaliable())
```


    "I'm a ReprAvaliable object."

## 容器与魔法函数

### len 与容器大小

我们知道，对 `list` 数据类型可以使用 `len` 方法返回其大小，这是因为 **Python** 对 `list` 类实现了 `__len__` 方法。由此可知，用户想要让其自定义容器可以返回大小，就可以在类中实现 `__len__` 方法：


```python
class LenAvaliable:
    def __len__(self):
        return 0
```


```python
len(LenAvaliable())
```


    0

### \[\] 与索引

- `__getitem__`：当对象的 `[]` 索引作为右值时调用此方法
- `__setitem__`：当对象的 `[]` 索引作为左值时调用此方法
- `__delitem__`：当使用 `del` 删除对象的指定索引时调用此方法


```python
class ItemAvaliable:
    def __getitem__(self, index):
        return index
    
    def __setitem__(self, index, value):
        print(index, '=', value)
        
    def __delitem__(self, index):
        print(index, 'deleted.')
```


```python
ItemAvaliable()[1]
```


    1


```python
ItemAvaliable()[1] = 2
```

    1 = 2

```python
del ItemAvaliable()[2]
```

    2 deleted.


### in 与从属判断

我们知道，对 `list` 数据类型可以直接使用 `in` 判断指定元素是否在列表内，这是因为 **Python** 对 `list` 类实现了 `__contains__` 方法。由此可知，用户想要让其自定义容器可以判断从属关系，就可以在类中实现 `__contains__` 方法：


```python
class ContainsAvaliable:
    def __contains__(self, item):
        return True
```


```python
False in ContainsAvaliable()
```


    True

### 迭代器

- 迭代是Python最强大的功能之一，是访问容器元素的一种方式。
- 迭代器是一个可以记住遍历的位置的对象。
- 迭代器对象从集合的第一个元素开始访问，直到所有的元素被访问完结束。迭代器只能往前不会后退。
- 迭代器有两个基本的方法：`iter()` 和 `next()`。
- 字符串，列表或元组对象都可用于创建迭代器


```python
l = [1, 2, 3, 4]
it = iter(l)
next(it), next(it), next(it), next(it)
```


    (1, 2, 3, 4)

把一个类作为一个迭代器使用需要在类中实现两个方法 `__iter__()` 与 `__next__()`：


```python
class MyIter:
    def __iter__(self):
        self.a = 1
        return self
 
    def __next__(self):
        x = self.a
        self.a += 1
        return x

my_iter = iter(MyIter())
for i in range(5):
    print(next(my_iter))
```

    1
    2
    3
    4
    5


## 类与魔法函数

### 构造函数与 \_\_new\_\_ & \_\_init\_\_


```python
class Constructor:
    def __init__(self):
        print('__init__() called.')
    
    def __new__(self):
        print('__new__() called.')
```

当实例化一个对象时，先调用 `__new__` 方法，然后调用 `__init__` 方法。其中 `__new__` 方法创建类并返回这个类的实例，而 `__init__` 只是将传入的参数来初始化该实例。


```python
Constructor()
```

    __new__() called.


### 析构函数与 \_\_del\_\_


```python
class Destructor:
    def __del__(self):
        print('__del__() called.')
```

`__del__` 方法会在对象的引用计数到零后执行：


```python
x = Destructor()
del x
```

    __del__() called.


### . 与属性

- `__getattr__`：当对象通过 `.` 获取的属性作为右值时调用此方法
- `__setattr__`：当对象通过 `.` 获取的属性作为左值时调用此方法
- `__delattr__`：当使用 `del` 删除对象的指定属性时调用此方法


```python
class AttrAvaliable:
    def __getattr__(self, item):
        print('__getattr__ called.')

    def __setattr__(self, key, value):
        print('__setattr__ called.')

    def __delattr__(self, item):
        print('__delattr__ called.')
```


```python
attr = AttrAvaliable()
```


```python
attr.name
```

    __getattr__ called.

```python
attr.age = 1
```

    __setattr__ called.

```python
del attr.sex
```

    __delattr__ called.


### 模拟函数行为

如果需要让一个对象可以通过 `objname()` 的方法模拟函数调用，可以让类实现 `__call__` 方法：


```python
class Callable:
    def __call__(self, *args, **kwargs):
        print('args:', args)
        print('kwargs:', kwargs)
```


```python
Callable()(*(1, 2, 3, 4), **{'a': 1, 'b': 2})
```

    args: (1, 2, 3, 4)
    kwargs: {'a': 1, 'b': 2}
