---
title: "MCP"
date: 2026-09-22T17:00:00+08:00
weight: 108
---

# MCP：AI 应用的 USB-C

> MCP（Model Context Protocol）由 Anthropic 于 2024 年 11 月开源，现已成为行业事实标准。官方定义：连接 AI 应用与外部数据源和工具的开放协议。

## 解决什么问题

没有协议的世界是这样的：M 个 AI 应用 × N 个外部系统（GitHub、Slack、数据库、文件系统……），每个应用都要为每个系统写一遍定制集成——**M×N 种组合，组合爆炸**。

MCP 把它变成 **M+N**：应用只需实现一次 MCP 客户端，系统只需实现一次 MCP 服务器，中间用统一协议对话。这也是它最常用的比喻：&#8203;**AI 应用的 USB-C 接口**&#8203;——设备（数据源）各异，接口统一。

## 架构：Host、Client、Server

MCP 采用客户端-服务器架构，三个角色各司其职：

```text
┌─────────────────────────────┐
│  Host（宿主应用，如 Claude Code、某个 IDE）│
│  ┌──────────┐  ┌──────────┐ │
│  │MCP Client│  │MCP Client│ │      1:1 连接
│  └────┬─────┘  └────┬─────┘ │
└───────┼─────────────┼───────┘
        ▼             ▼
  ┌──────────┐  ┌──────────┐
  │MCP Server│  │MCP Server│      连接 GitHub、Postgres、
  │ (GitHub) │  │(Postgres)│      文件系统……
  └──────────┘  └──────────┘
```

- **Host**：用户面对的 AI 应用，管理 MCP 客户端与安全策略。
- **Client**：Host 内部与单个 Server 保持 1:1 连接的组件。
- **Server**：暴露具体能力的轻量服务，通过 stdio 或 HTTP（Streamable HTTP）与 Client 通信。

## Server 提供什么

一个 MCP Server 可以暴露三类原语：

| 原语 | 含义 | 控制方 |
| ---- | ---- | ---- |
| **Tools** | 模型可主动调用的动作（查库、发消息、建 issue） | 模型决策 |
| **Resources** | 可读取的数据（文件、记录、schema），由应用决定何时注入 | 应用驱动 |
| **Prompts** | 预置的提示词模板，由用户显式选择 | 用户驱动 |

其中 Tools 是 Agent 场景的主角：协议会把 Server 声明的工具转成宿主模型的 function calling 格式——**MCP 在协议层，function calling 在模型 API 层，前者是后者的“分发网络”**。

## 一个实际的接入样例

以 Claude Code 为例，接入一个 GitHub Server 只需在配置中声明：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "..." }
    }
  }
}
```

启动后 Host 发现 Server 声明的全部工具并注入模型，Agent 即可“原生”操作 GitHub——应用方没有写过一行 GitHub 集成代码。

## 冷静看待 MCP

MCP 不是万能药，选型时注意：

- **它解决接入标准化，不解决工具质量**。Server 暴露的工具设计得差，模型照样用不好——工具设计原则一节依然适用。
- **信任边界在 Host**。第三方 Server 拥有你授予的权限，恶意或被投毒的 Server 是真实的安全面（工具描述本身可能携带提示注入）。权限最小化与人工确认机制不可省略——详见进阶篇“安全与权限”一章。
- **简单场景未必需要它**。内部系统自己写几个工具函数更直接；MCP 的价值随“要接的系统数量”增长。

## 参考

- [Model Context Protocol 规范仓库](https://github.com/modelcontextprotocol/modelcontextprotocol)
- [MCP 官方文档](https://modelcontextprotocol.io)
- [MCP Servers 参考实现](https://github.com/modelcontextprotocol/servers)
