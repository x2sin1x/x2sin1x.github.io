---
inHomePost: false
title: Python 面向对象
---

# Python 面向对象

## 类与对象


```python
class Student:
    "学生类"
    count = 0
    
    def __init__(self, stu_id, name):
        self.stu_id = stu_id
        self.name = name
        
    def get_count(self):
        return Student.count
    
    def get_student(self):
        return self.stu_id, self.name
    
    def add_student(self, num=1):
        Student.count += num
```

`count` 是一个类变量，相当于类的静态成员，它的值被类的所有成员共享：


```python
Student.count
```


    0


```python
Student('20210001', 'Tom').count
```


    0

`self` 代表类的实例，`self` 在定义类的方法时是必须有的，虽然在调用时不必传入相应的参数。

其实，`self` 并不是 **Python** 的关键字，换成其他标识符也是没有问题的。只不过，我们约定俗成认为 `self` 特指类的实例。


```python
class Test:
    def print_obj(obj):
        print(obj)
        print(obj.__class__)
```


```python
Test().print_obj()
```

    <__main__.Test object at 0x7fa8ee7cf210>
    <class '__main__.Test'>


## 内置属性

- `__dict__`：类的属性（包含一个字典，由类的数据属性组成）
- `__doc__`：类的文档字符串
- `__name__`：类名
- `__module__`：类定义所在的模块（类的全名是 `__main__.className`，如果类位于一个导入模块 `mymod` 中，那么 `className.__module__` 等于 `mymod`）
- `__bases__`：类的所有父类构成元素（包含了一个由所有父类组成的元组）


```python
Student.__doc__
```


    '学生类'


```python
Student.__name__
```


    'Student'


```python
Student.__module__
```


    '__main__'


```python
Student.__bases__
```


    (object,)


```python
Student.__dict__
```


    mappingproxy({'__module__': '__main__',
                  '__doc__': '学生类',
                  'count': 0,
                  '__init__': <function __main__.Student.__init__(self, stu_id, name)>,
                  'get_count': <function __main__.Student.get_count(self)>,
                  'get_student': <function __main__.Student.get_student(self)>,
                  'add_student': <function __main__.Student.add_student(self, num=1)>,
                  '__dict__': <attribute '__dict__' of 'Student' objects>,
                  '__weakref__': <attribute '__weakref__' of 'Student' objects>})

## 继承与派生


```python
class Parent:
    parent_attr = 100
    
    def __init__(self):
        print('调用父类构造函数')
 
    def parent_method(self):
        print('调用父类方法')
 
    def set_attr(self, attr):
        print('父类的set_attr方法被调用')
        Parent.parent_attr = attr
 
    def get_attr(self):
        return Parent.parent_attr
```


```python
p = Parent()
```

    调用父类构造函数

```python
p.parent_method()
```

    调用父类方法

```python
p.set_attr(150)
```

    父类的set_attr方法被调用

```python
p.get_attr()
```


    150


```python
class Child(Parent):
    def __init__(self):
        print('调用子类构造函数')
        
    def child_method(self):
        print('调用子类方法')
        
    def set_attr(self, attr):
        print('子类的set_attr方法被调用，父类方法被重写')
        Parent.parent_attr = attr
```


```python
c = Child()
```

    调用子类构造函数

```python
c.child_method()
```

    调用子类方法

```python
c.parent_method()
```

    调用父类方法

```python
c.set_attr(200)
```

    子类的set_attr方法被调用，父类方法被重写

```python
c.get_attr()
```


    200

## 访问控制权限

在 **Python** 中，私有 `private` 属性/方法以两个下划线 `__` 开头，只能由类内部的方法访问，类外（类的实例不能直接访问）。

而保护 `protected` 属性/方法则以一个下划线 `_` 开头，只能由其本身及其子类访问。


```python
class TestParent:
    def __init__(self):
        self.public = 'Tom'
        self._protected = 'Hello'
        self.__private = '123456'
        
    def get_private(self):
        return self.__private
```


```python
class TestChild(TestParent):
    pass
```


```python
tp = TestParent()
tc = TestChild()
```


```python
tp.public, tc.public
```


    ('Tom', 'Tom')


```python
tp._protected, tc._protected
```


    ('Hello', 'Hello')


```python
tp.__private, tc.__private
```


    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    <ipython-input-27-79f3545709a6> in <module>
    ----> 1 tp.__private, tc.__private
    

    AttributeError: 'TestParent' object has no attribute '__private'

```python
tp.get_private(), tc.get_private()
```


    ('123456', '123456')
