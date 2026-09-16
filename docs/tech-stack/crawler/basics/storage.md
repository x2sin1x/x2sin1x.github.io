---
title: 数据存储与去重
weight: 4
---

# 数据存储与去重

## 一、文本文件存储

### 1. 文件打开模式

| 模式 | 说明 |
| ---- | ---- |
| `r` / `rb` | 只读（文本 / 二进制），指针在开头 |
| `w` / `wb` | 写入，存在则覆盖，不存在则创建 |
| `a` / `ab` | 追加，指针在文件结尾 |
| `r+` / `w+` / `a+` | 对应的读写模式 |

爬虫写入数据几乎都用追加模式 `a`，避免翻页时覆盖前面的数据。

### 2. TXT 存储

```python
import requests
from bs4 import BeautifulSoup

url = 'https://www.zhihu.com/explore'
headers = {'User-Agent': 'Mozilla/5.0 ...'}
html = requests.get(url, headers=headers).text

soup = BeautifulSoup(html, 'lxml')
for title in soup.select('div .css-1g4zjtl a'):
    print(title.get_text())
    with open('data.txt', 'a', encoding='utf-8') as f:
        f.write(title.get_text() + '\n')
```

TXT 简单通用，缺点是不利于检索和结构化处理。

## 二、JSON 文件存储

JSON 由对象（`{}` 键值对）与数组（`[]` 索引）自由组合嵌套，结构化程度高：

```json
[{
  "name": "Bob",
  "gender": "male",
  "birthday": "1992-10-18"
}]
```

```python
import json

data_list = [{'href': '...', 'title': '...'}]

with open('data.json', 'w', encoding='utf-8') as f:
    # ensure_ascii=False 让中文正常显示；indent 美化缩进
    f.write(json.dumps(data_list, indent=2, ensure_ascii=False))
```

## 三、CSV 表格存储

CSV 是逗号分隔的纯文本表格，比 Excel 更轻量：

```python
import csv

# 1. 列表写入
with open('data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'name', 'age'])
    writer.writerows([['10001', 'Mike', 20], ['10002', 'Bob', 22]])

# 2. 字典写入（爬虫常用）
with open('data.csv', 'a', encoding='utf-8', newline='') as f:
    fieldnames = ['author', 'arcurl', 'tag']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'author': '张三', 'arcurl': 'https://...', 'tag': '动画'})
```

::: warning
Windows 下打开 CSV 要加 `newline=''`，否则每行之间会多出空行；中文 Excel 打开乱码时可把编码改为 `utf-8-sig`。
:::

## 四、MySQL 存储

```bash
pip install pymysql
```

### 1. 连接与建表

```python
import pymysql

db = pymysql.connect(host='localhost', user='root', password='root', db='spiders')
cursor = db.cursor()

sql = '''
CREATE TABLE IF NOT EXISTS students (
    id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    PRIMARY KEY (id))
'''
cursor.execute(sql)
db.close()
```

几个 SQL 基础概念，初学者先弄清再往下看：

- **主键（PRIMARY KEY）**：表中唯一标识一行的字段，不允许重复。爬虫表通常用一个 `id int auto_increment`（自增）列当主键，插入时传 0 或不传，数据库自动编号；
- **建表只需一次**：`CREATE TABLE IF NOT EXISTS` 保证表不存在时才建，爬虫每次启动都执行也不会报错；
- **参数化（%s 占位符）**：SQL 里不要用 f-string 直接拼值，一是值里含引号会破坏 SQL 语法，二是存在 SQL 注入风险；`cursor.execute(sql, (参数元组))` 由驱动负责安全转义，且预编译后批量执行更快。

### 2. 插入数据（参数化防注入）

```python
def insert_record(id_, name, age):
    db = pymysql.connect(host='localhost', user='root', password='root', db='spiders')
    cursor = db.cursor()
    sql = 'INSERT INTO students(id, name, age) values(%s, %s, %s)'
    try:
        cursor.execute(sql, (id_, name, age))
        db.commit()                       # 提交事务
        print('数据插入成功')
    except Exception as e:
        print(f'数据插入失败: {e}')
        db.rollback()                     # 出错回滚
    finally:
        db.close()
```

### 3. 结合爬虫入库

把数据库操作封装到爬虫类中，请求 → 解析 → `save_data` 一条龙：

```python
class Spider:
    def __init__(self):
        self.db = pymysql.connect(host='localhost', user='root', password='root', db='spiders')
        self.cursor = self.db.cursor()

    def save_data(self, name, requirement):
        sql = 'INSERT INTO jobs(id, name, requirement) values(%s, %s, %s)'
        try:
            self.cursor.execute(sql, (0, name, requirement))
            self.db.commit()
        except Exception as e:
            print(f'插入失败: {e}')
            self.db.rollback()
```

