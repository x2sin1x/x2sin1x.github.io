---
title: "Harness Engineering"
date: 2026-09-22T17:00:00+08:00
weight: 112
---

# Harness Engineering

> Harness（挽具）是把力量接出来的那套装具。Agent Harness 是包裹 LLM 的整个运行外壳——同一个模型，装在不同的 Harness 里，表现天差地别。

## 什么是 Harness

Harness 是模型之外、任务之内的一切工程。拿主流 Coding Agent 剖开看，通常包括：

| 组件 | 职责 | 基础篇对应 |
| ---- | ---- | ---- |
| 系统提示 | 角色、行为规范、领域知识 | Prompt Engineering |
| 工具面 | 内置工具集、MCP 接入、Skills | 工具 |
| 权限系统 | 哪些操作自动放行、哪些要确认 | 安全与权限 |
| 上下文管理 | 压缩、外置、缓存友好的组织 | Context Engineering |
| 事件循环 | 调用模型、执行工具、写回结果 | Agent 核心循环 |
| 持久层 | 会话恢复、任务清单、记忆文件 | 用户记忆与知识库 |

一个有力的行业观察：**模型能力的差距正在被 Harness 的差距放大甚至反超**。同一个模型，在精心调校的 Harness 里（比如 Claude Code）和裸 API 循环里的生产率差距，常常大于换一个更强模型。Claude Code、Codex、Pi、DeepSeek Harness 之间的竞争，本质上就是 Harness 工程的竞争。

## Harness Engineering 的核心决策

### 1. 工具面：宽而浅，还是窄而深？

内置多少工具、开放多少扩展？Claude Code 的选择是“窄内核 + 强扩展”：核心只给读写文件、执行命令、搜索等十来个原语，其余能力通过 MCP 和 Skills 加载。这个设计的哲学是：**原语越少越稳，能力按需注入**。

### 2. 权限模型：默认开放，还是默认收敛？

每个工具调用都要回答“允许吗”。三级策略由松到紧：全自动（快但危险）、白名单 + 确认（主流）、全确认（安全但烦人）。Harness 通常做成可配置的分级模式（如 Claude Code 的 permission modes），并把“哪些命令永远不用问”的记忆也纳入 Harness。

### 3. 上下文策略：何时压、压什么？

压缩阈值设在多少、系统提示如何为缓存保持稳定、哪些文件常驻、哪些按需读——这些参数直接决定长任务的后半程表现。Harness 的上下文策略往往比模型本身更长窗口更重要。

### 4. 人机接口：Agent 如何与用户对话？

进度如何呈现、何时停下来问、计划是否需要先批准（plan mode）、中断后如何恢复。好的 Harness 让人始终知情而不被打扰，坏的 Harness 让人要么失控要么疲于确认。

## 为什么不直接用框架

Anthropic 官方的建议值得抄录：框架降低了入门门槛，但额外的抽象层会遮蔽底层的 prompt 和响应，让调试变难；**很多模式用 LLM API 直接实现只需几行代码**。如果你使用框架（Claude Agent SDK、LangGraph 等），务必理解它底下在做什么——对底层的错误假设是客户事故的常见来源。

这也是本教程的结构逻辑：先弄懂 Harness 各组件的原理，框架只是把这些组件预先装配好的产物。

## 参考

- [Building Effective Agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Claude Agent SDK（官方 Harness 化的产物）](https://docs.anthropic.com/en/api/agent-sdk/overview)
- [Claude Code Docs：权限与沙箱](https://code.claude.com/docs/en/iam)
