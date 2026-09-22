---
title: "工具"
date: 2026-09-22T17:00:00+08:00
weight: 107
---

# 工具：给大脑装上手脚

> 大脑能说“我应该查一下天气”，但查天气这个动作必须有人替它完成。工具就是 Agent 的手脚——模型决策，工具执行，结果回到大脑。

## Function Calling：手脚的神经接口

现代 LLM API 的工具调用机制已经高度标准化：

```python
tools = [{
    "name": "get_weather",
    "description": "查询指定城市某日的天气",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名"},
            "date": {"type": "string", "description": "YYYY-MM-DD"}
        },
        "required": ["city"]
    }
}]

response = llm.chat(messages, tools=tools)
# response 中的 tool_use 块 = 模型决定调用 get_weather(city="上海")
result = execute(response.tool_use)      # 你的代码真正执行
messages.append(tool_result(result))     # 结果写回对话，进入下一轮循环
```

三点值得注意：

1. **模型不执行任何东西**。它只输出“我想调用 X 工具、参数是 Y”，真正执行的是你的代码，因此权限控制天然在你的手里。
2. **工具描述就是 prompt**。模型靠 `description` 和参数说明来判断“这个场景该不该用这个工具、参数怎么填”，写工具描述就是写 prompt，含糊的描述直接导致选错工具。
3. **错误信息也是 prompt**。工具失败时，返回结构化、可行动的错误（“日期格式应为 YYYY-MM-DD”）比返回 `Error 500` 更能让模型自我纠正。

## 工具设计的原则

Agent 系统中，工具集的质量往往比提示词技巧更影响成败。Anthropic 在《Writing effective tools for agents》中总结的经验：

- **少而清晰优于多而全**。一次暴露几十个工具会让选择错误率飙升；功能相近的工具要合并或明确划界。
- **为模型重新设计接口**。人用的 API 未必适合模型：返回分页、嵌套层级深、依赖隐式状态的接口，模型用起来步步出错。工具接口要“一次调用返回自足的结果”。
- **命名空间化**。大量工具时按前缀分组（`github_create_issue`、`github_list_prs`），帮助模型快速缩小搜索范围。
- **控制 token 占用**。所有工具的定义常驻系统提示，工具集越大基础开销越大——这是工具数量天然的软上限。

## 两条集成路线

有了接口标准，剩下的问题是：工具从哪里来？目前有两条互补的主流路线，本章各用一节展开：

- [MCP](/knowledge-planet/ai-agent/tools/mcp/) —— **连接器路线**：一个开放协议，把“接入外部系统”这件事标准化，解决 M×N 集成爆炸问题。
- [Skills 和 CLI](/knowledge-planet/ai-agent/tools/skills-cli/) —— **知识路线**：不新增连接，而是把领域知识、操作手册和命令行能力打包给 Agent，让它复用现成的软件世界。

两者的分工可以概括为：MCP 解决“**连不上**”的问题（没有接口的系统如何标准化接入），Skills 解决“**不会用**”的问题（有接口但不知道正确操作流程）。

## 参考

- [Writing Effective Tools for Agents — Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Building Effective Agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
