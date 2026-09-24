---
title: 采样与流式输出
weight: 100
---

# 采样与流式输出

> 本章回答：前向产出 logits 之后，token 如何被采出来、如何变成文本、又如何以流式形态送达客户端——覆盖 Sampler、增量反词元化与 OutputProcessor 三段。

## Sampler：一次前向后的 last mile

`Sampler`（`vllm/v1/sample/sampler.py:21`）是 `nn.Module`，`forward()`（`:72`）的流程是固定的四步管线：

1. logits 转 float32（`:91`）；
2. `apply_logits_processors()`（`:372`）：按请求叠加自定义 logits 处理器、结构化输出 bitmask 等约束；
3. `sample()`：按温度、top-k/top-p 采样或 argmax（温度与惩罚分别由 `apply_temperature`（`:229`）与 `apply_penalties`（`:421`）等在 logits 处理器阶段完成）；
4. 处理 logprobs：源码注释明确指出一个与 V0 不同的语义——**top-k logprobs 使用惩罚与温度缩放前的原始 logits**（`:78` 的 NOTE），保证用户看到的是模型原始分布。

采样结果被转成 int64（FlashInfer 返回 int32、PyTorch 返回 int64，`:100` 附近的注释解释了这次统一）。投机解码的验证采样在独立的 `rejection_sampler.py` 中，第 12 章再展开。

## 从 token id 到 EngineCoreOutput

采样完成后 Worker 打包 `ModelRunnerOutput` 回 EngineCore，`Scheduler.update_from_output()`（`vllm/v1/core/sched/scheduler.py:1967`）逐请求检查停止条件（stop token、stop string、`max_tokens`），产出 `EngineCoreOutputs`——每请求只有 token id 列表与完成标志，**没有文本**。文本重建被刻意留在 API 进程：EngineCore 不持有 tokenizer，跨进程传文本既浪费带宽又引入分片歧义。

## OutputProcessor：全批唯一的循环

API 进程侧，`output_handler` 把 `EngineCoreOutputs` 交给 `OutputProcessor.process_outputs()`（`vllm/v1/engine/output_processor.py:641`）。它的 docstring 写明了性能契约：这是**全系统中唯一应该遍历整个批次的循环**，任何需要触及每个请求的逻辑都应并入这里（`:658` 的 NOTE FOR DEVELOPERS）——把 Python 层的 O(batch) 循环收敛到一处，便于控制解释器开销。

循环内对每个请求做三件事：

::: mermaid
flowchart LR
    A["EngineCoreOutput<br/>token ids"] --> B["IncrementalDetokenizer.update<br/>detokenizer.py:31"]
    B --> C["RequestState.make_request_output<br/>output_processor.py:299"]
    C --> D{"流式?"}
    D -- "是" --> E["put 进 RequestOutputCollector<br/>覆盖式投递"]
    D -- "否" --> F["累计到最终 RequestOutput"]
    B -- "命中 stop string" --> G["reqs_to_abort<br/>交回 engine 补发 abort"]
:::

**增量反词元化**是这段的性能关键：`IncrementalDetokenizer`（`vllm/v1/engine/detokenizer.py:31`）只对新 token 解码、维护未完结的多字节 UTF-8 残片，避免每步重新解码整个序列。

## 流式语义：覆盖式 collector

流式请求在 `add_request` 时创建了 `RequestOutputCollector`（`output_processor.py:51`）。`put()`（`:67`）是**覆盖写**：若客户端消费慢、collector 里已有未取走的增量，新输出直接覆盖旧增量。这换来一个明确的背压契约——内存占用与批次规模线性相关，而与客户端速度无关；代价是慢客户端可能丢失中间 delta（对 SSE 场景通常可接受，非流式场景走累计路径不受影响）。

`RequestState.apply_streaming_update()`（`:203`）负责把 delta 包装成协议层需要的形态；stop string 检出后返回的 `reqs_to_abort` 会被 `output_handler` 转发回 EngineCore（`async_llm.py` 的 `:851` 一带），保证"字符串命中"与"引擎停止生成"两端的最终一致。

## 本章收束

- Sampler 是带 logits 处理器插槽的四步管线；logprobs 基于原始 logits 而非缩放后分布；
- token id 走全程，文本只在 API 进程由增量反词元化重建；
- `process_outputs` 是唯一的全批循环，流式背压靠覆盖式 collector 实现。

下一章转向模型本体：权重如何加载、量化方法如何嵌入层实现。
