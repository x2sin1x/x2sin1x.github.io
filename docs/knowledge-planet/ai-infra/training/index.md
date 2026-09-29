---
title: "训练 / 微调"
date: 2026-09-22T18:00:00+08:00
weight: 7
---

# 训练 / 微调

底座硬件与框架层都认识了，这一章回答：&#8203;**怎么在成百上千张卡上把一个模型的"能力"调出来**&#8203;。从预训练的万亿 token，到后训练的对齐与推理能力，再到资源受限下的参数高效微调与强化学习训练系统，最后是训练框架选型、显存优化与训练 Infra 三篇工程实战。

本章节内容：

1. [预训练](/knowledge-planet/ai-infra/training/pretraining)——scaling law、数据管道与训练循环。
2. [后训练](/knowledge-planet/ai-infra/training/post-training)——SFT、RLHF 与对齐的 Infra 视角。
3. [参数高效微调](/knowledge-planet/ai-infra/training/peft)——LoRA 家族：不动基座，只训增量。
4. [强化学习训练系统](/knowledge-planet/ai-infra/training/rl-systems)——rollout、训练与奖励的三方协作。
5. [训练框架选型](/knowledge-planet/ai-infra/training/training-frameworks)——Megatron、DeepSpeed、FSDP 与 Accelerate 的结构与取舍。
6. [显存优化与 Offload](/knowledge-planet/ai-infra/training/memory-optimization)——显存四要素估算、激活检查点、ZeRO-Offload 与 CPU/NVMe offload。
7. [训练 Infra](/knowledge-planet/ai-infra/training/training-infra)——数据管道、恢复一致性、实验管理与长上下文/多模态挑战。

并行策略（DP/TP/PP/SP/EP 的机制与数学）已独立成[并行策略](/knowledge-planet/ai-infra/parallelism/)章。贯穿本章的分析工具是[芯片架构](/knowledge-planet/ai-infra/hardware/chip-architecture)篇建立的 Roofline 与 $6ND$ 计算量公式：&#8203;**每种显存技巧、每个框架组件，本质上都是在算力、显存、带宽、通信四本账之间找新的平衡点**&#8203;。
