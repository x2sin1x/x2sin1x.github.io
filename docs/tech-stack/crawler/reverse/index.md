---
title: Web 逆向
weight: 2
---

# Web 逆向

当网站的数据接口带有 `sign`、`token`、加密的 Cookie 或加密的响应体时，普通的「发请求 + 解析」走不通了——需要搞清楚前端 JS 是如何生成这些参数的，并用 Python（或 Node）复现出来。这就是 **Web 逆向**（JS 逆向）。

::: danger 声明
本部分内容仅供学习交流，请遵守相关法律法规与目标网站的服务条款，严禁用于商业用途与非法用途。
:::

## 一、什么是 JS 逆向

- **JS 加密**：网站在浏览器端用各种算法对请求参数、Cookie 或响应数据进行加密保护
- **JS 逆向**：分析网页加密（解密）代码的过程，并用 Python 模拟出来

要特别强调：**逆向不是把密文还原成明文**。加密算法无法从密文反推明文；逆向要做的是复现加密过程——在请求前算出正确的加密参数，或在响应后调用网站的解密逻辑。

## 二、加密参数的常见位置

| 位置 | 特征 | 示例 |
| ---- | ---- | ---- |
| 请求头加密 | 请求头里出现 `sign`、`nonce` 等自定义字段 | 企查查 |
| 请求参数加密 | URL 或表单里出现 `sign`、`w`、`analysis` 等参数 | 排行榜接口 |
| Cookie 验证 | 首次请求返回 JS 代码生成 Cookie（`acw_sc__v2`、`__jsl_clearance_s`、瑞数） | 政务、资讯站 |
| 响应数据加密 | 接口返回一坨 Base64 / 密文，前端解密后渲染 | 行情、票房数据 |
| 全加密 | URL、参数、响应全部加密（如 URL 是一段 Base64） | 少数站点 |

## 三、工具准备

1. **Node.js**（建议 16+）：本地执行 / 调试扣下来的 JS 代码
2. **PyCharm 专业版**：安装 Node 插件，可断点调试 JS
3. **Chrome / Edge 浏览器**：开发者工具是主战场
4. **Python 库**：`PyExecJS`（调用 JS）、`crypto-js` / `jsencrypt` / `sm-crypto`（Node 侧算法库）
5. 可选：抓包工具 Charles、微信开发者工具破解版（小程序）、Java 环境（Sekiro RPC）

## 四、逆向的通用流程

```text
1. 抓包：找到数据接口，确认哪些参数是加密/变化的
2. 定位：搜索关键字 / XHR 断点 / DOM 断点 / Hook，找到加密函数位置
3. 分析：读懂加密逻辑（用了什么算法、密钥从哪来、有无混淆）
4. 复现：
   a. 标准算法 → 用 Python / Node 库直接实现
   b. 自定义逻辑 → 扣代码到本地，用 Node 执行（缺什么补什么）
   c. 太复杂 → 补环境 / RPC 调用浏览器 / Selenium 直接拿结果
5. 验证：加密结果与浏览器一致后，接入爬虫请求
```

## 五、学习路线

### 核心方法

| 章节 | 内容 |
| ---- | ---- |
| [JS 基础与浏览器调试](/tech-stack/crawler/reverse/js-debug) | JS 语法速览、断点定位、无限 debugger 对抗 |
| [Hook 与代码还原](/tech-stack/crawler/reverse/hook) | Hook 定位加密点、扣代码、Python/Node 互调 |
| [加密算法还原](/tech-stack/crawler/reverse/crypto) | MD5/SHA/HMAC、AES/DES、RSA、国密 SM 系列 |
| [Webpack、混淆与 AST](/tech-stack/crawler/reverse/webpack-ast) | Webpack 打包扣代码、OB 混淆、AST 解混淆 |

### 进阶专题

| 章节 | 内容 |
| ---- | ---- |
| [WASM 逆向](/tech-stack/crawler/reverse/wasm) | WebAssembly 加载原理、Node/pywasm 调用、wasm + Webpack 组合 |
| [RPC 逆向](/tech-stack/crawler/reverse/rpc) | WebSocket 双向通信、Sekiro 暴露浏览器加密函数 |
| [字体反爬](/tech-stack/crawler/reverse/font) | @font-face 原理、fontTools 解析、静态/动态字体映射 |
| [补环境](/tech-stack/crawler/reverse/env) | 环境检测、Proxy 吐环境、原型链补真、vm2、JSVMP |
| [Cookie 反爬](/tech-stack/crawler/reverse/cookie) | 阿里系、加速乐、瑞数、Akamai、TLS 指纹与风控 |
| [验证码](/tech-stack/crawler/reverse/captcha) | 滑块原理、ddddocr、轨迹生成、易盾协议分析 |
| [小程序逆向](/tech-stack/crawler/reverse/miniapp) | WeChatOpenDevTools、Authorization 签名、反调试对抗 |

建议每学完一个专题，配套完成一个实战网站练习（定位 → 分析 → 复现 → 采集跑通），逆向能力只能在实战中长出来。
