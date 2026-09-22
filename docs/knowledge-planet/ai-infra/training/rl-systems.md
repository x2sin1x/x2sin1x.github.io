---
title: "强化学习训练系统"
date: 2026-09-22T18:00:00+08:00
weight: 40
---

# 强化学习训练系统

> RLHF 之后，RL 训练从"算法问题"变成了"系统问题"。&#8203;**谁能把 rollout、训练、奖励组织得高效，谁就能训出更强的模型。**

## RL 训练的特殊负载形态

与[后训练](/knowledge-planet/ai-infra/training/post-training)篇的 PPO 流程对照，一个在线 RL 迭代包含三类异构负载：

::: mermaid
flowchart LR
    P["策略模型<br/>（权重）"] -- "1. 同步权重" --> R["Rollout 引擎<br/>（生成样本，decode 型）"]
    R -- "2. 样本" --> V["奖励/验证<br/>（打分，前向型）"]
    V -- "3. 轨迹+奖励" --> T["训练器<br/>（更新权重，计算型）"]
    T -- "4. 新权重" --> P
:::

- **Rollout（生成）**&#8203;：纯 decode，[带宽受限](/knowledge-planet/ai-infra/hardware/chip-architecture)，要大 batch 与 KV Cache 管理——就是推理服务的负载；
- **奖励/验证**&#8203;：奖励模型或可验证奖励（代码执行、数学验算）的前向，验证器甚至是 CPU 集群（跑代码沙箱）；
- **训练**&#8203;：前向+反向+优化器，计算受限。

三类负载轮转执行，&#8203;**任何一段在等，全集群都在烧钱**&#8203;。RL 训练系统的设计目标只有一个：让这三段尽量并行、尽量不互相等。

## 核心机制：权重与样本的流转

RL 训练与普通分布式训练的本质区别是**权重生产者（训练器）与权重消费者（rollout 引擎）分离**&#8203;。关键工程决策：

1. **同构部署**&#8203;（早期 verl/OpenRLHF 默认）：rollout 和训练用同一组卡、同一框架，训练完把权重在卡间传递给推理引擎（如 vLLM）。省机器，但生成与训练只能串行，切换时还要做权重重分发；
2. **异构分离**&#8203;（训练用 GPU、rollout 也用 GPU 但独立成池，或奖励用 CPU 集群）：两池交替工作，可以做**异步 RL**&#8203;——rollout 池基于旧权重持续生成，训练池消费样本流。代价是策略陈旧度（staleness）上升，需要重要性采样修正或限制异步深度。

## 一张图看懂 HybridFlow

verl（字节 HybridFlow 论文）把上述组织抽象为**控制器 + 资源池**&#8203;：每个角色（Actor/Critic/Rollout/Reward）是一个 worker 组，编程模型负责在它们之间搬运权重与样本，三段可以灵活绑定或分离部署。

## 数量级：为什么 rollout 是大头

设生成 1 个样本平均 512 token、训练一步需要 $B=1024$ 个样本：

- 生成 FLOPs：$B\times 512\times 2\Psi$（decode 每token 2 FLOP/参数）$= 1024\times512\times2\Psi\approx10^6\Psi$；
- 训练 FLOPs：$B\times512\times6\Psi\approx3\times10^6\Psi$。

计算量训练是生成的 3 倍，&#8203;**但 decode 是带宽受限**&#8203;：按[芯片架构](/knowledge-planet/ai-infra/hardware/chip-architecture)篇的 roofline，大 batch 生成可达 50~70% 利用率，所以两者时间量级接近——&#8203;**rollout 与训练几乎各占一半墙钟时间**&#8203;。任何让它们串行的调度（如生成完再训练再生成）都意味着一半资源在空转。

::: details 深入推导：异步深度与 off-policy 修正

设训练器每消费一批样本更新一次权重，rollout 池滞后 $k$ 个版本生成（异步深度 $k$）。样本由 $\pi_{\theta_{\text{old}}}$ 生成而目标策略为 $\pi_{\theta}$，梯度估计有偏。修正方式是重要性加权：

