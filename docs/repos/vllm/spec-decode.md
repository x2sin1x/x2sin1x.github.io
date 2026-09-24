---
title: 投机解码
weight: 130
---

# 投机解码

> 本章回答：vLLM 如何用一个通用 propose–verify 框架支持 n-gram、Eagle、Medusa、MTP 等多种草稿来源，以及这套机制如何嵌进第 6 章的统一调度模型而不增加调度器分支。

## propose–verify：用并行验证换串行 decode

自回归 decode 每步只产出 1 个 token，GPU 利用率极低。投机解码的思路是：用一个廉价的"提案者"一次猜出 k 个后续 token，再用目标模型**一次前向并行验证**这 k 个猜测，接受的 token 全部留下。单步产出从 1 变成 1..k+1，多出的算力消耗换来更高的解码吞吐。

vLLM V1 把该机制压缩成两个跨进程的令牌流：

- 下行：`SchedulerOutput.scheduled_spec_decode_tokens`（`vllm/v1/core/sched/output.py:232`），告诉 Worker 本步每个请求要验证哪些草稿 token；
- 上行：`DraftTokenIds`（`vllm/v1/outputs.py:358`），Worker 侧提案者产出的下一步草稿，经 `EngineCore.post_step`（`vllm/v1/engine/core.py:664`）调用 `take_draft_token_ids()`（`vllm/v1/worker/gpu_model_runner.py:4836`）取回，`Scheduler.update_draft_token_ids()`（`vllm/v1/core/sched/scheduler.py:2470`）写回请求的 `spec_token_ids` 字段。

这正呼应第 6 章的统一调度注释：调度器不认识"投机解码阶段"，请求的 `num_tokens_with_spec` 把草稿 token 计入总量，`schedule()` 为它们预留槽位（`draft_slots`，`scheduler.py:579`），验证失败的部分自然落选。

## 提案者家族

全部提案者在 `vllm/v1/spec_decode/`，共享基类 `SpecDecodeBaseProposer`，按草稿来源分三类：

| 类型 | 实现 | 草稿来源 |
|---|---|---|
| 无模型 | `NgramProposer`（`ngram_proposer.py:12`） | prompt 与已生成文本的 n-gram 匹配 |
| 小模型 | `EagleProposer`（`eagle.py:10`）、`MedusaProposer`（`medusa.py:18`）、MTP（多 token 预测头） | 独立 drafter 模型逐层前向 |
| 自定义 | `custom_class_proposer.py` | 用户注册的提案类 |

::: mermaid
sequenceDiagram
    participant S as Scheduler
    participant P as Proposer（Worker 侧）
    participant T as Target 模型
    S->>P: （上一步产出的）spec_token_ids 调度
    P->>T: 一次前向：prompt + k 个草稿并行验证
    T-->>S: 接受 m ≤ k+1 个 token + logits
    S->>S: update_draft_token_ids：为新请求补草稿
    note over S: 调度器视角只是 num_tokens_with_spec 增长
:::

`NgramProposer.propose()`（`ngram_proposer.py:138`）是理解框架的最佳起点：它只查请求自己的 token 序列历史，无模型、无 GPU 状态，快照中还有把 n-gram 匹配搬上 GPU 的 `ngram_proposer_gpu.py`。Eagle/Medusa 则需要额外的 drafter 权重——它们的 `load_model`、`dummy_run`（如 `medusa.py:58`、`:72`）参与 Worker 的初始化与 CUDA Graph 捕获。

## 验证与拒绝采样

草稿正确性由拒绝采样保证：目标模型对 k 个位置各产出一次分布，与草稿 token 逐一比对，按概率接受/拒绝，并保证最终输出分布与直接自回归采样**数学上完全一致**——投机解码是无损加速。核心实现在 `vllm/v1/sample/rejection_sampler.py`；快照中还出现了自适应验证开关（`speculative_config.enable_adaptive_verification`，`vllm/v1/attention/selector.py:139` 附近引用），允许按 head 动态修剪验证长度。

KV 侧有一个隐含契约：被拒绝的草稿 token 已经在前向中消耗了 KV 块（Eagle 的 drafter 自带 KV，故 `allocate_slots` 有 `num_lookahead_tokens` 参数，第 7 章），验证后未接受位置的缓存由 `_update_states` 按接受长度截断回收。

## 代价与边界

- ** Drafter 品质决定一切**：接受率低的场景（强 Temperature、代码以外的自由文本配 n-gram）收益可能为负——额外验证的前向是纯开销；
- **批次变大**：k 个草稿让每步 token 数放大，与 chunked prefill、`max_num_batched_tokens` 预算竞争；
- **双模型协调**：Eagle/MTP 需要 drafter 与 target 的词表映射（`spec_decode/vocab_mapping.py`）与独立的 CUDA Graph 捕获路径（`gpu_model_runner.py:2607` 附近注释）。

## 本章收束

- 投机解码 = 提案者（三类草稿来源）+ 拒绝采样（数学无损）+ 调度器的一个 token 计数字段；
- 调度器无投机解码分支：草稿 token 通过 `num_tokens_with_spec` 与 `draft_slots` 融入统一调度模型；
- 跨进程令牌流是两根：下行的 `scheduled_spec_decode_tokens`、上行的 `DraftTokenIds`。

下一章纵览四个横向扩展点：Platform、Plugin、KV Connector 与结构化输出。
