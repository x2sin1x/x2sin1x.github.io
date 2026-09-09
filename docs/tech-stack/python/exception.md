---
title: "Python 异常处理"
date: 2022-02-18T14:47:24+08:00
weight: 65
---
# Python 异常处理

## try/except 块

写代码的时候，出现错误必不可免，即使代码没有问题，也可能遇到别的问题。

看下面这段代码：

```python 
import math

while True:
    text = input('> ')
    if text[0] == 'q':
        break
    x = float(text)
    y = math.log10(x)
    print("log10({0}) = {1}".format(x, y))
```

这段代码接收命令行的输入，当输入为数字时，计算它的对数并输出，直到输入值为 `q` 为止。

乍看没什么问题，然而当我们输入 `0` 或者负数时：

> \> 0


```python
import math

while True:
    text = input('> ')
    if text[0] == 'q':
        break
    x = float(text)
    y = math.log10(x)
    print("log10({0}) = {1}".format(x, y))
```


    ---------------------------------------------------------------------------
    
    ValueError                                Traceback (most recent call last)
    
    ~\AppData\Local\Temp/ipykernel_2200/3405246205.py in <module>
          6         break
          7     x = float(text)
    ----> 8     y = math.log10(x)
          9     print("log10({0}) = {1}".format(x, y))


    ValueError: math domain error


`log10` 函数会报错，因为不能接受非正值。

一旦报错，程序就会停止执行，如果不希望程序停止执行，那么我们可以添加一对 `try/except`：

> \> 0
>
> \> q


```python
import math

while True:
    try:
        text = input('> ')
        if text[0] == 'q':
            break
        x = float(text)
        y = math.log10(x)
        print("log10({0}) = {1}".format(x, y))
    except ValueError:
        print("the value must be greater than 0")
```

    the value must be greater than 0


一旦 `try` 块中的内容出现了异常，那么 `try` 块后面的内容会被忽略，**Python** 会寻找 `except` 里面有没有对应的内容，如果找到，就执行对应的块，没有则抛出这个异常。

在上面的例子中，`try` 抛出的是 `ValueError`，`except` 中有对应的内容，所以这个异常被 `except` 捕捉到，程序可以继续执行。

## 捕捉不同的错误类型

假设我们将这里的 `y` 更改为 `1 / math.log10(x)`，此时输入 `1`：

> \> 1


```python
import math

while True:
    try:
        text = input('> ')
        if text[0] == 'q':
            break
        x = float(text)
        y = 1 / math.log10(x)
        print("log10({0}) = {1}".format(x, y))
    except ValueError:
        print("the value must be greater than 0")
```


    ---------------------------------------------------------------------------
    
    ZeroDivisionError                         Traceback (most recent call last)
    
    ~\AppData\Local\Temp/ipykernel_2200/1390458657.py in <module>
          7             break
          8         x = float(text)
    ----> 9         y = 1 / math.log10(x)
         10         print("log10({0}) = {1}".format(x, y))
         11     except ValueError:


    ZeroDivisionError: float division by zero


因为我们的 `except` 里面并没有 `ZeroDivisionError`，所以会抛出这个异常，我们可以通过下面的两种方式解决这个问题：

## 捕捉所有异常

将 `except` 的值改成 `Exception` 类，来捕获所有的异常。

> \> 1
>
> \> q


```python
import math

while True:
    try:
        text = input('> ')
        if text[0] == 'q':
            break
        x = float(text)
        y = 1 / math.log10(x)
        print("1 / log10({0}) = {1}".format(x, y))
    except Exception:
        print("invalid value")
```

    invalid value


## 指定特定值

这里，我们把 `ZeroDivisionError` 加入 `except`。

> \> 1
>
> \> q


```python
import math

while True:
    try:
        text = input('> ')
        if text[0] == 'q':
            break
        x = float(text)
        y = 1 / math.log10(x)
        print("1 / log10({0}) = {1}".format(x, y))
    except (ValueError, ZeroDivisionError):
        print("invalid value")
```

    invalid value


或者另加处理：

> \> 1
>
> \> q


```python
import math

while True:
    try:
        text = input('> ')
        if text[0] == 'q':
            break
        x = float(text)
        y = 1 / math.log10(x)
        print("1 / log10({0}) = {1}".format(x, y))
    except ValueError:
        print("the value must be greater than 0")
    except ZeroDivisionError:
        print("the value must not be 1")
```

    the value must not be 1


事实上，我们还可以将这两种方式结合起来，用 `Exception` 来捕捉其他的错误：

> \> 0
>
> \> 1
>
> \> !@#$%^&*
>
> \> q


