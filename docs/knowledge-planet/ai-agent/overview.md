---
title: "智能体 = 大脑 + 眼睛 + 手脚"
date: 2026-09-22T17:00:00+08:00
weight: 101
---

# 智能体 = 大脑 + 眼睛 + 手脚

> 参考阅读：Anthropic《Building Effective Agents》（2024）· ReAct: Synergizing Reasoning and Acting in Language Models（Yao et al., 2022）

## 什么是 Agent

"Agent" 这个词被用得很泛。Anthropic 在《Building Effective Agents》里给了一个实用的区分，把所有相关系统统称为&#8203;**agentic systems（智能体系统）**&#8203;，再进一步分成两类：

- **工作流（Workflow）**：LLM 和工具按照&#8203;**预先写死的代码路径**&#8203;被编排起来。每一步做什么、下一步是谁，都是开发者决定的。
- **智能体（Agent）**：LLM **自己决定**流程和工具的使用方式，对“怎么完成任务”保持控制权。

这个区分很关键：前者是“按剧本演戏”，后者是“给了目标自由发挥”。本教程讨论的重点是后者，但贯穿两者的底层组件是同一套——这正是我们把组件（大脑、眼睛、手脚）和编排方法分成两大部分来讲的原因。

## 大脑 + 眼睛 + 手脚

一个 Agent 可以拆成三个部分：

| 部件 | 对应能力 | 谁来提供 | 详细章节 |
| ---- | ---- | ---- | ---- |
| 大脑 | 理解、推理、规划、决策 | LLM | [LLM](/knowledge-planet/ai-agent/llm/) |
| 眼睛 | 感知环境：读文本、看屏幕、收结果 | 多模态输入 + 上下文管理 | [上下文](/knowledge-planet/ai-agent/context/) |
| 手脚 | 执行动作：调 API、跑命令、改文件 | 工具调用 | [工具](/knowledge-planet/ai-agent/tools/) |

这个比喻有两个隐含结论，值得在动手写代码之前想清楚：

1. **大脑只有一颗，而且是借来的。** Agent 的智能上限就是所用 LLM 的能力上限；系统其他部分做得再精巧，也无法弥补模型的推理短板。所以选模型、了解模型的脾气是第一课。
2. **大脑天生没有记忆、没有眼睛、没有手脚。** 模型的“知识”冻结在训练数据里，“经历”止于当前上下文窗口。Agent 的全部工程量，本质上都是在给大脑补齐这些缺失：记忆靠[用户记忆与知识库](/knowledge-planet/ai-agent/memory-and-knowledge/)，感知靠上下文工程，行动靠工具。

## Agent 核心循环

把三个部件组装起来，就得到所有 Agent 共享的那个循环：&#8203;**感知 → 思考 → 行动 → 观察**&#8203;。用伪代码写出来只有几行：

```python
context = system_prompt + task
while not task_done:
    observation = environment.observe()          # 眼睛：看到世界的变化
    context.append(observation)                  # 观察结果进入上下文
    thought = llm.think(context)                 # 大脑：推理并决定下一步
    action = thought.next_action                 # 决策：调用某个工具，或宣布完成
    result = tools.execute(action)               # 手脚：真正对世界产生作用
    context.append(result)
```

这个循环里有三个容易低估的难点，它们分别催生了后续的三个主题：

- **上下文是稀缺资源**。每一轮观察和结果都会挤占有限的窗口，塞多了模型会“看不过来”。如何管理这个不断膨胀的上下文，是[上下文工程](/knowledge-planet/ai-agent/context/)的主题。
- **循环的出口在哪里**。模型可能陷入死循环、可能过早宣布完成、可能在失败后无限重试。判断“任务做完了”本身就是一个工程问题，这属于工作流与编排的内容。
- **每次行动都有代价和风险**。删文件、转账、发邮件——手脚越灵活，出错的可能性越大。这催生了安全与权限的设计（进阶篇）。

## ReAct：把推理写出来

ReAct（Reasoning + Acting，2022）是上述循环最经典的具体化。它要求模型在每一步显式输出三段式结构：

```text
Thought:  用户要查上海明天的天气，我应该调用天气工具
Action:   get_weather(city="上海", date="明天")
Observation: 多云转小雨，18~24℃，降水概率 80%
Thought:  已经拿到结果，且预报有雨，可以提醒用户带伞并总结
Answer:   上海明天多云转小雨……建议携带雨具
```

ReAct 的贡献在于揭示了两个至今仍然成立的规律：

1. **推理和行动交替进行比直接给答案效果好**。模型在行动前“想一下”，能显著减少瞎猜工具参数、幻觉事实的次数。
2. **观察结果要写回上下文**。行动产生的真实世界反馈是纠错的最佳来源——“调用的工具报错了”比任何提示词技巧都更能让模型自我修正。

今天主流的 Agent（Claude Code、OpenAI 的 Agents SDK 等）在协议层面早已进化出原生的工具调用（function calling），不再需要让模型输出格式化的文本再解析，但“思考—行动—观察”这个骨架没有变。

## 与工作流：什么时候不需要 Agent

最后泼一盆冷水，也是 Anthropic 反复强调的原则：&#8203;**能用简单方案就不要用 Agent**&#8203;。

- 任务能拆成固定的几步？写一个 prompt chaining 工作流，可预测、可调试、便宜。
- 只需要查一次资料再回答？一次带检索的 LLM 调用就够了。
- 需要在开放环境中灵活应变、步骤事先无法穷举？这才轮到 Agent 上场。

Agent 用延迟和成本换灵活性。这个权衡没有标准答案，但“先问要不要，再问怎么做”应该成为默认习惯。工作流的具体模式（链式、路由、并行、orchestrator-worker）我们会在进阶篇展开。

## 本章小结

- Agent 与工作流的区别在于：**流程由谁决定**——代码还是模型。
- Agent = LLM（大脑）+ 感知与上下文（眼睛）+ 工具（手脚），工程量集中在给大脑补齐缺失能力。
- 一切 Agent 共享“感知 → 思考 → 行动 → 观察”的核心循环；ReAct 是它最经典的形式。
- 能用简单方案就不要用 Agent。

## 参考

- [Building Effective Agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [What Are Agents? — Anthropic](https://www.anthropic.com/research/building-effective-agents)
