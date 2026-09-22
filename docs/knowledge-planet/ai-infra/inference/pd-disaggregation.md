---
title: "P/D 分离"
date: 2026-09-22T18:00:00+08:00
weight: 80
---

# P/D 分离

> 预填充和解码是两种负载，为什么塞在一组卡上？&#8203;**分开部署，各自最优。**

## 为什么分开

[Chunked Prefill](/knowledge-planet/ai-infra/inference/chunked-prefill) 在时间维调和了 prefill 与 decode，但物理上仍共享资源，配比被焊死。两者的画像截然不同：

| 维度 | Prefill | Decode |
| ---- | ---- | ---- |
| 负载类型 | 计算受限 | 带宽受限 |
| 并行策略偏好 | 大 TP（吃算力，通信可摊薄） | 小 TP 或 EP（通信敏感） |
| KV Cache | 一次性写满 | 持续增长读取 |
| 扩展维度 | 加卡线性降 TTFT | 加卡线性提吞吐 |

**Splitwise 与 DistServe 独立证明了同一件事**&#8203;：分开后，各自用最优配置，双 SLO（TTFT/TPOT）同时达成，goodput 提升可达 2 倍以上，且故障域隔离（decode 不被 prefill 的长尾拖死）。

## 架构与 KV 传输

分离引入新组件：&#8203;**KV 传输层**&#8203;。prefill 完成的 KV 要搬到 decode 实例：

::: mermaid
flowchart LR
    U["用户请求"] --> P["Prefill 池<br/>（大 TP、算力优先）"]
    P -- "KV 传输<br/>（RDMA/IB/NVLink）" --> D["Decode 池<br/>（小 TP、带宽优先）"]
    D -- "流式输出" --> U
    C["KV Cache 池<br/>（前缀缓存共享）"] -.复用.-> P
    C -.复用.-> D
:::

传输代价（[集合通信](/knowledge-planet/ai-infra/hardware/collective-communication)篇模型）：$M_{\text{kv}}=2Ln_{\text{kv}}d_{\text{head}}s\,b\cdot\text{bytes}$ 走 IB 50 GB/s 时，8K token 的 7B 模型 KV（约 1 GB）需 20 ms——相对数秒的 decode 生命周期可接受，但**传输时间是分离架构的新的一等公民约束**&#8203;，也解释了为什么 P/D 分离优先在同超节点内做（NVLink 域传输近免费，[超节点](/knowledge-planet/ai-infra/hardware/supernode)篇）。

## 配比与调度

- **静态配比**&#8203;：按流量画像定 P:D 卡数比（RAG 重 prefill → P 多；长输出 → D 多）；
- **动态调度**&#8203;（DistServe 的 goodput 目标）：按实时 TTFT/TPOT 违约率调整两池规模与请求路由；
- **与[前缀缓存](/knowledge-planet/ai-infra/inference/prefix-caching)合体**&#8203;：Mooncake 把 KV 集中池化（CPU 内存池 + RDMA），prefill 池按"缓存命中优先"调度，命中率直接省算力——&#8203;**P/D 分离 + KV 池化 + 前缀缓存是现代 serving 三件套**&#8203;。

::: details 深入推导：goodput 目标函数与分离的收益边界

**goodput**&#8203;（DistServe 定义）：同时满足 TTFT/TPOT SLO 的有效吞吐 $\text{goodput}(r)$。单卡混合部署的资源被两种负载撕扯：prefill 想要大块迭代（降 TTFT）、decode 要小迭代（保 TPOT），chunked prefill 的块预算是妥协点。分离后各池独立满足：

$$\text{TTFT}: \frac{s_p}{c\cdot C_{\text{prefill}}^{\text{pool}}}\le D_1,\qquad \text{TPOT}: \frac{M_{\text{kv}}}{\beta_{\text{hbm}}}+\frac{s_\Psi\Psi/b}{\beta_{\text{hbm}}}\le D_2$$

两个约束在不同池内分别可解，不再互为约束——&#8203;**这就是分离带来的可行域扩大**&#8203;。

**收益边界**&#8203;。分离不是免费的：KV 传输时间 $M_{\text{kv}}/\beta_{\text{net}}$ 直接加进 TTFT（prefill 完到 decode 开工）；若 $\beta_{\text{net}}$ 太小或 $s$ 太长，传输吃掉分离收益。临界条件近似：$M_{\text{kv}}/\beta_{\text{net}} \ll \text{TTFT 节省}+\text{TPOT 稳定性收益}$。这也给出部署指引：&#8203;**超节点内分离（NVLink/UB，近零成本）优先，跨机分离要 IB 级带宽**&#8203;；KV 池化（Mooncake）则把传输从"点对点搬运"变成"池化共享"，进一步摊薄。

**配比推导**&#8203;。设到达率 $\lambda$、平均 prefill 算力 $w_p$、decode 占用时长 $w_d$：稳态下 $N_p : N_d = \lambda w_p : \lambda \bar T_d w_d'$（$w$ 为各池单位占用），流量画像直接给出卡数比——RAG 重 prefill 的 P:D 可到 1:1，纯 chat 约 1:2~1:3。

（据 Zhong et al. 2024、Patel et al. 2024、Qin et al. 2024。）

:::

## 思考题

1. 为什么 prefill 池偏好大 TP 而 decode 池偏好小 TP/EP？
2. 32K 长上下文、跨机分离（IB 50 GB/s）：KV 传输要多久？这决定了什么？
3. P/D 分离、chunked prefill、前缀缓存三个优化能叠加吗？各自解决什么？

::: details 参考答案

1. prefill 是计算受限：大 TP 摊薄权重读取、拉满算力利用率，通信虽重但单次 prefill 计算量大可掩盖；decode 是带宽受限、通信敏感（[张量并行](/knowledge-planet/ai-infra/training/parallelism/tensor-parallelism)篇：decode 的通信/计算比恶劣），小 TP 减少每 token 通信频次。
2. 7B/GQA：$M_{\text{kv}}\approx 2\times32\times8\times128\times32768\times2\text{B}\approx 4.3\ \text{GB}$，IB 传输约 86 ms——是 TTFT 的显著增量；这决定"分离优先域内、跨机必须算清传输账"，以及长上下文更倾向 KV 池化 + 本地 decode。
3. 可叠加且互补：chunked prefill 管时间维（同卡调度）、P/D 管空间维（分池部署）、前缀缓存管重复计算（命中省 prefill）。生产三件套（Mooncake 架构）同时启用，缓存池还是 P/D 之间 KV 的中转站。

:::

## 小结

- P/D 分离让两种负载各自最优配比与调度，双 SLO 同时达成，goodput 2 倍以上。
- KV 传输是新增的一等约束，决定了分离优先在超节点内、跨机需高带宽或池化。
- 与前缀缓存、KV 池化天然组合，构成现代 serving 的三件套。
- 配比由流量画像显式推导，不是玄学。

## 参考资料

- Zhong et al., [DistServe](https://arxiv.org/abs/2401.09670)（OSDI 2024，arXiv 2401.09670）
- Patel et al., [Splitwise](https://arxiv.org/abs/2311.18677)（ISCA 2024，arXiv 2311.18677）
- Qin et al., [Mooncake](https://arxiv.org/abs/2407.00079)（FAST 2025，arXiv 2407.00079）
- Hu et al., [Distributed Inference and Fine-tuning of LLMs Over a Fast Network](https://arxiv.org/abs/2406.16245)（arXiv 2406.16245）