```python
import math

while True:
    try:
        text = input('> ')
        if text[0] == 'q':
            break
        x = float(text)
        y = 1 / math.log10(x)
        print("1 / log10({0}) = {1}".format(x, y))
    except ValueError:
        print("the value must be greater than 0")
    except ZeroDivisionError:
        print("the value must not be 1")
    except Exception:
        print("unexpected error")
```

    the value must be greater than 0
    the value must not be 1
    the value must be greater than 0


## 得到异常的具体信息

在上面的例子中，当我们输入不能转换为浮点数的字符串时，它输出的是 `the value must be greater than 0`，这并没有反映出实际情况。


```python
float('a')
```


    ---------------------------------------------------------------------------
    
    ValueError                                Traceback (most recent call last)
    
    ~\AppData\Local\Temp/ipykernel_2200/1629398556.py in <module>
    ----> 1 float('a')


    ValueError: could not convert string to float: 'a'


为了得到异常的具体信息，我们将这个 `ValueError` 具现化。

> \> 0
>
> \> 1
>
> \> !@#$%^&*
>
> \> q


```python
import math

while True:
    try:
        text = input('> ')
        if text[0] == 'q':
            break
        x = float(text)
        y = 1 / math.log10(x)
        print("1 / log10({0}) = {1}".format(x, y))
    except ValueError as exc:
        message = exc.args[0]
        if message == "math domain error":
            print("the value must be greater than 0")
        else:
            print("could not convert '%s' to float" % text)
    except ZeroDivisionError:
        print("the value must not be 1")
    except Exception as exc:
        message = exc.args[0]
        print("unexpected error:", message)
```

    the value must be greater than 0
    the value must not be 1
    could not convert '!@#$%^&*' to float


当我们使用 `except Exception` 时，会捕获所有的 `Exception` 和它派生出来的子类，但不是所有的异常都是从 `Exception` 类派生出来的，可能会出现一些不能捕获的情况，因此，更加一般的做法是使用这样的形式：

```python
try:
    pass
except:
    pass
```

这样不指定异常的类型会捕获所有的异常，但是这样的形式并不推荐。

## 自定义异常

异常是标准库中的类，这意味着我们可以自定义异常类：


```python
class CommandError(ValueError):
    pass
```

这里我们定义了一个继承自 `ValueError` 的异常类，异常类一般接收一个字符串作为输入，并把这个字符串当作异常信息，例如：

> \> back


```python
valid_commands = {'start', 'stop', 'pause'}

while True:
    command = input('> ')
    if command.lower() not in valid_commands:
        raise CommandError('Invalid commmand: %s' % command)
```


    ---------------------------------------------------------------------------
    
    CommandError                              Traceback (most recent call last)
    
    ~\AppData\Local\Temp/ipykernel_2200/1947621995.py in <module>
          4     command = input('> ')
          5     if command.lower() not in valid_commands:
    ----> 6         raise CommandError('Invalid commmand: %s' % command)


    CommandError: Invalid commmand: back


这里，我们使用 `raise` 关键词来抛出异常。

我们可以使用 `try/except` 块来捕捉这个异常：

> \> back
>
> \> stop


```python
valid_commands = {'start', 'stop', 'pause'}

while True:
    command = input('> ')
    try:
        if command.lower() not in valid_commands:
            raise CommandError('Invalid commmand: %s' % command)
        if command.lower() == 'stop':
            break
    except CommandError:
        print('Bad command string: "%s"' % command)
```

    Bad command string: "back"


由于 `CommandError` 继承自 `ValueError`，我们也可以使用 `except ValueError` 来捕获这个异常。

## finally

`try/except` 块还有一个可选的关键词 `finally`。

不管 `try` 块有没有异常，`finally` 块的内容总是会被执行，而且会在抛出异常前执行，因此可以用来作为安全保证，比如确保打开的文件被关闭。


```python
try:
    print(1)
finally:
    print('finally was called')
```

    1
    finally was called


在抛出异常前执行：


```python
try:
    print(1 / 0)
finally:
    print('finally was called.')
```

    finally was called.

    ---------------------------------------------------------------------------
    
    ZeroDivisionError                         Traceback (most recent call last)
    
    ~\AppData\Local\Temp/ipykernel_2200/3900254831.py in <module>
          1 try:
    ----> 2     print(1 / 0)
          3 finally:
          4     print('finally was called.')


    ZeroDivisionError: division by zero


如果异常被捕获了，在最后执行：


```python
try:
    print(1 / 0)
except ZeroDivisionError:
    print('divide by 0.')
finally:
    print('finally was called.')
```

    divide by 0.
    finally was called.
