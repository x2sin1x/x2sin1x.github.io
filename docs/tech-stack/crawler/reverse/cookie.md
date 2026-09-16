---
title: Cookie 反爬
weight: 9
---

# Cookie 反爬

Cookie 反爬指服务器通过校验请求头中的 Cookie 值来区分正常用户与爬虫的手段，在 Web 应用中应用极广。从简单到困难，本章覆盖：响应 Set-Cookie、JS 计算型 Cookie（阿里系）、加速乐、瑞数、Akamai，以及 TLS 指纹与风控的概念。

::: danger 声明
本章内容仅供学习交流使用，严禁用于商业用途和非法用途。
:::

## 一、两大类 Cookie 反爬

```text
① 服务器响应型：浏览器请求 → 服务器响应头 Set-Cookie → 下次请求带上即可
② JS 计算型：   浏览器请求 → 服务器返回一段 JS 代码 → 浏览器执行 JS 生成 Cookie
               → 带着 JS 算出的 Cookie 重新请求才能拿到数据
```

调试通用心法：**逆向 Cookie 之前，先把目标 Cookie 全部清空再刷新页面**，否则 Cookie 早就生成好了，断点与 Hook 都无法命中。

## 二、响应 Set-Cookie 型

最简单的一类：先请求入口页面，从响应头（有时也在页面 HTML 里）拿到 Cookie 与 token，再请求真实接口。

实战要点（以某政务留言板为例）：

- 接口需要 `szxx_session` Cookie + `X-CSRF-TOKEN` 请求头
- token 是写死在页面 JS 里的：`var _CSRF = 'xxx';`，需要先请求页面用正则提取

```python
import re
import requests

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...'}

def get_cookie():
    # 第一次请求：拿响应 Cookie + 页面里的 token
    response = requests.get('http://www.xxx.gov.cn/hdjlpt/published?via=pc', headers=headers)
    session = response.cookies.get('szxx_session')
    csrf = re.findall("var _CSRF = '(.*?)';", response.text)[0]
    return session, csrf

def get_data():
    session, csrf = get_cookie()
    headers['X-Csrf-Token'] = csrf
    response = requests.post('http://www.xxx.gov.cn/hdjlpt/letter/pubList',
                             headers=headers, cookies={'szxx_session': session},
                             data={'offset': '0', 'limit': '20'})
    print(response.text)
```

## 三、JS 计算型：阿里系 acw_sc__v2

### 特征

- 首次请求返回一段混淆 JS（`_0x` 开头的十六进制字符串数组），其中含 `arg1='XXXX'`
- Cookie `acw_sc__v2` 由这段 JS 计算；没带它之前接口返回的就是这段 JS 而非数据
- 刷新时可能进入无限 debugger

### 逆向步骤

1. **过无限 debugger**：Hook `Function.prototype.constructor` 吞掉 debugger：

```javascript
Function.prototype.__constructor_back = Function.prototype.constructor;
Function.prototype.constructor = function () {
    if (arguments && typeof arguments[0] === 'string') {
        if ('debugger' === arguments[0]) return;    // 吞掉 debugger
    }
    return Function.prototype.__constructor_back.apply(this, arguments);
};
```

2. 断点调试找到加密位置，扣出核心算法（本质是**固定置换表 + 与 key 异或**，key 为 `3000176000856006061501533003690027800375`）；
3. Python 两次请求：第一次取 `arg1` 与 `acw_tc`，第二次带上算出的 Cookie：

```python
import re
import requests
import execjs

def get_cookie():
    response = requests.get('https://xueqiu.com/today', headers=headers)
    arg1 = re.findall("arg1='(.*?)';", response.text)[0]
    coo = response.cookies.get('acw_tc')
    js = execjs.compile(open('acw.js', encoding='utf-8').read())
    return coo, js.call('aaa', arg1)      # 返回 acw_sc__v2

def get_data():
    coo, coo2 = get_cookie()
    cookies = {'acw_tc': coo, 'acw_sc__v2': coo2}
    res = requests.get('https://xueqiu.com/today', headers=headers, cookies=cookies)
    print(res.status_code)
```

## 四、加速乐 `__jsl_clearance_s`

