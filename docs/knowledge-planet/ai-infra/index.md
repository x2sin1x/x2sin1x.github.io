---
title: "AI Infra"
weight: 107
---

# AI Infra

从一颗芯片到一个集群、从一次训练到一次推理服务，用数量级估算理解大模型基础设施的每一层设计。

本教程按"**从物理层到系统层、从训练到服务**"组织为十二章：前四章讲硬件与分布式底座（一颗芯片、一堆芯片、连接它们的网络、跑在卡上的高性能代码），中间四章讲训练主线（框架、编译、并行、训练系统），随后是量化压缩进入推理服务的主线，最后是支撑系统与性能分析收官。

## 第一章：硬件架构

- [芯片架构：算力、显存与带宽](/knowledge-planet/ai-infra/hardware/chip-architecture)
- [显存层次与存储](/knowledge-planet/ai-infra/hardware/memory-hierarchy)

## 第二章：分布式系统

- [集合通信](/knowledge-planet/ai-infra/distributed/collective-communication)
- [超节点](/knowledge-planet/ai-infra/distributed/supernode)
- [万卡集群](/knowledge-planet/ai-infra/distributed/large-scale-cluster)
- [容错与 Checkpoint](/knowledge-planet/ai-infra/distributed/fault-tolerance)

## 第三章：网络与通信

- [RDMA 与高性能网络](/knowledge-planet/ai-infra/network/rdma-highspeed-network)
- [NCCL 与通信优化](/knowledge-planet/ai-infra/network/nccl-tuning)

## 第四章：高性能计算

- [CUDA 编程模型](/knowledge-planet/ai-infra/hpc/cuda-programming)
- [算子优化与融合](/knowledge-planet/ai-infra/hpc/operator-optimization)
- [Attention Kernel：FlashAttention 与它的后继者](/knowledge-planet/ai-infra/hpc/attention-kernels)

## 第五章：框架与编译

- [PyTorch 内部机制](/knowledge-planet/ai-infra/framework/pytorch-internals)
- [torch.compile：Dynamo → Inductor → Triton](/knowledge-planet/ai-infra/framework/torch-compile)
- [AI 编译器：XLA、TVM、MLIR 与 TensorRT](/knowledge-planet/ai-infra/framework/compilers)

## 第六章：并行策略

- [数据并行](/knowledge-planet/ai-infra/parallelism/data-parallelism)
- [张量并行](/knowledge-planet/ai-infra/parallelism/tensor-parallelism)
- [流水并行](/knowledge-planet/ai-infra/parallelism/pipeline-parallelism)
- [序列并行](/knowledge-planet/ai-infra/parallelism/sequence-parallelism)
- [专家并行](/knowledge-planet/ai-infra/parallelism/expert-parallelism)

## 第七章：训练框架

- [预训练](/knowledge-planet/ai-infra/training/pretraining)
- [后训练](/knowledge-planet/ai-infra/training/post-training)
- [参数高效微调](/knowledge-planet/ai-infra/training/peft)
- [强化学习训练系统](/knowledge-planet/ai-infra/training/rl-systems)
- [训练框架选型：Megatron、DeepSpeed 与 FSDP](/knowledge-planet/ai-infra/training/training-frameworks)
- [显存优化与 Offload](/knowledge-planet/ai-infra/training/memory-optimization)
- [训练 Infra：数据管道、恢复与实验管理](/knowledge-planet/ai-infra/training/training-infra)

## 第八章：量化与稀疏

- [量化基础](/knowledge-planet/ai-infra/quantization/quantization-basics)
- [主流量化方法：GPTQ、AWQ 与 SmoothQuant](/knowledge-planet/ai-infra/quantization/quantization-methods)
- [蒸馏、剪枝与稀疏化](/knowledge-planet/ai-infra/quantization/compression)

## 第九章：推理引擎

- [KV Cache](/knowledge-planet/ai-infra/inference/kv-cache)
- [Continuous Batching](/knowledge-planet/ai-infra/inference/continuous-batching)
- [请求调度](/knowledge-planet/ai-infra/inference/request-scheduling)
- [Chunked Prefill](/knowledge-planet/ai-infra/inference/chunked-prefill)
- [Prefix Caching](/knowledge-planet/ai-infra/inference/prefix-caching)
- [投机采样](/knowledge-planet/ai-infra/inference/speculative-decoding)
- [P/D 分离](/knowledge-planet/ai-infra/inference/pd-disaggregation)
- [A/F 分离](/knowledge-planet/ai-infra/inference/af-disaggregation)
- [推理引擎版图](/knowledge-planet/ai-infra/inference/engine-landscape)

## 第十章：存储与 I/O

- [Checkpoint 存储与加载](/knowledge-planet/ai-infra/storage/checkpoint-storage)
- [数据管道与存储选型](/knowledge-planet/ai-infra/storage/data-pipeline)

