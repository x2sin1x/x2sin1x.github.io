---
title: 数据提取
weight: 3
---

# 数据提取

## 一、数据的分类

| 类型 | 举例 | 处理方式 |
| ---- | ---- | -------- |
| 结构化数据 | JSON、XML | 直接转换为 Python 类型处理 |
| 非结构化数据 | HTML、字符串 | 正则表达式、XPath、BeautifulSoup |

选择原则：接口返回的 JSON 用 `json` 模块；页面 HTML 优先用 XPath / CSS 选择器；零散字符串（如 JS 里的参数）用正则。

## 二、JSON 数据处理

JSON 是爬虫中最常见的数据格式，`json` 模块四个方法对应两组互逆操作：

| 方法 | 作用 |
| ---- | ---- |
| `json.dumps(obj)` | Python 对象 → JSON 字符串 |
| `json.loads(s)` | JSON 字符串 → Python 对象 |
| `json.dump(obj, f)` | Python 对象写入文件对象 |
| `json.load(f)` | 从文件对象读取 JSON → Python 对象 |

```python
import json

# dumps：indent 美化缩进，ensure_ascii=False 保留中文
json_str = json.dumps(mydict, indent=2, ensure_ascii=False)

# loads：字符串转字典
my_dict = json.loads(json_str)

# dump / load：与文件配合
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data_list, f, ensure_ascii=False, indent=2)

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

::: tip
requests 中可直接 `response.json()`；异步 aiohttp 中要注意 `await response.json(content_type=None)`。
:::

## 三、正则表达式

### 1. 单字符匹配

| 语法 | 功能 |
| ---- | ---- |
| `.` | 任意 1 个字符（除 `\n`） |
| `[abc]` / `[a-z]` | 枚举 / 区间内的 1 个字符 |
| `\d` / `\D` | 数字 / 非数字 |
| `\s` / `\S` | 空白 / 非空白 |
| `\w` / `\W` | 字母数字下划线汉字 / 特殊字符 |

### 2. 数量与边界

| 语法 | 功能 |
| ---- | ---- |
| `*` | 前一字符出现 0 次或无限次 |
| `+` | 至少 1 次 |
| `?` | 0 次或 1 次 |
| `{m}` / `{m,n}` | 恰好 m 次 / m 到 n 次 |
| `^` / `$` | 开头 / 结尾 |
| `[^abc]` | 除了 abc 以外的字符 |

### 3. 分组

| 语法 | 功能 |
| ---- | ---- |
| `\|` | 或，匹配左右任意一个表达式 |
| `(ab)` | 分组，`group(1)` 取第一组 |
| `\1` | 引用第 1 组匹配到的字符串 |
| `(?P<name>)` / `(?P=name)` | 分组命名 / 引用命名分组 |

```python
import re

match_obj = re.match(r'(\w+)@(?P<host>163|qq)\.com', 'hello@163.com')
print(match_obj.group())      # hello@163.com
print(match_obj.group(1))     # hello
print(match_obj.group('host'))  # 163

# \1 引用分组，匹配成对出现的标签
re.match(r'<([a-z1-6]+)>.*</\1>', '<html>hh</html>')
```

### 4. re 模块常用方法

```python
import re

re.match(r'\d+', '123abc')     # 从头匹配，返回 Match 对象
re.search(r'\d+', 'abc123')    # 扫描全文找第一个
re.findall(r'\d+', 'tu1ling2') # 找所有，返回列表 ['1', '2']（爬虫最常用）
re.sub(r'\d', '_', 'tu1ling2') # 替换
p = re.compile(r'\d+', re.S)   # 编译复用，可携带匹配模式
```

常用修饰符：`re.I` 忽略大小写、`re.S` 让 `.` 匹配换行（提取跨行 HTML 时必备）、`re.M` 多行模式。

### 5. 贪婪与非贪婪

- 默认**贪婪匹配**：尽可能多地匹配字符
- 量词后加 `?` 变**非贪婪**：尽可能少地匹配——爬虫提取 `.*?` 是最常见的写法

用一个具体例子感受差别。要从下面的 HTML 里提取两个书名：

```text
<a href="/book/1">斗破苍穹</a><a href="/book/2">凡人修仙传</a>
```

```python
html = '<a href="/book/1">斗破苍穹</a><a href="/book/2">凡人修仙传</a>'

# 贪婪：第一个 .*? 一口气咂到整个字符串里最后一个引号才肯停，
# 结果只匹配到 1 条且内容串了两个链接
re.findall(r'<a href="(.*)">(.*)</a>', html)
# [('1">斗破苍穹</a><a href="/book/2', '凡人修仙传')]

# 非贪婪：每个 .*? 碰到第一个能匹配的位置就停，准确拆出两条
re.findall(r'<a href="(.*?)">(.*?)</a>', html)
# [('/book/1', '斗破苍穹'), ('/book/2', '凡人修仙传')]
```

记忆口诀：**贪婪是「吃到最后一个」，非贪婪是「吃到第一个就停」**。所以只要目标字符串在文中出现多次，提取类正则几乎都应该用非贪婪。

```python
re.findall(r'title:"(.*?)",.*?preview_url:"(.*?)"', response.text)
```

### 6. 原始字符串与中文

正则务必配合 `r''` 原始字符串，避免 `\` 转义歧义。匹配中文用 Unicode 区间：

```python
import re

