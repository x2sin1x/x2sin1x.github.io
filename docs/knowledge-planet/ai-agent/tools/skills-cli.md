---
title: "Skills 和 CLI"
date: 2026-09-22T17:00:00+08:00
weight: 109
---

# Skills 和 CLI

> MCP 解决“连不上”，Skills 解决“不会用”。有了接口，还需要把领域知识、操作流程和现成的命令行世界交给 Agent。

## Agent Skills：把说明书打包给大脑

2025 年 Anthropic 提出 Agent Skills：**用文件夹承载知识，让 Agent 在需要时加载**。一个 Skill 就是一个目录，核心是 `SKILL.md`：

```text
pdf-processing/
├── SKILL.md          # 元数据 + 操作说明
├── scripts/
│   └── fill_form.py  # 可执行脚本（可选）
└── reference.md      # 详细参考（可选）
```

`SKILL.md` 的结构极简：

```markdown
---
name: pdf-processing
description: 处理 PDF 表单填写与提取，用于表单类任务
---

# PDF 表单处理

## 步骤
1. 先用 scripts/inspect.py 查看表单字段
2. 用 scripts/fill_form.py 填写，参数见文件头注释
3. 完成后用 pypdf 校验字段值
```

其精髓是**渐进式披露（progressive disclosure）**：启动时 Agent 只看到每个 Skill 的 `name` 和 `description`（几十 token）；判断相关后才读入正文；脚本和参考文档仅在执行时加载。Skill 可以带任意多层参考资料，却不占用平时的工作窗口——这与“高信号小窗口”的上下文原则完全一致。

::: tip Skills 与 MCP 的对比
两者是互补关系，不是竞争关系：

| | MCP | Skills |
| ---- | ---- | ---- |
| 本质 | 连接协议 | 知识包 |
| 提供 | 新的能力接口（连上 Slack、数据库） | 使用能力的知识（怎么正确操作） |
| 上下文代价 | 工具定义常驻 | 按需加载 |
| 依赖 | 需要协议栈 | 只需文件系统 |

一个典型的组合：用 MCP 连上内部 API，再写一个 Skill 告诉 Agent 调这些 API 的正确顺序、边界条件和常见坑。
:::

Skills 已有跨厂商的开放规范（[agentskills.io](https://agentskills.io)），Claude Code、Claude.ai 与 API 均已支持，官方示例见 [anthropics/skills](https://github.com/anthropics/skills)。

## CLI：最被低估的工具面

给 Agent 接上 shell，它就瞬间继承了整个 Unix 世界：`grep`、`curl`、`ffmpeg`、`git`……不需要为任何能力写专门的工具。Claude Code、OpenAI Codex 这类 Coding Agent 都把 shell 作为核心工具，原因有三：

1. **组合性**。命令行 50 年积累的工具生态天然可组合，`grep | sort | uniq` 一行抵得上十几个专用工具。
2. **可读的输出**。命令行工具的文本输出对模型天然友好，错误信息可直接指导下一步。
3. **零集成成本**。装好就能用，不需要协议、不需要 SDK。

代价是**风险**：shell 拥有完整系统权限。这正是 Coding Agent 都要配套权限沙箱、命令白名单与人工确认的原因（详见进阶篇“安全与权限”一章）。

如果为 Agent 设计 CLI 工具，几条经验：

- 输出对人和对机器分层：`--json` 或精简模式，避免让模型啃人类排版的美化输出。
- 错误信息写到标准错误，且包含“如何修正”的提示——错误信息是模型的老师。
- 幂等与 dry-run：`--dry-run` 让 Agent 可以先预演再执行，大幅降低破坏性操作的风险。

## 参考

- [anthropics/skills：官方 Skills 仓库](https://github.com/anthropics/skills)
- [Agent Skills 开放规范](https://agentskills.io)
- [Equipping Agents for the Real World with Agent Skills — Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Claude Code Docs：Skills](https://code.claude.com/docs/en/skills)
