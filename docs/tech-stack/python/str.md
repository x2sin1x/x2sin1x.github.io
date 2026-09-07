---
title: Python 字符串
---

# Python 字符串

## 生成字符串

**Python**中可以使用一对单引号 `''` 或者双引号 `""` 生成字符串。


```python
s = 'hello world'
s
```


    'hello world'


```python
s = "hello, world"
s
```


    'hello, world'

## 简单操作

加法：


```python
s = 'hello ' + 'world'
s
```


    'hello world'

字符串与数字相乘：


```python
"echo" * 3
```


    'echoechoecho'

字符串长度：


```python
len(s)
```


    11

## 字符串方法

### 分割

`s.split()` 将 `s` 按照空格（包括多个空格，制表符 `\t`，换行符 `\n` 等）分割，并返回所有分割得到的字符串。


```python
line = "1 2 3 4  5"
numbers = line.split()
numbers
```


    ['1', '2', '3', '4', '5']

`s.split(sep)` 以给定的 `sep` 为分隔符对 `s` 进行分割。


```python
line = "1,2,3,4,5"
numbers = line.split(',')
numbers
```


    ['1', '2', '3', '4', '5']

### 连接

与分割相反，`s.join(str_sequence)` 的作用是以 `s` 为连接符将字符串序列 `str_sequence` 中的元素连接起来，并返回连接后得到的新字符串：


```python
s = ' '
s.join(numbers)
```


    '1 2 3 4 5'


```python
s = ','
s.join(numbers)
```


    '1,2,3,4,5'

### 替换

`s.replace(part1, part2)` 将字符串 `s` 中指定的部分 `part1` 替换成想要的部分 `part2`，并返回新的字符串。


```python
s = "Hello World"
s.replace('World', 'Python')
```


    'Hello Python'

此时，s的值并没有变化，替换方法只是生成了一个新的字符串。


```python
s
```


    'Hello World'

### 大小写转换

- `s.upper()`：返回一个将s中的字母全部大写的新字符串。
- `s.lower()`：返回一个将s中的字母全部小写的新字符串。

这两种方法也不会改变原来s的值：


```python
s.upper()
```


    'HELLO WORLD'


```python
s.lower()
```


    'hello world'

### 去除多余空格

- `s.strip()`：返回一个将s两端的多余空格除去的新字符串。
- `s.lstrip()`：返回一个将s开头的多余空格除去的新字符串。
- `s.rstrip()`：返回一个将s结尾的多余空格除去的新字符串。

这三种方法也不会改变原来s的值：


```python
s = "  hello world   "
s.strip()
```


    'hello world'


```python
s.lstrip()
```


    'hello world   '


```python
s.rstrip()
```


    '  hello world'

## 多行字符串

Python 用一对三引号 `"""` 或者 `'''` 来生成多行字符串：


```python
a = """hello world.
it is a nice day."""
```

在储存时，我们在两行字符间加上一个换行符 `'\n'`


```python
a
```


    'hello world.\nit is a nice day.'

当代码太长或者为了美观起见时，我们可以可以使用 `()` 或者 `\` 来换行：


```python
a = ("hello, world. "
    "it's a nice day. "
    "my name is xxx")
a
```


    "hello, world. it's a nice day. my name is xxx"


```python
a = "hello, world. " \
    "it's a nice day. " \
    "my name is xxx"
a
```


    "hello, world. it's a nice day. my name is xxx"

## 强制转换为字符串

* `str(ob)` 强制将 `ob` 转化成字符串。 
* `repr(ob)` 也是强制将 `ob` 转化成字符串。

不同点如下：


```python
str(1.1 + 2.2)
```


    '3.3000000000000003'


```python
repr(1.1 + 2.2)
```


    '3.3000000000000003'

## 整数与不同进制的字符串的转化

可以将整数按照不同进制转化为不同类型的字符串。

十六进制、八进制和二进制：


```python
hex(255), oct(255), bin(255)
```


    ('0xff', '0o377', '0b11111111')

可以使用 `int` 将字符串转为整数：


```python
int('23')
```


    23

还可以指定按照多少进制来进行转换，最后返回十进制表达的整数：


```python
int('FF', 16), int('377', 8), int('11111111', 2)
```


    (255, 255, 255)

 `float` 可以将字符串转换为浮点数：


```python
float('3.5')
```


    3.5

## 格式化字符串

**Python** 用字符串的 `format()` 方法来格式化字符串。

具体用法如下，字符串中花括号 `{}` 的部分会被format传入的参数替代，传入的值可以是字符串，也可以是数字或者别的对象。


```python
'{} {} {}'.format('a', 'b', 'c')
```


    'a b c'

可以用数字指定传入参数的相对位置：


```python
'{2} {1} {0}'.format('a', 'b', 'c')
```


    'c b a'

还可以指定传入参数的名称：


```python
'{color} {n} {x}'.format(n=10, x=1.5, color='blue')
```


    'blue 10 1.5'

可以在一起混用：


```python
'{color} {0} {x} {1}'.format(10, 'foo', x = 1.5, color='blue')
```


    'blue 10 1.5 foo'

可以用`{<field name>:<format>}`指定格式，具体规则与C语言相同：


```python
from math import pi

'{0:10} {1:10d} {2:10.2f}'.format('foo', 5, 2 * pi)
```


    'foo                 5       6.28'

也可以使用旧式的`%`方法进行格式化：


```python
s = "some numbers:"
x = 1.34
y = 2
# 用百分号隔开，括号括起来
"%s %f, %d" % (s, x, y)
```


    'some numbers: 1.340000, 2'