title = '你好，hello，世界'
print(re.findall(r'[\u4e00-\u9fa5]+', title))   # ['你好', '世界']
```

## 四、XPath 与 lxml

XPath 是一门在 HTML/XML 文档中查找信息的语言，配合高性能解析库 lxml 使用：

```bash
pip install lxml
```

### 1. 基础语法

| 表达式 | 描述 |
| ------ | ---- |
| `nodename` | 选取该节点的所有子节点 |
| `/` | 从根节点选取 / 逐级过渡 |
| `//` | 选取任意位置的子孙节点 |
| `.` / `..` | 当前节点 / 父节点 |
| `@` | 选取属性 |
| `text()` | 选取文本 |

```text
//li                  选取所有 li 元素
//div[@class="s2"]    选取 class 为 s2 的 div
//ul/li[1]            ul 下第一个 li（注意下标从 1 开始）
//ul/li[last()]       最后一个 li
//a/@href             所有 a 标签的 href 属性
//a/text()            所有 a 标签的文本
//li/a[text()='无墟极道']   按文本筛选
```

### 2. lxml 使用流程

```python
import requests
from lxml import etree

url = 'https://www.77xsw.cc/fenlei/1_1/'
response = requests.get(url, headers=headers).content.decode('gbk')
html = etree.HTML(response)      # str/bytes → Element 对象

# 1. 先按 li 分组，返回 Element 列表，每组可继续 .xpath()
li_list = html.xpath('//div[@id="mm_14"]/ul/li[position()>1]')
for li in li_list:
    item = {
        # 三元运算兜底：节点可能不存在
        'title': li.xpath('.//span[@class="sp_2"]/a/text()')[0] if li.xpath('.//span[@class="sp_2"]/a/text()') else None,
        'href':  li.xpath('.//span[@class="sp_2"]/a/@href')[0]  if li.xpath('.//span[@class="sp_2"]/a/@href')  else None,
    }
    print(item)
```

::: warning 两个关键经验
1. **先分组再提取**：先拿到每条记录的父节点（如 `li`），再在组内提取字段，避免多个列表 `zip` 时因个别字段缺失而错位。
2. **etree 会自动补全残缺标签**：如果按源码写 XPath 取不到数据，用 `etree.tostring(html, encoding='utf-8').decode()` 打印解析后的 HTML，按修正后的结构写 XPath。
:::

::: tip
Chrome 插件 XPath Helper 可以辅助学习 XPath 语法，但它基于渲染后的 Elements，与 URL 对应的响应可能不同，写代码时不要依赖它。
:::

## 五、BeautifulSoup4

BS4 基于 DOM 树载入整个文档，API 友好、支持 CSS 选择器，性能低于 lxml 但上手更快：

```bash
pip install bs4
```

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')   # 显式指定解析器
```

| 解析器 | 特点 |
| ------ | ---- |
| `html.parser` | Python 内置，速度中等，容错好 |
| `lxml` | 速度快，容错强（推荐） |
| `html5lib` | 容错最好，以浏览器方式解析，速度慢 |

### 1. find / find_all

```python
soup.find_all('span')                        # 按标签名
soup.find_all(re.compile('^b'))              # 按正则
soup.find_all(['a', 'span'])                 # 按列表
soup.find_all(attrs={'class': 'blue'})       # 按属性

soup.find('div', class_='wrap')              # find 返回第一个匹配
```

### 2. CSS 选择器 select

CSS 选择器是前端「选中某个元素」的语法，规则简单：

| 符号 | 含义 | 示例 |
| ---- | ---- | ---- |
| （无符号） | 标签名 | `div` 选中所有 div |
| `.` | class | `.item` 选中 class 含 item 的元素 |
| `#` | id | `#main` 选中 id 为 main 的元素 |
| 空格 | 后代（任意层级） | `div a` 选中 div 里面所有 a（不管嵌套多深） |
| `>` | 直接子元素 | `ul > li` 只选 ul 的直接子 li |
| `[attr="v"]` | 属性 | `a[target="_blank"]` |

```python
soup.select('title')                       # 标签选择器
soup.select('.divcenter')                  # 类选择器
soup.select('#footercopyright')            # id 选择器
soup.select('div .navigation')             # 层级选择器
soup.select('tr[align="center"]')          # 属性选择器
soup.select('tr td:nth-child(3)')          # 伪类选择器
```

### 3. 取文本与属性

```python
for a in soup.select('li a.blue'):
    print(a.get_text())      # 或 a.text / a.string
    print(a.get('href'))     # 取属性
```

### 完整案例：下载音频

```python
import os
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
os.makedirs('音频', exist_ok=True)

url = 'https://sc.chinaz.com/yinxiao/index_1.html'
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')

for div in soup.select('#AudioList .container .audio-item'):
    mp3_url = 'https:' + div.select('audio')[0].get('src')
    title = div.select('.name')[0].get_text().strip()

    res = requests.get(mp3_url, headers=headers)
    with open(f'音频/{title}.mp3', 'wb') as f:
        f.write(res.content)
        print(f'正在下载 {title}')
```

## 六、小结与选型

- 接口 JSON → `json` / `response.json()`
- 页面结构规整 → **lxml + XPath**（先分组再提取）
- 想写 CSS 选择器 / 小脚本 → **BS4**
- 字符串片段、JS 代码里的参数 → **正则非贪婪** `.*?`
- 需要按 JSON 路径取深层数据时，还可以了解 `jsonpath` 库
