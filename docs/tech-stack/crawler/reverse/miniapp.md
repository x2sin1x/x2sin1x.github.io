---
title: 小程序逆向
weight: 11
---

# 小程序逆向

## 一、准备工作

::: warning
小程序调试存在封号风险，务必使用小号操作。
:::

需要的环境：

1. **PC 端微信**（版本需与工具兼容，过新可能无法注入）
2. **WeChatOpenDevTools**：把小程序的开发者工具「打开」，项目地址 github.com/JaveleyQAQ/WeChatOpenDevTools-Python
3. 安装工具所需的 Python 依赖：

```bash
pip3 install -r requirements.txt
```

4. 注入启动（自动打开微信，登录后打开目标小程序即可调试）：

```bash
python main.py -all
```

之后在微信里打开小程序，就拥有了与 Chrome DevTools 相同的调试面板：Network 抓包、Sources 断点、Console 执行 JS。

## 二、小程序抓包与逆向流程

小程序本质是「跑在微信容器里的网页 + 原生组件」，请求多为 HTTPS 接口。流程与网页逆向一致：

```text
打开 DevTools → Network 抓包找到数据接口 → 确认加密参数
→ Sources 搜索关键字 / XHR 断点定位 → 扣代码 / 补环境 → Python 复现
```

注意点：

- 小程序的请求会带特有请求头：`User-Agent` 含 `MicroMessenger`、`MiniProgramEnv`，以及 `xweb_xhr: 1` 等——Python 请求时要原样带上
- 部分接口校验 Referer / 签名（Authorization），需要一并复现

## 三、实战：解析 Authorization 请求头

以某租房小程序为例，接口请求头需要 `Authorization`，格式为：

```text
timestamp=1728287289;oauth2=xxx;signature=xxx;secret=xxx
```

### 1. 定位

在 DevTools 里搜索关键字 `oauth2` / `signature`，定位到签名函数，逻辑为多重 MD5 拼接。

### 2. 扣出签名函数

```javascript
// 引用 crypto-js：npm install crypto-js
var CryptoJS = require('crypto-js');

function MD5Test(text) {
    return CryptoJS.MD5(text).toString();
}

function generate(url, method) {
    var _timestamp = Math.round(new Date().getTime() / 1000).toString();
    var _oauth = MD5Test(_timestamp);                       // oauth = md5(时间戳)
    var _url = url;
    var _method = method;
    var _source = 'request_url='.concat(_url, '&content=', _timestamp,
        '&request_method=', _method, '&timestamp=', _timestamp, '&secret=', _oauth);
    var _signature = MD5Test(_source);                      // signature = md5(拼接串)
    return 'timestamp='.concat(_timestamp, ';oauth2=', _oauth,
        ';signature=', _signature, ';secret=', _oauth);
}
```

### 3. Python 接入

```python
import requests
import execjs

js = execjs.compile(open('1111.js', encoding='utf-8').read())
authorization = js.call('generate', 'client/search/house', 'get')

headers = {
    'Authorization': authorization,
    # 伪装成微信小程序环境
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... MicroMessenger/7.0.20.1781'
                  '(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF'
                  ' WindowsWechat(0x63090a13) XWEB/8555',
    'xweb_xhr': '1',
}
url = 'https://66miniapp-api.66zhizu.com/client/search/house'
params = {'city': '上海', 'sequence': '...'}
print(requests.get(url, headers=headers, params=params).text)
```

## 四、Webpack 打包的小程序

很多小程序用 Webpack/类 Webpack 打包，模块分散。批量收集模块的技巧（详见 [Webpack 一章](/tech-stack/crawler/reverse/webpack-ast)）：

1. XHR 断点定位到 `n(模块号)` 调用，进入加载器；
2. 清空缓存对象（`r = {}`）让模块能重复进入；
3. 在模块注册处下一个**条件断点**（条件写 `0`，不暂停只执行），把模块收集到全局变量：

```javascript
aaa[n] = e[n], 0;
```

4. 收集完成后在控制台导出所有模块源码：

```javascript
result = '{';
for (let x of Object.keys(aaa)) { result += '"' + x + '":' + aaa[x] + ','; }
result += '}';
copy(result);
```

5. 本地拼回「加载器 + 模块集合」骨架，暴露加载器调用入口。

::: warning
复制下来的代码要把 `\n` 清理掉，且注意格式问题（缺逗号、被截断的函数等），逐一排除。
:::

## 五、对抗：打开 DevTools 就关闭页面

部分小程序/网页检测到调试面板打开会自动关闭页面（如某土地平台）。应对：

1. **知道哪些操作会关页面**：`window.close()`、`window.open('','_self')`、`location.href` 跳转等
2. **定位检测代码**：控制台被清空多半是 `console.clear()`，追踪该方法的调用位置；也可以用「脚本（Snippets）」提前下断点拦住
3. **替换文件置空**：用 Overrides 把检测代码所在的 JS 文件替换为空/注释掉相关逻辑

## 六、其他注意事项

- **接口复现**：小程序接口常带时间戳 + 签名，注意时间单位（秒/毫秒）与拼接顺序
- **登录态**：需要登录的接口可用抓包工具（Charles / Reqable）从小程序里导出 Cookie / token，Python 直接携带
- **分包与加密资源**：图片、音视频常在 CDN 且带防盗链签名，签名逻辑同样在小程序 JS 里
- **合规**：小程序数据同样受法律约束，控制频率、只采集公开数据

## 七、小结

小程序逆向 = 网页逆向 + 微信特有环境：

1. WeChatOpenDevTools 打开调试面板，抓包与断点手段全部通用
2. 请求头要伪装 `MicroMessenger` UA 与 `xweb_xhr`
3. Webpack 模块批量收集、Overrides 反调试等技巧与网页逆向完全一致
