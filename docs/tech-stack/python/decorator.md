---
inHomePost: false
title: "Python 装饰器"
---

# Python 装饰器

## 铺垫

### 函数也是对象

**Python** 是面向对象的高级程序设计语言，所有的概念最终都可以认为是类和对象。面向过程的函数同样也不例外。


```python
def foo():
    print('Hello World!')
```

下面我们将函数对象（即函数名，不进行 `()` 函数调用）赋值给另外的一个变量，然后用这个变量来进行函数调用。


```python
func = foo
func()
```

    Hello World!
    

### 函数的嵌套定义

**Python** 支持在函数中定义函数，就像 **Java** 的内部类一样。不过，这样定义的函数在外函数体外不能被访问，而当外函数体被调用时，内部的函数才会被定义。


```python
def foo():
    dis = 'Hello world!'
    
    def display(s):
        print('display:', s)
    
    print('foo:', dis)
    display(dis)
```

当我们直接调用外部函数 `foo` 时，输出的第一行是外函数体内的打印语句内容，输出的第二行是调用内部函数而输出的打印语句内容。


```python
foo()
```

    foo: Hello world!
    display: Hello world!
    

### 返回函数的函数

这个标题较为拗口，可以理解为“从函数中返回函数”或者“返回函数对象的函数”。


```python
def foo():
    def display():
        print('Hello world!')
    
    return display
```

我们直接调用 `foo`，发现 **iPython** 解释器给我们返回了一个函数对象：


```python
foo()
```


    <function __main__.foo.<locals>.display()>

我们尝试用一个变量来捕获该对象，然后在对其进行函数调用操作。


```python
func = foo()
func()
```

    Hello world!
    

### 接收函数作为参数的函数

函数也是对象，因此函数也可以接收其他函数作为参数。


```python
def display():
    return 'Hello world!'
```

下面的函数接收一个函数作为参数：


```python
def foo(func):
    print(func())
```

现在，我们这样来调用上面的函数：


```python
foo(display)
```

    Hello world!
    

## 入门

有了上面的内容作为铺垫，下面想要理解装饰器就不难了。下面，我们编写一个更实用更清晰的程序，来帮助理解装饰器的本质。


```python
def a_new_decorator(a_func):
 
    def wrap_function():
        print("I am doing some boring work before executing a_func().")
        a_func()
        print("I am doing some boring work after executing a_func().")
 
    return wrap_function
```

上面的代码中我们定义了一个嵌套函数。其中，外部函数为 `a_new_decorator`，内部函数为 `wrap_function`。外部函数以一个函数作为参数，并且返回内部函数。内部函数负责调用从外部函数传入的函数，并在前后输出一些提示信息。

下面，我们来定义一个简单的函数：


```python
def a_function_requiring_decoration():
    print("I am the function which needs some decoration to remove my foul smell.")
```

我们直接调用它，就会直接输出函数体内部的打印语句：


```python
a_function_requiring_decoration()
```

    I am the function which needs some decoration to remove my foul smell.
    

倘若我们将这个函数作为参数传入到刚刚定义的嵌套函数中，看看会发生什么？


```python
decorator = a_new_decorator(a_function_requiring_decoration)
decorator()
```

    I am doing some boring work before executing a_func().
    I am the function which needs some decoration to remove my foul smell.
    I am doing some boring work after executing a_func().
    

和之前的直接调用相比，好像添加了一些本不属于原始函数的功能。这其实就是装饰器，它们封装一个函数，并且用自定义的方式来修改它的行为。

## 代码规范

在实际代码编写中，我们一般采用 `@` 加上装饰器的名称来修饰被装饰的普通函数。例如上面的函数可以这样被修饰：


```python
@a_new_decorator
def a_function_requiring_decoration():
    print("I am the function which needs some decoration to remove my foul smell.")
```

直接调用这个普通函数：


```python
a_function_requiring_decoration()
```

    I am doing some boring work before executing a_func().
    I am the function which needs some decoration to remove my foul smell.
    I am doing some boring work after executing a_func().
    

另外，如果我们直接查看这个函数对象的 `__name__` 信息，会得到：


```python
a_function_requiring_decoration.__name__
```


    'wrap_function'

这说明了装饰器的内部函数把被装饰的原始函数重写了，但实际上我们并不希望这样。幸运的是，**Python** 提供给我们一个简单的模块来解决这个问题，那就是 `functools.wraps`。


```python
from functools import wraps
```

