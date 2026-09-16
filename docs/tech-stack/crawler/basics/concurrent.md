---
title: 高性能爬虫
weight: 5
---

# 高性能爬虫

爬虫是典型的 **IO 密集型**任务：发出请求后程序一直在等响应，什么也不做。并发就是让「等待」的时间被其他任务利用起来。

## 一、基本概念

| 概念 | 关注点 | 说明 |
| ---- | ------ | ---- |
| 同步 / 异步 | 消息通信机制 | 同步需要协调等待结果；异步调用后立即返回，不关心结果何时到达 |
| 阻塞 / 非阻塞 | 等待结果时的状态 | 阻塞时程序挂起什么都做不了；非阻塞可以继续处理其他事情 |

此外要理解 Python 的 **GIL**（全局解释器锁）：CPython 解释器规定，同一时刻一个进程内**只有一个线程**在执行 Python 字节码。打个比方：厨房里有 5 个厨师（线程），但只有一口锅（GIL），大家只能轮流用锅。那多线程还有意义吗？有——因为**发请求后的「等待响应」不占锅**：线程在等待网络 IO 时会释放 GIL，让其他线程去干活。爬虫恰恰是 90% 时间都在等的 IO 密集任务，所以多线程对爬虫依然有效；但若是 CPU 密集任务（如大规模图片处理、计算哈希），等待时间几乎为零，多线程毫无加速效果，应该用多进程（每个进程有自己的一口锅）。

## 二、多线程 + 队列

多线程爬虫的经典思路：**把爬虫每个环节（取 URL → 请求 → 解析 → 入库）封装成函数，各用线程执行，线程间用队列传递数据实现解耦**。

```python
import time
import threading
import requests
import pymongo
from queue import Queue

class Aqiyi:
    def __init__(self):
        self.collection = pymongo.MongoClient(host='127.0.0.1', port=27017)['spider']['aqy']
        self.url = 'https://pcw-api.iqiyi.com/search/recommend/list?channel_id=2&mode=11&page_id={}&ret_num=48'
        self.url_queue = Queue()           # URL 队列
        self.json_queue = Queue()          # 响应队列
        self.item_queue = Queue()          # 数据队列

    def get_url(self):
        """生产 URL"""
        for i in range(1, 5):
            self.url_queue.put(self.url.format(i))

    def get_data(self):
        """请求网页（多个线程跑同一个 while True）"""
        while True:
            url = self.url_queue.get()
            response = requests.get(url).json()
            self.json_queue.put(response)
            self.url_queue.task_done()     # get 后必须 task_done 让计数 -1

    def parse_data(self):
        """解析数据"""
        while True:
            data = self.json_queue.get()
            for video in data['data']['list']:
                self.item_queue.put({'title': video['title'],
                                     'playUrl': video['playUrl']})
            self.json_queue.task_done()

    def save_data(self):
        """入库"""
        while True:
            item = self.item_queue.get()
            self.collection.insert_one(item)
            self.item_queue.task_done()

    def main(self):
        thread_list = [threading.Thread(target=self.get_url)]
        thread_list += [threading.Thread(target=self.get_data) for _ in range(3)]
        thread_list += [threading.Thread(target=self.parse_data),
                        threading.Thread(target=self.save_data)]

        for t in thread_list:
            t.setDaemon(True)              # 守护线程：主线程结束子线程随之结束
            t.start()

        # 阻塞等待三个队列的计数都归零，保证数据全部处理完
        for q in [self.url_queue, self.json_queue, self.item_queue]:
            q.join()

if __name__ == '__main__':
    start = time.time()
    Aqiyi().main()
    print('总耗时:', time.time() - start)
```

::: warning 队列的两个易错点
1. `put` 使队列计数 +1，但 `get` 不会自动 -1，必须配套调用 `task_done()`；
2. `task_done()` 不能放在下一个队列 `put` 之前，否则可能出现数据未处理完程序就退出。
:::

用 `url_queue` 走一遍计数，帮助理解 `join()` 为什么能等全部任务完成：

```text
生产者 put 了 4 个 URL          → 计数 4
3 个请求线程各自 get 走 1 个     → 计数仍为 4（get 不减！）
每个线程处理完调用 task_done()  → 计数 3 → 2 → 1 → 0
主线程的 q.join() 在计数归 0 时放行，继续检查下一个队列
```

所以「三队列 + join」的含义是：**直到每个 URL 都被请求完、每个响应都被解析完、每条数据都被入库完，主线程才结束**。少写一处 `task_done()`，计数永远到不了 0，程序就会卡死在 `join()`。

## 三、线程池

线程池复用固定数量的线程，避免频繁创建销毁的开销，写法也比手动管理简单：

