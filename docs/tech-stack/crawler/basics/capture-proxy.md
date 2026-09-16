---
title: 抓包与代理池
weight: 7
---

# 抓包与代理池

## 一、抓包工具 Charles

Charles（青花瓷）是一款基于 HTTP 协议的代理服务器：让它成为电脑或手机的代理，所有请求经它转发，即可截取请求与响应进行分析。

### 1. 工作原理

```text
客户端 → Charles（代理）→ 服务端
客户端 ← Charles（代理）← 服务端
```

前提：运行 Charles 并配置代理端口（默认 8888），客户端指向该代理。

主要功能：HTTP/HTTPS 代理、流量控制（弱网模拟）、并发请求、**重复发包（Repeat）**、**断点修改请求与响应**。

### 2. HTTPS 抓包配置

先理解为什么需要证书。HTTPS 建连时，客户端会**验证服务器证书的真伪**（是否由可信机构签发、域名是否匹配），验证不通过就拒绝连接。抓包工具的原理是做「中间人」：

```text
客户端 ←→ Charles（对客户端伪装成服务器）←→ 真实服务器
```

Charles 给浏览器出示的是**自己签发**的证书，浏览器自然不认，连接直接失败。解决办法就是把 Charles 的根证书装进系统并设为「受信任」——相当于告诉浏览器「这张假证书也是可信的」，之后 Charles 就能把加密流量解密后再转发，你才能看到明文。配置步骤：

1. `Help → SSL Proxying → Install Charles Root Certificate`，安装到「受信任的根证书颁发机构」；
2. `Proxy → SSL Proxying Settings` 添加要解密的域名与端口（`*:443`），否则抓到的 HTTPS 内容是乱码；
3. PC 端浏览器配合 SwitchyOmega 等插件指向 127.0.0.1:8888 即可。

### 3. 断点调试

选中目标请求 → 右击勾选 Breakpoints，请求发出时会暂停，可以：

- 修改请求参数后再放行（构造测试数据）
- 修改响应内容，观察页面表现，快速定位接口与数据的关系

### 4. 安卓 / 模拟器抓包

App 爬虫的第一步是抓包看接口。以夜神模拟器为例（要求手机与电脑同一局域网）：

1. `cmd` 执行 `ipconfig` 查到电脑 IPv4 地址；
2. 模拟器 WiFi 设置 → 长按当前网络 → 修改网络 → 手动代理，填电脑 IP 与 8888 端口；
3. 模拟器浏览器访问 `chls.pro/ssl` 下载证书，到「设置 → 安全 → 从存储设备安装」导入。

::: tip
高版本 Android（7+）出于安全考虑，App 默认**只信任预装在系统目录里的证书**，用户手动安装的证书对 App 无效——所以装完证书浏览器能抓、App 却抓不到。解决办法：把 Charles 证书伪装成系统证书写入系统目录（需要 root / 模拟器），或用 Xposed/LSPosed 模块（如 JustTrustMe）让 App 信任用户证书；部分 App 还会内置「证书锁定（SSL Pinning）」，需要用 Frida 等工具绕过。
:::

抓到接口后，就可以用 requests 模拟 App 的请求头（通常是移动端 UA + 加密参数）直接采集，例如豆果美食 App：

```python
import requests

url = 'https://api.douguo.net/home/notes/40/20'
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; SM-G973N) ... Mobile Safari/537.36'
}
data = {
    'client': '4',
    '_session': '1670347900014351564608872123',
    'direction': '2',
    'request_count': '1',
    'sign_ran': '8b3bbbd68fead8c06020f4fc3f266e3f',
    'code': '54adff5470d6b097',
}
response = requests.post(url, headers=headers, data=data)
print(response.json())
```

## 二、免费代理采集与检测

### 1. 代理的作用

- 隐藏真实 IP，避免被服务器封禁
- 更换 IP 绕过频率限制（反反爬的核心手段之一）

免费代理站：快代理、89 免费代理、云代理、无忧代理、66 免费代理等。**免费 IP 可用率通常不足 20%**，采集后必须逐一测试。

### 2. 采集 + 验证流程

思路：爬代理站列表页 → 解析出 `IP:端口` → 逐个请求 `http://httpbin.org/ip` 验证 → 可用的存入文件或数据库。

