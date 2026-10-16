---
title: 客户端 Web API
weight: 100
---

# 客户端 Web API

> 本节目标：分清 JavaScript 语言与浏览器 API，并使用 DOM、事件、Fetch 和存储完成简单页面交互。

## Web API 是什么

Web API 是浏览器向脚本提供的一组接口。ECMAScript 不定义页面元素、窗口或网络请求；浏览器通过 DOM、Fetch、Storage、Canvas、媒体等 API 提供这些能力。不同 API 有自己的权限、异步方式和兼容性要求。

## DOM 与事件

DOM 将 HTML 文档表示为可查询和修改的节点树。事件监听器响应点击、输入等交互：

```html
<button id="count-button" type="button">点击</button>
<p id="output">已点击 0 次</p>
<script type="module" src="./app.js"></script>
```

```js
const button = document.querySelector("#count-button");
const output = document.querySelector("#output");
let count = 0;

button.addEventListener("click", () => {
  count += 1;
  output.textContent = `已点击 ${count} 次`;
});
```

处理用户输入时，优先用 `textContent` 写入纯文本；不要把不可信文本赋给 `innerHTML`，否则可能产生跨站脚本风险。事件可以冒泡，复杂组件可利用事件委托。

## 网络请求

`fetch()` 发起请求并返回 Promise。检查 `response.ok`，再解析响应体。跨域请求还受同源策略和服务器 CORS 响应头约束。

```js
const response = await fetch("/api/topics");
if (!response.ok) throw new Error(`HTTP ${response.status}`);
const topics = await response.json();
```

## 客户端存储

`localStorage` 跨页面会话保留字符串；`sessionStorage` 通常只保留当前标签页会话。存储容量有限，访问可能因浏览器策略失败。不要在 Web Storage 中保存密码、会话令牌等敏感数据。复杂或大量数据可了解 IndexedDB。

```js
localStorage.setItem("theme", "dark");
const theme = localStorage.getItem("theme") ?? "light";
```

存对象时需 `JSON.stringify()`，读取后用 `JSON.parse()`；解析外部数据要做好异常处理。

## 其他客户端能力

Canvas 和 WebGL 用于绘图，Audio/Video API 处理媒体，Geolocation 需要用户授权，Web Worker 用于独立线程计算。API 可能受安全上下文（HTTPS）、权限和浏览器支持限制。先查看 [MDN Web API 参考](https://developer.mozilla.org/zh-CN/docs/Web/API)及兼容性信息。

## 小结与练习

- DOM、Fetch 和存储都是浏览器提供的 Web API，不是 ECMAScript 核心语言。
- 使用事件监听器响应交互；写用户文本时优先用 `textContent`。
- 网络状态、权限、跨域和安全上下文都可能影响 API 调用。

练习：构建一个页面按钮，切换明暗主题并把选择保存在 `localStorage`；页面初始化时恢复选择。
