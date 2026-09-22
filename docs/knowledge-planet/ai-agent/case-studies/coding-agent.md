---
title: "Coding Agent"
date: 2026-09-22T17:00:00+08:00
weight: 121
---

# Coding Agent

> Claude Code、Codex、Pi、DeepSeek Harness……形态各异，但解剖开来是同一副骨架：shell + 文件系统作为工具面，测试作为验收，权限系统作为闸门。

## 为什么编程是 Agent 的主场

Coding Agent 是当前最成熟的 Agent 类别，原因写在环境的性质里：

1. **工具面天然完备**。代码仓库 = 文件系统 + 终端。读文件、写文件、跑命令三个原语覆盖几乎全部操作，不需要任何专门集成。
2. **验证闭环免费赠送**。编译器、测试、lint 是现成的机器可判验收标准——Agent 写完代码自己就能检查对不对。这个“行动 → 验证 → 纠错”的闭环在其他领域（写邮件、订机票）要昂贵得多。
3. **迭代便宜**。改错了就 git 回滚，试错的代价极低。

这解释了一个行业现象：Agent 能力的评测基准（SWE-bench）和最成熟的落地产品都集中在编程领域——不是巧合，是环境的可验证性决定的。

## 典型解剖：Claude Code 风格的架构

把代表产品拆到组件层面（细节各家不同，骨架高度一致）：

| 组件 | 典型实现 |
| ---- | ---- |
| 工具面 | Read / Write / Edit / Bash / Grep / Glob 等窄内核 + MCP 扩展 + Skills |
| 系统提示 | 领域规范（代码风格、安全戒律、何时询问用户） |
| 权限系统 | 命令分级确认 + 白名单记忆 + 沙箱 |
| 上下文管理 | 自动压缩 + 任务清单常驻 + 文件按需读取 |
| 记忆 | 仓库内 `CLAUDE.md` / `AGENTS.md`（项目约定）+ 用户级偏好 |
| 协作 | Plan mode（先对齐方案再动手）+ Subagents（并行探索/评审） |
| 验收 | 测试、lint、类型检查进循环，作为 Loop 的出口闸门 |

对照可以发现：**各家产品的差异主要是 Harness 工程的差异**——同一个模型换不同的 Harness，生产率差异显著。

## DeepSeek Harness 的启示

值得单独一提的是 2026 年 DeepSeek 发布的 Agent Harness 论文：它把“Harness”从产品内部实现提升为一等研究对象——同一模型下，工具设计、上下文管理、错误恢复机制的系统性改进，能带来接近换代模型的能力提升。这印证了本教程的基本立场：&#8203;**Agent 工程（补齐大脑的缺失）与模型工程同等重要**&#8203;。

## 选择与使用建议

- **用产品还是自建？** 先用成熟产品跑通业务，识别出不满足的具体环节，再决定是否用 Agent SDK 自建——多数团队的答案是不需要自建。
- **评估看什么？** SWE-bench Verified 榜单作为初筛，真正的决策依据是你自己仓库上的实测（见“Agent 的评估”一章）。
- **最大的杠杆在人机协作方式**：把 Goal 写清楚（验收标准、边界）、提供 `AGENTS.md` 项目约定、善用 plan mode 先对齐方案——这些使用侧的功夫，常常比换模型更能改变产出质量。

## 参考

- [Claude Code](https://github.com/anthropics/claude-code)
- [Claude Code Best Practices — Anthropic Engineering](https://www.anthropic.com/engineering/claude-code-best-practices)
- [DeepSeek：Agent Harness 研究](https://github.com/deepseek-ai)
- [SWE-bench](https://www.swebench.com)
