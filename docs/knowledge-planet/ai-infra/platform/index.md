---
title: "平台与调度"
date: 2026-09-29T10:00:00+08:00
weight: 11
---

# 平台与调度

[分布式系统](/knowledge-planet/ai-infra/distributed/)章回答了"机器怎么组成一台计算机"，本章回答"任务怎么用好这台计算机"：谁先谁后（调度）、谁用多少（配额与多租户）、坏了怎么办（平台级容灾）、花多少钱（成本核算）。这也是面试中区分度最高的一类题——开放式的系统设计。

本章节内容：

1. [集群调度](/knowledge-planet/ai-infra/platform/cluster-scheduling)——Slurm 与 Kubernetes、gang scheduling、拓扑感知调度与 GPU 分配。
2. [训练平台设计](/knowledge-planet/ai-infra/platform/training-platform)——设计一个 1000 卡训练平台：组件、隔离、成本与可观测。
3. [推理服务设计](/knowledge-planet/ai-infra/platform/inference-serving)——设计一个 10 万 QPS 推理服务：扩缩容、路由、SLO 与准入控制。

阅读前提：[集群调度]依赖[万卡集群](/knowledge-planet/ai-infra/distributed/large-scale-cluster)章的组网与故障认知；推理服务的单机机制（batching、调度、KV Cache）见[推理引擎](/knowledge-planet/ai-infra/inference/)章——平台章只讲这些机制之上的一层。
