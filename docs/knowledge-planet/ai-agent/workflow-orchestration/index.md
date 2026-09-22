---
title: "工作流与任务编排"
date: 2026-09-22T17:00:00+08:00
weight: 110
---

# 工作流与任务编排

> 基础篇讲的是零件，本章开始讲装配：如何把单个 Agent 的循环变成可靠完成长任务、复杂任务的系统。

基础篇的 Agent 核心循环（感知 → 思考 → 行动 → 观察）面对短任务绰绰有余。但真实任务往往持续几十分钟到几小时：要改十个文件、要跑多次测试、会中途出错、可能被打断。从“能循环”到“能交付”，中间隔着三层工程，这正是本章组的三节：

- [Planning 与 Goal](/knowledge-planet/ai-agent/workflow-orchestration/planning-goal/) —— 先解决“做什么、按什么顺序做”：目标设定与计划分解。
- [Harness Engineering](/knowledge-planet/ai-agent/workflow-orchestration/harness-engineering/) —— 再解决“Agent 住在什么样的壳里”：系统提示、工具面、权限、上下文管理的整体设计。
- [Loop Engineering](/knowledge-planet/ai-agent/workflow-orchestration/loop-engineering/) —— 最后解决“循环本身怎么跑得稳”：终止条件、重试、压缩时机、断点续跑。

三者合起来回答一个工程问题：&#8203;**如何让“脆弱的单次调用”串成“健壮的长时间运行系统”**&#8203;。

一个值得先建立的判断：Anthropic 反复强调，成熟团队的实现大多用的是&#8203;**简单、可组合的模式**&#8203;而非重型框架。编排的复杂度应该跟着任务走——先把 Goal 和循环跑稳，再谈更复杂的协作。

## 参考

- [Building Effective Agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Claude Agent SDK](https://docs.anthropic.com/en/api/agent-sdk/overview)