### 特征

- Cookie 名里带 `jsl` 字样
- **连续三次请求**：前两次返回 512 状态码 + 一段 JS，第三次才 200
- 抓包工具预览里看不到数据，需要借助抓包工具的「脚本」面板或浏览器 Sources 分析

### 三次请求流程

```text
第 1 次请求 → 512 + JS 代码 A（eval 执行即得 Cookie ①）
第 2 次请求（带 Cookie ①）→ 512 + JS 代码 B（含 go 函数，算出 Cookie ②）
第 3 次请求（带 Cookie ②）→ 200 正常数据
```

分析要点：

- 第一段 JS 直接本地 `eval` 执行即可得到第一个 Cookie
- 第二段 JS 调用 `go` 函数生成挑战值：其中 `ha` 参数决定哈希方式（**md5 / sha1 / sha256 都可能出现**，都要兼容）
- 调试时把断点下在 `go` 函数内部，观察最终生成的 Cookie 结构

Python 侧用 session 串联三次请求，中间两步用 execjs 执行返回的 JS 得到 Cookie。

## 五、瑞数（RiverSecurity）

瑞数 Botgate 是国产最强商反之一，以「动态安全」为核心：动态封装、动态验证、动态混淆、动态令牌，持续变换页面底层代码。

### 特征识别

- 页面 URL **请求两次**，第二次才返回正确内容；第一次常为 **412 状态码**
- 第二次请求带上了 `cookie_s` / `cookie_t` 系列 Cookie（`FSSBBIl1UgzbN7N80T...`）
- **两层无限 debugger**；加密代码通过 `eval` 在 VM 脚本（`VM+数字` 标签）中执行

### 逆向路径（以瑞数 5 为例）

```text
1. 过两层无限 debugger（Hook Function 构造器）
2. Hook document.cookie 定位 Cookie 生成点
   → 发现 Cookie 由 $FG 函数生成，$FG 的代码在 VM 里
3. 向上跟栈找到 eval 调用位置 = VM 入口
   → 入口代码来自第一次 412 请求返回的 HTML（自执行函数）
4. 把 412 页面代码整体保存，同时取下其外链 JS（一般是 ts 数据文件，
   需要用抓包工具的脚本功能拦截下载）
5. 在 Node 中补环境执行，最终通过 document.cookie 拿到正确 Cookie
```

补环境的重点（Proxy 吐环境 + 手工补真，见 [补环境一章](/tech-stack/crawler/reverse/env)）：

```javascript
delete __dirname;
delete __filename;

window = global;
window.top = window;
window.addEventListener = function () {};
window.setTimeout = function () {};
window.setInterval = function () {};

document = {
    createElement: function (arg) { /* 按吐环境日志返回对应结构 */ },
    getElementsByTagName: function (arg) { /* meta / base / script 等 */ },
    addEventListener: function () {},
    documentElement: { addEventListener: function () {} },
};
location = {
    href: 'https://sugh.szu.edu.cn/Html/News/Columns/6/Index.html',
    origin: 'https://sugh.szu.edu.cn',
    protocol: 'https:',
    host: 'sugh.szu.edu.cn',
    pathname: '/Html/News/Columns/6/Index.html',
    ...
};
navigator = {};
navigator.userAgent = 'Mozilla/5.0 ...';
```

Python 侧两步请求：第一次拿 meta content 与动态生成函数并注入 JS 执行取 Cookie，第二次带 Cookie 拿数据。瑞数 6/7 结构类似，检测点更多、补环境更细。

::: tip
瑞数每周小改、每月大改。若非研究目的，**RPC 直接调浏览器**或用现成的补环境框架更省力。
:::

## 六、Akamai

Akamai 是国际 CDN 大厂，其 Bot Manager 通过 Cookie `_abck` 与 `bm_sz` 校验。常见版本 1.75（明文）与 2（编码后）。

### 请求流程

```text
1. 请求网页 → 响应头 Set-Cookie: bm_sz=xxx，页面含外链 sensor JS
2. GET 外链 JS → 拿到采集与加密代码
3. POST 指定路径，带上 sensor_data 参数 → 响应设置正确的 _abck
4. 带着 _abck + bm_sz 正常请求业务接口
```