```python
from concurrent.futures import ThreadPoolExecutor
import requests

def crawl(page):
    url = f'https://talent.baidu.com/httservice/getPostListNew'
    data = {'recruitType': 'SOCIAL', 'pageSize': 10, 'curPage': page}
    response = requests.post(url, data=data)
    return response.json()

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(crawl, i) for i in range(1, 10)]
        for future in futures:
            result = future.result()      # 阻塞获取结果
            print(len(result['data']['list']))
```

关键 API：`submit(fn, *args)` 提交任务返回 Future、`future.done()` 判断是否结束、`future.result()` 取返回值、`shutdown()` 关闭线程池。

## 四、多进程

受 GIL 限制，多线程在 CPython 下未必真并行；CPU 密集或需要真并行时用多进程，思路与多线程相同，注意两点：

- 进程间通信用 `multiprocessing.JoinableQueue`（普通 Queue 会阻塞报错）
- 数据库连接等对象不能被 pickle，要在各进程内部创建

```python
from multiprocessing import Process
from multiprocessing import JoinableQueue as Queue

def get_data(data_queue, json_queue):
    while True:
        data = data_queue.get()
        response = requests.get(url, json=data)
        json_queue.put(response.json())
        data_queue.task_done()

def main():
    data_queue, json_queue = Queue(), Queue()
    for i in range(1, 10):
        data_queue.put(build_payload(i))

    process_list = [Process(target=get_data, args=(data_queue, json_queue)) for _ in range(5)]
    for p in process_list:
        p.daemon = True
        p.start()

    json_queue.join()

if __name__ == '__main__':
    main()
```

## 五、异步协程

### 1. 原理

`asyncio` 实现单线程并发 IO：`async` 声明异步函数，`await` 处把控制权交还给事件循环去跑其他任务。并发请求量大的场景，异步比多线程更轻量。

```bash
pip install aiohttp
```

### 2. 同步 vs 异步对比

```python
# 同步：30 次请求串行，总耗时 ≈ 30 × 单次耗时
import requests, time

def main_sync():
    for i in range(30):
        requests.get('https://www.baidu.com')
```

```python
# 异步：30 次请求并发，总耗时 ≈ 最慢的一次
import asyncio
import aiohttp

async def fetch(session, i):
    async with session.get('https://www.baidu.com') as res:
        print(f'第 {i + 1} 次，status = {res.status}')

async def main():
    async with aiohttp.ClientSession() as session:   # 类似 requests.session()
        tasks = [asyncio.create_task(fetch(session, i)) for i in range(30)]
        await asyncio.wait(tasks)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
```

aiohttp 与 requests 的差异：代理参数叫 `proxy`（单数）；获取二进制用 `await response.read()`；取文本 `await response.text(encoding='gbk')`。

### 3. 异步图片下载实战

```python
import asyncio
import aiohttp
import os

class CrawlImage:
    def __init__(self):
        self.skin_url = 'https://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/{}/{}/{}-bigskin-{}.jpg'
        self.list_url = 'https://pvp.qq.com/web201605/js/herolist.json'
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        os.makedirs('图片', exist_ok=True)

    async def download(self, session, ename, cname):
        for i in range(1, 10):
            async with session.get(self.skin_url.format(ename, ename, i),
                                   headers=self.headers) as response:
                if response.status != 200:
                    break
                content = await response.read()
                with open(f'图片/{cname}-{i}.jpg', 'wb') as f:
                    f.write(content)
            print(f'下载 {cname} 第 {i} 张成功')

    async def run(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.list_url, headers=self.headers) as res:
                hero_list = await res.json(content_type=None)
            tasks = [asyncio.create_task(self.download(session, h['ename'], h['cname']))
                     for h in hero_list]
            await asyncio.wait(tasks)

if __name__ == '__main__':
    asyncio.run(CrawlImage().run())
```

### 4. 异步存储：aiomysql 与 motor

异步爬虫配套的异步驱动：MySQL 用 `aiomysql`，MongoDB 用 `motor`。

```python
import asyncio
import aiomysql

async def main():
    # 创建连接池
    pool = await aiomysql.create_pool(host='127.0.0.1', port=3306,
                                      user='root', password='root', db='spiders')
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT * FROM tx LIMIT 5')
            print(await cursor.fetchall())
            await conn.commit()

asyncio.run(main())
```

在 `save_data` 中先通过连接池 `acquire` 连接、再执行 SQL，配合 Redis 去重即可组成完整的异步爬虫；抓取侧给每页请求之间加 `await asyncio.sleep(random.uniform(0.5, 0.8))` 控制频率。

## 六、方案选择

| 场景 | 推荐 |
| ---- | ---- |
| 几百到几千页的普通采集 | 线程池（代码最简单） |
| 环节多、需要解耦 | 多线程 + Queue 生产消费模型 |
| CPU 密集（如解析大文件） | 多进程 |
| 上万并发请求、高吞吐 | asyncio + aiohttp + 异步驱动 |
| 更大规模 | 直接上 Scrapy / feapder 框架（见下一章） |
