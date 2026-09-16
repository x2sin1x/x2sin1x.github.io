---
title: 请求发送 requests
weight: 2
---

# 请求发送 requests

## 一、requests 入门

Socket 需要手工处理 HTTP 协议细节，而 `requests` 把这些全部封装好了。安装：

```bash
pip install requests
```

最小示例——请求百度首页：

```python
import requests

url = 'https://www.baidu.com'
response = requests.get(url)
print(response.text)
```

### 1. Response 常用属性

| 属性 | 说明 |
| ---- | ---- |
| `response.text` | 响应体（str 类型，自动推测编码） |
| `response.content` | 响应体（bytes 类型，二进制数据用它） |
| `response.status_code` | 状态码 |
| `response.headers` | 响应头 |
| `response.request.headers` | 实际发出的请求头 |
| `response.cookies` | 服务器设置的 Cookie（CookieJar 对象） |
| `response.url` | 最终请求的 URL（重定向后） |
| `response.json()` | 把 JSON 响应直接解析成 Python 对象 |

### 2. text 与 content 的区别

- `response.text`：requests 根据 HTTP 头推测编码解码成字符串，推测错误会乱码，可手动指定 `response.encoding = 'gbk'`
- `response.content`：原始字节流，自己控制解码 `response.content.decode('utf-8')`

**获取网页源码的通用方式**：先 `response.content.decode()`，乱码再换 `decode('gbk')`，最后才用 `response.text`。

### 3. 下载二进制文件

```python
import requests

url = 'https://www.baidu.com/img/bd_logo1.png'
response = requests.get(url)

with open('baidu.png', 'wb') as f:   # 二进制写入模式
    f.write(response.content)
```

## 二、请求头与请求参数

### 1. 为什么要带请求头

不带 UA 直接请求，服务器返回的内容往往与浏览器不一致，甚至直接拒绝。带上 `User-Agent` 模拟浏览器是最基本的伪装：

```python
import requests

url = 'https://www.baidu.com'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
response = requests.get(url, headers=headers)
print(response.request.headers)   # 验证请求头已生效
```

### 2. 发送带参数的 GET 请求

查询参数既可以拼在 URL 里，也可以用 `params` 传字典（自动 URL 编码）：

```python
import requests

headers = {'User-Agent': 'Mozilla/5.0'}

# 方式一：params 参数
url = 'https://www.sogou.com/web'
kw = {'query': 'python'}
response = requests.get(url, headers=headers, params=kw)

# 方式二：参数直接写进 URL
url = 'https://www.sogou.com/web?query=python'
response = requests.get(url, headers=headers)
```

::: tip
抓包时经常看到 URL 上挂着一长串参数，其中很多是没用的。逐个删掉再请求，只保留必要的参数，代码会干净很多。
:::

### 3. 发送 POST 请求

登录、提交表单、翻页接口通常都是 POST。数据用 `data`（表单）还是 `json`（JSON 体）传递，**必须与抓包时看到的请求一致**，二者的区别：

| 参数 | 实际发出的请求头 | 请求体长什么样 |
| ---- | ---------------- | ---------------- |
| `data={'a': 1}` | `Content-Type: application/x-www-form-urlencoded` | `a=1&b=2`（表单格式） |
| `json={'a': 1}` | `Content-Type: application/json` | `{"a": 1, "b": 2}`（JSON 格式） |

服务器会按 `Content-Type` 决定怎么解析请求体：抓包里是 `application/json` 你却用 `data` 传，服务器解析不到参数，轻则返回 400，重则返回空数据还看不出原因。**判断方法：看 DevTools 载荷面板里参数是「表单数据」还是「请求 JSON」**。另外上传文件用 `files` 参数：`requests.post(url, files={'f': open('a.jpg', 'rb')})`。

传参方式：

```python
import requests

url = 'http://www.cninfo.com.cn/new/disclosure'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
data = {
    'column': 'szse_latest',
    'pageNum': '2',
    'pageSize': '30',
    'clusterFlag': 'true',
}
response = requests.post(url, headers=headers, data=data)
print(response.json())
```

::: warning
GET 的 URL 长度有上限（IE 2083 字符等），大文本传输务必使用 POST；POST 参数也相对更不容易出现在服务器日志里。
:::

## 三、Cookie 的三种处理方式

### 1. Cookie 放在 headers 中

从浏览器复制整个 Cookie 字符串（分号分隔的 `name=value` 对）：

```python
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Cookie': 'JSESSIONID=204BABEA1EEB; insert_cookie=45380249; routeId=.uc1',
}
requests.get(url, headers=headers)
```

简单粗暴，但 Cookie 有过期时间，过期后要重新复制。

### 2. Cookie 以字典传给 cookies 参数

```python
cookies = {
    'JSESSIONID': '204BABEA1EEB',
    'insert_cookie': '45380249',
}
requests.get(url, headers=headers, cookies=cookies)
```

