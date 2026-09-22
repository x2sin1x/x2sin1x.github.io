---
title: "Continuous Batching"
date: 2026-09-22T18:00:00+08:00
weight: 20
---

# Continuous Batching

> 一次解码迭代能塞进多少请求，就塞多少。&#8203;**这个看似显然的想法，把推理吞吐翻了一倍以上。**

## 静态批的问题

最早的 serving 按"批"调度：凑一批请求，整批跑完整条序列，全部结束才接新请求。两条致命浪费：

- **长等短**&#8203;：批内最长的请求决定整批时长，短请求早早完成后其算力与 KV 显存全程空置；
- **新请求排队**&#8203;：哪怕卡上有空隙，也要等整批释放。

用[芯片架构](/knowledge-planet/ai-infra/hardware/chip-architecture)篇的 roofline 看，decode 是带宽受限、batch 内每多一个请求几乎白送吞吐（batch 阈值 $b\gtrsim I^*s_\Psi/2$，通常 300 以上才饱和）——&#8203;**静态批的浪费恰恰浪费在最该堆并发的地方**&#8203;。

## Iteration 级调度

Orca（2022）提出、如今所有主流引擎标配的 **continuous batching**&#8203;：调度粒度从"批"降到"解码迭代"。每完成一次迭代，就检查队列：新请求随时插入、完成请求随时退出、KV 显存随之增删：

::: mermaid
flowchart TB
    subgraph iter0["迭代 t"]
        A0["请求 1（生成中）"] & B0["请求 2（刚完成✓退出）"] & C0["请求 3（生成中）"]
    end
    subgraph iter1["迭代 t+1"]
        A1["请求 1"] & N1["请求 4（新插入）"] & C1["请求 3"]
    end
    iter0 -- "每次迭代后重排 batch" --> iter1
:::

配合 [PagedAttention](/knowledge-planet/ai-infra/inference/kv-cache)（KV 显存随插随取），batch 组成每步都在变——&#8203;**batch 满载率从"批首到批尾衰减"变成"始终接近上限"**&#8203;。

## 吞吐账

设请求平均 300 token、batch 上限 64。静态批：平均每请求占整批时长 $\approx1+300/2/300$ 的冗余（长尾效应），实测吞吐约为 continuous 的 40~60%（vLLM 论文对 FasterTransformer 的对比：2~4 倍吞吐）。本质是**队列论的收益**&#8203;： iteration 级调度把"批"的离散性抹平，服务强度逼近 1。

::: details 深入推导：为什么 prefill 混入 batch 后 decode 会卡顿

Continuous batching 的 naive 版本把 prefill 也当普通迭代插入。问题：prefill 一个 $s=2048$ 的 prompt，单迭代计算量 $\approx2\times2048\times s_\Psi\Psi$ 字节级的权重读取可摊薄，但它是一个**长迭代**&#8203;——同批 decode 请求必须等它完成才进下一步。decode 迭代约 10~20 ms，prefill 迭代可达 100 ms 以上：&#8203;**TPOT（每 token 延迟）被周期性拉爆**&#8203;。

定量：设 prefill 迭代 100 ms、每 20 个 decode 迭代混入一次，decode 用户的平均 TPOT 从 15 ms 涨到 $15+100/20=20\ \text{ms}$，P99 更糟。解法即 [Chunked Prefill](/knowledge-planet/ai-infra/inference/chunked-prefill)（切块限长）与 [P/D 分离](/knowledge-planet/ai-infra/inference/pd-disaggregation)（干脆分开部署）。

**batch 上限的确定**&#8203;。上限受两约束：显存（KV 增长，见 [KV Cache](/knowledge-planet/ai-infra/inference/kv-cache)篇公式）与 roofline 饱和点（$b\approx I^*s_\Psi/2$ 再往上，吞吐趋平而延迟上升）。生产配置通常在两者之间取值并用 SLO 监控动态调（如 vLLM 的 max_num_seqs）。

（据 Yu et al. 2022 Orca、Kwon et al. 2023。）

:::

## 思考题

1. 为什么 continuous batching 在 PagedAttention 出现之前无法高效实现？
2. decode 阶段 batch 从 8 加到 64，单请求延迟怎么变、总吞吐怎么变？何时应该停止加？
3. 静态批在什么负载下损失最小？

::: details 参考答案

1. KV 必须能随请求动态插入/释放，而连续分配的 KV 需要整块搬迁或预留 max 长度——搬迁成本（拷贝全部历史 KV）比解码本身还贵。分页（块表间接寻址）让"增删一个请求"变成 O(1) 块分配，调度才能 iteration 级跑起来。
2. roofline 上（$b<300$ 量级）：单请求延迟几乎不变（每步时间被权重读取主导），总吞吐近线性涨。加到显存约束或带宽饱和点后：延迟开始上升、吞吐趋平——停止条件是 SLO（TPOT 上限）触线。
3. 请求长度高度一致且到达可整批化的场景（如离线批量标注）：长尾损失趋近零。这也是为什么离线批处理至今仍可用静态批 + 预算最大化。

:::

## 小结

- 静态批的两大浪费（长等短、新请求排队）在带宽受限的 decode 负载上代价加倍。
- Continuous batching 把调度粒度降到迭代级，依赖分页式 KV 管理才能高效实现。
- 吞吐收益 2~4 倍，来源是 batch 满载率而非单步加速。
- naive 混入 prefill 会周期性拉爆 TPOT，引出 chunked prefill 与 P/D 分离。

## 参考资料

- Yu et al., [Orca: A Distributed Serving System for Transformer-Based Generative Models](https://arxiv.org/abs/2208.12233)（OSDI 2022，arXiv 2208.12233）
- Kwon et al., [Efficient Memory Management with PagedAttention](https://arxiv.org/abs/2309.06180)（vLLM，arXiv 2309.06180）
- Anyscale，《Continuous batching: A significant increase in LLM inference throughput》（[博客](https://www.anyscale.com/blog/continuous-batching-llm-inference)）
