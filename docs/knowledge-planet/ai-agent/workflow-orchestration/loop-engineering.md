---
title: "Loop Engineering"
date: 2026-09-22T17:00:00+08:00
weight: 113
---

# Loop Engineering

> Harness 决定 Agent 住在什么房子里，Loop Engineering 决定它的心跳——那个 while 循环如何稳定地跳上几个小时而不骤停、不失速、不空转。

## 循环的骨架

把基础篇的核心循环展开，一个生产级 Loop 至少要处理五件事：

```python
while True:
    # 1. 终止检查：任务完成 / 达到上限 / 用户中断
    if should_stop(context, budget):
        break
    # 2. 上下文治理：接近阈值时压缩
    if token_count(context) > COMPACT_THRESHOLD:
        context = compact(context)          # 保留近期 + 摘要历史 + 常驻文件
    # 3. 调用模型（带重试与超时）
    response = call_model(context, tools, retries=3)
    # 4. 执行工具（按权限策略放行或询问）
    for call in response.tool_uses:
        result = execute_with_policy(call)
        context.append(result)
    # 5. 检查点：状态落盘，支持断点恢复
    checkpoint(context)
```

逐项展开其中最要紧的三个。

## 终止：循环出口的三重门

无限循环是 Agent 最经典的故障。成熟 Loop 用三道闸门：

1. **模型自判完成**。任务清单全部勾销、模型输出完成声明。这是正常出口，但不可信任——模型可能过早放弃，也可能“完成”与验收标准不符。
2. **机器可验的验收标准**。把 Goal 写成可执行检查（测试通过、编译成功），出口由检查结果决定，而不是由模型的自信决定。这是[Goal 设计](/knowledge-planet/ai-agent/workflow-orchestration/planning-goal/)的直接回报。
3. **预算硬上限**。步数上限、token 预算、墙钟时间。无论模型多执着，超限即停并报告进度——宁可交回一个诚实的半成品，不要一个烧穿预算的幻觉。

## 错误处理：把失败变成上下文

Loop 对错误的姿态，决定 Agent 是“试错学习”还是“原地崩溃”：

- **工具失败写回上下文**。报错信息原文进入对话，让下一轮模型看到失败原因并调整——这是 ReAct 纠错机制的直接应用。
- **区分可重试与不可重试**。网络超时重试（指数退避），参数错误不重试（重试同样的调用只会得到同样的错），权限拒绝立刻停。
- **挫败感检测**。连续多轮同类型失败、反复回滚到同一状态，是模型陷入循环的信号。Harness 应识别模式并强制注入“换一条路或先停下来”的指令。

## 检查点与断点续跑

长任务必须假设进程会死：崩溃、超时、发布重启。Loop Engineering 的应对是**状态外置**：

- 对话历史、任务清单、关键中间产物周期性落盘。
- 重启后从检查点重建上下文，而不是从零再来。
- LangGraph 的 durable execution、Claude Code 的会话恢复（`--resume`）都是这个机制的产物。

## 节奏与可观测

最后是容易被忽略的运行质量：

- **进度可见**。用户应能随时看到“做到哪一步了”（当前任务、最近动作、token 消耗），而不是盯着一个转圈的 spinner。
- **日志即调试界面**。每轮的完整 prompt、响应、工具结果都应可回放——Agent 的 bug 几乎只能靠轨迹回放定位，这直接引出[评估]章的轨迹评估方法。
- **中断友好**。用户随时插话，Loop 应把插入的指令当新一轮观察处理，而不是丢弃或重启。

## 参考

- [Building Effective Agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [LangGraph：Durable Execution](https://docs.langchain.com/oss/python/langgraph/durable-execution)
- [Claude Code Docs：常见工作流（长任务与检查点）](https://code.claude.com/docs/en/common-workflows)
