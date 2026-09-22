---
title: "后训练"
date: 2026-09-22T18:00:00+08:00
weight: 20
---

# 后训练

> 预训练教模型"说话"，后训练教它"好好说话"。&#8203;**对齐质量的一半在算法，另一半在 Infra。**

## 后训练的三个阶段

现代后训练流水线（以 InstructGPT/ChatGPT 路线为原型）：

::: mermaid
flowchart LR
    A["基座模型<br/>（预训练产物）"] --> B["SFT 监督微调<br/>（示范数据）"]
    B --> C["奖励模型 RM<br/>（偏好对比数据）"]
    C --> D["RL 优化<br/>（PPO/GRPO）"]
    B --> E["直接对齐<br/>（DPO 等）"]
:::

1. **SFT（监督微调）**&#8203;：用人类示范的"指令→回答"对做监督训练，机制上与[预训练](/knowledge-planet/ai-infra/training/pretraining)同构，只是数据从网页换成了高质量对话，规模从万亿 token 降到百万~千万级；
2. **奖励模型（RM）**&#8203;：训练一个模型给回答打分（通常用偏好对 $A\succ B$ 的成对损失），是 RL 阶段的"裁判"；
3. **RL 优化**&#8203;：让模型生成回答、按 RM 打分更新策略。DPO 等直接对齐方法把 RL 简化为一个监督式的分类损失，省掉在线采样。

## SFT 的 Infra 账

SFT 数据量小（相对预训练三个数量级），但**序列长度方差极大**&#8203;（几十到几万 token），这带来一个经典的效率问题：按条padding 会浪费大量计算。解法是 **packing**&#8203;——把多条样本拼进同一序列（配合 attention mask 隔离），把利用率拉回矩阵乘主导的水平。其余账目与预训练一致（$6ND$、ZeRO、[并行策略](/knowledge-planet/ai-infra/training/parallelism/)），单机到数十卡即可胜任，是后训练里最"便宜"的一段。

## RLHF 的 Infra 难题

RL 阶段同时驻留**四个模型**&#8203;（策略、参考、奖励、价值），且多了在线采样环节：

- **显存**&#8203;：四个模型同台。策略要存优化器状态（[显存公式](/knowledge-planet/ai-infra/hardware/memory-hierarchy)的 $16\Psi$），参考/奖励模型只需推理权重（$2\Psi$ 字节）。PPO 还要一个价值网络（常与 RM 共享底座）；
- **采样与训练的跷跷板**&#8203;：生成（decode，[带宽受限](/knowledge-planet/ai-infra/hardware/chip-architecture)）与训练（计算受限）是两种负载，交替执行时相互等待——这是[强化学习训练系统](/knowledge-planet/ai-infra/training/rl-systems)篇的主题；
- **PPO 目标函数**&#8203;：

$$\mathcal{L}(\theta) = \mathbb{E}\left[\min\left(r_t(\theta)\hat{A}_t,\ \text{clip}(r_t(\theta),1-\epsilon,1+\epsilon)\hat{A}_t\right)\right] - \beta\,\mathbb{E}\big[\mathrm{KL}(\pi_\theta\Vert\pi_{\text{ref}})\big]$$

  其中 $r_t(\theta)=\pi_\theta(a_t\mid s_t)/\pi_{\text{old}}(a_t\mid s_t)$ 是重要性比率，KL 项把策略拴在参考模型附近防止"胡言乱语换高分"。&#8203;**每个 KL 项都要求对参考模型做一次前向**&#8203;——这就是显存账里参考模型的用途。

## DPO：把 RL 变成监督

DPO 从 PPO 目标函数的闭式解出发，把 RLHF 问题改写为对偏好对的直接分类损失：

$$\mathcal{L}_{\text{DPO}} = -\mathbb{E}\left[\log\sigma\left(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\text{ref}}(y_w\mid x)} - \beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\text{ref}}(y_l\mid x)}\right)\right]$$

Infra 视角：&#8203;**没有在线采样、没有独立奖励模型**&#8203;，只需策略与参考的前向/反向——负载形态退化为 SFT 级别，Infra 成本骤降。代价是对离线数据的隐式依赖（分布外泛化弱于在线 RL），因此前沿实验室仍然保留 PPO/GRPO 在线流程。

