---
inHomePost: false
title: "Python 操作系统调用"
---

# Python 操作系统调用

`os` 模块提供了对系统文件进行操作的方法：


```python
import os
```

## 文件目录操作

### 当前工作目录


```python
os.getcwd()
```

当前目录的符号


```python
os.curdir
```


    '.'

### 更变当前目录


```python
os.chdir('D:')
```


```python
os.chdir('../')
```

### 新建文件夹


```python
os.mkdir('bin')
```

如果中间路径的文件夹不存在，则直接创建文件夹。


```python
os.makedirs('lib/bin')
```

### 删除文件夹

`rmdir` 既可以删除文件夹，又可以删除文件。


```python
os.rmdir('bin')
```

`unlink` 仅用于删除文件，如果路径不是文件则会出错。


```python
os.unlink('foo.txt')
```

删除文件夹，并删除中间路径中的空文件夹。


```python
os.removedirs('lib/bin')
```

### 重命名

第一个参数是原文件（夹）路径，第二个参数是目标文件（夹）路径。


```python
os.rename('foo.txt', 'bin/foo.txt')
```

如果中间路径的文件夹不存在，`renames` 函数会创建文件夹。


```python
os.renames('foo.txt', 'lib/bin/foo.txt')
```

### 列出所有文件（夹）名

`listdir` 返回给定目录下的所有文件夹和文件名（`list`），不包括 `.` 和 `..` 以及子文件夹下的目录。


```python
os.listdir(os.curdir)
```

## 系统常量

当前操作系统的换行符：


```python
# Windows 为 \r\n
# Linux 为 \n
os.linesep
```


    '\n'

当前操作系统的路径分隔符：


```python
os.sep
```


    '/'

当前操作系统的环境变量中的分隔符（`;` 或 `:`）：


```python
os.pathsep
```


    ';'

存储当前操作系统所有环境变量的字典：


```python
os.environ
```

## 文件路径操作

### 测试

检测一个路径是否为普通文件


```python
os.path.isfile('../foo.txt')
```


    False

检测一个路径是否为文件夹


```python
os.path.isdir('../bin')
```


    False

检测路径是否存在


```python
os.path.exists('../lib')
```


    False

检测路径是否为绝对路径


```python
os.path.isabs('/usr/bin')
```


    True

### 切分

`split` 函数可以将一个路径拆分为 `(head, tail)` 两部分。


```python
os.path.split(r'C:\Users\Administrator\Desktop\foo.txt')
```


    ('C:\\Users\\Administrator\\Desktop', 'foo.txt')


```python
os.path.split('/home/user/bin')
```


    ('/home/user', 'bin')

### 合并

`join` 函数使用系统的路径分隔符，将各个部分合成一个路径。


```python
os.path.join(r'C:\Program Files\Microsoft Office', 'WINWORD.exe')
```


    'C:\\Program Files\\Microsoft Office\\WINWORD.exe'


```python
os.path.join('/etc/apt/', 'sources.list')
```


    '/etc/apt/sources.list'

### 其他

返回路径的绝对路径


```python
os.path.abspath('../')
```


    'D:\\'

返回路径中的文件夹部分


```python
os.path.dirname(r'D:\Program Files (x86)\Steam\steam.exe')
```


    'D:\\Program Files (x86)\\Steam'

返回路径中的文件部分


```python
os.path.basename(r'D:\Program Files (x86)\Steam\steam.exe')
```


    'steam.exe'

将路径与扩展名分开


```python
os.path.splitext(r'D:\Program Files (x86)\Steam\steam.exe')
```


    ('D:\\Program Files (x86)\\Steam\\steam', '.exe')