这样，我们在装饰器的内部函数头部使用 `@wraps` 来修饰就可以避免这个问题。


```python
def a_new_decorator(a_func):

    @wraps(a_func)
    def wrap_function():
        print("I am doing some boring work before executing a_func().")
        a_func()
        print("I am doing some boring work after executing a_func().")
    
    return wrap_function
```


```python
@a_new_decorator
def a_function_requiring_decoration():
    print("I am the function which needs some decoration to remove my foul smell.")
```

现在我们再看看 `__name__` 属性：


```python
a_function_requiring_decoration.__name__
```


    'a_function_requiring_decoration'

## 装饰器的应用

### 测量代码运行时间

装饰器在实际中有着广泛的应用。例如，我们可以编写一个装饰器，测试任何函数的运行时间：


```python
import time

def cal_time(func):

    @wraps(func)
    def wrap():
        st = time.time()
        func()
        et = time.time()
        print('time: {}s'.format(et - st))

    return wrap
```

我们定义下面的函数，求解 1~$1,000,000$ 的和：


```python
@cal_time
def sum_1000():
    print(sum(i for i in range(1, 1000001)))
```


```python
sum_1000()
```

    500000500000
    time: 0.14763474464416504s
    

### 记录日志

日志是装饰器运用的另一个亮点。下面是一个例子：


```python
def logit(func):
    
    @wraps(func)
    def with_logging(*args, **kwargs):
        print(func.__name__ + " was called")
        return func(*args, **kwargs)
    
    return with_logging
 
@logit
def addition_func(x):
   """Do some math."""
   return x + x
```

上面的装饰器定义的内部函数接收 `func` 传入的一切参数，首先打印函数已经调用的提示信息，然后将函数的返回值返回。当调用被该装饰器修饰的函数时，除了能够捕获到它的返回值外，还能够得到提示信息。


```python
addition_func(4)
```

    addition_func was called
    


    8

## 带参数的装饰器

在铺垫一节中，我们已经知道 **Python** 中一切皆为对象。因此，装饰器本身其实也是对象。那么，装饰器应该和对象一样，具有函数调用的行为，也能够作为返回值被返回。据此，我们在装饰器的外面再嵌套一层函数。


```python
def logit(logfile='out.log'):
    
    def logging_decorator(func):
        
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            log_string = func.__name__ + " was called"
            print(log_string)
            print('written in {}'.format(logfile))
            return func(*args, **kwargs)
        
        return wrapped_function
    
    return logging_decorator
```

由于每个需要被记录日志的函数可能需要记录到不同的日志文件当中，因此上面代码的含义是记录日志的同时指定日志文件的路径。


```python
@logit()
def myfunc1():
    pass
 
myfunc1()
```

    myfunc1 was called
    written in out.log
    

`@logit()` 中的 `()` 必不可少，因为装饰器被封装在 `logit` 函数中了，因此要通过函数调用行为获取返回值，即装饰器对象本身。


```python
@logit(logfile='func2.log')
def myfunc2():
    pass
 
myfunc2()
```

    myfunc2 was called
    written in func2.log
    

上面的代码给 `@logit` 传入了参数，表示 `myfunc2` 的日志信息记录到 `func2.log` 文件中。

## 装饰器类

既然装饰器也是对象，那么把装饰器对象抽象出来，就得到了装饰器类。


```python
class Logit:
    
    def __init__(self, logfile='out.log'):
        self.logfile = logfile
        
    def __call__(self, func):
        
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            log_string = func.__name__ + " was called"
            print(log_string)
            print('written in {}'.format(self.logfile))
            self.notify()
            return func(*args, **kwargs)
        
        return wrapped_function

    def notify(self):
        print('done')
```

和之前的函数嵌套方法类似，在使用 `@` 声明装饰器时，`()` 必不可少，因为类名加 `()` 表示实例化对象。


```python
@Logit()
def myfunc1():
    pass

myfunc1()
```

    myfunc1 was called
    written in out.log
    done
    

我们也可以继承这个基类，然后重写 `notify` 方法：


```python
class EmailLogit(Logit):
    
    def __init__(self, email='admin@myproject.com', *args, **kwargs):
        self.email = email
        super(EmailLogit, self).__init__(*args, **kwargs)
 
    def notify(self):
        print('sent to ' + self.email)
```

用子类来修饰 `myfunc1`：


```python
@EmailLogit()
def myfunc1():
    pass

myfunc1()
```

    myfunc1 was called
    written in out.log
    sent to admin@myproject.com
