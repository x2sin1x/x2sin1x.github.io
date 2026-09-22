---
title: "AI Infra"
weight: 107
---

# AI Infra

从一颗芯片到一个集群、从一次训练到一次推理服务，用数量级估算理解大模型基础设施的每一层设计。

## 板块一：算力、存储与网络

- [芯片架构：算力、显存与带宽](/knowledge-planet/ai-infra/hardware/chip-architecture)
- [显存层次与存储](/knowledge-planet/ai-infra/hardware/memory-hierarchy)
- [超节点](/knowledge-planet/ai-infra/hardware/supernode)
- [万卡集群](/knowledge-planet/ai-infra/hardware/large-scale-cluster)
- [容错与 Checkpoint](/knowledge-planet/ai-infra/hardware/fault-tolerance)
- [集合通信](/knowledge-planet/ai-infra/hardware/collective-communication)

## 板块二：训练 / 微调

- [预训练](/knowledge-planet/ai-infra/training/pretraining)
- [后训练](/knowledge-planet/ai-infra/training/post-training)
- [参数高效微调](/knowledge-planet/ai-infra/training/peft)
- [强化学习训练系统](/knowledge-planet/ai-infra/training/rl-systems)
- 并行策略
    - [数据并行](/knowledge-planet/ai-infra/training/parallelism/data-parallelism)
    - [张量并行](/knowledge-planet/ai-infra/training/parallelism/tensor-parallelism)
    - [流水并行](/knowledge-planet/ai-infra/training/parallelism/pipeline-parallelism)
    - [序列并行](/knowledge-planet/ai-infra/training/parallelism/sequence-parallelism)
    - [专家并行](/knowledge-planet/ai-infra/training/parallelism/expert-parallelism)

## 板块三：推理 / 服务

- [KV Cache](/knowledge-planet/ai-infra/inference/kv-cache)
- [Continuous Batching](/knowledge-planet/ai-infra/inference/continuous-batching)
- [请求调度](/knowledge-planet/ai-infra/inference/request-scheduling)
- [Chunked Prefill](/knowledge-planet/ai-infra/inference/chunked-prefill)
- [Prefix Caching](/knowledge-planet/ai-infra/inference/prefix-caching)
- [量化](/knowledge-planet/ai-infra/inference/quantization)
- [投机采样](/knowledge-planet/ai-infra/inference/speculative-decoding)
- [P/D 分离](/knowledge-planet/ai-infra/inference/pd-disaggregation)
- [A/F 分离](/knowledge-planet/ai-infra/inference/af-disaggregation)

## 板块四：Profiling 性能分析

- [性能指标](/knowledge-planet/ai-infra/profiling/metrics)
- [性能分析工具](/knowledge-planet/ai-infra/profiling/tools)
