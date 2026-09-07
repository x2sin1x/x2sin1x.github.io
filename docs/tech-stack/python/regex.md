---
inHomePost: false
title: Python 正则表达式
---

# Python 正则表达式

```python
import re
```

## compile 方法

`compile` 方法返回一个正则表达式对象：


```python
re.compile(r'\d+')
```


    re.compile(r'\d+', re.UNICODE)

## findall 方法

findall 方法返回一个列表，包含字符串中所有匹配成功的子串，常用于在长字符串（例如 html）中检索数据。


```python
re.findall(r'\d+', 'runoob 123 google 456')
```


    ['123', '456']

也可以先编译正则表达式，然后再检索：


```python
pattern = re.compile(r'\d+')
pattern.findall('127.0.0.1')
```


    ['127', '0', '0', '1']

## search 方法

search 方法的返回值是一个匹配类型，它包含正则从头扫描字符串首次成功匹配的信息。


```python
reg_str = "127.0.0.1"
reg = r"(\d+)\.(\d+)\.(\d+)\.(\d+)"
result = re.search(reg, reg_str)
result
```


    <re.Match object; span=(0, 9), match='127.0.0.1'>

`groups` 方法返回组匹配所得串按顺序排列的元组。


```python
result.groups()
```


    ('127', '0', '0', '1')

`group(0)` 表示整个匹配到的串，其后表示组匹配所得字串。


```python
result.group(0)
```


    '127.0.0.1'

`group(1)` 表示第1组捕获到的串，以此类推。


```python
result.group(1)
```


    '127'

`span` 方法返回第一个成功匹配的信息。输出结果的含义是从下标为0处开始匹配成功3个字符。


```python
result.span()
```


    (0, 9)

## match 方法

`match` 方法的返回值也是一个匹配类型，它包含正则从头扫描字符串首次成功匹配的信息，并且如果一开始就匹配失败，则认为匹配失败。

下面的这个例子匹配 IP 地址，并获取端口号：


```python
reg_str = "127.0.0.1:8000"
reg = r"\d+\.\d+\.\d+\.\d+:(\d+)"
result = re.match(reg, reg_str)
result
```


    <re.Match object; span=(0, 14), match='127.0.0.1:8000'>


```python
result.groups()
```


    ('8000',)

## sub 方法

sub 方法用于替换原串中正则匹配所得的内容。


```python
phone = "2004-959-559 # 这是一个电话号码"
```

删除注释：


```python
re.sub(r'#.*$', "", phone)
```


    '2004-959-559 '

移除非数字的内容：


```python
re.sub(r'\D', "", phone)
```


    '2004959559'

将匹配的数字乘以 2：


```python
def double(matched):
    value = int(matched.group('value'))
    return str(value * 2)
 
s = 'A23G4HFD567'
print(re.sub('(?P<value>\d+)', double, s))
```

    A46G8HFD1134
