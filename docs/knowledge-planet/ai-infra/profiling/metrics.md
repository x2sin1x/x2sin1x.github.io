---
title: "性能指标"
date: 2026-09-22T18:00:00+08:00
weight: 10
---

# 性能指标

> 指标是优化的语言。&#8203;**选错指标，优化就是自欺欺人。**

## 训练侧：MFU 与它的分解

**MFU**&#8203;（Model FLOPs Utilization，见[万卡集群](/knowledge-planet/ai-infra/hardware/large-scale-cluster)篇）：

$$\text{MFU} = \frac{\text{实测吞吐（tokens/s）}\times 6N}{n\times A_{\text{peak}}}$$

它是训练的第一指标，但 MFU 只说"丢了多少"，不说"丢在哪"。归因分解（按时间去向）：

- **计算时间**&#8203;：有效 FLOPs ÷ 峰值（理想 MFU=100% 的部分）；
- **通信暴露**&#8203;：allreduce/all-to-all 未被 overlap 掩盖的墙钟时间；
- **流水气泡**&#8203;：$（p-1)/(M+p-1)$（[流水并行](/knowledge-planet/ai-infra/training/parallelism/pipeline-parallelism)篇）；
- **数据等待**&#8203;：输入管道供给不足；
- **优化器与同步**&#8203;：optimizer step、checkpoint 停顿。

一线水平参考：MegaScale 55.2%、Llama 3 约 40%（含故障影响）。&#8203;**低于 35% 时几乎总有低垂的果实**&#8203;。

## 推理侧：延迟、吞吐与 SLO

| 指标 | 定义 | 决定者 |
| ---- | ---- | ---- |
| TTFT | 请求到首 token 的时间 | prefill 吞吐 + 排队 |
| TPOT | 首 token 后每 token 间隔 | decode 带宽 + batch 抢占 |
| 吞吐 | 系统 token/s 总和 | batch 满载率 × [continuous batching](/knowledge-planet/ai-infra/inference/continuous-batching) 效率 |
| Goodput | **同时满足 SLO** 的有效吞吐 | 双 SLO 下的一切调度 |

三个易错点：

1. **吞吐与延迟的冲突是结构性的**&#8203;（roofline 上的 batch 加大），必须以 SLO 约束下的 goodput 为纲（[P/D 分离](/knowledge-planet/ai-infra/inference/pd-disaggregation)篇）；
2. **TTFT 要看 P99**&#8203;：长尾来自排队与长 prompt，均值会掩盖；
3. **KV 显存利用率**是隐藏指标：它决定并发上限（[KV Cache](/knowledge-planet/ai-infra/inference/kv-cache)篇）与[前缀缓存](/knowledge-planet/ai-infra/inference/prefix-caching)命中率。

## 硬件侧：利用率的三张表

- **算力利用率**&#8203;：SM busy / Tensor Core active（Nsight Compute）；
- **带宽利用率**&#8203;：HBM 带宽占比（decode 应接近饱和，训练应远低——低则说明不是带宽瓶颈）；
- **互联利用率**&#8203;：NVLink/IB 发送/接收（对照 allreduce 理论时间，[集合通信](/knowledge-planet/ai-infra/hardware/collective-communication)篇模型）。

::: details 深入推导：从 profile 时间线到优化优先级

把一次训练步的墙钟时间 $T_{\text{step}}$ 分解为互斥桶：

$$T_{\text{step}} = T_{\text{compute}} + T_{\text{comm-exposed}} + T_{\text{bubble}} + T_{\text{data}} + T_{\text{opt}}$$

则 MFU 的损失分解为 $\sum_i T_i / T_{\text{step}}$。优化优先级 = 各桶时长 × 该桶可压缩性。经验矩阵：

| 桶 | 常见占比 | 首选手段 |
| ---- | ---- | ---- |
| comm-exposed | 5~20% | 通信 overlap、bucket 调优、[集合通信](/knowledge-planet/ai-infra/hardware/collective-communication)算法切换 |
| bubble | 5~30%（PP 大时） | 加 M、交错流水、[zero bubble](https://arxiv.org/abs/2401.10241) |
| data | <5%（正常） | 数据管道预取 |
| opt | 1~5% | 异步优化器、 fused optimizer |

**推断优于穷举**&#8203;：拿到 profile 后先算理论值（allreduce 应耗时 = 模型值），实测 > 模型 20% 说明通信实现有问题（不是模型问题）；实测 ≈ 模型但占比高，说明该改并行策略（结构问题）。&#8203;**把 [Roofline](/knowledge-planet/ai-infra/hardware/chip-architecture) 当作零假设来做假设检验，是 AI Infra 性能分析的正确姿势**&#8203;。

（据 MegaScale、HolisticTraceAnalysis 的归因框架。）

:::

## 思考题

1. 某 7B 训练任务 MFU 30%，profile 显示 comm-exposed 占 25%：下一步优化什么？怎么验证有效？
2. 推理服务 P99 TTFT 3 s、均值 200 ms：最可能的原因与验证方法？
3. 为什么"GPU 利用率 100%"可能是坏消息？

::: details 参考答案

1. 25% 通信暴露过高。先算 allreduce 理论时间（梯度量与 $B_{\text{eff}}$，[集合通信](/knowledge-planet/ai-infra/hardware/collective-communication)篇模型）对照实测：远超理论 → 修实现（bucket、算法、拓扑）；等于理论 → 结构问题（通信在关键路径），改并行（减 TP、加 DP overlap）。验证：改后重 profile，看该桶是否消失、MFU 是否上升——单一归因单一验证。
2. 长尾来自队列积压 + 长 prompt prefill（排队论：P99 由到达率峰值时的逗留时间决定，Little 定律）。验证：打点排队时间与 prefill 时间分离；若是排队 → 准入控制/扩容；若是 prefill → 前缀缓存 + chunked prefill。
3. "利用率 100%"若指 SM busy 但吞吐低，说明卡在跑低效 kernel（访存型算子、精度不足的 fallback kernel）——忙不等于有效。要看的是有效 FLOPs（MFU）而非活跃度。

:::

## 小结

- 训练看 MFU 并做时间桶分解；推理看 TTFT/TPOT 双 SLO 下的 goodput。
- profile 的正确用法：理论模型当零假设，实测差值做归因，优化后单点复测。
- 硬件侧三张表：算力、显存带宽、互联带宽，分别对应三种瓶颈假设。
- 指标体系是分层的：硬件 → 单步 → 作业 → 服务 SLO，逐层向上校准。

## 参考资料

- Wei et al., [MegaScale](https://arxiv.org/abs/2402.15627)（arXiv 2402.15627）
- Zhong et al., [DistServe](https://arxiv.org/abs/2401.09670)（arXiv 2401.09670，goodput）
- Kwon et al., [vLLM](https://arxiv.org/abs/2309.06180)（arXiv 2309.06180）
- Chowdhery et al., [PaLM 训练剖析](https://arxiv.org/abs/2204.02311)（arXiv 2204.02311，MFU 分解的经典案例）
