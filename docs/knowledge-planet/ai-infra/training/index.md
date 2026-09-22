---
title: "训练 / 微调"
date: 2026-09-22T18:00:00+08:00
weight: 1
---

# 训练 / 微调

底座硬件认识了，这一板块回答：&#8203;**怎么在成百上千张卡上把一个模型的"能力"调出来**&#8203;。从预训练的万亿 token，到后训练的对齐与推理能力，再到资源受限下的参数高效微调，最后是大模型时代最重要的训练形态——强化学习训练系统。

本板块内容：

1. [预训练](/knowledge-planet/ai-infra/training/pretraining)——scaling law、数据管道与训练循环。
2. [后训练](/knowledge-planet/ai-infra/training/post-training)——SFT、RLHF 与对齐的 Infra 视角。
3. [参数高效微调](/knowledge-planet/ai-infra/training/peft)——LoRA 家族：不动基座，只训增量。
4. [强化学习训练系统](/knowledge-planet/ai-infra/training/rl-systems)——rollout、训练与奖励的三方协作。
5. [并行策略](/knowledge-planet/ai-infra/training/parallelism/)——数据并行、张量并行、流水并行、序列并行、专家并行，以及它们为什么如此组合。

贯穿本板块的分析工具是[芯片架构](/knowledge-planet/ai-infra/hardware/)篇建立的 Roofline 与 $6ND$ 计算量公式：&#8203;**每种并行策略、每种显存技巧，本质上都是在算力、显存、带宽、通信四本账之间找新的平衡点**&#8203;。
