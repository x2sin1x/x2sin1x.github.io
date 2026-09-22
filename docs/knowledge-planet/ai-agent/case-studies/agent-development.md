---
title: "Agent 开发"
date: 2026-09-22T17:00:00+08:00
weight: 123
---

# Agent 开发

> 开发框架不服务终端用户，服务开发者：把基础篇里散落的组件——循环、工具、记忆、编排——预先装配成可复用的抽象。

## 框架图谱

| 框架 | 抽象重心 | 一句话定位 |
| ---- | ---- | ---- |
| **LangChain / LangGraph** | 图编排 + 状态机 | 把 Agent 流程显式建模为图：节点是步骤，边是控制流，状态在图上流动 |
| **OpenAI Agents SDK** | Agent + Handoff | 轻量原语：Agent（指令 + 工具）、handoff（控制权移交）、guardrail（护栏） |
| **AutoGen（微软）** | 多智能体会话 | 以 Agent 间对话为核心组织协作（现已演进并入 agent-framework） |
| **CrewAI** | 角色协作 | 用“团队角色”（研究员、写手、审核）组织 Agent 分工 |
| **Claude Agent SDK** | 内置 Harness | Anthropic 把 Claude Code 的 Harness 沉淀为 SDK：循环、工具、权限开箱即用 |

## 框架真正卖给你的是什么

剥开各家 API 差异，框架的价值集中在四件事：

1. **循环与状态管理**：durable execution、断点恢复、human-in-the-loop 中断——Loop Engineering 的工程化封装（LangGraph 的核心卖点）。
2. **编排抽象**：把 Supervisor、handoff、并行分派做成一等概念，免于手写协调代码。
3. **组件生态**：现成的工具连接器、记忆后端、观测面板（如 LangSmith）。
4. **最佳实践的固化**：框架作者把已知有效的模式烘进了默认行为。

## 框架的代价

Anthropic 在《Building Effective Agents》中的提醒依然有效，且被大量实践反复验证：

- **抽象遮蔽调试信息**。自定义框架里，你能看到每一轮的完整 prompt 与响应；框架封装后，出错时不知道“它到底给模型发了什么”——这是 Agent 调试中最贵的黑盒。
- **诱导过度复杂**。框架让搭复杂拓扑变得容易，于是人们搭了不需要的复杂拓扑。而“简单、可组合的模式”通常更好调试、更省 token。
- **错误的底层假设**。不理解框架替你做了什么（重试？压缩？消息怎么拼？），故障时无从下手。

::: tip 务实的采用策略
从 LLM API 裸写开始（核心循环不过几十行），把框架当作“遇到了对应问题再引入”的方案库：需要断点恢复 → 看 LangGraph 的 durable execution；需要多 Agent 对话 → 看 AutoGen 的会话模型；需要内置 Harness → 看 Claude Agent SDK。**用框架的原因应该是“它解决的问题我确实有”，而不是“别人都在用”。**
:::

## 学习框架的正确姿势

无论选哪个框架，检验理解的标准是同一个：**能否用裸 API 复现它的核心行为？**能徒手写出框架替你做的循环、状态流转与工具调度，框架才是你的工具；否则你就是框架的载体——出了问题既改不动它，也绕不开它。

## 参考

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [AutoGen / Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Claude Agent SDK](https://docs.anthropic.com/en/api/agent-sdk/overview)
- [Building Effective Agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
