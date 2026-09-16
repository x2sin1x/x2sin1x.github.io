---
title: feapder 框架
weight: 9
---

# feapder 框架

Scrapy 优秀但"裸"：数据入库、去重、断点续爬、报警监控都要自己拼插件。**[feapder](https://feapder.com/) 把这些全部内置**——写好解析函数后，数据能根据数据库表自动批量入库，任务自动去重、失败自动重试、异常自动报警，官方文档：[feapder.com](https://feapder.com)，源码：[github.com/Boris-code/feapder](https://github.com/Boris-code/feapder)。

## 一、简介与安装

### 1. 四种爬虫

feapder 内置四种爬虫，覆盖从单机脚本到分布式批次采集的全部场景：

| 爬虫 | 定位 | 依赖 | 典型场景 |
| ---- | ---- | ---- | ---- |
| **AirSpider** | 轻量单机爬虫 | 无需 Redis | 数据量少、无需断点续爬与分布式 |
| **Spider** | 基于 Redis 的分布式爬虫 | Redis | 海量数据采集、断点续爬、数据自动入库 |
| **TaskSpider** | 分布式任务爬虫 | Redis（MySQL 可选） | 种子任务存放在 Redis / MySQL 的场景 |
| **BatchSpider** | 分布式批次爬虫 | Redis + MySQL | 周期性采集（如每日更新商品销量），自动维护批次信息表 |

学习路线建议 AirSpider → Spider → BatchSpider：它们对外暴露的接口完全一致，后者基于前者逐步丰富，只需更换继承的基类即可平滑升级。

### 2. 安装

环境要求 Python 3.6+，支持 Linux / Windows / macOS。按需选择三个版本：

```bash
pip install feapder               # 精简版
pip install "feapder[render]"     # 浏览器渲染版
pip install "feapder[all]"        # 完整版
```

- 精简版：不支持浏览器渲染、不支持基于内存的去重、不支持入库 mongo
- 浏览器渲染版：不支持基于内存的去重、不支持入库 mongo
- 完整版：支持所有功能（安装出错时参考官方[安装问题](https://feapder.com/#/question/安装问题)）

### 3. 功能概览

- 支持周期性批次采集、分布式采集，且可随时重启爬虫，任务不丢失
- 支持爬虫集成：把多个爬虫以插件形式集成为一个，适合周期一致但数据源多个的项目
- 内置 3 种海量数据去重机制，可对任务与数据自动去重，也可单独作为模块使用
- 数据自动入库：根据数据库表生成 item，赋值后直接 yield 即可批量入库
- 强状态控制任务：URL 抓取 100% 不丢失，多次失败的 URL 进入错误队列并记录原因
- 支持 Debug 模式：针对单个任务调试，默认数据不入库、不修改任务状态
- 完善的报警机制：抓取超时预判、爬虫卡死报警、任务失败数过多报警；下载监控可打入 InfluxDB 结合 Grafana 面板展示

## 二、架构与工作流程

```text
 start_requests → request_buffer（请求缓冲队列） → 任务队列数据库
                                                      ↑↓
                     collector（任务收集器，批量取任务到内存）
                                                      ↓
                     parser_control（模板控制器，多线程） → request（下载器） → response
                                                      ↓
                     parser（解析函数）→ item / 新 request
                                                      ↓
                     item_buffer（数据缓冲队列） → 批量入库
```

模块职责：

- **spider**：框架调度核心
- **parser_control**：模板控制器，负责调度 parser（图示多个即多线程）
- **collector**：任务收集器，从任务队列批量取任务到内存，降低对任务队列数据库的访问频率与并发量
- **request_buffer / item_buffer**：请求与数据的缓冲队列，批量写入任务队列 / 批量入库
- **request**：下载器，封装了 requests
- **response**：响应封装，支持 xpath、css、re 解析，自动处理中文乱码

流程：spider 调度 `start_request` 生产任务 → 经 request_buffer 批量存入任务队列 → collector 批量取任务到内存 → parser_control 调度 request 下载 → 封装成 response 交给 parser 解析 → 解析出的 item 与新 request 分别流入 item_buffer 与 request_buffer 批量入库/下发。

## 三、快速上手

### 1. 创建爬虫

```bash
pip install feapder
feapder create -s first_spider    # 创建单个爬虫（-p 创建项目，-i 创建 item）
```

生成的代码可直接运行：

```python
import feapder


class FirstSpider(feapder.AirSpider):
    def start_requests(self):
        yield feapder.Request("https://www.baidu.com")

    def parse(self, request, response):
        print(response)


if __name__ == "__main__":
    FirstSpider().start()
```

代码讲解：

1. `start_requests`：初始任务下发入口（生产任务）
2. `feapder.Request`：基于 requests 封装的请求，支持 requests 所有参数，还可携带任意自定义参数
3. `parse`：数据解析函数
4. `response`：支持 xpath、re、css 等解析方式
5. 除这两个函数外，框架还内置了下载中间件 `download_midware` 等钩子（见 BaseParser）

### 2. 加快采集速度

默认 1 线程，启动时传线程数即可：

```python
if __name__ == "__main__":
    FirstSpider(thread_count=10).start()
```

### 3. 主动停止爬虫

```python
def parse(self, request, response):
    self.stop_spider()    # 可在任意地方调用
```

## 四、翻页与请求

### 1. yield Request 下发新任务

解析函数中可以直接下发新任务，写法与 `start_requests` 一致：

```python
def parse(self, request, response):
    for article in response.xpath('//a[@class="recmd-content"]'):
        title = article.xpath("./text()").extract_first()
        url = article.xpath("./@href").extract_first()
        yield feapder.Request(url, callback=self.parse_detail, title=title)

def parse_detail(self, request, response):
    print(request.url, request.title)    # url 自动补全为绝对地址
    content = response.xpath('string(//div[@class="content"])').extract_first()
```

### 2. 自定义解析函数与携带参数

- `callback` 指定回调函数，不指定时默认回调 `parse`
- **跨解析函数传数据不需要 meta**：直接以关键字参数写在 Request 里，如 `feapder.Request(url, title=title)`，在回调中用 `request.title` 取回，可携带字典、类等任意类型（key 不能与 Request 默认参数冲突）

### 3. Request 常用参数

```python
feapder.Request(url, callback=None, retry_times=0, priority=300,
                filter_repeat=True, render=False, render_time=0,
                method=None, params=None, data=None, headers=None,
                cookies=None, proxies=None, timeout=None, **kwargs)
```

| 参数 | 说明 |
| ---- | ---- |
| `callback` | 回调函数，也可以是函数名（配合 `parser_name` 可跨类回调） |
| `retry_times` | 当前重试次数（框架内部维护） |
| `priority` | 请求优先级，越小越优先，默认 300 |
| `filter_repeat` | 是否去重，需配合配置 `REQUEST_FILTER_ENABLE = True` 生效 |
| `auto_request` | 是否自动请求下载网页，设为 `False` 时 response 为空，需自己去请求 |
| `request_sync` | 是否同步请求。默认异步排队；url 即将过期时可设 `True` 立即响应 |
| `download_midware` | 自定义下载中间件（只对该请求生效） |
| `is_abandoned` | 异常时是否放弃重试，默认 `False` |
| `render` / `render_time` | 是否浏览器渲染 / 渲染等待时长 |
| `**kwargs` | 其余键值对直接挂到 request 上，如 `title=title` → `request.title` |

method、params、data、headers、cookies、proxies、timeout 等与 requests 用法一致。

## 五、Response 解析

Response 对 requests 的返回体做了封装，除原有方法外增强了：

- **智能解码**：自动处理绝大多数乱码；相对链接**自动转为绝对链接**
- `xpath()` / `css()`：与 Scrapy 一致，`extract_first()` / `extract()` 取值，两种定位方式可混用（`response.css("a").xpath("./@href")`）
- `re()` / `re_first()`：正则提取，源码中提取 json 时建议 `replace_entities=False`，避免 `&nbsp;` 等被转义破坏结构
- `bs4()`：BeautifulSoup 解析，默认 `html.parser`
- `response.json`：取 json（注意是属性不是方法）；`response.code = "gbk"` 指定编码（`encoding` 的简写）；`response.open()` 在浏览器中打开下载内容方便核对

```python
# 乱码处理：框架解码默认用 strict 模式，字符解不出来会直接报错，
# 防止乱码混入数据。遇到报错时指定编码，或改为 ignore 忽略
response.code = "网页编码"
response.encoding_errors = "ignore"    # strict / replace / ignore
```

## 六、数据自动入库（Item 与 Pipeline）

这是 feapder 相比 Scrapy 最省心的部分：**配置好数据库连接后，yield 出的 item 自动批量入库**。

### 1. 生成 Item 并入库

```bash
feapder create -i spider_data    # 根据 mysql 表生成 item（表名去掉 Item 即数据表）
```

```python
from feapder import Item


class SpiderDataItem(Item):
    """
    This class was generated by feapder.
    command: feapder create -i spider_data.
    """

    def __init__(self, *args, **kwargs):
        # self.id = None  # type : int(10) unsigned | key : PRI | extra : auto_increment
        self.title = None  # type : varchar(255) | allow_null : YES
```

解析时给 item 赋值后直接 yield：

```python
def parse(self, request, response):
    for li in response.xpath("//ol/li"):
        item = SpiderDataItem()
        item.title = li.xpath(".//span[1]/text()").extract_first()
        yield item
```

item 会流入框架的 ItemBuffer，**每 0.5 秒或积攒到 5000 条批量入库**；表名为类名去掉 Item 后的小写（`SpiderDataItem` → `spider_data` 表）。也可以不生成类，直接 `item = Item(); item.table_name = "spider_data"; item.title = title`。

### 2. Item 指纹（入库前去重）

默认用所有字段值排序后计算的 md5 做指纹，但数据里若有采集时间就不合理了，可指定参与去重的 key：

```python
class SpiderDataItem(Item):
    __unique_key__ = ["title", "url"]    # 指纹为 title 与 url 联合计算的 md5
```

还可用 `item.unique_key = ["title", "url"]` 动态指定，或重写 `fingerprint` 属性完全自定义。入库前的回调 `pre_to_db` 可做清洗（如 `self.title = self.title.strip()`）。

### 3. 更新数据：UpdateItem

漏采或解析出错时，可将已入库数据做更新而不是插入：

```python
item = SpiderDataItem.to_UpdateItem()    # 或让 Item 类直接继承 UpdateItem
```

### 4. Pipeline

默认使用 MysqlPipeline，内置 mysql、mongo、csv、console 管道，在 setting.py 的 `ITEM_PIPELINES` 中启用；elasticsearch、kafka 等更多管道从 [feapder_pipelines](https://github.com/Boris-code/feapder_pipelines) 按需安装。自定义管道继承 `BasePipeline`，实现 `save_items(table, items) -> bool`（item 会被聚合成多条批量流入，返回 `False` 会触发重试且不入去重库）：

```python
from feapder.pipelines import BasePipeline
from typing import Dict, List


class Pipeline(BasePipeline):
    """pipeline 是单线程的，不建议在这里写下载图片等网络请求代码"""

    def save_items(self, table, items: List[Dict]) -> bool:
        print("保存数据 >>>>", table, items)
        return True
```

```python
ITEM_PIPELINES = ["pipeline.Pipeline"]    # 值为类的模块路径，需指定到类名
```

### 5. MysqlDB / RedisDB

框架封装了 `MysqlDB`（线程池）与 `RedisDB`（支持哨兵、集群），也可手动取出来写 SQL：

```python
from feapder.db.mysqldb import MysqlDB

# setting.py 或 __custom_setting__ 里配好连接信息后：
db = MysqlDB()
db.find("select * from spider_data limit 10")

# 没有配置文件时传连接信息：
db = MysqlDB(ip="localhost", port=3306, user_name="feapder",
             user_pass="feapder123", db="feapder")
```

## 七、去重（Dedup）

框架内置 3 种去重机制，通过配置即可对**请求与入库数据**自动去重：

```python
ITEM_FILTER_ENABLE = False     # item 去重
REQUEST_FILTER_ENABLE = False  # request 去重
ITEM_FILTER_SETTING = dict(filter_type=1)
REQUEST_FILTER_SETTING = dict(filter_type=3, expire_time=2592000)
```

| filter_type | 机制 | 特点 |
| ---- | ---- | ---- |
| 1 | 永久去重 BloomFilter | 基于 redis，一万条约 3.5 秒，一亿条占内存约 285MB |
| 2 | 内存去重 MemoryFilter | 一万条约 0.5 秒，一亿条约 285MB |
| 3 | 临时去重 ExpireFilter | 基于 redis，有时效性，一万条约 0.26 秒，一亿条约 1.43G |

Dedup 也可单独作为模块使用，支持批量去重与过滤已存在数据：

```python
from feapder.dedup import Dedup

dedup = Dedup(Dedup.BloomFilter, redis_url="redis://@localhost:6379/0")
dedup.add(datas)                  # 返回 1 表示是新数据
dedup.filter_exist_data(datas)    # 原地过滤掉已存在的数据
```

注意：AirSpider 不支持去重，去重配置对其无效。常用参数还有 `name`（不同数据源用不同去重库）、`error_rate`（误判率，默认 0.00001）、`to_md5`（去重前先转 md5）。

## 八、校验与失败重试

### 1. validate 校验函数

```python
def validate(self, request, response):
    """
    校验 response 是否正确
    - 抛出异常：重试请求
    - 返回 True / None：进入解析函数
    - 返回 False：抛弃当前请求
    可通过 request.callback_name 区分不同回调编写不同校验逻辑
    """
    if response.status_code != 200:
        raise Exception("response code not 200")    # 触发重试
```

### 2. 重试机制

下载失败或解析函数抛出异常会自动重试，默认最大重试次数 100 次，可通过配置修改：

```python
SPIDER_MAX_RETRY_TIMES = 10    # 每个请求最大重试次数
```

## 九、下载中间件与浏览器渲染

### 1. 下载中间件

```python
def download_midware(self, request):
    request.headers = {"User-Agent": "lalala"}    # 支持 requests 所有参数
    return request
```

默认所有请求都会经过此中间件，适合统一加 cookie、header。也可以给单个请求指定专属中间件：`feapder.Request(url, download_midware=self.xxx)`。

### 2. 自定义下载器

在下载中间件里自己下载并返回 response，即可换掉内置下载器（如用 httpx 支持 http2）：

```python
import httpx

def download_midware(self, request):
    with httpx.Client(http2=True) as client:
        response = client.get(request.url)
    return request, response
```

此时解析函数拿到的就是自定义 response，想用 xpath 解析需包一层：`Selector(response.text).xpath(...)`。

### 3. 浏览器渲染

请求上加 `render=True` 即可，支持 Selenium（CHROME / EDGE / PHANTOMJS）与 Playwright 两种渲染下载器：

```python
def start_requests(self):
    yield feapder.Request("https://news.qq.com/", render=True)
```

```python
WEBDRIVER = dict(
    pool_size=1,               # 浏览器数量
    load_images=True,          # 是否加载图片
    proxy=None,                # 代理，xxx.xxx.xxx.xxx:xxxx 或无参函数
    headless=False,            # 无头浏览器
    driver_type="CHROME",      # CHROME、EDGE、PHANTOMJS
    timeout=30,
    window_size=(1024, 800),
    render_time=0,             # 打开网页等待指定时间后再取源码
    xhr_url_regexes=None,      # 拦截 xhr 接口，支持正则
    use_stealth_js=False,      # 用 stealth.min.js 隐藏浏览器特征
    auto_install_driver=True,  # 自动下载浏览器驱动
)
```

::: tip
`xhr_url_regexes` 可以**直接拦截页面里加密前的 XHR 响应**，省去逆向加密参数的步骤，配合逆向章节使用效果更佳；Playwright 对应的参数为 `PLAYWRIGHT` 配置块中的 `url_regexes`。
:::

## 十、配置文件

项目根目录下建 `setting.py`（全部参数见[官方配置文档](https://feapder.com/#/source_code/配置文件)），关键项：

```python
# 数据库
MYSQL_IP = "localhost"
MONGO_IP = "localhost"
REDISDB_IP_PORTS = "localhost:6379"    # 集群/哨兵用逗号分隔，哨兵需加 REDISDB_SERVICE_NAME

# 爬虫
SPIDER_THREAD_COUNT = 1        # 爬虫并发数，追求速度推荐 32
SPIDER_SLEEP_TIME = 0          # 下载间隔，支持随机 [2, 5]
SPIDER_MAX_RETRY_TIMES = 10    # 每个请求最大重试次数
KEEP_ALIVE = False             # 爬虫是否常驻

# 下载
RETRY_FAILED_REQUESTS = False  # 启动时重新抓取失败的 requests
SAVE_FAILED_REQUEST = True     # 保存失败的 request
REQUEST_LOST_TIMEOUT = 600     # request 防丢：超时未完成会重新下发重做
REQUEST_TIMEOUT = 22

# 下载缓存（基于 redis，建议仅开发调试用，防止每次 debug 都重新请求）
RESPONSE_CACHED_ENABLE = False
RESPONSE_CACHED_EXPIRE_TIME = 3600

# 代理与 UA
PROXY_EXTRACT_API = None       # 代理提取 API，返回格式为 ip:port，\r\n 分隔
RANDOM_HEADERS = True          # 随机 User-Agent
USER_AGENT_TYPE = "chrome"     # chrome / opera / firefox / internetexplorer / safari / mobile

# 报警
WARNING_INTERVAL = 3600        # 相同报警的间隔，防止刷屏
WARNING_LEVEL = "DEBUG"        # DEBUG / ERROR
WARNING_FAILED_COUNT = 1000    # 任务失败数超过此值报警

# 日志
LOG_LEVEL = "DEBUG"            # 线上部署建议改为 INFO
LOG_IS_WRITE_TO_FILE = False
LOG_PATH = "log/feapder.log"
```

一个项目下多个爬虫需要不同配置时，用类变量 `__custom_setting__` 自定义，支持配置文件中的所有参数；**优先级：自定义配置 > 配置文件**，且只对自己有效：

```python
class SpiderTest(feapder.AirSpider):
    __custom_setting__ = dict(
        SPIDER_MAX_RETRY_TIMES=20,
        PROXY_EXTRACT_API="代理提取地址",
    )
```

::: warning
setting.py 必须放在**工作区间的根目录**下才会生效；数据库账号等敏感信息建议写到环境变量里（环境变量的 key 与配置文件的 key 相同，框架读取不到 setting 时会取环境变量）。
:::

## 十一、分布式 Spider 与断点续爬

单机 AirSpider 的任务队列在内存里；**Spider 把任务队列搬到公共 Redis**，多台服务器即可共享任务实现分布式，且天然支持断点续爬：

```python
import feapder


class SpiderTest(feapder.Spider):
    # 自定义数据库，若项目中有 setting.py 文件，此自定义可删除
    __custom_setting__ = dict(
        REDISDB_IP_PORTS="localhost:6379", REDISDB_USER_PASS="", REDISDB_DB=0
    )

    def start_requests(self):
        yield feapder.Request("https://www.baidu.com")

    def parse(self, request, response):
        print(response)


if __name__ == "__main__":
    SpiderTest(redis_key="feapder:spider_test").start()
```

- `redis_key`：redis 中存储任务等信息的 key 前缀，如 `feapder:spider_test` 会在 redis 下生成任务队列、失败任务等一组 key
- **分布式**：直接启动多份 Spider（多机部署或单机多进程）即可，框架保证任务不重复下发
- **断点续爬 / 防丢**：任务状态持久化在 redis，可随时重启；`REQUEST_LOST_TIMEOUT` 时间内没做完的 request 会重新下发重做
- Spider 支持 AirSpider 的全部方法，数据自动入库见第六节

### 1. Debug 调试

`to_DebugSpider` 把原爬虫直接转为 debug 爬虫，针对某条任务调试（通常配合断点），运行产生的数据默认不入库：

```python
spider = SpiderTest.to_DebugSpider(
    redis_key="feapder:spider_test",
    request=feapder.Request("http://www.baidu.com"),   # 也可传 request_dict={"url": "..."}
)
spider.start()
```

### 2. 运行多个 Spider

建议把启动入口统一放到项目根目录的 main.py，用框架自带的 `ArgumentParser` 做命令行参数：

```python
from feapder import ArgumentParser

parser = ArgumentParser(description="Spider测试")
parser.add_argument("--test_spider", action="store_true", help="测试Spider", function=test_spider)
parser.start()
```

```bash
python3 main.py --test_spider
```

### 3. TaskSpider

种子任务存放于 Redis / MySQL 时可用 TaskSpider：重写 `add_task` 往 redis 里塞种子任务（zset），`start_requests(self, task)` 接收任务字段并拼接请求，master 用 `start_monitor_task()` 下发监控任务，worker 用 `start()` 采集。

## 十二、批次爬虫 BatchSpider

周期性采集（如每 7 天全量更新商品价格）优先用 BatchSpider，它会自动维护**任务表**与**批次信息表**，详细记录每个批次的抓取状态，本批次未完成下一批次不会开始，且自动为每条数据维护 `batch_date` 批次时间，方便业务做时序展示。

```python
import feapder


class BatchSpiderTest(feapder.BatchSpider):
    def start_requests(self, task):
        id, url = task                       # task 为任务表里取出的每条任务
        yield feapder.Request(url, task_id=id)

    def parse(self, request, response):
        print(response)
        yield self.update_task_batch(request.task_id, 1)   # 任务做完，更新状态为 1


if __name__ == "__main__":
    spider = BatchSpiderTest(
        redis_key="feapder:batch_spider",    # 分布式爬虫调度信息存储位置
        task_table="batch_spider_task",      # mysql 中的任务表，需提前建好
        task_keys=["id", "url"],             # 需要获取的任务表字段，可多个
        task_state="state",                  # 任务状态字段
        batch_record_table="batch_record",   # 批次信息表，爬虫自动创建
        batch_name="批次爬虫测试",            # 批次名字，用于报警等
        batch_interval=7,                    # 批次周期，天为单位；小时可写 1 / 24
    )
    # spider.start_monitor_task()   # master：下发及监控任务
    spider.start()                   # worker：采集
```

关键点：

- 任务表需包含 `id` 与任务状态两个字段，状态有 4 种：**0 待抓取、1 抓取完毕、2 抓取中、-1 抓取失败**。框架分批下发状态为 0 的任务（置为 2），队列空且仍有状态 2 的任务时视为丢失任务、重置为 0 再下发，直到只剩 1 和 -1 才算采集完毕
- 每个批次开始时默认重置状态非 -1 的任务为 0 重新抓取；需要**增量采集**时把 `init_task` 方法置空即可
- 无效任务更新为 -1 防止一直重试：重写 `failed_request`，对超过最大重试次数的请求 `yield self.update_task_batch(request.task_id, -1)`；失败任务会存到 redis 中（key 以 `z_failed_requests` 结尾）便于排查。`exception_request` 则可处理请求/解析异常的请求（如换 cookie 后重新 yield）
- task 取值方式灵活：`id, url = task`、`task[0]`、`task.id`、`task["id"]` 均可
- 调试用 `to_DebugBatchSpider`，可传 `task_id` 或 `task`，`save_to_db` / `update_task` 控制是否入库与更新任务状态

## 十三、报警与监控

内置报警渠道：钉钉、飞书、企业微信、邮件（163）、Qmsg（QQ 推送），配置机器人 Webhook 即可：

```python
# 钉钉报警（安全设置选择自定义关键词，填入 feapder；或用加签 DINGDING_WARNING_SECRET）
DINGDING_WARNING_URL = ""       # 钉钉机器人 api
DINGDING_WARNING_PHONE = ""     # 报警人，支持列表
DINGDING_WARNING_ALL = False    # 是否提示所有人

# 企业微信 / 飞书 / 邮件
WECHAT_WARNING_URL = ""
FEISHU_WARNING_URL = ""
EMAIL_SENDER = ""               # 163 邮箱账号
EMAIL_PASSWORD = ""             # 授权码（非登录密码）
EMAIL_RECEIVER = ""
```

报警场景（保证数据的全量性、准确性、时效性）：

1. **抓取超时预判**：实时计算抓取速度、估算剩余时间，预判在指定抓取周期内是否会超时
2. **爬虫卡死报警**
3. **任务失败数过多报警**：超过 `WARNING_FAILED_COUNT` 触发，通常意味着网站模板改动或被封堵

此外框架对请求总数、成功数、失败数、解析异常数做监控打点，可打入 InfluxDB 结合 Grafana 面板查看（需 feapder >= 1.6.6，配合 feaplat 爬虫管理平台）。

## 十四、常见问题速查

| 问题 | 解决 |
| ---- | ---- |
| 完整版安装出错 | 参考官方安装问题文档，或先装精简版按需补依赖 |
| 解析时抛 `UnicodeDecodeError` | strict 模式防乱码的正常表现：`response.code = "正确编码"` 或 `response.encoding_errors = "ignore"` |
| setting.py 配置不生效 | 确认在工作区间根目录；`__custom_setting__` 优先级更高会覆盖；数据库连接信息优先读环境变量 |
| AirSpider 配置去重无效 | AirSpider 不支持去重，需换 Spider |
| 找不到工作目录/模块导入报错 | 项目根目录有 main.py，编辑器中将项目设为 Sources Root |

## 十五、小结

- 记住一条数据流：**start_requests → 任务队列 → collector → 下载器 → parser → item_buffer 批量入库**，与 Scrapy 思路一致，但缓冲队列批量入库是框架自动完成的
- 跨解析函数传数据直接挂在 Request 上（`request.xxx`），不需要 meta
- 换 UA / 代理在 `download_midware`，动态页面用 `render=True`，能拦截 XHR 时优先 `xhr_url_regexes`
- 选型经验：轻量单机用 AirSpider，海量数据与断点续爬用 Spider，周期性批次采集用 BatchSpider；需要部署调度平台时上 feaplat
