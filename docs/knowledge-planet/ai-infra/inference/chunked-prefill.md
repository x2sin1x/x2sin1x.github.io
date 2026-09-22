---
title: "Chunked Prefill"
date: 2026-09-22T18:00:00+08:00
weight: 40
---

# Chunked Prefill

> 一条 32K 的 prompt 一次性 prefill，会让同卡的 decode 停摆一整秒。&#8203;**切块，是 prefill 与 decode 和平共处的第一步。**

## 问题：长 prefill 是个巨型迭代

Prefill 一次处理整个 prompt：计算量 $2s_p\Psi$ FLOP、单迭代时间随 $s_p$ 线性增长（$s_p=32\text{K}$ 的 70B 模型在 8 卡上也是数百 ms 级）。[Continuous batching](/knowledge-planet/ai-infra/inference/continuous-batching) 篇推导过：混入这样的长迭代，同批 decode 的 TPOT 被周期性拉爆。

## 机制：把 prefill 切成 N 块

把 prompt 切成固定大小的块（如 512/1024 token），每个迭代只 prefill 一块；块间传递增量 KV（[PagedAttention](/knowledge-planet/ai-infra/inference/kv-cache) 的块天然支持续写）：

::: mermaid
flowchart TB
    subgraph it1["迭代 1"]
        c1["prompt 块 1（512 tok）"] & d1["decode：请求 A/B/C"]
    end
    subgraph it2["迭代 2"]
        c2["prompt 块 2"] & d2["decode：A/B/C"]
    end
    subgraph it3["迭代 N"]
        cN["prompt 块 N → 进入 decode"] & dN["decode：A/B/C"]
    end
    it1 --> it2 --> it3
:::

**关键洞察（Sarathi-Serve）**&#8203;：prefill 块的计算是算力受限的，decode 是带宽受限的——&#8203;**把两者混在同一迭代，可以让 prefill 的计算"顺手"把 decode 需要的权重读取掩护掉**&#8203;。decode 部分几乎是搭 prefill 的便车：prefill 迭代的算力有富余（roofline 的算力侧没吃满），decode 的加入基本不增加墙钟时间，却让 decode 的 TPOT 尖刺消失。

## 收益与代价

| 维度 | 效果 |
| ---- | ---- |
| TPOT 尖刺 | 消除（长 prefill 不再阻塞 decode 迭代） |
| TTFT | 略升（切块引入多迭代开销与调度延迟） |
| 吞吐 | 提升或持平（计算强度混合后算力利用率更均匀） |
| 实现 | 需要 KV 续写与迭代内混合调度 |

**chunk 大小是旋钮**&#8203;：越大越接近原始 prefill（TTFT 好但 decode 受干扰），越小 decode 越平滑（TTFT 变差、调度开销升）。Sarathi-Serve 给出按 SLO 自动配比的方法。

::: details 深入推导：混合迭代的 roofline 与 prefill 预算

**混合迭代的性能模型**&#8203;。单迭代内：prefill 块 $c$ token + $b$ 个 decode 请求。计算量 $2(c+b)\Psi$，权重读取 $s_\Psi\Psi$（一次），KV 读取 $2Ln_{\text{kv}}d_{\text{head}}\bar s\,b$。运算强度：

$$I = \frac{2(c+b)\Psi}{s_\Psi\Psi + 2Ln_{\text{kv}}d_{\text{head}}\bar s\,b}$$

纯 decode（$c=0$）时 $I$ 低（带宽受限）；加入 $c$ 后 $I$ 上升、逐步逼近 $I^*$——&#8203;**prefill 块是在给整个迭代"提强度"**&#8203;，让带宽侧的浪费变成有效计算。最优 $c$：让 $I$ 恰好达到 $I^*$（再大就计算受限、挤压 decode），即 $c^{*}\approx \frac{I^*}{2\Psi}\left(s_\Psi\Psi+2Ln_{\text{kv}}d_{\text{head}}\bar s b\right)-b$。这是一个可实盘计算的公式，Sarathi-Serve 的"token 预算"即其工程化。

**TTFT 的下界**&#8203;。$s_p$ token 的 prompt 切成 $s_p/c$ 块，TTFT $\ge (s_p/c)\times t_{\text{iter}}$。$c$ 由 decode SLO 决定后，TTFT 下界随之确定——&#8203;**双 SLO 在 chunked prefill 框架下可以显式联立求解**&#8203;，解不出的就说明单卡容量不够，需 [P/D 分离](/knowledge-planet/ai-infra/inference/pd-disaggregation)加资源。

（据 Agrawal et al. 2023 Sarathi、2024 Sarathi-Serve。）

:::

## 思考题

1. 为什么 chunked prefill 能让 decode "搭便车"，而纯 decode 之间互相搭不了？
2. chunk 设得过大或过小分别伤害什么指标？
3. chunked prefill 与 [P/D 分离](/knowledge-planet/ai-infra/inference/pd-disaggregation)解决的是同一个问题的哪个层次？

::: details 参考答案

1. decode 是带宽受限、算力大量闲置；prefill 块提供的是算力侧负载，两者互补填满 roofline。纯 decode 之间都是带宽受限，混在一起只会在同样的权重读取上多算几个 batch——那正是 continuous batching 的正常形态，没有额外互补收益。
2. 过大：单迭代时长上升，decode TPOT 尖刺回来了，且 chunk 内注意力算完前该请求的 KV 不能被后续块使用（TTFT 变差）；过小：迭代数增多，权重读取次数×块数（每迭代都要读一遍权重）使总带宽消耗上升，TTFT 恶化。
3. 同一问题（prefill 干扰 decode）的两个层次：chunked prefill 在**时间维**&#8203;（同一组卡上切块混合调度），P/D 分离在**空间维**&#8203;（不同组卡、物理隔离）。前者是软件调度优化、零额外资源；后者是架构级方案、可独立扩展但引入 KV 传输成本。

:::

## 小结

- 长 prefill 是巨型迭代，是 TPOT 尖刺的来源；切块后 prefill 与 decode 每迭代共存。
- 混合迭代在 roofline 上互补：prefill 的算力填 decode 的带宽闲置，decode 搭便车。
- chunk 大小有闭式近似（迭代强度逼近 $I^*$），双 SLO 可显式联立。
- 做不平的题升级到 P/D 分离。

## 参考资料

- Agrawal et al., [Sarathi: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills](https://arxiv.org/abs/2308.16369)（arXiv 2308.16369）
- Agrawal et al., [Taming Throughput-Latency Tradeoff with Sarathi-Serve](https://arxiv.org/abs/2403.02310)（OSDI 2024，arXiv 2403.02310）
- Zhong et al., [DistServe](https://arxiv.org/abs/2401.09670)（arXiv 2401.09670，双 SLO 框架）
