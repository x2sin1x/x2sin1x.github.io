---
title: Hook 与代码还原
weight: 2
---

# Hook 与代码还原

## 一、Hook 技术

### 1. 原理

Hook（钩子）就是在目标函数执行前插入自己的逻辑：既可以在原函数基础上加工参数，也可以借机 `debugger` 断下。**修改原有 JS 代码就是 Hook**。

Hook 能成立的原因：

- 客户端拥有 JS 的最高解释权，服务器无法阻止注入
- JS 是弱类型语言，同一个变量/方法可以随时被重新赋值

与 DOM/XHR 断点相比，Hook 的优势是**直接在加密点断下**，省去逐帧跟栈。

### 2. Hook 的步骤

1. 寻找要 Hook 的点（加密数据经过的函数）
2. 编写 Hook 逻辑（保留原函数 → 重写 → 插入 debugger → 调用原函数）
3. 在控制台执行（要赶在加密发生之前，必要时刷新页面）

第 3 步展开说：Hook 是「拦截即将发生的函数调用」，所以必须**在加密代码执行之前**就位。执行入口有三种：控制台直接粘贴（刷新后失效）、Sources 代码段（Snippets，可重复执行）、Overrides 替换文件（随页面加载自动生效）。正确的操作顺序是：**先让 Hook 代码就位 → 刷新页面 → 再触发加密操作**，顺序反了加密早就完成，Hook 不会命中。

### 3. Hook JSON.parse / JSON.stringify

部分站点加密前会调用这两个方法：

```javascript
(function () {
    var _parse = JSON.parse;
    JSON.parse = function (ps) {
        console.log('Hook JSON.parse ——>', ps);
        debugger;                       // 断下后逐帧向上找加密点
        return _parse(ps);              // 不改变原有执行逻辑
    };
})();
```

### 4. Hook Cookie（Object.defineProperty）

`Object.defineProperty(obj, prop, descriptor)` 可以拦截对象属性的读写。Hook `document.cookie` 的 `set` 方法，即可在 Cookie 被写入时断下：

```javascript
(function () {
    cookieTemp = document.cookie;
    Object.defineProperty(document, 'cookie', {
        set: function (val) {
            if (val.indexOf('v') !== -1) {      // 匹配目标 Cookie 名
                debugger;
            }
            console.log('Hook 捕获到 cookie 设置 ->', val);
            cookieTemp = val;
        },
        get: function () {
            return cookieTemp;
        },
    });
})();
```

::: tip
Hook Cookie 前先在 Application 面板清空目标 Cookie，否则它早就生成好了，断不下来。
:::

### 5. Hook XHR 请求

重写 `XMLHttpRequest.prototype.open`，URL 含目标关键字就断下：

```javascript
(function () {
    var open = window.XMLHttpRequest.prototype.open;
    window.XMLHttpRequest.prototype.open = function (method, url, async) {
        if (url.indexOf('analysis') !== -1) {   // indexOf 返回 -1 表示不包含
            debugger;
        }
        return open.apply(this, arguments);
    };
})();
```

### 6. XMLHttpRequest 与 axios 拦截器

XHR 的核心 API：`open(method, url, async)` 初始化请求、`send(body)` 发送、`setRequestHeader(key, value)` 设置请求头（必须在 open 之后 send 之前）。

现代前端多用 axios，其拦截器是加密参数的高发区：

```javascript
// 请求拦截器：发包前加工参数/请求头
axios.interceptors.request.use(function (config) {
    config.headers['sign'] = 'lili';
    return config;
});

// 响应拦截器：拿到响应后先解密/格式化
axios.interceptors.response.use(function (response) {
    return response.data;
});
```

执行顺序：

```text
加载 html → 加载 js → 触发 ajax → 构造请求对象 → 请求拦截器 → 发送
→ 收到响应 → 响应拦截器 → 业务回调
```

::: warning
并非所有网站都用拦截器。加密代码若在异步过程中执行，栈里看不到——先在异步起点断点粗调，或直接查找响应/请求拦截器位置。
:::

## 二、Python 调用 JS

定位并扣出加密函数后，需要让 Python 用上它。三种方式：

### 1. PyExecJS（最常用）

```bash
pip install PyExecJS    # 需已安装 Node.js
```

```python
import execjs

node = execjs.get()                       # 运行环境：Node.js (V8)

with open('crypto.js', encoding='utf-8') as f:
    js_code = f.read()
ctx = node.compile(js_code)               # 编译加载

# 两种调用方式
data1 = ctx.eval('get_data({"aa": "123"})')       # eval：整段表达式为字符串
data2 = ctx.call('get_data', ['123'])             # call：函数名 + 参数列表
```

