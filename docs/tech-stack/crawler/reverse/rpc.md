---
title: RPC 逆向
weight: 6
---

# RPC 逆向

## 一、什么是逆向中的 RPC

RPC（Remote Procedure Call，远程过程调用）指一个进程通过网络调用另一个进程的方法。放到逆向场景里：

> **把浏览器和本地 Python 看作服务端与客户端**，二者之间通过 WebSocket 协议通信。在浏览器里把加密函数「暴露」出来，Python 直接调用浏览器中现成的加密函数拿到结果——**完全不用关心函数内部逻辑**，省去扣代码、补环境的全部工作量。

适用场景：

- 加密代码极度复杂（瑞数、Akamai、jsvmp 等），还原成本过高
- 只需要低频调用签名/加密函数（如登录加密、签名参数）
- 加密代码更新频繁，逆向跟不上版本迭代

代价：需要保持一个浏览器环境在线，并发能力弱于本地算法。

## 二、WebSocket 基础

WebSocket 是 HTML5 下的新协议（本质基于 TCP），实现了浏览器与服务器之间的**全双工通信**：

- 与 HTTP 的短/长连接不同，WebSocket 是**持久化**协议，协议名为 `ws`（加密为 `wss`）
- 握手阶段借用 HTTP：客户端发 HTTP 请求携带 `Upgrade`、`Connection` 等头，服务端以 HTTP 应答确认切换协议
- 之后双方在同一条 TCP 信道上双向收发消息

### 1. 浏览器端（客户端）

```html
<script>
    // 与服务器约定的连接与端口
    const websocket = new WebSocket('ws://127.0.0.1:8080/');

    websocket.onerror = () => console.log('连接发生错误');
    websocket.onopen = function () { console.log('连接成功'); };
    websocket.onmessage = function (event) {
        console.log('收到服务端消息:', event.data);   // 接收数据
    };
    websocket.onclose = function () { console.log('连接关闭'); };

    function ps() {
        websocket.send(document.getElementById('box').value);  // 发送数据
    }
</script>
```

### 2. Python 服务端

```bash
pip install websockets
```

```python
import asyncio
import websockets

async def echo(websocket):
    message = 'hello world'
    await websocket.send(message)          # 发送数据

async def recv_msg(websocket):
    while 1:
        recv_text = await websocket.recv() # 持续接收数据
        print(recv_text)

async def main_logic(websocket, path):
    await echo(websocket)
    await recv_msg(websocket)

start_server = websockets.serve(main_logic, '127.0.0.1', 8080)
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()          # 保持长连接，持续监听
```

## 三、WebSocket 方案实战：解析加密响应

以「全国建筑市场监管公共服务平台」为例：接口返回的是**加密数据**，页面上由 JS 解密后渲染。

**思路**：与其逆向解密算法，不如把页面里的解密函数借来用——

1. 定位到解密函数 `b`（数据在 `b` 调用后被渲染）；
2. 通过 **Overrides 替换文件**的方式把 WebSocket 客户端代码注入页面：

```javascript
!(function () {
    if (window.flag) return;               // 防止重复注入
    window.flag = true;
    const websocket = new WebSocket('ws://127.0.0.1:8080');
    websocket.onmessage = function (event) {
        var data = event.data;
        var res = b(data);                 // 调用页面现成的解密函数
        console.log(res);
        websocket.send(res);               // 把解密结果发回服务端
    };
})();
```

3. 注入后**刷新页面**让 JS 执行起来；
4. Python 服务端把密文发给浏览器，收浏览器解密后的明文：

```python
import asyncio
import websockets
import requests
import json

def get_data(page):
    headers = {
        'v': '231012',                     # 注意：不带 v 请求头拿到的是密文
        'Referer': 'https://jzsc.mohurd.gov.cn/data/company',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    }
    url = 'https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/list'
    response = requests.get(url, headers=headers,
                            params={'pg': page, 'pgsz': '15', 'total': '450'})
    return response.text

async def echo(websocket):
    for i in range(1, 4):
        data = get_data(i)
        await websocket.send(data)         # 密文发给浏览器

async def recv_msg(websocket):
    while 1:
        recv_text = await websocket.recv()
        print(json.loads(recv_text))       # 浏览器解密后的明文

async def main_logic(websocket, path):
    await echo(websocket)
    await recv_msg(websocket)

start_server = websockets.serve(main_logic, '127.0.0.1', 8080)
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()
```

::: warning
原生 WebSocket 方案需要自己管理「创建连接 → 双向收发 → 保持监听」的整个流程，代码繁琐且容易断线。生产上更推荐下面的 Sekiro。
:::

## 四、Sekiro-RPC

