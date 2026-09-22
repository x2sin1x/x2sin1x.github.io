---
title: "Prompt Engineering"
date: 2026-09-22T17:00:00+08:00
weight: 104
---

# Prompt Engineering

> Prompt 是离大脑最近的输入。写好它，是性价比最高的优化。

Prompt Engineering 常被误以为玄学，但它有清晰的方法论：核心是三件事——**把任务说清楚、给足参照物、约束输出形式**。

## 说清楚：指令设计

模型不会读心，但它会忠实地执行你说出的（以及你没说出的）一切假设。几条经过大量实践检验的原则：

- **具体优于抽象**。“写得专业一点”不如“面向有 3 年经验的 Python 开发者，避免入门概念，直接给代码”。
- **正面指令优于负面清单**。告诉模型“做什么”，比罗列一串“不要做……”更有效；负面清单只作为补充。
- **把复杂任务拆成编号步骤**。对多步任务，显式的步骤清单能显著提升完成率——这本质上是把外部的规划结构借给模型。
- **给逃生通道**。加上“如果信息不足，先提问再动手”或“如果无法确定，回答‘不知道’”，能明显减少幻觉和瞎猜。模型乱编，常常是因为没有体面地说“我不会”的选项。

::: tip 为什么 System Prompt 里全是“戒律”？
读一读 Claude Code 或各类 Agent 的系统提示就会发现：大部分篇幅不是能力描述，而是行为约束——什么时候该用哪个工具、什么时候必须停下来询问、哪些操作禁止自动执行。Agent 的 prompt 本质上是给一个能力很强、但不知道分寸的实习生写岗位手册。
:::

## 给参照物：少样本与示例

少样本（few-shot）示例是改变输出质量最快的单一手段：

- **输入-输出对**优于纯描述。一个精心挑选的例子胜过三段解释。
- 示例要覆盖**边界情况**：一个正常样例加一个边界样例，好过五个正常样例。
- 谨防示例的“锚定效应”：模型会过度模仿示例的格式、长度甚至错误。示例的格式即输出格式，要按最终想要的样子写。

## 约束输出：结构化与工具

Agent 的输出经常要被程序解析，自由文本是解析的天敌。两个层次的结构化：

1. **格式约束**：要求 JSON、表格或固定段落结构。有效但偶尔失效，解析侧要做容错。
2. **原生结构化输出**：API 层面用 JSON Schema 或工具签名约束解码过程，模型只能产出合法结构。Agent 中应优先使用——工具调用本身就是一种结构化输出。

对推理类任务，要求模型“先思考再回答”（或使用推理模型的原生思考模式）几乎总是提升准确率：强迫输出前先推理，等于把 ReAct 的思想用在了单次调用里。

## 与 Context Engineering 的分工

Prompt 工程管的是“每一块内容写得好不好”，但它有一个天花板：&#8203;**再好的 prompt 也救不了被塞爆的窗口**&#8203;。当会话变长、工具结果堆积、多个任务并行时，问题就不再是“写好每一块”，而是“整个上下文如何治理”——那是 [Context Engineering](/knowledge-planet/ai-agent/context/context-engineering/) 的领域。

## 参考

- [Prompt Engineering Overview — Anthropic Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Prompt Engineering Guide — OpenAI](https://platform.openai.com/docs/guides/prompt-engineering)
- [Building Effective Agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
