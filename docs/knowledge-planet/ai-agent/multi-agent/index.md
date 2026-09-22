---
title: "多智能体协同"
date: 2026-09-22T17:00:00+08:00
weight: 114
---

# 多智能体协同

> 单个 Agent 的窗口和注意力终究有限。多智能体不是“更多大脑”的堆砌，而是把任务在**空间上并行、在上下文上隔离**。

## 什么时候需要多智能体

先说清动机，因为多智能体的代价比单 Agent 大得多。三个真实的收益来源：

1. **上下文隔离**。子任务的探索过程（读几十个文件、试错多次）不需要污染主 Agent 的窗口，只需要把结论带回来。这是最被低估的收益——多智能体首先是上下文架构，其次才是并行架构。
2. **并行加速**。独立的子任务（互不依赖的搜索、多模块重构）并行执行，墙钟时间缩短。
3. **视角专门化**。不同子 Agent 用不同的系统提示、甚至不同的模型——一个挑剔的评审者比“自己审自己”有效得多。

代价同样明确。Anthropic 在多智能体研究系统的工程复盘里给出过量级估计：多智能体系统消耗的 token 约为普通对话的 15 倍；协调开销（任务描述、结果整合、意见冲突）会吃掉一部分并行收益；且单个子 Agent 的错误会被主 Agent 当作事实采信。

**经验法则**：单 Agent + 好的上下文管理能解决的事，不要上多智能体。

## 本章地图

- [Subagents 与任务派生](/knowledge-planet/ai-agent/multi-agent/subagents-task-delegation/) —— 最基本的形态：主 Agent 派生一个一次性子 Agent 干活、只回收结论。
- [编排模式](/knowledge-planet/ai-agent/multi-agent/orchestration-patterns/) —— 多个 Agent 的组织形状：Supervisor、Orchestrator-Worker、Swarm。
- [通信与协议](/knowledge-planet/ai-agent/multi-agent/communication-protocols/) —— Agent 之间如何对话：消息、状态与 A2A。
- [上下文隔离与共享](/knowledge-planet/ai-agent/multi-agent/context-isolation/) —— 什么必须隔离、什么必须共享，以及共享状态的一致性。

这四节的递进：先会派一个子 Agent，再会组织一群 Agent，然后解决它们怎么说话、怎么共享工作成果。

## 参考

- [How we built our multi-agent research system — Anthropic Engineering](https://www.anthropic.com/engineering/built-multi-agent-research-system)
- [Building Effective Agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
