---
title: Scrapy 框架
weight: 8
---

# Scrapy 框架

前面的章节里，去重、调度、并发、限速、重试这些通用能力全部要自己手写——每个新项目都重复一遍。**Scrapy 把这些通用能力全部内置**，你只需要关心三件事：从哪爬（Spider）、怎么解析（parse 函数）、怎么存（Pipeline），其余的调度与并发都由框架自动完成。它是基于 Twisted 异步网络框架构建的，天生就是高并发。官方文档：[docs.scrapy.org](https://docs.scrapy.org)。

## 一、简介与安装

### 1. 安装

```bash
pip install scrapy
scrapy version        # 查看 Scrapy 版本
scrapy version -v     # 查看包括 Python、Twisted、lxml 在内的详细版本
```

Windows 下若安装 Twisted 报错，先手动 `pip install twisted`（或安装预编译 wheel）再装 Scrapy。

### 2. 命令行工具

命令分两类：不带项目就能用的全局命令（`startproject`、`runspider`、`shell`、`fetch`、`view`、`version`、`settings`、`bench`），以及必须在项目目录内运行的项目命令（`crawl`、`list`、`genspider`、`parse`、`check`、`edit`）。

| 命令 | 说明 |
| ---- | ---- |
| `scrapy startproject myspider` | 创建项目 |
| `scrapy genspider douban example.com` | 按模板生成一个爬虫文件 |
| `scrapy crawl douban` | 运行项目里的爬虫，`-a key=value` 可传 Spider 参数 |
| `scrapy list` | 列出项目中的所有爬虫 |
| `scrapy runspider spider.py` | 不建项目，直接运行单个爬虫文件 |
| `scrapy shell url` | 交互式调试终端 |
| `scrapy parse url --spider douban` | 用指定爬虫的回调解析 url 并输出结果（`--callback` 指定回调） |
| `scrapy fetch url` | 用 Scrapy 下载器抓取 url 并打印到终端 |
| `scrapy view url` | 用 Scrapy 抓取后在本机浏览器打开，查看"Scrapy 眼中的页面" |
| `scrapy check` | 运行 Spider Contracts（`@url`、`@returns` 契约测试） |
| `scrapy settings [option]` | 打印某个配置的最终生效值 |
| `scrapy bench` | 快速基准测试，估算硬件吞吐 |

### 3. 项目结构

```text
myspider/
├── scrapy.cfg            # 部署配置文件
└── myspider/
    ├── __init__.py
    ├── items.py          # Item 定义
    ├── middlewares.py    # 下载中间件与爬虫中间件
    ├── pipelines.py      # Item Pipeline
    ├── settings.py       # 项目配置
    └── spiders/          # 爬虫目录
```

## 二、架构与工作流程

```text
                        ┌──────────┐
        ┌── 请求队列 ──→│  调度器   │
        │               └──────────┘
        │                    ↑↓
   ┌─────────┐   请求    ┌──────┐   响应   ┌─────────┐
   │  引擎    │ ←──────→ │ 下载器 │ ──────→ │ Spider  │
   └─────────┘           └──────┘           └─────────┘
        ↑                                       │
        │            Item 数据                   ↓
   ┌─────────┐  ←──────────────────────  (下载中间件/爬虫中间件)
   │ Pipeline │
   └─────────┘
```

核心组件：

| 组件 | 职责 |
| ---- | ---- |
| 引擎 Engine | 全局调度，控制所有组件之间的数据流 |
| 调度器 Scheduler | 接收引擎发来的 Request 入队，引擎再要时出队 |
| 下载器 Downloader | 基于 Twisted 真正发请求拿响应 |
| Spider | 解析响应，产出 Item 与新 Request |
| Item Pipeline | 清洗、校验、存储 Item |
| 下载中间件 | 引擎与下载器之间的钩子 |
| 爬虫中间件 | 引擎与 Spider 之间的钩子 |

1. Spider 生成初始 Request → 引擎 → 下载中间件 → 调度器入队；
2. 调度器出队 Request → 下载中间件 → 下载器发请求拿响应；
3. 响应经下载中间件 → 引擎 → 爬虫中间件 → Spider 的解析函数；
4. 解析出的数据 yield Item → Pipeline 处理保存；解析出的新 URL 组装成 Request → 回到调度器。

关键点：**所有模块相互独立、只与引擎交互**；中间件的位置决定其职责（下载中间件管请求/响应，爬虫中间件管 Spider 的输入输出）。

## 三、快速上手

### 1. 虚拟环境（以 miniconda 为例）

```bash
conda create -n spider python=3.10   # 创建
conda activate spider                # 激活
pip freeze > requirements.txt        # 导出依赖
pip install -r requirements.txt      # 恢复依赖
```

### 2. 创建项目与爬虫

```bash
pip install scrapy
scrapy startproject myspider         # 创建项目
cd myspider
scrapy genspider douban movie.douban.com   # 生成爬虫（名字 + 允许的域名）
scrapy crawl douban                  # 运行
```

### 3. 编写 Spider

```python
import scrapy

class DoubanSpider(scrapy.Spider):
    name = 'douban'                       # 爬虫名字，运行时用
    allowed_domains = ['douban.com']      # 限制爬取范围（start_urls 不受限）
    start_urls = ['https://movie.douban.com/top250']

    def parse(self, response):
        # response 可直接 .xpath()/.css()
        for ol in response.xpath('//ol[@class="grid_view"]/li'):
            item = {}
            item['title'] = ol.xpath('.//div[@class="hd"]/a/span[1]/text()').extract_first()
            item['rating'] = ol.xpath('.//div[@class="bd"]//span[2]/text()').extract_first()
            item['quote'] = ol.xpath('.//div[@class="bd"]//span[@class="inq"]/text()').extract_first()
            yield item    # yield 只能是 dict / Item / Request / None
```

注意：

- `extract()` 返回字符串列表，`extract_first()` 取第一个（空时为 `None`，不会报错）
- response 常用属性：`url`、`status`、`body`、`text`、`xpath()`、`css()`、`urljoin()`（拼接绝对地址）

### 4. Item 定义字段

```python
import scrapy

class MyspiderItem(scrapy.Item):
    title = scrapy.Field()
    rating = scrapy.Field()
    quote = scrapy.Field()
```

提前规划字段，防止手误；使用方式与字典一致。

### 5. Pipeline 保存数据

```python
import pymysql
import pymongo

class MySQLPipeline:
    def open_spider(self, spider):                 # 爬虫启动时执行一次
        if spider.name == 'douban':
            self.db = pymysql.connect(host='localhost', user='root',
                                      password='root', db='spiders')
            self.cursor = self.db.cursor()

    def process_item(self, item, spider):          # 每个 item 都会经过
        sql = 'INSERT INTO douban(id, title, rating, quote) values(%s, %s, %s, %s)'
        try:
            self.cursor.execute(sql, (0, item['title'], item['rating'], item['quote']))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
        return item    # 必须 return，否则后面的 pipeline 拿到的数据为 None

    def close_spider(self, spider):                # 爬虫关闭时执行一次
        if spider.name == 'douban':
            self.db.close()

class MongoDBPipeline:
    def open_spider(self, spider):
        self.collection = pymongo.MongoClient()['spiders']['douban']

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))     # Item 要先转 dict
        return item
```

在 `settings.py` 开启（数字越小越先经过）：

```python
ITEM_PIPELINES = {
    'myspider.pipelines.MySQLPipeline': 300,
    'myspider.pipelines.MongoDBPipeline': 400,
}
```

多个 pipeline 的意义：按 `spider.name` 区分不同爬虫的数据；或对不同爬虫做不同处理（一个清洗、一个入库）。

## 四、Spider 详解

### 1. Spider 的常用成员

| 成员 | 说明 |
| ---- | ---- |
| `name` | 爬虫唯一标识，`scrapy crawl` 用它选择爬虫，必须唯一 |
| `allowed_domains` | 允许爬取的域名列表（OffsiteMiddleware 过滤依据，`start_urls` 不受限） |
| `start_urls` | 初始 URL 列表；默认实现会逐个 yield Request 且 `dont_filter=True` |
| `start_requests()` | 覆写它可自定义初始请求；Scrapy 2.13+ 改为异步 `start()`，旧的同步写法仍然兼容 |
| `custom_settings` | 类属性字典，仅对该爬虫覆盖项目配置（如并发数、pipeline） |
| `self.logger` | 以爬虫名为前缀的 logger：`self.logger.info('A response from %s just arrived!', response.url)` |
| `closed(reason)` | 爬虫关闭时的回调（`finished`、`cancelled`、`spider_error` 等），等价于挂载 `spider_closed` 信号 |

回调函数的输出约定：只能返回 dict / Item / Request / None 或它们的可迭代组合；给 `callback` 传 `cb_kwargs={'key': value}`，回调可直接以关键字参数接收（如 `def parse_detail(self, response, key)`），比塞进 meta 更规范。

### 2. Spider 参数

用 `-a` 向爬虫传参，参数&#8203;**只能是字符串**&#8203;，需要自行解析成数字或列表：

```bash
scrapy crawl myspider -a category=electronics -a pages=10
```

```python
class MySpider(scrapy.Spider):
    name = 'myspider'

    def __init__(self, category=None, pages=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [f'http://www.example.com/categories/{category}']
```

默认 `__init__` 会把所有参数复制为爬虫属性，所以也可以直接用 `self.category`。

### 3. CrawlSpider：规则化跟进链接

需要"整站跟进链接"时不用手写翻页逻辑，用 `CrawlSpider` + `Rule` 声明式爬取：

```python
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class MySpider(CrawlSpider):
    name = 'example.com'
    allowed_domains = ['example.com']
    start_urls = ['http://www.example.com']

    rules = (
        # 提取 category.php 链接并继续跟进（无 callback 时 follow 默认 True）
        Rule(LinkExtractor(allow=(r'category\.php',), deny=(r'subsection\.php',))),
        # 提取 item.php 链接交给 parse_item 解析
        Rule(LinkExtractor(allow=(r'item\.php',)), callback='parse_item'),
    )

    def parse_item(self, response):
        yield {
            'name': response.xpath('//h1/text()').get(),
            'price': response.xpath('//p[@id="price"]/text()').get(),
        }
```

- `LinkExtractor` 常用参数：`allow` / `deny`（正则）、`allow_domains` / `deny_domains`、`restrict_xpaths` / `restrict_css`（在页面局部提取链接）、`process_value`（对每个链接值再加工）
- `Rule` 参数：`callback`（解析回调）、`follow`（是否继续跟进）、`cb_kwargs`、`process_links` / `process_request`（过滤与加工请求，可用于设优先级）、`errback`
- 多条 Rule 都匹配同一个链接时，**按定义顺序取第一条**；初始 URL 的响应交给 `parse_start_url` 处理

### 4. XMLFeedSpider / CSVFeedSpider：解析 feed

```python
from scrapy.spiders import XMLFeedSpider

class MySpider(XMLFeedSpider):
    name = 'example.com'
    start_urls = ['http://www.example.com/feed.xml']
    iterator = 'iternodes'   # 基于 lxml 的快速迭代器，推荐；xml/html 会整页加载 DOM
    itertag = 'item'         # 要迭代的节点名

    def parse_node(self, response, node):
        yield {
            'id': node.xpath('@id').get(),
            'name': node.xpath('name').get(),
        }
```

CSVFeedSpider 类似，按行迭代：`delimiter`（默认 `,`）、`quotechar`（默认 `"`）、`headers`（列名列表），回调方法为 `parse_row(self, response, row)`，row 是列名到值的字典。

### 5. SitemapSpider：从 sitemap 发现 URL

```python
from scrapy.spiders import SitemapSpider

class MySpider(SitemapSpider):
    name = 'example.com'
    sitemap_urls = ['http://www.example.com/sitemap.xml']   # 也可直接指向 robots.txt
    sitemap_rules = [('/product/', 'parse_product')]        # (正则, 回调)，顺序匹配取第一条

    def parse_product(self, response):
        yield {'name': response.xpath('//h1/text()').get()}
```

支持嵌套 sitemap（`sitemap_follow` 按正则筛选要跟进的 sitemap）与多语言 alternate 链接（`sitemap_alternate_links=True`）。

## 五、选择器 Selectors

Scrapy 的选择器基于 lxml 构建，response 可直接 `.xpath()` / `.css()`。

### 1. 取值 API

```python
>>> response.css('title::text').get()        # 新 API：取第一个，无结果返回 None
'Welcome to Python.org'
>>> response.xpath('//a/@href').getall()     # 新 API：取全部，返回列表
# 等价旧 API：extract_first() / extract()
>>> response.css('a::attr(href)').attrib     # 快捷取属性字典，SelectorList 也可用
```

- `.get()` 有多个匹配只返回第一个；想拿"第一个非空"可用 `response.css('img::text').get(default='')` 指定默认值
- `.getall()` 返回列表，空结果为 `[]`

### 2. CSS 扩展语法

- `::text` 选中**直接子文本节点**——注意 `p::text` 只取 `<p>` 自己的文本，要含子孙文本用 `p *::text` 或 xpath 的 `string(//p)`
- `::attr(name)` 取属性值：`a::attr(href)`
- 括号内的属性值无需引号也能匹配

### 3. 相对 XPath 的坑

以 `/` 开头的 XPath 是**相对于整个文档**而不是当前节点。想在循环里基于当前元素继续选择，务必以 `./` 开头：

```python
for p in response.xpath('//div[@class="post"]'):
    # 错误：links 是全页面的链接
    # 正确：只取这条 post 内的链接
    links = p.xpath('.//a/@href').getall()
```

### 4. 混用与正则

```python
response.css('a').xpath('./@href').getall()          # css 与 xpath 可链式混用
response.xpath('//a[contains(@href, "image")]').re(r'image-(\d+)\.jpg')   # 正则提取
response.xpath('//a/@href').re_first(r'https://(.*?)\.com')               # 正则取第一个
```

其他实用点：

- XML 文档带命名空间时先 `response.selector.remove_namespaces()` 再解析
- 也可以脱离 response 直接构造：`Selector(text=html_string)`，或对响应体重新构造 `Selector(text=response.text)`
- xpath 内嵌变量：`response.xpath('//a[@href=$url]', url='http://example.com')`

## 六、Item 与数据建模

### 1. Item 与 Field 元数据

`scrapy.Field()` 支持&#8203;**字段元数据**&#8203;，最常见的用途是给 Item Exporter 声明序列化顺序：

```python
import scrapy

class Product(scrapy.Item):
    name = scrapy.Field(serializer=str)
    price = scrapy.Field()
```

`item.fields` 可查看全部声明字段；访问未定义字段会抛 `KeyError`，正好防手误。除 Item 外，Scrapy 同样支持 **dict、dataclass、attrs、pydantic model** 作为 item 类型，pipeline 对它们一视同仁。Item 可以继承扩展（子类加字段或覆盖元数据，如重新指定 `serializer`）。

### 2. ItemLoader：结构化填充 item

页面字段来源分散（多个 xpath、正则、固定值）时，用 ItemLoader 收集，配合输入/输出处理器做清洗：

```python
from scrapy.loader import ItemLoader
from myproject.items import Product

def parse(self, response):
    l = ItemLoader(item=Product(), response=response)
    l.add_xpath('name', '//div[@class="product_name"]')
    l.add_xpath('name', '//div[@class="product_title"]')   # 同一字段可多次 add，结果合并为列表
    l.add_css('stock', 'p#stock')
    l.add_value('last_updated', 'today')
    return l.load_item()
```

- 收集到的数据内部按列表存储，字段可累计多个值
- **输入处理器**（`itemloaders.processors.MapCompose(str.strip)` 等）逐条清洗，**输出处理器**（默认 `TakeFirst`，取第一个非空）决定最终值；在 `ItemLoader` 类中用 `name_in = MapCompose(str.strip)`、`name_out = TakeFirst()` 声明
- 常用处理器：`MapCompose`（串联多个函数）、`TakeFirst`、`Join()`、`Identity`；局部覆盖可用 `l.add_xpath('name', xpath, TakeFirst())`

## 七、翻页与请求

### 1. yield Request 翻页

```python
def parse(self, response):
    for ol in response.xpath('//ol[@class="grid_view"]/li'):
        ...
    next_url = response.xpath("//a[text()='后页>']/@href").extract_first()
    if next_url:
        yield response.follow(next_url, callback=self.parse)
        # 等价于 yield scrapy.Request(response.urljoin(next_url), callback=self.parse)
```

`response.follow` 的优势：&#8203;**自动 urljoin**&#8203;，且直接接收 Selector / `<a>` 元素（自动提取 href），还支持 `cb_kwargs`。

### 2. 重写 start_requests 批量生成

```python
def start_requests(self):
    for i in range(10):
        url = f'https://movie.douban.com/top250?start={i * 25}&filter='
        yield scrapy.Request(url)
```

### 3. scrapy.Request 常用参数

```python
scrapy.Request(url, callback=None, method='GET', headers=None,
               cookies=None, body=None, meta=None, dont_filter=False,
               errback=None, cb_kwargs=None, priority=0)
```

- `callback`：响应交给哪个解析函数
- `cb_kwargs`：&#8203;**传参给回调的首选方式**&#8203;（推荐替代 meta 传参）
- `meta`：仍然可以跨解析函数传数据，如 `yield scrapy.Request(detail_url, callback=self.parse_detail, meta={'item': item})`，在 `parse_detail` 里用 `response.meta['item']` 取回；meta 中还有固定键 `proxy`（代理）与 `download_timeout`
- `dont_filter`：默认 `False` 会按 URL 去重；对内容多变的页面（如贴吧翻页）设 `True` 才能重复请求
- `errback`：请求失败（DNS、超时、连接被拒）时的回调，收到 Twisted `Failure`，可判断异常类型、`failure.request` 拿到原请求；下载成功但状态码为 404 之类的响应**不会**走 errback
- `priority`：调度优先级，数字越大越先出队

```python
def start_requests(self):
    yield scrapy.Request('http://httpbin.org/status/404',
                         callback=self.parse, errback=self.handle_error)

def handle_error(self, failure):
    self.logger.error(repr(failure))
    if failure.check(HttpError):
        response = failure.value.response       # 404 等错误响应
        self.logger.error('HttpError on %s', response.url)
```

### 4. POST 请求：FormRequest

```python
yield scrapy.FormRequest(
    url='http://www.cninfo.com.cn/new/disclosure',
    formdata={'column': 'szse_latest', 'pageNum': str(page), 'pageSize': '30'},
    callback=self.parse,
)
```

模拟登录时可基于页面已有表单自动回填字段，再覆盖账号密码：

```python
yield scrapy.FormRequest.from_response(
    response,
    formdata={'username': 'xxx', 'password': 'xxx'},
    callback=self.after_login,
)
```

### 5. Response 类型

- `TextResponse`：文本响应，支持 `.text`、`.xpath()`、`.css()`
- `HtmlResponse` / `XmlResponse`：TextResponse 的子类
- `JsonResponse`：响应体是 JSON 时自动选用，可直接 `response.json` 取数据（此时不能再 xpath）

### 6. scrapy shell 调试

```bash
scrapy shell https://movie.douban.com/top250
>>> response.xpath('//ol[@class="grid_view"]/li').extract_first()
>>> response.request.headers
```

shell 内置辅助对象：

| 对象 | 说明 |
| ---- | ---- |
| `response` / `request` | 当前响应与生成它的请求 |
| `spider` | 处理该 URL 的 Spider 对象 |
| `sel` | response 的选择器 |
| `shelp()` | 打印以上可用对象的帮助 |
| `fetch(url)` / `fetch(request)` | 抓取新地址并更新 shell 里的变量 |
| `view(response)` | 用本机浏览器打开"Scrapy 抓到的"页面，检查与真实浏览器渲染的差异 |

不用跑整个爬虫就能验证 XPath，是日常调试利器。

## 八、Item Pipeline

### 1. 自定义 Pipeline 保存数据

见第三节的 MySQL / MongoDB Pipeline。`process_item` 返回 item 继续流向后续 pipeline，抛 `DropItem` 则丢弃该 item（并计数到 `item_dropped` 统计）。

### 2. 去重 Pipeline

官方示例：丢弃已处理过的 item（适合内容型数据，如商品）：

```python
from scrapy.exceptions import DropItem

class DuplicatesPipeline:
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['id'] in self.ids_seen:
            raise DropItem(f'Duplicate item found: {item!r}')
        self.ids_seen.add(item['id'])
        return item
```

### 3. 内置 Files / Images Pipeline

item 中给出&#8203;**媒体 URL 列表字段**&#8203;，框架自动异步下载并落盘：

```python
class MyImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item['image_urls']:
            yield scrapy.Request(url)          # 下载失败会自动重试并在 item_completed 收到结果

    def file_path(self, request, response=None, info=None, *, item=None):
        return f'full/{request.url.split("/")[-1]}'   # 自定义保存路径
```

- 数据字段：FilesPipeline 用 `item['file_urls']` / 结果存 `item['files']`；ImagesPipeline 用 `item['image_urls']` / 结果存 `item['images']`（含 `path`、`checksum`、图片尺寸）
- 图片管道额外支持格式转换与压缩：`IMAGES_MIN_HEIGHT` / `IMAGES_MIN_WIDTH` 过滤小图，`IMAGES_THUMBS` 生成缩略图，`IMAGES_EXPIRES` 过期重下
- 相关配置：`FILES_STORE` / `IMAGES_STORE`（本地路径，或 `s3://` 桶）、`MEDIA_ALLOW_REDIRECTS`（默认禁止重定向）
- 用途声明：务必写明下载图片的目的（如图像识别数据集），并尊重版权与网站条款

## 九、Feed 导出（内置导出）

不想写 pipeline 时，&#8203;**一行配置把 item 直接导出成文件**&#8203;，支持 json / jsonlines / csv / xml / pickle / marshal：

```python
FEEDS = {                                   # 新版统一配置（推荐）
    'items_%(time)s.json': {                # %(time)s、%(name)s 会被替换
        'format': 'json',
        'encoding': 'utf8',
        'indent': 4,
        'store_empty': False,               # 没抓到数据就不生成文件
        'item_classes': [MyItem],           # 只导出指定 item 类型（过滤器）
        'overwrite': True,
    },
    'ftp://user:pass@ftp.example.com/%(name)s/%(time)s.csv': {'format': 'csv'},
}
```

常用配套配置：

```python
FEED_EXPORT_ENCODING = 'utf-8'        # json 默认用数字编码输出，常需指定
FEED_EXPORT_FIELDS = ['title', 'rating']   # 指定字段顺序（csv 必配，否则顺序不定）
FEED_EXPORT_BATCH_ITEM_COUNT = 1000   # 每千条分一个文件，配合 %(batch_id)s 命名
```

存储后端开箱支持：本地文件系统、FTP、S3（`pip install scrapy[s3]`）、Google Cloud Storage、stdout；URI 里可用 `%(time)s`、`%(name)s`、`%(batch_id)s` 参数生成带时间戳的文件名。旧版配置项 `FEED_FORMAT` + `FEED_URI` 仍然兼容。

## 十、settings.py 关键配置

### 1. 常用配置

```python
ROBOTSTXT_OBEY = False              # 是否遵守 robots 协议
USER_AGENT = 'Mozilla/5.0 ...'      # 默认 UA
DEFAULT_REQUEST_HEADERS = {}        # 默认请求头
CONCURRENT_REQUESTS = 16            # 并发请求数（全局）
CONCURRENT_REQUESTS_PER_DOMAIN = 8  # 每个域名的并发上限
DOWNLOAD_DELAY = 0.5                # 下载延迟
DOWNLOAD_TIMEOUT = 180              # 下载超时（秒），可被 meta['download_timeout'] 覆盖
COOKIES_ENABLED = True              # 是否启用 Cookie
RETRY_TIMES = 2                     # 失败重试次数（含超时、50x 等）
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
REDIRECT_MAX_TIMES = 20             # 最大重定向次数
LOG_LEVEL = 'WARNING'               # 日志等级（默认 DEBUG）
LOG_FILE = './log.txt'              # 日志写入文件（另见 LOG_FILE_APPEND、LOG_ENABLED）
```

### 2. AutoThrottle 自动限速

与其手工调 `DOWNLOAD_DELAY`，不如开启自动限速（默认已开启），根据**响应延迟**动态调整每个域名的延迟，把并发稳定在目标值附近：

```python
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5.0        # 初始延迟
AUTOTHROTTLE_MAX_DELAY = 60.0         # 最大延迟
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0 # 每站点平均目标并发
AUTOTHROTTLE_DEBUG = True             # 打开可看到每次调整的延迟
```

算法要点：爬虫总是以 `DOWNLOAD_DELAY` 起步；每收到一个响应，按 `延迟/AUTOTHROTTLE_TARGET_CONCURRENCY` 调整该域名的延迟；发生错误响应时自动放慢——这比固定小延迟 + 硬并发上限更友好。

### 3. HTTP 缓存

调试阶段给请求加缓存，重复运行不再真正联网：

```python
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0         # 0 表示永不过期
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
```

### 4. 配置优先级

命令行 `-s KEY=VALUE` > Spider 的 `custom_settings` > 项目 `settings.py` > 各命令默认配置 > 全局默认配置。

## 十一、下载中间件

中间件是 Scrapy 最强的扩展点：换 UA、挂代理、接 Selenium 都在这里做。

### 1. 随机 User-Agent

```python
# middlewares.py
import random
from myspider.settings import USER_AGENTS_LIST

class UserAgentMiddleware:
    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(USER_AGENTS_LIST)
```

```python
# settings.py
DOWNLOADER_MIDDLEWARES = {
    'myspider.middlewares.UserAgentMiddleware': 543,
}
```

### 2. 代理 IP

代理写在 `request.meta['proxy']`（框架内置的 HttpProxyMiddleware 会读取它，也可用 `request.meta['auth']` 做认证）：

```python
class ProxyMiddleware:
    def process_request(self, request, spider):
        request.meta['proxy'] = random.choice(PROXIES)   # 'http://ip:port'
        request.meta['download_timeout'] = 3

    def process_response(self, request, response, spider):
        if response.status not in (200, 302):
            # 该代理不可用：换代理重试
            request.meta['proxy'] = get_another_proxy()
            return request        # 返回 Request 交给调度器重新调度
        return response

    def process_exception(self, request, exception, spider):
        # 下载异常（超时、连接拒绝等）在此处理，返回 Request 可重新调度
        request.meta['proxy'] = get_another_proxy()
        return request
```

四个钩子方法的返回约定：

| 方法 | 返回值含义 |
| ---- | ---- |
| `process_request` | `None` 继续流程；返回 `Response` 则不再请求；返回 `Request` 交回调度器 |
| `process_response` | 返回 `Response` 继续向上；返回 `Request` 重新调度 |
| `process_exception` | 返回 `None` 交给内置异常处理（重试中间件等）；返回 `Request` 重新调度 |
| `from_crawler` | 类方法构造器，可访问 crawler（settings、signals、stats） |

**权重规则**：数字越小越先执行 `process_request`；数字越大越先执行 `process_response`；`process_exception` 沿权重从小到大依次尝试。

### 3. 内置下载中间件

这些能力默认已挂好，多数只需调配置：

| 中间件 | 作用 | 关键配置 |
| ---- | ---- | ---- |
| RobotsTxtMiddleware | 拉取并遵守 robots.txt | `ROBOTSTXT_OBEY` |
| HttpAuthMiddleware | HTTP Basic 认证 | `HTTPUSER` / `HTTPPASS` |
| DownloadTimeoutMiddleware | 读 meta['download_timeout'] | `DOWNLOAD_TIMEOUT` |
| DefaultHeadersMiddleware | 填充默认请求头 | `DEFAULT_REQUEST_HEADERS` |
| UserAgentMiddleware | 设置 UA | `USER_AGENT` |
| RetryMiddleware | 失败重试 | `RETRY_TIMES` / `RETRY_HTTP_CODES` |
| HttpCompressionMiddleware | gzip/deflate/br 解压 | `COMPRESSION_ENABLED` |
| RedirectMiddleware | 跟随重定向 | `REDIRECT_ENABLED` / `REDIRECT_MAX_TIMES` |
| CookiesMiddleware | Cookie 持久化与会话 | `COOKIES_ENABLED` / `COOKIES_DEBUG` |
| HttpProxyMiddleware | 读 meta['proxy'] 设置代理 | — |
| HttpCacheMiddleware | 请求/响应缓存 | `HTTPCACHE_ENABLED` 等 |
| AjaxCrawlMiddleware | 抓取 `#!` 形式的可爬取 AJAX 页面 | `AJAXCRAWL_ENABLED` |

### 4. Selenium 中间件（应对动态渲染）

```python
import scrapy
from scrapy import signals
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class SeleniumMiddleware:
    def __init__(self):
        self.browser = webdriver.Chrome()

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_request(self, request, spider):
        self.browser.get(request.url)
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'recruit-list-link')))
        # 用渲染后的源码构造 Response，不再经过下载器
        return scrapy.http.HtmlResponse(url=request.url, body=self.browser.page_source,
                                        request=request, encoding='utf-8')

    def spider_closed(self):
        self.browser.quit()
```

## 十二、Spider 中间件与扩展

### 1. Spider 中间件

爬虫中间件位于引擎与 Spider 之间，处理 Spider 的输入（response）与输出（item/request）：

- `process_spider_input(response)`：response 到达 Spider 前调用，返回 `None` 继续；抛异常则交给 `process_spider_exception`
- `process_spider_output(response, result, spider)`：处理回调产出的 item/Request，**必须**返回可迭代结果
- `process_spider_exception(response, exception, spider)`：回调抛异常时调用，返回可迭代结果可"接住"异常，返回 `None` 则继续传递

```python
SPIDER_MIDDLEWARES = {
    'myspider.middlewares.MySpiderMiddleware': 543,
}
```

权重含义与下载中间件相反方向：数字越小越先执行 `process_spider_input`，数字越大越先执行 `process_spider_output`。内置的 `HttpErrorMiddleware`（权重 900，过滤非 200 响应并计入 HttpError 统计）与 OffsiteMiddleware（500，域名过滤）都在这条链上。

### 2. 内置扩展

| 扩展 | 作用 |
| ---- | ---- |
| CoreStats | 统计核心指标（请求数、响应数、item 数等） |
| LogStats | 每分钟向日志打印抓取速度（items/min、pages/min） |
| MemoryUsage | 内存超限报警/关停（`MEMUSAGE_LIMIT_MB` + 邮箱配置） |
| MemoryDebugger | 追踪内存泄漏，需开 `MEMDEBUG_ENABLED` |
| CloseSpider | 按条件自动关停：`CLOSESPIDER_TIMEOUT`、`CLOSESPIDER_ITEMCOUNT`、`CLOSESPIDER_PAGECOUNT`、`CLOSESPIDER_ERRORCOUNT` |
| SpiderState | 配合 `JOBDIR` 持久化爬虫状态，实现断点续爬 |
| TelnetConsole | 远程控制台，默认 `localhost:6023` 可 `telnet` 进去查看/修改运行状态 |
| PeriodicLog | 定期把统计数据打点输出，便于监控 |

### 3. 信号与自定义扩展

Scrapy 内置了丰富的信号：`spider_opened`、`spider_closed`、`spider_idle`、`item_scraped`、`item_dropped`、`item_error`、`response_received`、`bytes_received` 等，可在中间件 / 扩展 / pipeline 中用 `crawler.signals.connect` 挂载，实现事件监控。自定义扩展即一个带 `from_crawler` 的类：

```python
class MyExtension:
    def __init__(self, crawler):
        crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)
        self.stats = crawler.stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def spider_closed(self, spider):
        self.stats.get_value('response_received_count')   # 读取统计值
```

```python
EXTENSIONS = {'myspider.extensions.MyExtension': 0}
```

## 十三、运行中调试

- **inspect_response**：在解析函数里随时"跳进" shell 检查现场，退出（Ctrl-D）后爬虫继续跑：

```python
from scrapy.shell import inspect_response

def parse(self, response):
    inspect_response(response, self)   # 需要实时验证选择器时插入
    ...
```

- **scrapy view url**：对比浏览器渲染的页面与 Scrapy 抓到的原始 HTML，判断内容是否由 JS 注入
- **scrapy parse url --spider xxx**：只调试单个 URL 的解析逻辑，`--callback`、`--pipelines` 控制范围
- **日志**：代码里用 `self.logger.info(...)`（自带爬虫名前缀）；统计信息可用 `crawler.stats.get_stats()` 全量导出，排查"为什么没抓到数据"先看 `response_received_count` 与 `httperror_count`

## 十四、部署与断点续爬

### 1. JOBDIR 断点续爬

```bash
scrapy crawl douban -s JOBDIR=crawls/douban-1
```

- 暂停方式：发 `Ctrl-C` 两次（第一次进入"温和停机"，跑完当前任务再停）
- 调度队列、去重指纹、spider.state 都持久化在 JOBDIR 目录，再次用同一 JOBDIR 启动即恢复现场
- 官方说明：恢复存在极少量重复请求的可能，对幂等任务无影响

### 2. scrapyd

生产环境把爬虫常驻部署在服务器上，用 [scrapyd](https://scrapyd.readthedocs.io/)（HTTP 服务守护多爬虫）+ [scrapyd-client](https://scrapyd.readthedocs.io/en/latest/deploy.html)（`scrapyd-deploy` 打包上传 egg）。通过 `schedule.json` API 远程调度、取消、查看任务；云端托管可选 Zyte Scrapy Cloud（`shub` 命令部署），自托管也可用 Docker 镜像运行。

## 十五、分布式 scrapy-redis

单机 Scrapy 的调度队列与去重指纹都在内存里；**scrapy-redis 把它们搬到公共 Redis**，多台服务器即可共享任务队列，实现分布式：

- 请求对象持久化 + 去重指纹持久化（基于 Redis set）
- 所有机器从同一个 Redis 取任务；Master 往 `redis_key` 里 push 初始 URL，Slave 负责下载与入库

核心配置：

```python
# 使用 scrapy-redis 的调度器与去重器
SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
REDIS_URL = 'redis://172.25.197.89:6379/0'

# 调度队列：默认 PriorityQueue（有序集合）；可选 FifoQueue / LifoQueue
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'

# 爬取队列与指纹集合持久化（默认爬完自动清空）
SCHEDULER_PERSIST = True

# Item 也可以直接写入 Redis
ITEM_PIPELINES = {'scrapy_redis.pipelines.RedisPipeline': 400}
```

Spider 改为继承 `RedisSpider`，不再写 `start_urls`，改由 Redis 分发任务：

```python
from scrapy_redis.spiders import RedisSpider

class DangdangSpider(RedisSpider):
    name = 'dangdang'
    redis_key = 'dd:start'      # Redis 列表键

    def parse(self, response):
        for li in response.xpath('//ul[@class="bigimg"]/li'):
            item = DdItem()
            item['title'] = li.xpath('./a/@title').extract_first()
            item['price'] = li.xpath('./p[@class="price"]/span[1]/text()').extract_first()
            yield item
        # 翻页照常
        next_url = response.xpath('//li[@class="next"]/a/@href').extract_first()
        if next_url:
            yield response.follow(next_url, callback=self.parse)
```

向 Redis 投放起始任务：

```python
import redis
r = redis.Redis()
r.lpush('dd:start', 'http://search.dangdang.com/?key=python&act=input&page_index=1')
```

::: warning
`SCHEDULER_FLUSH_ON_START = True` 会在每次启动时清空队列——分布式环境下只允许一台机器在首次启动时使用，否则会反复清空任务。
:::

## 十六、常见报错速查

| 报错 | 解决 |
| ---- | ---- |
| `AttributeError: module 'OpenSSL.SSL' has no attribute 'SSLv3_METHOD'` | 降级：`pip install pyOpenSSL==22.0.0 cryptography==38.0.4 Twisted==20.3.0` |
| `TypeError: ProactorEventLoop is not supported`（Windows） | settings 中加 `asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())` |
| 爬虫跑完没数据 | 检查 `ROBOTSTXT_OBEY`、UA、`allowed_domains`，用 `scrapy view url` 对比 scrapy 看到的页面 |
| pipeline 拿到 None | 前一个 pipeline 的 `process_item` 忘了 `return item` |
| `Filtered offsite request` 日志刷屏 | 链接域名不在 `allowed_domains` 里；确认是否需要加域名或显式 `dont_filter` |
| 回调收不到 meta / 参数 | 优先改用 `cb_kwargs`；检查 `parse(self, response, **kwargs)` 签名是否接收了关键字参数 |

## 十七、小结

- 记住一条数据流：**Spider → 引擎 → 调度器 → 下载器 → Spider → Item Pipeline**，中间件是各环节的插桩点
- 翻页与详情页数据传递靠 `yield Request + cb_kwargs`（旧写法 meta），`response.follow` 自动补全相对地址
- 解析优先 `get()` / `getall()`，循环内相对 XPath 记得以 `./` 开头
- 换 UA / 代理 / Selenium 都在下载中间件完成；限速交给 AutoThrottle，调试缓存交给 HTTPCACHE
- 不写 pipeline 也能用 FEEDS 直接导出 json / csv；断点续爬用 JOBDIR，常驻部署用 scrapyd
- 数据量大、需要多机协作时上 scrapy-redis 或 [feapder](/tech-stack/crawler/basics/feapder)
