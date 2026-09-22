---
title: "案例研究"
date: 2026-09-22T17:00:00+08:00
weight: 120
---

# 案例研究

> 前面所有章节的组件——大脑、眼睛、手脚、编排、安全——在真实产品里是如何被装配起来的？本章拆解四类代表案例。

案例按**工作环境与验证方式**分类，而不是按厂商：

- [Coding Agent](/knowledge-planet/ai-agent/case-studies/coding-agent/) —— 住在代码仓库和终端里，产出可被编译器和测试机器验证。代表：Claude Code、Codex、Pi、DeepSeek Harness。
- [Working Agent](/knowledge-planet/ai-agent/case-studies/working-agent/) —— 住进用户的聊天渠道和桌面，处理日常事务，结果往往只能由人来验收。代表：OpenClaw、WorkBuddy。
- [Agent 开发](/knowledge-planet/ai-agent/case-studies/agent-development/) —— 不直接服务最终用户，而是服务开发者：装配 Agent 的框架与 SDK。代表：LangChain/LangGraph、AutoGen、OpenAI Agents SDK。
- [Agent 与软件工程](/knowledge-planet/ai-agent/case-studies/agents-software-engineering/) —— 不是某个产品，而是一场方法论变迁：Agent 进入软件工程流程后，工程实践本身如何变化。

四类案例的阅读价值不同：Coding Agent 展示**Harness 工程的极致**，Working Agent 展示**开放环境下的安全与记忆挑战**，开发框架展示**组件的标准化封装**，软件工程篇展示**Agent 对工作方式本身的重塑**。

::: tip 带着架构眼光读案例
读每个案例时，建议对照基础篇的组件清单问四个问题：它的循环长什么样？工具面怎么组织？上下文和记忆怎么管理？权限怎么分级？所有案例的差异，几乎都能归结为这四问的不同答案。
:::

## 参考

- [Building Effective Agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
