---
title: 补环境
weight: 8
---

# 补环境

扣代码（把加密函数复制到 Node 本地执行）时几乎必然遇到：

```text
if (navigator['userAgent']) {
    ^

ReferenceError: navigator is not defined
```

**补环境**就是在 Node 里伪造出与浏览器一致的对象与行为，让网站的加密代码「以为自己运行在真浏览器中」，从而输出正确的加密结果。它是扣代码路线的核心技能，也是瑞数、抖音 `a_bogus` 等高强度对抗的必经之路。

## 一、环境检测是什么

浏览器与 Node 的运行环境差异，被网站用作「反 Node 运行」的检测点。常见检测：

```javascript
// 1. 对象存在性检测
if (navigator['userAgent']) { ... }        // Node 下 navigator 未定义

// 2. 属性长度检测（判断是不是空壳对象）
location = {};
location.href = '123123';
if (location['href'].length > 3) { ... }

// 3. 浏览器与 Node 的 API 差异
// Node 中 exports 是模块导出对象，浏览器中是 undefined
sss = 'undefined' != typeof exports ? exports : void 0;

// 4. global 检测
glb = 'undefined' == typeof window ? global : window;
```

调试技巧：很多加密代码用 `try-catch` 把异常吞掉，导致你拿到「错误的结果」却看不到报错。可以**暂时删掉 catch**或打印 `e`，把真实错误暴露出来逐个解决。

## 二、从「补空」到「补真」

### 1. 第一层：补空对象

最粗暴的补法——缺什么补什么：

```javascript
navigator = {};
navigator.userAgent = '11111';

function ps() {
    return navigator['userAgent'] ? 'hello world' : '失败';
}
```

适合简单检测；遇到深度检测（原型链、属性描述符）就会露馅。

### 2. 第二层：按原型链补真

真实浏览器中 `document.createElement` 是挂在原型链上的方法（`document → HTMLDocument.prototype → Document.prototype`），属性描述符有讲究。用 `Object.getOwnPropertyDescriptor` 检测：

```javascript
// 浏览器里执行：属性在原型上，实例上是 undefined
Object.getOwnPropertyDescriptor(navigator, 'userAgent');  // undefined（真浏览器）
```

两种补法：

```javascript
// 方式一：补隐式原型
navigator = {};
navigator.__proto__.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...';

// 方式二：构造函数 + defineProperty 补显式原型（更接近真实）
Document = function Document() {};
Object.defineProperty(Document.prototype, 'createElement', {
    configurable: true,
    enumerable: true,
    writable: true,
    value: function createElement() {},
});
HTMLDocument = function HTMLDocument() {};
// 把 HTMLDocument 的原型挂到 Document 上，形成真实的两级原型链
Object.setPrototypeOf(HTMLDocument.prototype, Document.prototype);
document = new HTMLDocument();

console.log(Object.getOwnPropertyDescriptor(document.__proto__.__proto__, 'createElement'));
// {writable: true, enumerable: true, configurable: true, value: f}
```

### 3. toString 检测

真实浏览器中：

```javascript
document.createElement.toString()
// 'function createElement() { [native code] }'   ← 原生函数
```

而 Node 里自定义函数会输出函数源码。网站常借此检测，需要重写：

```javascript
document.createElement.toString = function () {
    return 'function createElement() { [native code] }';
};
```

### 4. 环境从哪来

要「补得像」，理论上需要把浏览器里这些 API 的真实源码抄下来：

- 控制台用 `dir(document)`、`dir(navigator)` 逐层展开查看
- 也可到 Chromium 源码仓库（github.com/chromium/chromium）查实现

但硬扣浏览器源码太耗时。**实践建议直接用现成的补环境框架**（社区已有成熟开源项目把整套浏览器环境封装好），或用下面 jsdom / Selenium 的方式。

## 三、Proxy「吐环境」

手工逐个报错地补效率极低。**Proxy 代理器**可以一次性拦截全局对象的全部读写，把加密代码访问过的每个属性都打印出来——这就是「自吐环境」：跑一遍代码，环境检测点全部自己吐出来，再按清单统一补齐。

### 1. Proxy 基础

Proxy 由 `target`（目标对象）与 `handler`（拦截行为）组成，常用两个拦截器：

```javascript
var target = { name: 'JACK', age: 18 };

var p = new Proxy(target, {
    get: function (target, propertyKey, receiver) {
        // 1.原对象 2.访问的属性 3.代理对象
        console.log('get:', propertyKey);
        return Reflect.get(target, propertyKey, receiver);   // 还原默认行为
    },
    set: function (target, propertyKey, value, receiver) {
        console.log('set:', propertyKey, '=', value);
        return Reflect.set(target, propertyKey, value, receiver);
    },
});
p.age;          // 触发 get
p.user = 'aa';  // 触发 set
```