### 3. 使用 Session 会话保持（推荐）

`requests.session()` 可以理解为「**一个自带记忆的简易浏览器**」：它自动保存服务器返回的 Cookie（Set-Cookie 下来、下次请求自动带上），并在多次请求间复用 TCP 连接加快速度。登录、翻页等多步操作都应该用 Session 而不是裸的 `requests.get()`，否则第二步请求不带第一步的 Cookie，服务器会把你当陌生访客：

```python
import requests

session = requests.session()
# 第一次请求：服务器返回的 Cookie 自动保存在 session 中
session.get('http://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice',
            headers=headers)
# 第二次请求：自动带上前一次的 Cookie
res = session.get('http://www.cninfo.com.cn/new/disclosure', headers=headers)
print(res.request.headers)
```

CookieJar 转字典的小工具：

```python
cookies = requests.utils.dict_from_cookiejar(response.cookies)
```

## 四、代理的使用

### 1. 正向代理与反向代理

- **正向代理**：客户端知道服务器的真实地址，代理替客户端转发请求（如 VPN），爬虫用的是这种
- **反向代理**：客户端不知道真实服务器在哪，由 nginx 等统一转发

### 2. 代理的分类

按匿名程度：

- **透明代理**：隐藏了 IP 但服务器仍能查到真实来源
- **匿名代理**：知道你用了代理，但不知道你是谁
- **高匿代理**：完全看不出在用代理，效果最好

按协议：http、https、socks 代理，需与目标网站协议匹配。

### 3. 代码示例

proxies 字典的**键表示哪种协议的请求走这个代理，值是代理地址**：只配 `http` 键时，HTTPS 请求不走代理；目标站是 HTTPS 就要把 `https` 键也配上。代码示例：

```python
import requests

proxies = {'http': 'http://106.15.190.190:3128'}
response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=3)
print(response.text)   # 返回的 IP 应该是代理的 IP，而不是你本机的
```

带用户名密码认证的付费代理：

```python
proxies = {
    'http': 'http://%(user)s:%(pwd)s@%(proxy)s/' % {'user': 'xxx', 'pwd': 'xxx', 'proxy': 'ip:port'},
    'https': 'http://%(user)s:%(pwd)s@%(proxy)s/' % {'user': 'xxx', 'pwd': 'xxx', 'proxy': 'ip:port'},
}
```

::: tip 反反爬思路
即使使用了代理，服务器仍可能通过**访问频率**、**Cookie/UA/Referer 校验**、**代理 IP 黑名单**识别爬虫。应对方式：随机选择代理而不是固定用一个、控制请求频率、请求头保持完整一致。代理池的搭建见[抓包与代理池](/tech-stack/crawler/basics/capture-proxy)一章。
:::

## 五、超时与重试

### 1. 超时参数

不设超时的请求在网络波动时可能永久挂起，让整个爬虫卡死。`timeout` 强制限时：

```python
response = requests.get(url, timeout=3)   # 3 秒未响应即抛异常

# 更精细的写法：元组分别限制「建立连接」和「等待响应」的时间
code = requests.get(url, timeout=(3, 10))   # 连接最多 3 秒，读数据最多 10 秒
```

超时参数也可以用来检测代理质量——长时间无响应的代理直接从池中剔除。

### 2. retrying 自动重试

```bash
pip install retrying
```

```python
import requests
from retrying import retry

headers = {'User-Agent': 'Mozilla/5.0'}

@retry(stop_max_attempt_number=3)   # 最多重试 3 次
def _parse_url(url):
    response = requests.get(url, headers=headers, timeout=3)
    assert response.status_code == 200, '状态码不正确'   # 非 200 也触发重试
    return response

def parse_url(url):
    try:
        return _parse_url(url)
    except Exception as e:
        print(e)
        return None
```

### 3. 证书错误

HTTPS 建连时，requests 默认会（`verify=True`）用系统内置的 CA 证书列表校验服务器证书的真伪。有些网站证书过期、自签名或被公司代理替换，就会报 `ssl.CertificateError`，此时关闭校验即可（数据仍是加密的，只是不验证对方身份，生产环境更推荐用 `verify='证书.pem'` 指定证书）：

```python
import urllib3
urllib3.disable_warnings()   # 屏蔽告警

response = requests.get(url, verify=False)
```

## 六、小结

一条爬虫请求的「标准姿势」：

```python
import requests

session = requests.session()
session.headers.update({'User-Agent': '...'})
response = session.get(url, params=params, timeout=5, proxies=proxies)
response.raise_for_status()
```

- 二进制用 `content`，乱码手动指定编码
- 需要维持登录态/多步请求时优先用 Session
- 代理 + 超时 + 重试是爬虫稳定运行的三件套