```python
import requests
from lxml import etree

class ProxyPool:
    def __init__(self):
        self.base_url = 'https://www.kuaidaili.com/free/inha/{}/'
        self.test_url = 'http://httpbin.org/ip'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    def get_response(self, url, proxies=None):
        try:
            return requests.get(url, headers=self.headers, proxies=proxies, timeout=3).text
        except Exception as e:
            print('请求有误:', e)
            return None

    def parse(self, html):
        tree = etree.HTML(html)
        for tr in tree.xpath('//table//tbody/tr'):
            ip, port = tr.xpath('./td/text()')[0], tr.xpath('./td/text()')[1]
            proxies = {'http': f'http://{ip}:{port}'}
            self.verify(proxies)

    def verify(self, proxies):
        try:
            response = requests.get(self.test_url, headers=self.headers,
                                    proxies=proxies, timeout=2)
            if response.status_code == 200:
                print('可用:', proxies, response.text)
                with open('proxy.txt', 'a') as f:
                    f.write(proxies['http'] + '\n')
        except Exception:
            print('超时淘汰:', proxies)

    def run(self, pages=3):
        for page in range(1, pages + 1):
            html = self.get_response(self.base_url.format(page))
            if html:
                self.parse(html)

if __name__ == '__main__':
    ProxyPool().run()
```

::: warning
免费代理过期很快：入池前要验证，**每次使用前也要验证**，并定期重测清理失效 IP。
:::

## 三、付费代理

「免费：除了免费没有优点；付费：除了付费没有缺点。」生产环境建议购买付费代理（如快代理、芝麻代理等）：

1. 注册账号，按项目选择套餐；
2. 在订单页生成 **API 提取链接**（可设置提取数量、返回格式、分隔符）；
3. 代码里定期请求该链接获取新 IP，配合队列维护一个本地代理池。

使用私密代理（带认证）的示例：

```python
import requests
from queue import Queue
from retrying import retry

class Crawler:
    def __init__(self):
        self.ip_url = 'https://dps.kdlapi.com/api/getdps/?secret_id=xxx&num=1&signature=xxx'
        self.username, self.password = '账号', '密码'
        self.ip_queue = Queue()

    def get_ip(self):
        """后台线程：代理池不足时从 API 补充"""
        while True:
            if self.ip_queue.empty():
                self.ip_queue.put(requests.get(self.ip_url).text.strip())

    @retry(stop_max_attempt_number=3)
    def get_data(self, url):
        ip = self.ip_queue.get()
        auth = {'user': self.username, 'pwd': self.password, 'proxy': ip}
        proxies = {
            'http': 'http://%(user)s:%(pwd)s@%(proxy)s/' % auth,
            'https': 'http://%(user)s:%(pwd)s@%(proxy)s/' % auth,
        }
        response = requests.get(url, proxies=proxies, timeout=2, verify=False)
        if response.status_code == 200:
            self.ip_queue.put(ip)        # 好用的 IP 放回去复用
        else:
            assert '状态码错误'
        return response
```

## 四、代理池的设计

一个完整的代理池包含四个模块：

```text
采集器 ──→ 存储（Redis DB）──→ 校验器（定时重测）──→ 调度 API（随机取一个可用 IP）
   ↑__________________________________________________|
                     失效 IP 删除
```

- **存储**：Redis 的 `zset`，score 存可用分数（成功 +1，失败 -1，低于阈值删除）
- **校验**：定时任务批量重测，兼顾「刚采的」和「池里的」
- **调度**：Flask/FastAPI 暴露 `/get`（随机取一个）与 `/pop`（取出并删除）接口
- **使用方**：爬虫请求失败时换一个 IP 重试；也可以把 `dont_filter`/重试逻辑与代理结合

社区现成方案可参考 [proxy_pool](https://github.com/jhao104/proxy_pool)，原理与上图一致。

## 五、小结

- App 爬虫三步走：**抓包 → 分析接口 → 代码模拟**
- 免费代理要「采集即验证、用前再验证」；付费代理用 API 提取 + 本地池维护
- 代理只是反反爬的一环，还需配合随机 UA、Cookie 管理、请求频率控制
- 代理失效被识别时，Charles 的 Repeat 与断点功能也能帮助复现和调试问题请求
