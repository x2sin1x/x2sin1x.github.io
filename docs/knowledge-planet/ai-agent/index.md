---
title: "AI Agent"
date: 2026-09-22T17:00:00+08:00
weight: 108
---

# AI Agent

> 一个面向开发者的 Agent 原理与实践教程 · 参考体系以 Anthropic《Building Effective Agents》与主流开源项目为骨架

大语言模型本身只会“续写文本”。要让它能查资料、写代码、订机票、持续完成一个复杂任务，就需要在模型外面套一层系统：给它记忆、给它工具、给它一个不断运转的循环。这个系统就是&#8203;**智能体（Agent）**&#8203;。

本教程用一个贯穿始终的比喻来组织内容：&#8203;**智能体 = 大脑 + 眼睛 + 手脚**&#8203;。大脑是 LLM，眼睛是感知与上下文，手脚是工具与执行。围绕这个比喻，我们依次讨论基础组件、工程方法、多智能体协作，最后落到评估与演进。

## 基础篇

- [智能体 = 大脑 + 眼睛 + 手脚](/knowledge-planet/ai-agent/overview/) —— Agent 的定义、核心循环与 ReAct，全篇的概念地图
- [LLM](/knowledge-planet/ai-agent/llm/) —— 作为“大脑”的语言模型：能做什么、不能做什么，模型特性如何塑造 Agent 行为
- [上下文](/knowledge-planet/ai-agent/context/) —— Prompt Engineering 与 Context Engineering：如何喂养大脑
- [用户记忆与知识库](/knowledge-planet/ai-agent/memory-and-knowledge/) —— 长期记忆与 RAG 两条线，让 Agent 记得住、查得到
- [工具](/knowledge-planet/ai-agent/tools/) —— MCP 与 Skills/CLI：让 Agent 真正“动手”

## 进阶篇

- [工作流与任务编排](/knowledge-planet/ai-agent/workflow-orchestration/) —— Planning 与 Goal、Harness Engineering、Loop Engineering
- [多智能体协同](/knowledge-planet/ai-agent/multi-agent/) —— Subagents、编排模式、A2A 通信、上下文隔离与共享
- [安全与权限](/knowledge-planet/ai-agent/security/) —— 威胁模型、权限最小化、沙箱与 human-in-the-loop
- [案例研究](/knowledge-planet/ai-agent/case-studies/) —— Coding Agent、Working Agent、Agent 开发、Agent 与软件工程
- [Agent 的评估](/knowledge-planet/ai-agent/evaluation/) —— 轨迹评估、基准与在线评估
- [Agent 的持续进化](/knowledge-planet/ai-agent/evolution/) —— 从经验沉淀到自我改进

::: tip 阅读建议
基础篇按顺序阅读即可，章节之间有明确的依赖关系。进阶篇各章相对独立，可按需取用。
:::
