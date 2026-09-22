---
title: "A/F 分离"
date: 2026-09-22T18:00:00+08:00
weight: 90
---

# A/F 分离

> 更细的一刀：&#8203;**把 Attention 和 FFN 拆到不同的卡上。** DeepSeek-V3、RServe 这类大 MoE 模型服务的进阶架构。

## 为什么要拆

Attention 与 FFN 的负载画像在 MoE 时代进一步分化：

- **Attention（A）**&#8203;：小矩阵乘 + softmax，带宽敏感；MoE 模型里它是 **dense** 的（每 token 都要算），且是 KV 的家；
- **FFN/MoE（F）**&#8203;：专家是大矩阵乘，算力敏感；但专家是**稀疏激活**的，需要 all-to-all dispatch/combine（[专家并行](/knowledge-planet/ai-infra/training/parallelism/expert-parallelism)篇）。

两者的显存需求也解耦：A 占 KV（随并发长），F 占专家权重（固定但巨大）。塞在一起时，"KV 多的卡"和"专家多的卡"被迫同配——&#8203;**A/F 分离让两种资源各自按需扩展**&#8203;。

## 机制

在 TP/EP 之上再切一刀：A 组卡持有注意力 + KV，F 组卡持有专家；层间以 all-to-all（或 P2P）连接两组成员：

::: mermaid
flowchart LR
    subgraph A["Attention 组（EP 内）"]
        A1["A 卡：注意力 + KV Cache"]
    end
    subgraph F["FFN/MoE 组（EP）"]
        F1["F 卡：专家 1"] & F2["F 卡：专家 2"] & F3["..."]
    end
    A1 -- "dispatch（隐藏态）" --> F1 & F2 & F3
    F1 & F2 & F3 -- "combine（专家输出）" --> A1
:::

注意与 [P/D 分离](/knowledge-planet/ai-infra/inference/pd-disaggregation)的区别：P/D 沿**时间轴**&#8203;（prefill 阶段 vs decode 阶段）拆，A/F 沿**模型结构**&#8203;（层内的两种子层）拆，两者正交可叠加。

## 收益与代价

**收益**&#8203;：

1. 资源按需配比：KV 池（A 组）与专家池（F 组）独立扩缩，MoE 模型权重巨大时尤其重要；
2. 通信与计算重叠的空间更大：A 组做下一个 token 的注意力时，F 组仍在算上一个 token 的专家（微流水），all-to-all 延迟被藏；
3. 故障域分离：专家热/坏只影响 F 组。

**代价**&#8203;：每 token 每层多两跳跨卡通信（隐藏态往返），对互联带宽的胃口比 P/D 更大——&#8203;**A/F 分离几乎只在超节点内部署**&#8203;（DeepSeek-V3 的 prefill/decode 节点内部即 A/F 分离式组织，UB 全互联 384 卡）。

::: details 深入推导：A/F 分离的流水收益与通信账

**微流水（RServe/DeepSeek 风格）**&#8203;。decode 中第 $i$ token 的 FFN 与第 $i+1$ token 的 attention 可重叠：A 组算 $t_{i+1}$ 的 attention 的同时，F 组算 $t_i$ 的专家。设 $t_a$、$t_f$ 为两段耗时，稳定态周期 $T=\max(t_a, t_f)+t_{\text{comm}}$，理想下吞吐由较长段决定——&#8203;**把两段塞同卡时周期是 $t_a+t_f$，分离后压到 max**&#8203;，这是收益的理论来源。

**通信账**&#8203;。每 token 每层：dispatch 传输隐藏态 $2h$ 字节 × 每 token 平均激活专家数 $k$、combine 同量级。70B×MoE 场景（$h=4096$、$k=8$、FP8）：每层 $2\times4096\times8\times1\text{B}\times2\approx131\ \text{KB}$/token；80 层累计 10 MB/token。NVLink 域（900 GB/s）0.01 ms 级——免费；跨 IB 则 0.2 ms/token/层级别，80 层 16 ms——吃掉大半个 TPOT。&#8203;**结论与 P/D 分离一致：A/F 分离的部署半径由互联带宽决定**&#8203;。

**与 EP 的关系**&#8203;。A/F 分离不排斥 EP：F 组内部仍是 EP+TP 切专家。可以把 A/F 看作"EP 的外层再分类"——按子层角色把卡分成资源池，池内再细化并行。

（据 DeepSeek-AI 2024 V3、Griggs et al. 2024 RServe。）

:::

## 思考题

1. A/F 分离与 P/D 分离是竞争还是互补？画出一个两层分离的生产拓扑。
2. 为什么 A/F 分离比 P/D 分离对互联带宽更敏感？
3. 什么样的模型让 A/F 分离的收益最大？

::: details 参考答案

1. 互补且正交：P/D 分时间轴、A/F 分模型结构。生产拓扑示例：prefill 池（内含 A/F 两组）→ KV 传输 → decode 池（内含 A/F 两组）；F 组可跨池共享（专家池化），A 组按阶段分。
2. P/D 的 KV 传输每请求只发生一次（prefill 完）；A/F 的隐藏态往返每 token 每层都发生（$O(L)$ 次），频次高两个数量级，带宽不足时直接乘进 TPOT。
3. 大 MoE（专家权重巨大、激活稀疏、all-to-all 频繁）+ 长上下文（KV 显存占比高）——两头都极端时，A/F 的资源解耦价值最大；小 dense 模型分离反而摊薄算力、得不偿失。

:::

## 小结

- A/F 分离沿模型结构切：注意力+KV 一组、专家一组，资源按需扩缩。
- 微流水让 attention 与 FFN 的执行重叠，周期从 $t_a+t_f$ 压到 $\max(t_a,t_f)+t_{\text{comm}}$。
- 通信频次 $O(L)$/token 决定它对互联带宽最挑剔，几乎只在超节点内部署。
- 与 P/D 分离（时间轴）、EP（专家切分）正交互补，构成分离式 serving 的完整谱系。

## 参考资料

- Griggs et al., [RServe: Speeding Up Long-Context LLM Inference via Out-of-Order Computing](https://arxiv.org/abs/2410.20150)（arXiv 2410.20150）
- DeepSeek-AI, [DeepSeek-V3 Technical Report](https://arxiv.org/abs/2412.19437)（arXiv 2412.19437）
- Wu et al., [Serving LLMs on Huawei CloudMatrix384](https://arxiv.org/abs/2506.12708)（arXiv 2506.12708）
- Zhu et al., [Loogle: Towards distributed long-context language modeling](https://arxiv.org/abs/2408.10845)（arXiv 2408.10845，注意力分离的探索）