**逆向目标就是第二步到第三步之间的 `sensor_data`**——它由浏览器环境信息（UA、屏幕、插件、canvas 指纹、鼠标轨迹、事件时序等上百项）采集后加密生成。

### 定位与还原

1. XHR 断点或启动器定位 `sensor_data` 生成点，代码经 `bwt` / `RST` 等高度混淆；
2. 整体扣代码到本地，按吐环境日志补齐环境；核心数据是一段 JSON（含 `ua`、屏幕尺寸、时间戳、鼠标事件等），再经过置换 + 异或 + Base64 自定义字符表编码；
3. Python 三步请求（DHL 为例）：

```python
from curl_cffi import requests       # 注意：用 curl_cffi 过 TLS 指纹
import execjs

session = requests.Session()
response = session.get(url, headers=headers)
bm_sz = response.cookies.get('bm_sz')

sensor_data = execjs.compile(open('1111.js').read()).call('get_data', bm_sz)
response = session.post(sensor_url, headers=headers,
                        data='{"sensor_data":' + sensor_data + '}')
print(response.cookies)              # 拿到 _abck
```

### 风控评分

Akamai 后台有一套评分模型（满分 100）：浏览器插件数组长度、屏幕大小（真用户不会开着抓包工具）、IP、canvas 指纹等每一项都可能扣分，分数不足就不返回正确数据。风控分级：

- **初级**：UA、插件、屏幕分辨率
- **中级**：显卡配置、canvas 指纹、权限指纹
- **高级**：鼠标轨迹、函数执行次数

所以补 Akamai 环境**每个参数都要细致**，这不是「能跑就行」的活。

## 七、TLS 指纹

### 是什么

HTTPS 建连时，TLS 握手的 ClientHello 包（支持的加密套件、扩展、椭圆曲线、顺序等）会形成一个指纹（如 JA3）。**每个客户端库的指纹都不同**：Chrome 是 Chrome 的指纹，Python requests（底层 urllib3）是 urllib3 的指纹。

### 后果

「浏览器能访问、requests 带全请求头也失败」的网站，多半在检测 TLS 指纹——指纹不像浏览器的直接拒绝。注意 TLS 校验发生在 HTTP 请求之前，**与应用层参数无关**，补再多请求头也没用。

### 测试与应对

测试站点：`https://tls.browserleaks.com/json`。

```python
# pip install curl_cffi
from curl_cffi import requests

# impersonate 参数模拟不同浏览器的 TLS 指纹
print(requests.get('https://tls.browserleaks.com/json', impersonate='edge99').json())
print(requests.get('https://tls.browserleaks.com/json', impersonate='chrome110').json())
print(requests.get('https://tls.browserleaks.com/json', impersonate='safari15_3').json())
```

应对方案：`curl_cffi`（首选，API 与 requests 几乎一致）、`tls-client`，或直接 RPC / 真浏览器。Akamai、Cloudflare 系站点基本都要求过 TLS 指纹。

## 八、小结

| 方案 | 强度 | 特征 | 破解思路 |
| ---- | ---- | ---- | -------- |
| 响应 Set-Cookie | ★ | 二次请求带 Cookie | session 自动处理 + 页面提 token |
| 阿里系 acw_sc__v2 | ★★ | 返回混淆 JS + arg1 | Hook 过 debugger → 扣置换异或算法 |
| 加速乐 | ★★ | 三次请求、512 状态码 | 本地 eval 两段 JS，兼容 md5/sha1/sha256 |
| 瑞数 | ★★★★★ | 412 + eval VM + 双 debugger | 补环境 + VM 入口整体执行 |
| Akamai | ★★★★★ | sensor_data + _abck | 补环境细致到风控评分项 + 过 TLS 指纹 |
| TLS 指纹 | 独立维度 | 参数正确仍被拒 | curl_cffi / tls-client 模拟浏览器握手 |

通用方法论：**Hook Cookie 定位生成点 → 过 debugger → 找到入口代码 → 本地补环境执行 → session 串联请求**，强度越高的方案，「补环境」的比重越大。