批量插入可改用 `cursor.executemany(sql, data_list)`，效率远高于逐条插入。

## 五、MongoDB 存储

MongoDB 是基于分布式文件存储的**非关系型数据库**（NoSQL）：没有「表」和固定的列，数据以**文档**（一个类似 JSON 的字典）为单位存储，文档与文档之间的字段可以不一样。这对爬虫太友好了——很多页面字段不齐全，MySQL 要求每列都有值，MongoDB 缺什么就少存什么，且不用提前建表。层级对应关系：MySQL 的「库-表-行」 ≈ MongoDB 的「库-集合（collection）-文档（document）」。

```bash
pip install pymongo
```

```python
import pymongo

client = pymongo.MongoClient(host='127.0.0.1', port=27017)
collection = client['spider']['aqy']        # 库.集合

# 插入单条 / 多条
collection.insert_one({'id': '20170101', 'name': 'Jordan', 'age': 20})
collection.insert_many([student1, student2])
```

结合爬虫的完整示例：

```python
import requests
import pymongo

class Iqiyi:
    def __init__(self):
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        self.collection = self.client['spider']['aqy']
        self.url = 'https://pcw-api.iqiyi.com/search/recommend/list'

    def save_data(self, item):
        self.collection.insert_one(item)

    def main(self):
        for page in range(1, 3):
            params = {'channel_id': '2', 'mode': '11', 'page_id': page,
                      'ret_num': '48', 'three_category_id': '15;must'}
            data = requests.get(self.url, params=params).json()
            for video in data['data']['list']:
                self.save_data({'title': video['title'],
                                'playUrl': video['playUrl'],
                                'description': video['description']})
```

常用 mongo shell 命令：`show dbs`、`use 库名`、`show collections`、`db.集合.find()`、`db.集合.drop()`。

## 六、数据去重

### 1. 应用场景

- 防止发出重复的请求
- 防止存储重复的数据

### 2. 去重容器

先看去重的完整流程，所有方案都是这个骨架：

```text
新数据 → 计算指纹（MD5 等哈希）
      → 询问容器：这个指纹见过吗？
            ├─ 没见过 → 数据入库，指纹写入容器
            └─ 见过   → 丢弃，跳过
```

容器分两类：

| 类型 | 代表 | 优点 | 缺点 |
| ---- | ---- | ---- | ------ |
| 临时容器 | Python `set` / `list` | 简单方便 | 程序重启即失效，无法共享 |
| 持久化容器 | Redis、MySQL | 可持久化、可多进程/分布式共享 | 实现相对复杂 |

### 3. 指纹计算

直接拿整条数据做 key 太大，通常先做哈希：

- **MD5 / SHA 等信息摘要**：把数据变成固定长度指纹，比较快
- **SimHash**：适合模糊文本的相似去重
- **布隆过滤器**：适合上亿级别的海量去重，内存占用极小

### 4. Redis + MD5 实战

```python
import hashlib
import redis
import requests
import pymongo

class Mgtv:
    def __init__(self):
        self.collection = pymongo.MongoClient()['spider']['mgtv']
        self.red = redis.Redis()
        self.url = 'https://pianku.api.mgtv.com/rider/list/pcweb/v3'

    def get_md5(self, val):
        """把目标数据哈希成指纹，用于快速去重"""
        md5 = hashlib.md5()
        md5.update(str(val).encode('utf-8'))
        return md5.hexdigest()

    def save_data(self, item):
        value = self.get_md5(item)
        # sadd 向集合添加，返回 0 表示已存在
        if self.red.sadd('mg:filter', value):
            self.collection.insert_one(item)
            print('插入成功')
        else:
            print('数据重复')

    def main(self):
        for page in range(1, 3):
            params = {'channelId': '2', 'pn': page, 'pc': '80', 'sort': 'c2'}
            data = requests.get(self.url, params=params).json()
            for video in data['data']['hitDocs']:
                self.save_data({'title': video['title'],
                                'subtitle': video['subtitle'],
                                'story': video['story']})
```

Redis 相关命令：`redis-cli` 进入、`select 1` 切库、`keys *` 查看键、`sadd key value` 加集合、`smembers key` 看集合、`del key` 删除。

## 七、小结

| 需求 | 推荐方案 |
| ---- | -------- |
| 临时查看 / 小数据 | TXT、JSON |
| 给非技术人员用 / 导 Excel | CSV |
| 结构化、需要 SQL 查询 | MySQL（参数化 + 批量插入） |
| 字段灵活、嵌套文档 | MongoDB |
| 请求 / 数据去重 | Redis 集合 + MD5 指纹，海量数据上布隆过滤器 |
