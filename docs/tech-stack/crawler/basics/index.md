---
title: 基础爬虫
weight: 1
---

# 基础爬虫

本部分从 HTTP 原理讲起，覆盖一条完整爬虫链路的每个环节：

1. [HTTP 协议与爬虫基础](/tech-stack/crawler/basics/http) —— 爬虫是什么、请求与响应、开发者工具
2. [请求发送 requests](/tech-stack/crawler/basics/request) —— 用代码模拟浏览器发请求
3. [数据提取](/tech-stack/crawler/basics/extract) —— 从响应中解析出想要的数据
4. [数据存储与去重](/tech-stack/crawler/basics/storage) —— 把数据落到文件或数据库
5. [高性能爬虫](/tech-stack/crawler/basics/concurrent) —— 多线程、多进程与异步协程
6. [Selenium 浏览器自动化](/tech-stack/crawler/basics/browser) —— 应对 JS 动态渲染页面
7. [抓包与代理池](/tech-stack/crawler/basics/capture-proxy) —— 分析 App 接口与突破 IP 封锁
8. [Scrapy 框架](/tech-stack/crawler/basics/scrapy) —— 工程化采集与分布式
9. [feapder 框架](/tech-stack/crawler/basics/feapder) —— 内置入库、去重、报警的全家桶式框架

学习建议：每章的实战案例请动手跑一遍，遇到新网站时按照「抓包分析 → 发送请求 → 提取数据 → 存储」的流程独立完成一次完整爬虫。
