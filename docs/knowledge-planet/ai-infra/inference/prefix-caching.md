---
title: "Prefix Caching"
date: 2026-09-22T18:00:00+08:00
weight: 50
---

# Prefix Caching

> 相同前缀的 KV，算一次就够。&#8203;**对多轮对话和批量任务，这是TTFT 的数量级优化。**

## 命中的场景

同一前缀（system prompt、few-shot 样例、RAG 检索结果、多轮对话历史）被反复请求时，其 KV 是确定性的——&#8203;**prompt 相同 + 采样参数不影响 KV**&#8203;。缓存命中即跳过这部分 prefill，TTFT 从"按 $s_p$ 线性"降到"只算增量"：

$$\text{TTFT} \approx \frac{(s_p - s_{\text{hit}})\cdot t_{\text{prefill-tok}}}{ } + t_{\text{overhead}}$$

$RAG$ 场景（system+文档 8K、问题 50 token）命中后 prefill 计算量只剩 0.6%。

## 机制：Radix Tree

SGLang 的 **RadixAttention** 用基数树管理缓存：路径即 token 序列、节点即前缀分支，天然表达"共享前缀 + 分叉"：

::: mermaid
flowchart TB
    R["< system prompt >"] --> D1["< 文档 A >"]
    R --> D2["< 文档 B >"]
    D1 --> Q1["问题 1（命中到此处）"]
    D1 --> Q2["问题 2"]
    D2 --> Q3["问题 3"]
:::

新请求沿树匹配最长前缀 → 复用对应 KV 块（[PagedAttention](/knowledge-planet/ai-infra/inference/kv-cache) 的块表指向缓存块即可）→ 只 prefill 分叉部分。&#8203;**前缀缓存与分页 KV 是绝配**&#8203;：块即树的物理载体。

## 管理难题

1. **驱逐**&#8203;：显存有限，LRU 驱逐长尾前缀；但要优先保留"高频前缀"（按命中次数加权），避免抖动；
2. **一致性**&#8203;：缓存按 token 序列精确匹配，采样参数与模型版本不影响 KV，但权重更新（换 checkpoint）必须全量失效；
3. **多副本路由**&#8203;：缓存驻留在特定实例的显存里，负载均衡器需**前缀亲和路由**&#8203;（同前缀请求路由到同实例），否则命中率归零——这是缓存把无状态 serving 变成"半有状态"的代价。

::: details 深入推导：命中率的经济学与跨实例 KV 传输

**省的是什么**&#8203;。prefill 是计算受限（[roofline](/knowledge-planet/ai-infra/hardware/chip-architecture)），省 1 个 prefill token ≈ 省 $2\Psi$ FLOP；对 TTFT 的节省按 prefill 吞吐折算。设前缀 $s_c$、命中率 $h$、每秒 $\lambda$ 请求：集群节省算力 $\lambda h s_c\times2\Psi$ FLOP/s，可折算成 $\lambda h s_c/\text{(吞吐)}$ 张卡——&#8203;**命中率是可折现的**&#8203;。

**值不值得跨实例传 KV**&#8203;。实例 A 缓存命中但过载、实例 B 空闲：把 KV 从 A 传到 B（$M_{\text{kv}}/\beta_{\text{net}}$）还是 B 重新 prefill（$(s_p)\times2\Psi/C_{\text{prefill}}$）？Mooncake 的答案：KV Cache 集中放到 CPU 内存池/远端节点（带宽协议化的 KVCache 层），传输时间 $\approx M_{\text{kv}}/\beta$ 与重算时间相当甚至更快，且省下 GPU 算力给别处——&#8203;**当 KV 池化带宽足够，"传输"战胜"重算"**&#8203;，缓存从"实例私有"升级为"集群公共资源"。

**复用前缀的采样陷阱**&#8203;。命中前缀的 KV 是确定性的，但decode 之后分支是采样的——对 temperature>0 的生成，两个"相同请求"的输出本就应不同；缓存不破坏这一点。对 temperature=0（贪心）要求可复现时，需固定调度与算子版本，与缓存无关但常被误归因。

（据 Zheng et al. 2023 SGLang、Qin et al. 2024 Mooncake。）

:::

## 思考题

1. 你的产品是编程助手：system prompt 2K + 代码库上下文 30K + 用户问题，多轮对话平均 10 轮。哪部分最该进前缀缓存？
2. 前缀亲和路由为什么可能与负载均衡冲突？怎么调和？
3. 为什么采样参数不影响 KV 命中，而模型版本影响？

::: details 参考答案

1. 系统提示与代码库上下文是跨请求共享的稳定前缀（30K token 的 prefill 占绝对大头），必须缓存；多轮对话历史是会话内增长的树状前缀（Radix 树的典型形态），按会话路由缓存；用户问题是每请求的增量，无从缓存。
2. 亲和路由把同前缀请求固定到同实例，热点前缀会让该实例过载而其他实例空闲，与最小负载路由冲突。调和：分池（按前缀簇划分实例池）或 KV 池化（Mooncake 式，路由自由 + 缓存共享），后者是终局方案。
3. KV 由输入 token 序列 + 权重决定（前向是确定性的）；temperature/top-p 只作用于最终 logits 的采样步骤，发生在 KV 生成之后。模型版本换权重则 KV 全错，必须失效。

:::

## 小结

- 前缀缓存把重复前缀的 prefill 降为零，TTFT 数量级改善；对 RAG/多轮/批量场景是刚需。
- RadixTree + 分页块是标准实现；驱逐按命中率加权而非纯 LRU。
- 缓存让 serving 半有状态化，前缀亲和路由与负载均衡产生张力，KV 池化是终局解。
- 命中率可以直接折算成卡数，是可量化运营的优化。

## 参考资料

- Zheng et al., [SGLang: Efficient Execution of Structured Language Model Programs](https://arxiv.org/abs/2312.07104)（RadixAttention，arXiv 2312.07104）
- Qin et al., [Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving](https://arxiv.org/abs/2407.00079)（FAST 2025，arXiv 2407.00079）
- Gawryosiak & Bala, [Prompt Cache](https://arxiv.org/abs/2403.11108)（arXiv 2403.11108，模块化复用）
- SGLang 项目，[GitHub](https://github.com/sgl-project/sglang)