$$\nabla_\theta J \approx \mathbb{E}_{a\sim\pi_{\text{old}}}\left[\frac{\pi_\theta(a\mid s)}{\pi_{\text{old}}(a\mid s)}\nabla_\theta \log\pi_\theta(a\mid s)\,\hat A\right]$$

比率随 KL（约 $O(k\cdot\beta)$）增大而方差爆炸。实践约束：PPO 截断 $\epsilon=0.2$ 隐式容忍的比率偏离有限，因此异步深度通常限制在 $k\le2\sim4$，或对过长 KL 的样本直接丢弃。&#8203;**异步 RL 的调度本质是"新鲜度-吞吐"折中**&#8203;：verl、OpenRLHF 均提供 0（同步）到有限 $k$ 的档位。

**可验证奖励（RLVR）的 Infra 意义**&#8203;：数学答案验算、代码单元测试等奖励不依赖奖励模型，验证器是 CPU 沙箱集群——与 GPU 池天然解耦，可完全并行且无陈旧性问题。DeepSeek-R1 证明这类奖励可以撑起大规模推理训练，也让"验证器即服务"成为 RL Infra 的新组件。

（据 Sheng et al. 2024 HybridFlow、Hu et al. 2024 OpenRLHF、DeepSeek-AI 2025。）

:::

## 思考题

1. rollout 池与训练池各 256 张卡、单步轮转中生成占 45%、训练占 50%、权重同步占 5%：完全同步执行时集群利用率的上限是多少？
2. 为什么可验证奖励的 RL（数学/代码）比奖励模型 RL 更适合大扩展？
3. 权重重分发（训练器 → rollout 引擎）在什么部署模式下可以完全消除？

::: details 参考答案

1. 串行时总时长 100%，任意时刻只有一类卡在忙：利用率为 $0.45+0.5=95\%$？不对——两池各自看：训练池在生成阶段闲置（占 45%+5%），rollout 池在训练阶段闲置（占 50%+5%）。整体等效利用率 $\approx(0.45\times0.5+0.5\times0.5)\times2/1$……直接算：理想（两池各自满转且流水）墙钟 $\max(0.45,0.5)+\text{同步} \approx 0.55$，串行墙钟 1.0，故串行等效利用率约 55%，流水化后可近 95%。&#8203;**分离部署的收益正是这 40 个百分点**&#8203;。
2. 奖励模型有"天花板"：它本身是学习出来的代理，超过其判别能力的样本无法给分，且易被 reward hacking 攻击；可验证奖励与任务真值对齐，验证器还能水平扩容（CPU 沙箱加机器即可），奖励吞吐不再卡 GPU。
3. 同构共存 + 权重原地共享（训练器与引擎在同一卡上换指针/改张量，verl 的 hybrid engine 思路）——此时"分发"退化为框架内的张量重绑，代价是两负载必须串行分时复用同一组卡。

:::

## 小结

- RL 训练系统 = rollout（推理负载）+ 训练（训练负载）+ 奖励/验证（前向或 CPU 负载）的流水线编排。
- rollout 与训练时间量级相当，串行调度浪费近一半算力；分离 + 有限异步（$k\le2\sim4$）是主流解。
- 异步引入 off-policy 偏差，重要性采样修正与 KL 约束共同框定异步深度。
- 可验证奖励把验证器变成可水平扩展的 CPU 服务，是 RL Infra 的关键新组件。

## 参考资料

- Sheng et al., [HybridFlow: A Flexible and Efficient RLHF Framework](https://arxiv.org/abs/2409.19256)（verl，arXiv 2409.19256）
- Hu et al., [OpenRLHF: An Easy-to-use, Scalable and High-performance RLHF Framework](https://arxiv.org/abs/2405.11143)（arXiv 2405.11143）
- DeepSeek-AI, [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via RL](https://arxiv.org/abs/2501.12948)（arXiv 2501.12948）
- Shao et al., [DeepSeekMath](https://arxiv.org/abs/2402.03300)（GRPO，arXiv 2402.03300）
- verl 项目，[GitHub](https://github.com/volcengine/verl)；OpenRLHF 项目，[GitHub](https://github.com/OpenRLHF/OpenRLHF)