`Reflect.get/set` 负责在拦截后**还原对象本来的读写逻辑**，否则代码会被打乱。

### 2. 递归代理封装

对象套对象（`window.document.title`）需要递归挂代理：

```javascript
function XlProxy(obj, name) {
    return new Proxy(obj, {
        get(target, p, receiver) {
            let temp = Reflect.get(target, p, receiver);
            console.log(`对象${name} --> get 属性 --> ${p} 值是 --> ${temp}`);
            if (typeof temp === 'object' && temp !== null) {
                temp = XlProxy(temp, `${name}-->${p}`);   // 嵌套对象继续挂代理
            }
            return temp;
        },
    });
}
```

### 3. 批量吐环境模板（直接可抄）

```javascript
function get_enviroment(proxy_array) {
    for (var i = 0; i < proxy_array.length; i++) {
        handler = `{
            get: function (target, property, receiver) {
                console.log('get  对象: ${proxy_array[i]}  属性:', property,
                            '值类型:', typeof target[property]);
                return target[property];
            },
            set: function (target, property, value, receiver) {
                console.log('set  对象: ${proxy_array[i]}  属性:', property, '值:', value);
                return Reflect.set(...arguments);
            }
        }`;
        eval(`try { ${proxy_array[i]} = new Proxy(${proxy_array[i]}, ${handler}) }
               catch (e) {
                   ${proxy_array[i]} = {};
                   ${proxy_array[i]} = new Proxy(${proxy_array[i]}, ${handler});
               }`);
    }
}

proxy_array = ['window', 'document', 'location', 'navigator', 'history', 'screen'];
get_enviroment(proxy_array);
```

### 4. 进阶：undefined 自动断点

配合 `node --inspect-brk` 的 Chrome 联调（见下文），在 get 到 `undefined` 时自动断下，一步定位到缺失的环境：

```javascript
get: function (target, property, receiver) {
    if (typeof target[property] === 'undefined') { debugger; }  // 缺失环境直接断
    return target[property];
}
```

## 四、vm2 沙箱框架

### 1. 为什么需要沙箱

Node 的 `vm` 模块提供隔离执行环境，但隔离不完善；`vm2` 在其上优化，提供更干净的沙箱——**在沙箱里打造一个尽量真实的浏览器环境**，让网站检测更难过、全局变量互不污染（类似 Python 虚拟环境的隔离思想）。

```bash
npm install vm2
```

```javascript
const { VM, VMScript } = require('vm2');

const script = new VMScript('let a = 2; a;');
let vm = new VM();
console.log(vm.run(script));
```

### 2. 补环境框架的组织

成熟的补环境项目通常分三部分：

```text
env/main.js       —— 需要加载的浏览器环境（window/document/navigator 等）
JsCode/main.js    —— 扣下来的网站加密代码
main.js           —— vm2 主文件：拼接环境 + 业务代码，放入沙箱执行
```

```javascript
// main.js
const { VM, VMScript } = require('vm2');
const vm = new VM();
const fs = require('fs');
const { read } = require('./env/main');          // 环境代码
const { readJsCode } = require('./JsCode/main'); // 业务代码

let jscode = '';
jscode += read();
jscode += readJsCode();

const script = new VMScript(jscode, { filename: '/myvmscript.js' });
console.log(vm.run(script));
```

配合 Express 暴露成 HTTP 服务，Python 即可 HTTP 调用取签名。

## 五、Node 联调 Chrome DevTools

补环境最难的是「不知道代码在哪访问了什么」。Node 可以直接用 Chrome DevTools 调试：

```bash
node --inspect-brk demo.js
# 浏览器打开 chrome://inspect/#devices
# 检测到进程后点击 inspect，即可像调试网页一样给 Node 代码下断点
```

组合拳：**吐环境脚本（打印访问记录）+ undefined 自动断点 + DevTools 单步**，可以高效逼出所有缺失的环境点。

## 六、jsdom 补环境

