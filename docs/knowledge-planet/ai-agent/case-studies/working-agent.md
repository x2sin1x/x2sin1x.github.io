---
title: "Working Agent"
date: 2026-09-22T17:00:00+08:00
weight: 122
---

# Working Agent

> Coding Agent 住在仓库里，Working Agent 住在你身边：聊天软件里回复消息、桌面上操作应用、日程里安排事务。开放环境没有测试套件替它兜底。

## 与 Coding Agent 的本质差异

| 维度 | Coding Agent | Working Agent |
| ---- | ---- | ---- |
| 工作环境 | 代码仓库、终端（结构化） | 聊天渠道、GUI、网页（开放） |
| 操作方式 | 文件与命令 | 浏览器/桌面自动化、API、消息 |
| 结果验证 | 编译、测试（机器可判） | 用户满意（只有人能判） |
| 失败代价 | git 回滚，几可忽略 | 发错消息、订错票，真实外溢 |
| 上下文重心 | 代码与任务 | 长期偏好、人际关系、历史事务 |

环境决定了工程重心完全不同：Coding Agent 的难点在 Harness 与验证闭环，Working Agent 的难点在**感知、记忆与安全**。

## 代表产品：OpenClaw

OpenClaw（开源，前身经历 Clawdbot/Moltbot 的更名）是目前最有代表性的个人助理 Agent：运行在用户自己的设备上，接入 Discord、iMessage、Telegram、WhatsApp 等 20 多个聊天渠道，加上 macOS/iOS/Android 等原生应用。它的几个架构决策很有教学价值：

- **数据主权**：状态、记忆、凭证全部留在用户自己的硬件上，Gateway 架构把“可信网关”与“不可信执行”分开。
- **模型可插拔**：Claude、Codex、本地模型都是插件——又一次印证 Harness 与模型解耦的设计。
- **渠道即界面**：用户不需要新 App，Agent 出现在既有聊天软件里。这极大降低了使用门槛，也放大了安全责任（下述）。

WorkBuddy 一类产品走的是企业内部助理路线：接入办公套件、审批流、知识库，验证方式从“用户主观满意”部分转向“业务规则可判”。

## 三大工程挑战

### 1. 感知：GUI 是给人类的

浏览器和桌面应用没有为 Agent 准备接口。感知依赖多模态截图理解（看懂按钮与状态）与 DOM/无障碍树解析（拿到结构化元素）。前者通用但 token 昂贵，后者精确但脆弱——多数 Working Agent 两条腿走路。

### 2. 记忆：助理的价值在“认识你”

“帮我像上次那样订”依赖对上次的记忆；“用户不吃辣”依赖长期偏好积累。Working Agent 的记忆系统（见“用户记忆与知识库”一章）承担远比 Coding Agent 更重的角色：情景记忆（办过的事）、语义记忆（用户画像）、程序记忆（个人事务的处理流程）都要持续维护，且要处理过时与冲突。

### 3. 安全：外溢操作是常态

发消息、转账、代订，每一个动作都是不可回滚的真实世界影响。Working Agent 的权限设计必须比 Coding Agent 保守得多：

- 消息发送、支付类操作默认人工确认，且确认信息要展示“将以谁的身份、对谁、做什么”。
- 凭证管理是重灾区：接入 20 个平台意味着 20 份凭证，必须集中保管、最小授权、绝不进上下文。
- 提示注入的攻击面横跨所有渠道——任何一条收到的消息都是注入载体（见“安全与权限”一章）。

## 参考

- [OpenClaw](https://github.com/openclaw/openclaw)
- [OpenClaw Docs：Why OpenClaw（架构与安全设计）](https://docs.openclaw.ai/start/why-openclaw)
- [Building Effective Agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