::: details 深入推导：DPO 的闭式来源与 KL 预算

RLHF 的原始目标 $\max_\pi\ \mathbb{E}_{x,y\sim\pi}[r(x,y)] - \beta\,\mathrm{KL}(\pi\Vert\pi_{\text{ref}})$ 有解析解：

$$\pi^*(y\mid x) = \frac{1}{Z(x)}\pi_{\text{ref}}(y\mid x)\exp\left(\frac{1}{\beta}r(x,y)\right)$$

反解奖励 $r(x,y)=\beta\log\frac{\pi^*(y\mid x)}{\pi_{\text{ref}}(y\mid x)}+\beta\log Z(x)$，代入 Bradley-Terry 偏好模型 $p(y_w\succ y_l)=\sigma(r(x,y_w)-r(x,y_l))$，配分函数 $Z(x)$ 在成对相减时消去，得到 DPO 损失。&#8203;**推导告诉我们两件事**&#8203;：偏好对的相对奖励差才是有效信号；超参 $\beta$ 同时控制偏离参考模型的 KL 预算，Infra 上对应"参考模型前向的频次与权重"。

GRPO（DeepSeekMath）进一步去掉价值网络：对同一 prompt 采样 $G$ 个回答，用组内奖励归一化 $\hat{A}_i=(r_i-\bar r)/\text{std}(r)$ 作优势——&#8203;**用采样换价值模型**&#8203;，每次更新的显存与计算都省一截，这正是 DeepSeek 系列选择 GRPO 的 Infra 动机。

（据 Ouyang et al. 2022、Rafailov et al. 2023、Shao et al. 2024。）

:::

## 思考题

1. 一个 70B 模型做 PPO：策略（训练态）、参考、奖励三个模型各占多少显存（BF16，忽略激活与优化器差异）？需要几张 80 GB 卡？
2. SFT 的 packing 为什么需要 attention mask 配合？不加会发生什么？
3. DPO 相比 PPO 省掉了哪些 Infra 组件？什么场景下这些省略会变成劣势？

::: details 参考答案

1. 策略训练态 $(2+2+12)\Psi=1.12\ \text{TB}$；参考 $2\Psi=140\ \text{GB}$；奖励 $140\ \text{GB}$；合计约 $1.4\ \text{TB}\to$ 至少 18 张 80 GB 卡，实际考虑激活需 32 卡以上。
2. packing 把多条独立样本拼成一个序列，mask 防止位置 $i$ 的 token 注意到其他样本的 token。不加会"串味"：模型在无关样本间建立虚假注意力连接，训练信号被污染。
3. 省掉：在线 rollout 引擎、独立奖励模型服务、价值网络、采样与训练的调度协调。劣势场景：策略分布漂移大的任务（推理类长链条任务），离线偏好数据覆盖不了新分布，此时在线 RL 的探索不可替代（DeepSeek-R1 式推理训练仍用在线 RL）。

:::

## 小结

- 后训练 = SFT（监督）→ RM（裁判）→ RL（优化），DPO 把后两步折叠成一个监督损失。
- SFT 的效率关键是 packing + mask，对付序列长度方差。
- RLHF 的 Infra 核心矛盾：四模型驻留的显存账 + 采样与训练的负载切换，KL 约束的每次前向都是真实成本。
- GRPO 用组内采样换掉价值网络，是"算法选择受 Infra 约束塑造"的范例。

## 参考资料

- Ouyang et al., [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155)（InstructGPT，arXiv 2203.02155）
- Rafailov et al., [Direct Preference Optimization](https://arxiv.org/abs/2305.18290)（DPO，arXiv 2305.18290）
- Shao et al., [DeepSeekMath](https://arxiv.org/abs/2402.03300)（GRPO，arXiv 2402.03300）
- Schulman et al., [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347)（PPO，arXiv 1707.06347）
- DeepSeek-AI, [DeepSeek-R1](https://arxiv.org/abs/2501.12948)（arXiv 2501.12948）