[jsdom](https://github.com/jsdom/jsdom) 是纯 JS 实现的 WHATWG DOM / HTML 标准，能在 Node 里模拟一个真实度较高的浏览器子集——比自己手写 document 对象完整得多：

```bash
npm install jsdom
```

```javascript
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

// 基本用法
const dom = new JSDOM(`<!DOCTYPE html><p>Hello world</p>`);
console.log(dom.window.document.querySelector('p').textContent);

// 指定 URL / referrer 等参数，让 location、document.referrer 更真实
const dom2 = new JSDOM('', {
    url: 'https://q.10jqka.com.cn/',
    referrer: 'https://q.10jqka.com.cn/',
    contentType: 'text/html',
    includeNodeLocations: true,
    storageQuota: 10000000,
});
```

局限：jsdom 毕竟不是真浏览器，canvas、部分 BOM 属性仍有特征差异，高强度检测需再手工补齐。

## 七、Selenium 补环境

另一种思路：**浏览器本身就是真实环境**。把扣下来的加密代码塞进一个本地 HTML 文件，用 Selenium 打开并执行，根本不需要补环境：

```python
import os
from selenium import webdriver

PRO_DIR = os.path.dirname(os.path.abspath(__file__))

def driver_sig(html_file):
    option = webdriver.ChromeOptions()
    option.add_argument('--disable-blink-features=AutomationControlled')
    option.add_argument('headless')
    driver = webdriver.Chrome(options=option)
    driver.get(PRO_DIR + '/' + html_file)    # 打开放了加密代码的本地页面
    return driver

driv = driver_sig('index.html')
print(driv.execute_script('return window.aaa()'))   # 调用页面里的加密函数
```

再配合 Flask 包装成接口，实现「Selenium 版签名服务」：

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/s', methods=['get', 'post'])
def hello():
    context = {'v': driv.execute_script('return window.aaa()')}
    return jsonify(context=context)

app.run()
```

优点是环境绝对真实；缺点是性能差，适合低频签名。

## 八、了解 JSVMP

**JSVMP**（JS 虚拟机保护）把源代码编译成**自定义字节码**，浏览器里跑的是一个自定义解释器一边解释一边执行——看到大段 `case 1: ... case 2: ...` 的 switch 分发结构，就是它了。

核心思想（简化示意）：

```javascript
// 源代码 var a='丽丽'; var b='菲菲'; var d=a+b;
// 先转成指令数组：3=声明 1=赋值 2=加法
_stack = [
    [3, 'var', 'a'],
    [1, 'a', '丽丽'],
    [3, 'var', 'b'],
    [1, 'b', '菲菲'],
    [2, 'a', 'b'],
    [1, 'd', '?'],       // ? 表示暂存寄存器
];

// 自写解释器逐条执行
!function (_stack) {
    var register, variable = {};
    for (let i = 0; i < _stack.length; i++) {
        const [instruct, left, right] = _stack[i];
        if (instruct === 3) variable[right] = '';            // 声明
        if (instruct === 1) variable[left] = right === '?' ? register : right;  // 赋值
        if (instruct === 2) register = variable[left] + variable[right];        // 运算
    }
    console.log(variable);
}(_stack);
```

真实 JSVMP（如抖音 `a_bogus`、瑞数 VM 代码）会复杂得多：字节码加密、操作数百个指令集、配合环境检测。应对策略：

1. **补环境**：不管字节码多复杂，它总要访问环境对象——把环境补真即可
2. **插桩扣逻辑**：在解释器分发处插日志，追踪执行流
3. **RPC**：直接调浏览器里的现成函数，绕过一切分析

## 九、实战：抖音 a_bogus（补环境 + jsvmp）

流程概览：

1. XHR 断点定位 `a_bogus` 生成，跟栈到自执行的 jsvmp 函数；
2. 用吐环境脚本跑一遍，按日志补齐 `window.requestAnimationFrame`、`document.createElement`、`XMLHttpRequest`、`navigator.userAgent` 等；
3. 解释器执行完把入口函数挂到 `window._U`，通过 `get_a_bogus` 带参调用：

```javascript
function get_a_bogus(arg) {
    const r = window._U._v;
    return window._U._u(r[0], arg, r[1], r[2], null);
}

function get_ab(argStr) {
    const arg = [0, 1, 0, argStr, '', 'Mozilla/5.0 ... Chrome/124.0.0.0 Safari/537.36'];
    return get_a_bogus(arg);
}
```

4. Python 用 execjs 调用，把结果拼到请求 URL 上完成采集。

## 十、小结

| 手段 | 适用 |
| ---- | ---- |
| 补空对象 | 简单存在性检测 |
| 原型链 + defineProperty + toString | 属性描述符/原生函数检测 |
| Proxy 吐环境 | 快速定位所有环境检测点（必学） |
| vm2 沙箱 | 组织环境 + 业务代码，隔离执行 |
| jsdom / 现成补环境框架 | 减少手补工作量 |
| Selenium / RPC | 不想补，借真实浏览器环境 |

补环境的口诀：**报错补全 → Proxy 吐环境 → 原型链补真 → vm2 组装 → 联调验证**。
