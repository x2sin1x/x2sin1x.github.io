---
title: Web 爬虫与逆向
weight: 60
---

# Web 爬虫与逆向

从零开始的 Python 爬虫教程，分为**基础爬虫**与 **Web 逆向**两个部分：

- **基础爬虫**：HTTP 原理、requests 请求、数据提取、数据存储、并发加速、浏览器自动化、抓包与代理、Scrapy 框架与分布式。
- **Web 逆向**：JS 基础与浏览器调试、Hook 与扣代码、加密算法还原、Webpack 混淆与 AST、以及补环境、Cookie 反爬、验证码等进阶专题。

## 目录

### 第一部分 · 基础爬虫

- [HTTP 协议与爬虫基础](/tech-stack/crawler/basics/http) —— 爬虫概念、HTTP 请求响应、开发者工具、Socket
- [请求发送 requests](/tech-stack/crawler/basics/request) —— GET/POST、请求头、Cookie、代理、超时重试
- [数据提取](/tech-stack/crawler/basics/extract) —— JSON、正则、XPath、BeautifulSoup
- [数据存储与去重](/tech-stack/crawler/basics/storage) —— 文本、CSV、MySQL、MongoDB、Redis 去重
- [高性能爬虫](/tech-stack/crawler/basics/concurrent) —— 多线程、线程池、多进程、异步协程
- [Selenium 浏览器自动化](/tech-stack/crawler/basics/browser) —— 节点定位、交互、等待、绕过检测
- [抓包与代理池](/tech-stack/crawler/basics/capture-proxy) —— Charles 抓包、App 抓包、代理池搭建
- [Scrapy 框架](/tech-stack/crawler/basics/scrapy) —— 架构流程、中间件、Pipeline、scrapy-redis、feapder

### 第二部分 · Web 逆向

- [JS 基础与浏览器调试](/tech-stack/crawler/reverse/js-debug) —— JS 语法速览、断点定位、无限 debugger
- [Hook 与代码还原](/tech-stack/crawler/reverse/hook) —— Hook 定位、扣代码、pyexecjs / Express 调用
- [加密算法还原](/tech-stack/crawler/reverse/crypto) —— MD5/SHA/HMAC、AES/DES、RSA、国密 SM 系列
- [Webpack、混淆与 AST](/tech-stack/crawler/reverse/webpack-ast) —— Webpack 扣代码、OB 混淆、AST 解混淆
- [WASM 逆向](/tech-stack/crawler/reverse/wasm) —— WebAssembly 加载原理与 Node / pywasm 调用
- [RPC 逆向](/tech-stack/crawler/reverse/rpc) —— WebSocket 与 Sekiro 调用浏览器加密函数
- [字体反爬](/tech-stack/crawler/reverse/font) —— @font-face 原理与 fontTools 字形映射
- [补环境](/tech-stack/crawler/reverse/env) —— 环境检测、Proxy 吐环境、vm2、JSVMP
- [Cookie 反爬](/tech-stack/crawler/reverse/cookie) —— 阿里系、加速乐、瑞数、Akamai、TLS 指纹
- [验证码](/tech-stack/crawler/reverse/captcha) —— 滑块识别、轨迹生成、易盾协议分析
- [小程序逆向](/tech-stack/crawler/reverse/miniapp) —— WeChatOpenDevTools 与签名还原

## 术语速查

初学时经常被术语绕晕，这里集中解释教程中反复出现的概念：

| 术语 | 通俗解释 |
| ---- | ------ |
| 抓包 | 把浏览器与服务器之间的请求/响应记录下来查看，找数据位置的第一步 |
| 接口（API） | 返回 JSON 等结构化数据的网址，爬虫最爱的目标 |
| Ajax / XHR | 页面加载后由 JS 在后台发出的请求（不刷新页面），动态数据都在这类请求里 |
| 请求头（Headers） | 请求自带的「名片」：UA、Referer、Cookie 等，反爬检测的主战场 |
| UA（User-Agent） | 声明「我是哪个浏览器」的字符串，不带它服务器一眼认出你不是浏览器 |
| Cookie / Session | 浏览器存的身份凭证 / 服务器端的会话记录，带 Cookie 才算「登录着的人」 |
| Token | 服务端下发的临时通行证，常出现在请求头或参数里 |
| 代理 / 高匿 | 用别人的 IP 访问目标站；高匿指服务器完全看不出你在用代理 |
| 并发 / 异步 | 同时发多个请求而不是一个个排队等；异步是单线程内高效等待的实现方式 |
| 反反爬 | 破解网站反爬手段的统称：随机 UA、Cookie 管理、代理、限速… |
| 逆向 / 扣代码 | 分析前端加密逻辑并在本地复现；扣代码指把加密函数复制到 Node 本地执行 |
| 补环境 | 在 Node 里伪造浏览器对象（window/navigator…），让网站 JS「以为」在浏览器里运行 |
| 加密 / 哈希 | 加密可逆（有密钥能解回），哈希（摘要）单向不可逆，只用于校验与签名 |
| 密钥 / IV / Padding | 对称加密三要素：钥匙 / 初始化向量 / 补齐明文长度的填充规则 |
| 混淆 / AST | 把代码改得难读（变量乱名、字符串加密）；AST 是把代码变成可程序化修改的语法树 |
| 指纹 | 数据指纹：内容哈希，用于去重；浏览器/TLS 指纹：客户端特征，用于风控 |
| Webpack / WASM | 前端模块打包器（加密逻辑拆散在模块里）/ 浏览器字节码格式（加密核心藏在 .wasm） |
| Hook | 拦截并替换原函数（如 JSON.stringify、cookie 写入），在加密点断下定位 |
| 打码平台 | 花钱让 AI/人工帮你识别验证码的第三方服务 |

## 声明

本教程仅供学习与技术交流使用，请遵守目标网站的 `robots.txt` 与相关法律法规：控制请求频率、不采集敏感个人信息、不将爬取数据用于商业或非法用途。逆向相关内容仅用于理解前端加密原理。
