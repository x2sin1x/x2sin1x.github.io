---
title: "上下文"
date: 2026-09-22T17:00:00+08:00
weight: 103
---

# 上下文：喂养大脑

> 参考阅读：Anthropic《Effective Context Engineering for AI Agents》（2025）

大脑只有一颗，而每一次对话、每一次工具结果都要挤进有限的窗口。**上下文（Context）就是大脑在每个时刻能“看见”的全部内容**，它由几类成分构成：

| 成分 | 内容 | 特点 |
| ---- | ---- | ---- |
| 系统提示 | 角色、规则、工具说明 | 整个会话常驻 |
| 用户输入 | 任务描述与后续指令 | 逐步累积 |
| 工具结果 | 文件内容、API 返回、命令输出 | 体积最大、增长最快 |
| 历史轨迹 | 之前的思考、行动与观察 | 越来越长 |

上下文管理之所以是 Agent 工程的核心难题，是因为三股力量互相拉扯：**窗口有限**（塞不下）、**注意力稀释**（塞得下也看不过来）、**成本随长度线性增长**（每次循环都为全部历史付费）。

本章分两条线展开，它们解决同一个问题的不同层：

- [Prompt Engineering](/knowledge-planet/ai-agent/context/prompt-engineering/) —— 怎么**写好**进入上下文的每一块内容：指令、示例、输出约束。这是“静态质量”。
- [Context Engineering](/knowledge-planet/ai-agent/context/context-engineering/) —— 怎么**管理**上下文这个随时间变化的资源：压缩、隔离、检索注入。这是“动态治理”。

一个容易混淆的点值得先说清：Prompt Engineering 的对象是&#8203;**单次调用**&#8203;的输入质量，Context Engineering 的对象是&#8203;**整个会话生命周期**&#8203;的信息流。前者是写作，后者是资源管理。两者都做好，大脑才能持续保持清醒。

## 参考

- [Effective Context Engineering for AI Agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