## 第十一章：平台与调度

- [集群调度](/knowledge-planet/ai-infra/platform/cluster-scheduling)
- [训练平台设计](/knowledge-planet/ai-infra/platform/training-platform)
- [推理服务设计](/knowledge-planet/ai-infra/platform/inference-serving)

## 第十二章：Profiling 性能分析

- [性能指标](/knowledge-planet/ai-infra/profiling/metrics)
- [性能分析工具](/knowledge-planet/ai-infra/profiling/tools)
- [负载特征与性能归因](/knowledge-planet/ai-infra/profiling/workload-analysis)

## 与 305 题面经的对照

本教程同时覆盖 [AI Infra 305 题面经](https://riddlego.github.io/ai-infra-interview-305/study.html)的 23 个模块，对照如下：

| 题库模块（题号） | 对应章节 |
| ---- | ---- |
| PyTorch 底层（1–15） | 第五章 [PyTorch 内部机制](/knowledge-planet/ai-infra/framework/pytorch-internals) |
| TensorFlow 与 XLA（16–20） | 第五章 [AI 编译器](/knowledge-planet/ai-infra/framework/compilers) |
| 自定义算子开发（21–30） | 第四章 [算子优化与融合](/knowledge-planet/ai-infra/hpc/operator-optimization) |
| 编译器优化（31–45） | 第五章 [AI 编译器](/knowledge-planet/ai-infra/framework/compilers) |
| 数据并行（46–60） | 第六章 [数据并行](/knowledge-planet/ai-infra/parallelism/data-parallelism) |
| 模型并行与流水线（61–75） | 第六章 [张量并行](/knowledge-planet/ai-infra/parallelism/tensor-parallelism)、[流水并行](/knowledge-planet/ai-infra/parallelism/pipeline-parallelism) |
| 显存优化与 Offload（76–85） | 第七章 [显存优化与 Offload](/knowledge-planet/ai-infra/training/memory-optimization) |
| 通信优化（86–95） | 第三章 [NCCL 与通信优化](/knowledge-planet/ai-infra/network/nccl-tuning) |
| 推理引擎（96–115） | 第九章 [推理引擎版图](/knowledge-planet/ai-infra/inference/engine-landscape) 及各机制篇 |
| 量化与压缩（116–130） | 第八章 [量化基础](/knowledge-planet/ai-infra/quantization/quantization-basics)、[主流量化方法](/knowledge-planet/ai-infra/quantization/quantization-methods)、[蒸馏剪枝稀疏](/knowledge-planet/ai-infra/quantization/compression) |
| 服务化与调度（131–145） | 第十一章 [推理服务设计](/knowledge-planet/ai-infra/platform/inference-serving) |
| 训练框架（146–160） | 第七章 [训练框架选型](/knowledge-planet/ai-infra/training/training-frameworks)、[训练 Infra](/knowledge-planet/ai-infra/training/training-infra) |
| 存储与 IO（161–170） | 第十章 [存储与 I/O](/knowledge-planet/ai-infra/storage/) |
| 集群调度（171–180） | 第十一章 [集群调度](/knowledge-planet/ai-infra/platform/cluster-scheduling) |
| 性能分析工具（181–195） | 第十二章 [Profiling](/knowledge-planet/ai-infra/profiling/) |
| 优化技术（196–215） | 第四章 [Attention Kernel](/knowledge-planet/ai-infra/hpc/attention-kernels)、第六章并行策略、第七章显存优化 |
| 训练平台设计（216–235） | 第十一章 [训练平台设计](/knowledge-planet/ai-infra/platform/training-platform) |
| 推理平台设计（236–255） | 第十一章 [推理服务设计](/knowledge-planet/ai-infra/platform/inference-serving) |
| C++/CUDA 编程（256–270） | 第四章 [CUDA 编程模型](/knowledge-planet/ai-infra/hpc/cuda-programming) |
| Python 高级（271–280） | 第五章 [PyTorch 内部机制](/knowledge-planet/ai-infra/framework/pytorch-internals)、[训练 Infra](/knowledge-planet/ai-infra/training/training-infra) 中按需展开 |
| 算法与数据结构（281–290） | 第十一章 [推理服务设计](/knowledge-planet/ai-infra/platform/inference-serving)（LRU/限流）、[存储与 I/O](/knowledge-planet/ai-infra/storage/)（哈希/索引）中按需展开 |
| 网络（291–300） | 第三章 [RDMA 与高性能网络](/knowledge-planet/ai-infra/network/rdma-highspeed-network) |
| 存储与虚拟化（301–305） | 第十一章 [集群调度](/knowledge-planet/ai-infra/platform/cluster-scheduling) |