::: warning
execjs 每次调用都启动一个新 Node 进程，性能一般；只适合低频调用签名函数，高并发场景用 Express 起服务。
:::

### 2. Express 开放 HTTP 接口

```bash
npm install express -S
```

```javascript
// server.js
const express = require('express');
const app = express();
app.use(express.json());

function get_sign(data) {
    // ... 加密逻辑
    return data + '_signed';
}

app.post('/sign', function (req, res) {
    res.send(get_sign(req.body.data));    // 返回加密结果
});

app.listen(8080, () => console.log('running at http://127.0.0.1:8080'));
```

```python
import requests

res = requests.post('http://127.0.0.1:8080/sign', json={'data': 'hello'})
print(res.text)
```

### 3. subprocess 调用 Node 脚本

适合带异步逻辑的脚本（execjs 对 Promise 不友好）：

```javascript
// 2222.js
function getAsyncData(num) {
    return new Promise(resolve => {
        num >= 10 ? resolve(num) : resolve('number 小于10');
    });
}
module.exports.init = function (a, b) {
    getAsyncData(a + b).then(data => console.log(data));
};
module.exports.init(parseInt(process.argv[3]), parseInt(process.argv[4]));
```

```python
import subprocess

result = subprocess.run(['node', '2222.js', 'init', '7', '5'],
                        capture_output=True, text=True)
print(result.stdout.strip())
```

## 三、扣代码实战：七麦 analysis 参数

以七麦数据为例演示完整流程。

### 1. 定位

- 接口的 `analysis` 参数加密；直接搜索 `analysis` 搜不到（混淆/拼接）
- 使用上面的 **Hook XHR** 代码断下，逐帧跟栈
- 发现加密发生在**异步过程**（拦截器）中：在发异步的位置粗调后定位到加密函数

### 2. 扣代码

把加密函数及其依赖原样复制到本地 JS 文件，缺什么补什么：

```javascript
// 1111.js
function o(n) {
    t = '';
    ['66','72','6f','6d','43','68','61','72','43','6f','64','65'].forEach(function (n) {
        t += unescape('%u00' + n);
    });
    var t, e = t;
    return String[e](n);        // String.fromCharCode
}

function v(t) {
    t = encodeURIComponent(t).replace(/%([0-9A-F]{2})/g, function (n, t) {
        return o('0x' + t);
    });
    return btoa(t);             // Base64 编码
}

function h(n, t) {
    for (var e = (n = n.split('')).length, r = t.length, a = 'charCodeAt', i = 0; i < e; i++)
        n[i] = o(n[i][a](0) ^ t[(i + 10) % r][a](0));   // 逐字符异或
    return n.join('');
}

function get_analysis(a) {
    a = a.sort().join('');
    a = v(a);
    r = +new Date() - 4421027 - 1661224081041;
    a = (a += '@#' + '/indexV2/getIndexRank') + ('@#' + r) + ('@#' + 3);
    var d = 'xyz517cda96efgh';
    return v(h(a, d));
}
```

### 3. Python 接入

```python
import requests
import execjs

headers = {
    'origin': 'https://www.qimai.cn',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
}
url = 'https://api.qimai.cn/indexV2/getIndexRank'
params = {'setting': '0', 'genre': '6014'}

js = execjs.compile(open('1111.js', encoding='utf-8').read())
params['analysis'] = js.call('get_analysis', list(params.values()))

print(requests.get(url, headers=headers, params=params).json())
```

### 4. 扣代码的经验总结

| 情况 | 处理 |
| ---- | ---- |
| `navigator is not defined` 等报错 | 缺浏览器对象，先补空对象 `navigator = {}`，不够再补属性（见补环境章节） |
| 关键字搜不到 | 混淆或字符串拼接；换 Hook / XHR 断点 |
| 加密在异步/拦截器里 | 异步起点粗调 + 精调；或直接找 axios 拦截器 |
| 多个函数嵌套调用 `(0, r.default)(t)` | 逗号操作符，可直接写 `r.default(t)` 调用 |
| 扣完结果与浏览器不一致 | 检查密钥/盐值是否动态（从接口返回）、时间戳、参数顺序 |

## 四、小结

- Hook 三大件：`JSON.stringify`、`document.cookie`、`XMLHttpRequest.open`，都遵循「保留原函数 → 重写 → debugger → 还原调用」的模式
- 拦截器（axios）是异步加密的高发区，请求拦截器在响应拦截器上面
- 扣代码闭环：**定位 → 复制 → 补报错 → Python 调用**，低频用 execjs，高频起 Express 服务
