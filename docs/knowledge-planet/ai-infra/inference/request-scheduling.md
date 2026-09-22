---
title: "请求调度"
date: 2026-09-22T18:00:00+08:00
weight: 30
---

# 请求调度

> [Continuous batching](/knowledge-planet/ai-infra/inference/continuous-batching) 决定了"每次迭代带谁"，请求调度决定"谁先进来、谁被挤出去"。&#8203;**SLO 不是口号，是调度的输入。**

## 两个 SLO 指标

分布式 serving 论文（DistServe）确立的标准双指标：

- **TTFT**&#8203;（Time To First Token）：用户点发送到看见第一个字——交互体验的"响应感"；
- **TPOT**&#8203;（Time Per Output Token）：之后每个 token 的间隔——阅读流畅度。

两者由不同负载决定（TTFT 由 prefill 决定、TPOT 由 decode 决定），&#8203;**资源竞争却此消彼长**&#8203;——这是推理调度的基本张力。

## 调度器的日常决策

每个迭代，调度器要回答：

1. **准入**&#8203;：新请求进 batch 吗？看 KV 显存余量（[PagedAttention](/knowledge-planet/ai-infra/inference/kv-cache) 的可分配块数）与当前 batch 大小；
2. **优先级**&#8203;：新请求的 prefill 与在跑请求的 decode 谁先？chunked prefill 配额给多少？
3. **驱逐与抢占**&#8203;：显存不够时，暂停谁？现代引擎支持 **recompute-style 抢占**&#8203;——把低优先级请求的 KV 整体逐出，恢复时重新 prefill（用时间换显存）；
4. **换出**&#8203;（swapping）：KV 移到 CPU 内存而非丢弃，恢复免重算，但要付 PCIe 搬运。

## 常见策略

| 策略 | 做法 | 偏向 |
| ---- | ---- | ---- |
| FCFS + 无抢占 | 先来先服务，满了就拒 | 简单、公平，但队头阻塞 |
| Shortest-Job-First | 预估输出长度优先 | 低平均延迟，需长度预测器 |
| 优先级 + 抢占 | 交互请求 > 离线任务 | SLO 分级服务 |
| Dynamic splitwise / Prefill-decode 配比 | 按实时负载调 prefill 预算 | 双 SLO 兼顾 |

::: details 深入推导：抢占的代价模型与准入控制

**recompute 抢占的代价**&#8203;。被抢占请求已生成 $s_g$ token，恢复需重新 prefill $s_p+s_g$（prompt+已生成）。代价 $\approx$ prefill 计算 $2(s_p+s_g)\Psi$ FLOP 摊在恢复时刻 + KV 显存在此期间为别人让路。设被抢占概率 $p$，期望额外计算 $p\times2(s_p+s_g)\Psi$。&#8203;**结论：抢占是"显存现货"与"重复计算"之间的期货交易**&#8203;，s_g 越大越不该抢（沉没的 KV 越多）——所以调度器优先抢占"刚进来"的请求。

**准入控制与队列论**&#8203;。设 TTFT SLO 为 $D_{\text{ttft}}$，prefill 吞吐 $C_{\text{prefill}}$（token/s）。Little 定律：系统内平均请求数 $\mathcal{L}=\lambda W$（$\lambda$ 到达率、$W$ 平均逗留）。当 $\lambda\times\bar s_p > C_{\text{prefill}}\times\rho_{\max}$（$\rho_{\max}$ 是允许 prefill 占用的算力份额），TTFT 必然违约——&#8203;**准入控制必须在队列积压之前限流**&#8203;，而不是等违约后驱逐。生产系统（DistServe、SGLang router）按双 SLO 反推 prefill/decode 资源配比与最大并发。

（据 Zhong et al. 2024 DistServe、 Patel et al. 2024 Splitwise。）

:::

## 思考题

1. 为什么 TTFT 和 TPOT 优化天然冲突？举一个具体的资源竞争点。
2. recompute 抢占 vs swap-out：什么 KV 长度下选后者？
3. 你的服务 TTFT SLO 1 s、TPOT SLO 50 ms，早高峰持续违约 TPOT：调度上有什么旋钮？

::: details 参考答案

1. prefill 吃算力（计算受限、可高利用率），decode 吃带宽（被 KV 读取主导）。同一批卡上，prefill 的大迭代直接推迟 decode 迭代（TPOT 尖刺）；decode 的持续占用又推迟 prefill 开工（TTFT 变差）。块预算（chunked prefill 的每迭代 prefill token 数）就是两者的分配器。
2. 设 swap 代价 = PCIe 搬运 $M_{\text{kv}}/\beta_{\text{pcie}}$（64 GB/s），recompute 代价 $\approx(s_p+s_g)\times2\Psi/\beta_{\text{compute-equivalent}}$。$s_g$ 小（刚生成几个 token）时 recompute 便宜；KV 大（长上下文）时搬运慢、重算更贵——粗略临界点在 KV 读写时间 ≈ 重算时间处，随模型/硬件变动，应实测定。
3. 旋钮清单：调低单迭代 prefill 预算（保护 decode）、限制 max_num_seqs（准入）、对低优先级流量 recompute 抢占、开启 prefill-decode 更彻底的分离（[P/D 分离](/knowledge-planet/ai-infra/inference/pd-disaggregation)）、以及横向加卡。

:::

## 小结

- 推理调度以 TTFT/TPOT 双 SLO 为纲，两者对应 prefill/decode 两种负载的竞争。
- 调度器四件事：准入、优先级、抢占、换出；抢占是显存与重复计算的期货交易。
- 准入控制应基于 Little 定律在违约前限流，而非事后驱逐。
- 调度做不平的题，交给系统架构（chunked prefill、P/D 分离）。

## 参考资料

- Zhong et al., [DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving](https://arxiv.org/abs/2401.09670)（OSDI 2024，arXiv 2401.09670）
- Patel et al., [Splitwise: Efficient Generative LLM Inference Using Phase Splitting](https://arxiv.org/abs/2311.18677)（ISCA 2024，arXiv 2311.18677）
- Agrawal et al., [Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve](https://arxiv.org/abs/2403.02310)（OSDI 2024，arXiv 2403.02310）
- vLLM 文档，[Preemption 与 Scheduling](https://docs.vllm.ai/en/latest/)
