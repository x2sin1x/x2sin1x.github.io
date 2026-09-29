---
title: "训练框架选型：Megatron、DeepSpeed 与 FSDP"
date: 2026-09-29T10:30:00+08:00
weight: 50
---

# 训练框架选型：Megatron、DeepSpeed 与 FSDP

> [并行策略](/knowledge-planet/ai-infra/parallelism/)章讲了切法的数学，本篇讲承载切法的框架：**Megatron（极致性能）、DeepSpeed（易用与 offload）、FSDP（PyTorch 原生）** 的代码结构与选型逻辑。

## Megatron-LM：性能上限的代名词

NVIDIA 的 Megatron-LM 是大模型训练框架的性能标杆，代码结构对应其分层并行模型（题库 146）：

- `megatron/core`：与训练策略无关的模型与并行原语——`tensor_parallel/`（column/row parallel 层，见[张量并行](/knowledge-planet/ai-infra/parallelism/tensor-parallelism)篇）、`pipeline_parallel/`（1F1B/interleaved 调度，见[流水并行]篇）、`optimizer/`（分布式优化器，参数与状态按并行组切分）。
- `pretrain_*.py`：任务侧入口，把模型、数据、并行配置拼装成训练循环。

工程特点：**3D/5D 并行的一等公民**（TP×PP×DP×SP×EP 的组合调优最深）、通信与计算重叠做得最细、大集群 MFU 一贯领先。代价是绑定 NVIDIA 生态较深、配置复杂、门槛高——千卡以上预训练的事实标准。

## DeepSpeed：ZeRO 与 offload 的工程化

DeepSpeed 的核心资产是 **ZeRO**（见[数据并行](/knowledge-planet/ai-infra/parallelism/data-parallelism)篇的 1/2/3 级切分）与 **offload 家族**：

- **ZeRO-Offload**（题库 076）：把优化器状态与梯度 offload 到 CPU 内存——FP32 优化器状态 + FP32 梯度副本在 CPU 上做更新，GPU 只保留 BF16 权重与前向激活。带宽账：CPU↔GPU PCIe 约 32–64 GB/s，而优化器状态每步只需读写一次，用计算换显存是划算的。
- **ZeRO-Infinity / NVMe offload**（题库 077）：进一步把优化器状态和参数 offload 到 NVMe（约 3–7 GB/s per 盘），配合**参数预取**（下一层参数在计算上一层时提前搬到 GPU）与**计算重叠**，让"单卡训大模型"成为可能。代价：吞吐显著下降，适合资源受限场景而非产能场景。

Megatron 与 DeepSpeed 有官方融合版（Megatron-DeepSpeed），ZeRO 数据并行 + Megatron 模型并行的组合曾是主流配方，如今 NVIDIA 主推自己的 Megatron 全家桶 + FSDP 式 HSDP。

## FSDP / FSDP2：PyTorch 原生方案

`torch.distributed.fsdp`（fully sharded data parallel）本质是 ZeRO-3 的原生实现：参数按 DP 组切分，前向/反向时 **all-gather 取回当前层参数、用完即弃**。关键配置（题库 048–049/151）：

- **sharding_strategy**：`FULL_SHARD`（参数+梯度+优化器状态全切，ZeRO-3）到 `SHARD_GRAD_OP`（只切梯度+状态，ZeRO-2）之间取平衡——切得越狠通信越多。
- **auto_wrap_policy**：按层粒度套 FSDP 包装，切分粒度决定 all-gather 的频次与显存峰值（细粒度省显存、通信次数多）。
- **limit_all_gathers**：限制 in-flight 的预取 all-gather 数量，防止预取把显存提前吃满。

FSDP2（per-parameter DTensor 版）改善了与 TP/mixed precision 的组合。**FSDP 的生态位**：不想引入重型框架、模型在几百亿以内、需要快速实验的团队；以及 **HSDP/多机分组**（机内 shard + 机间 replicate/aggregate）这类现代混合并行。

## 选型决策

| 场景 | 推荐 | 理由 |
| ---- | ---- | ---- |
| 千卡以上预训练 | Megatron(+DeepSpeed 特性) | 3D 并行成熟度、MFU 上限 |
| 百亿内微调/中型训练 | FSDP2 + torch.compile | 原生、简单、生态顺滑 |
| 单机/少卡 + 大模型、科研验证 | DeepSpeed ZeRO-3-Offload | offload 优先保"能跑" |
| MoE/超大规模混合并行 | Megatron core + 自研调度 | EP/5D 并行的工程深度 |

另外两条支线：**HuggingFace Accelerate** 不是并行策略而是"配置分发器"——把 DDP/FSDP/DeepSpeed 的样板代码（设备放置、wrap、launch）统一成薄封装（题库 150），选它选的是开发体验；**Colossal-AI 的 Gemini / PatrickStar**（题库 148）探索的是异构内存的自动分层放置（热参数留 GPU、温冷下沉 CPU），思想与 ZeRO-Infinity 同源但放置策略更动态。

## 小结

- 框架选型的第一分叉是**产能 vs 能跑**：Megatron 求上限，DeepSpeed offload 求下限兜底，FSDP 求生态顺滑。
- ZeRO 家族的统一逻辑：把状态沿"优化器状态→梯度→参数"逐级切分/offload，每进一步用更多通信或更慢的存储换显存。
- FSDP = 原生 ZeRO-3，sharding 策略与 wrap 粒度是仅有的两个关键旋钮。
- Accelerate 类封装器不解决并行问题，只解决配置分发；异构内存自动放置是 Colossal-AI 一线的差异点。

## 思考题

1. ZeRO-2 与 FSDP 的 `SHARD_GRAD_OP` 有何对应关系？各自的通信模式是什么？
2. ZeRO-Offload 把优化器更新放 CPU，为什么更新过程不怕 CPU 慢？
3. auto_wrap_policy 切分粒度太细会怎样？给出一个每层通信量的估算式。

::: details 参考答案

1. 对应 ZeRO-2：两者都切梯度与优化器状态、保留完整参数。通信都是 reduce-scatter（梯度）+ 参数 all-gather……ZeRO-2 不需要 all-gather（参数不切），FSDP SHARD_GRAD_OP 也不 all-gather 参数——严格对应，通信同源。
2. 优化器更新是每步一次的批量操作且计算强度高（对每个状态字节做多次运算），CPU 的 GFLOPS 足够；真正的约束是 PCIe 带宽，而那笔账已经算过：每步只搬一次状态。
3. 切太细 → all-gather/reduce-scatter 次数暴涨，每次通信的固定延迟（launch、同步）无法被消息量摊薄。估算：单层切分粒度 $g$ 参数 → 每层每步 $2\times$ all-gather $g$ 字节（前向+反向重取）+ reduce-scatter $g$ 字节；频次 $\propto$ 层数×切分数。

:::

## 参考资料

- NVIDIA/Microsoft, [Megatron-LM](https://github.com/NVIDIA/Megatron-LM) 与 [DeepSpeed](https://github.com/microsoft/DeepSpeed) 官方文档
- PyTorch, [FSDP 入门与 Advanced tutorials](https://pytorch.org/tutorials/intermediate/FSDP_tutorial.html)
- Rasley et al., [DeepSpeed: System Optimizations Enable Training Deep Learning Models with Over 100 Billion Parameters](https://dl.acm.org/doi/10.1145/3394486.3406703)（KDD 2020）；Rajbhandari et al., [ZeRO-Infinity](https://arxiv.org/abs/2104.07857)