[Sekiro](https://sekiro.iinti.cn/sekiro-doc/) 把连接管理、心跳重连、负载均衡全部封装好，Python 侧直接走 **HTTP 接口**调用，是最省心的方案。

### 1. 架构与核心概念

```text
Python(requests) ──HTTP──→ Sekiro 服务端 ──WebSocket──→ 浏览器(注入的 SekiroClient)
                               │
                    /business-demo/invoke   调用转发接口
                    /business-demo/groupList 分组列表
```

| 概念 | 说明 |
| ---- | ---- |
| `group` | 业务类型（接口组），一个业务一个 group，可挂多个 Action |
| `clientId` | 设备标识，多设备可提供负载均衡与群控 |
| `SekiroClient` | 服务提供者客户端（注入到手机/浏览器），每个 client 有唯一 clientId |
| `registerAction` | 注册接口，同一 group 下可注册多个接口做不同功能 |
| `resolve` | 把结果回传给服务端的方法 |
| `request` | 服务端传来的请求参数，可按键值提取 |

### 2. 环境搭建

1. 安装 Java 环境（JDK 8）；
2. 下载 Sekiro，Windows 双击 `bin/sekiro.bat`（Linux/Mac 为 `sekiro.sh`）启动服务端；
3. 浏览器端加载官方客户端脚本 [sekiro_web_client.js](http://file.virjar.com/sekiro_web_client.js?_=123)。

### 3. 注入代码模板

```html
<script src="http://file.virjar.com/sekiro_web_client.js?_=123"></script>
<script>
    // 生成唯一 uuid
    function guid() {
        function S4() {
            return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
        }
        return (S4() + S4() + '-' + S4() + '-' + S4() + '-' + S4() + '-' + S4() + S4() + S4());
    }

    // 连接服务端并注册
    var client = new SekiroClient(
        'ws://127.0.0.1:5620/business-demo/register?group=rpc-test&clientId=' + guid()
    );

    // 注册业务接口：把页面里的加密函数暴露出去
    client.registerAction('clientTime', function (request, resolve, reject) {
        resolve('' + new Date());
    });
</script>
```

注入方式：

- **控制台直接粘贴**：适合临时调试（注意先过无限 debugger）
- **Overrides 替换文件**：把注入代码加到网站 JS 文件末尾保存，刷新生效，适合长期挂机

### 4. Python 调用

```python
import requests

params = {'group': 'rpc-test', 'action': 'clientTime'}
res = requests.get('http://127.0.0.1:5620/business-demo/invoke', params=params)
print(res.text)
```

### 5. 实战一：同花顺 Cookie（v 参数）

目标 `q.10jqka.com.cn`，`v` 是 JS 生成的 Cookie。

1. Hook Cookie 定位生成点（`rt.update()`）；
2. 替换文件注入 Sekiro 客户端，把生成函数暴露：

```javascript
client.registerAction('ths', function (request, resolve, reject) {
    resolve(rt.update());
});
```

3. Python 每次请求前取一个新 Cookie：

```python
import requests

data = {'group': 'rpc-test', 'action': 'ths'}
res = requests.get('http://127.0.0.1:5620/business-demo/invoke', params=data)
cookie_v = res.json()['data']
```

### 6. 实战二：建筑平台解密 + 传参

`registerAction` 的 handler 里可以直接读取 Python 传来的参数，实现「浏览器函数 + 自定义入参」：

```javascript
client.registerAction('jz', function (request, resolve, reject) {
    const e = request['data'];     // Python 传来的密文
    resolve(b(e));                 // 调用页面解密函数后回传
});
```

Python 侧用 POST 传参（数据量大时用 POST）：

```python
class JianZhu:
    def parse_data(self, data):
        payload = {'group': 'rpc-test', 'action': 'jz', 'data': data}
        res = requests.post('http://127.0.0.1:5620/business-demo/invoke',
                            data=payload, verify=False)
        if res.json().get('data'):
            print(res.json()['data'])
```

## 五、Sekiro 大报文与心跳

SekiroClient 内部已处理两个工程问题，了解即可：

- **心跳重连**：`onclose` 后 2 秒自动重连，避免浏览器休眠后掉线
- **大报文分片**：响应超过 6KB 自动按 5KB 分片（`__sekiro_frame_total` / `__sekiro_index` 标记），Python 侧拿到的仍是完整结果

## 六、RPC 的工程化建议

| 问题 | 方案 |
| ---- | ---- |
| 浏览器掉线 / 页面被关 | 用 headless Chrome + 守护脚本自动打开目标页并重新注入 |
| 并发不足 | 多开浏览器标签/实例，注册不同 `clientId`，Sekiro 自动负载均衡 |
| 注入时机 | 用 Overrides 持久化注入 + 页面加载即执行（避免手动粘贴） |
| 加密依赖 Cookie/登录态 | 保持浏览器里的会话，RPC 调用时自动使用 |
| 频率限制 | RPC 只解决「算签名」，业务请求仍由 Python 发，注意限速 |

## 七、小结

- 原生 WebSocket：`new WebSocket('ws://127.0.0.1:8080')` + `onmessage/send`，自己管连接
- Sekiro：服务端（Java）+ 浏览器注入 `SekiroClient` + `registerAction` 暴露函数，Python HTTP 调 `/business-demo/invoke`
- 注入用 Overrides 持久化，注入后刷新页面生效
- RPC 是「借力」的思路：加密函数在哪运行，就让哪里的函数被你调用
