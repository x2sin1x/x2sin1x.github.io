---
title: "Subagents 与任务派生"
date: 2026-09-22T17:00:00+08:00
weight: 115
---

# Subagents 与任务派生

> Subagent 是多智能体世界的氢原子：主 Agent 生成一个子 Agent，交出一个任务描述，等它带回一份结论。

## 最小工作样例

```python
# 主 Agent 决定派生
result = spawn_subagent(
    task="调研本项目所有使用 requests 的位置，总结超时与重试配置的现状",
    tools=["read", "grep", "glob"],       # 能力可以收窄
    context="fresh",                       # 不带主 Agent 的对话历史
)
# result 只有几百 token：调研结论 + 关键文件清单
# 子 Agent 过程中消耗的几万 token，全部留在它自己的窗口里，用完即弃
```

三个参数就是 Subagent 机制的全部灵魂：

1. **任务描述（task）**。子 Agent 对主 Agent 的对话一无所知，任务描述必须自足：目标、验收标准、相关线索、输出格式。写好派生任务是主 Agent 的新技能——本质上还是 [Prompt Engineering]。
2. **工具与权限（tools）**。探索型子 Agent 只需要读类工具；有破坏力的工具默认不给。权限最小化在派生时最容易执行。
3. **上下文（context）**。默认全新窗口。子 Agent 的价值恰恰在于“不带偏见地看现场”——主 Agent 的既有判断反而会污染探索。

## 何时派生、何时不派

适合派生的信号：

- **搜索/调研型工作**：读大量材料、产出小结论，输入输出比悬殊。
- **可并行的独立子任务**：三个模块的性能分析互不依赖，并行派三个。
- **需要“干净眼光”的审查**：代码评审、方案质询——没有执行者立场的新窗口，比“自己检查自己”可靠。

不适合的信号：子任务强依赖主 Agent 已建立的上下文（澄清成本超过隔离收益）、或任务本身就两三步（派生的开销大于收益）。

## 从 Subagent 到多智能体

单个派生只涉及一次“主—从”交互，还没有真正的“协同”。当出现以下需求时，就需要[编排模式]的系统化组织：

- 多个子 Agent 之间需要传递中间结果（A 的产出是 B 的输入）；
- 需要稳定的角色分工（有人规划、有人执行、有人评审）；
- 子任务有先后依赖，需要调度。

理解 Subagent 是理解一切多智能体模式的前提——所有复杂的拓扑，拆到底都是一次次的“派生—执行—回收”。

## 参考

- [How we built our multi-agent research system — Anthropic Engineering](https://www.anthropic.com/engineering/built-multi-agent-research-system)
- [Claude Code Docs：Subagents](https://code.claude.com/docs/en/sub-agents)
