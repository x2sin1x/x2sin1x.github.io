---
title: "基准与评估方法"
date: 2026-09-22T17:00:00+08:00
weight: 126
---

# 基准与评估方法

> 从公开基准到自建评测，再到在线监控——评估方法要覆盖“和别人比”、“和自己比”、“和真实用户比”三个问题。

## 公开基准

| 基准 | 测什么 | 特点 |
| ---- | ---- | ---- |
| **SWE-bench**（及 Verified / Pro） | 修真实 GitHub issue | Coding Agent 的事实标准；Verified 子集经人工校验，参考价值更高 |
| **GAIA** | 通用助理任务（多步推理 + 工具 + 网页） | 贴近 Working Agent 的开放环境 |
| **TAU-bench** | 客服类对话式 Agent（带工具、带规则） | 考察规则遵循与多轮交互 |
| **WebArena / WebVoyager** | 网页操作 | Working Agent 的 GUI 能力 |
| **AgentBench** | 多环境综合 Agent 能力 | 广度优先的总览 |

读基准分数的三个提醒：

1. **分数是分布，不是保证**。榜单第一名在你的任务上可能不如第二名——任务分布不同。公开基准的正确用法是初筛，决策靠自己的评测集。
2. **警惕过拟合与污染**。基准题目可能混进训练数据；刷分式的 prompt 微调不代表真实能力。
3. **基准测的是“能做对”，生产还要看“做得多便宜、多稳”**。成本与延迟在榜单上不可见。

## 自建评测：最重要的一套

自己的评测集是唯一能反映真实业务的，设计要点：

- **从真实失败里长出来**。每个线上 bad case 转化为一个评测用例——评测集是组织的学习沉淀。
- **按性质断言，不按字面断言**。“回答包含正确的退款政策要点”优于“回答等于某段文本”；给关键场景配 LLM-as-judge 的 rubric。
- **分层覆盖**：组件层（工具选择正确率）、轨迹层（步数上限、无空转）、结果层（端到端通过率）。
- **含安全用例**：注入攻击样本、越权请求必须被拦截（见安全与权限），安全指标是回归测试的一部分。

## 在线评估：离线测不出的部分

离线评测环境再真实，也和生产的流量分布、用户行为有差距。上线后的补充手段：

- **A/B 实验**。新 prompt / 新模型 / 新 Harness 参数灰度放量，对比任务完成率、用户干预率、成本。
- **护栏指标监控**。完成率骤降、平均步数飙升、工具错误率异常——这些都是回归的实时信号。
- **用户干预率**是 Working Agent 的黄金指标：人插手越多，Agent 越不合格。

## 把评估做成习惯

评估的最高形态不是某个工具，而是开发节奏：每次改动（prompt、模型、工具、编排）都在同一评测集上出报告，回归可回放定位。做到这一点，前面各章的所有优化——上下文策略、编排模式、Harness 参数——才有了客观的裁判。

## 参考

- [SWE-bench](https://www.swebench.com)
- [GAIA: a Benchmark for General AI Assistants](https://huggingface.co/papers/2311.12983)
- [TAU-bench](https://github.com/sierra-research/tau-bench)
- [Building Effective Agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
