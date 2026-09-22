---
title: "编排模式"
date: 2026-09-22T17:00:00+08:00
weight: 116
---

# 编排模式

> 把多个 Agent 组织起来，业界收敛出了三种基本形状。它们不是框架特性，而是拓扑结构——你完全可以自己实现。

## Orchestrator-Worker：主从分派

最常用、也最简单的形状。一个编排者把任务拆成子任务，分派给多个 Worker，汇总结果：

```text
        ┌──────────────┐
        │ Orchestrator │  拆解任务 / 汇总结论
        └──┬────┬────┬─┘
           ▼    ▼    ▼
       [Worker][Worker][Worker]   并行执行，互不通信
```

- **适用**：子任务可独立、可并行的场景——多源资料调研、批量文件处理、多模块分析。Anthropic 的多智能体研究系统就是典型的 Orchestrator-Worker：主 Agent 拆出研究方向，若干并行子 Agent 分头搜索，主 Agent 汇总成报告。
- **关键点**：Worker 之间不说话，所有协调发生在 Orchestrator。拆分质量决定一切——拆出依赖冲突的子任务，并行就变成事故。

## Supervisor：带流程管控的主从

Supervisor 在主从结构上加了一层**流程状态管理**：它不一次性派完全部任务，而是逐派、逐验、再决定下一步。Worker 产出后 Supervisor 审查质量，不合格打回重做，全部合格才进入下一阶段。

- **适用**：质量敏感、步骤间有依赖的流水线，如“起草 → 事实核查 → 润色”的内容生产。
- **与 Orchestrator-Worker 的区别**：后者是一次性分发 + 汇总；Supervisor 持有流程状态，Worker 只是可替换的手。代价是 Supervisor 成为串行瓶颈。

## Swarm / Handoffs：去中心的接力

没有常驻的主管，Agent 之间**直接移交控制权**（handoff）：客服 Agent 判断这是退款问题，连同上下文把对话移交给退款专员 Agent，此后由它接管。

```text
[前台 Agent] --handoff--> [退款 Agent] --handoff--> [物流 Agent]
   （每个 Agent 独立窗口，移交时打包必要上下文）
```

- **适用**：业务像“流水道岔”一样按类型分流——客服路由、多领域咨询。OpenAI 的 Agents SDK 把 handoff 作为一等原语，LangGraph 也支持 swarm 拓扑。
- **关键点**：移交的是**控制权和上下文包**，移交后原 Agent 退出循环。没有全局协调者意味着没有全局视图，复杂任务容易在移交链中丢上下文。

## 模式选择速查

| 形态 | 协调方式 | 适合 | 警惕 |
| ---- | ---- | ---- | ---- |
| Orchestrator-Worker | 一次性拆分汇总 | 可并行、可独立 | 子任务依赖冲突 |
| Supervisor | 逐步派发 + 质量把关 | 流水线、质量敏感 | 中心瓶颈 |
| Swarm / Handoffs | 控制权直接移交 | 类型分流的对话业务 | 全局上下文丢失 |

::: tip 模式是菜单，不是宪法
真实系统经常混用：主 Orchestrator 内部对一个子任务用 Supervisor 流水线，某个环节再 handoff 给专家。判断标准始终是任务结构，而不是框架提供了哪种 API。
:::

## 参考

- [Building Effective Agents — Anthropic Engineering（orchestrator-workers 等）](https://www.anthropic.com/engineering/building-effective-agents)
- [How we built our multi-agent research system — Anthropic Engineering](https://www.anthropic.com/engineering/built-multi-agent-research-system)
- [OpenAI Agents SDK：Handoffs](https://openai.github.io/openai-agents-python/handoffs/)
