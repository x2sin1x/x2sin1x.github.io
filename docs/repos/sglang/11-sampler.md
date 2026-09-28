---
title: "第 11 章 采样"
---

# 第 11 章 采样

> 本章回答：logits 如何变成下一个 token？温度、top-k、top-p、重复惩罚如何作用于批中不同请求？结构化输出（grammar 约束）在哪里介入？延迟采样（delay sampling）是什么？

## 11.1 Sampler 的位置

采样是前向与调度之间的最后一步 GPU 工作：`TpModelWorker.forward_batch_generation` 在 `model_runner.forward` 返回 logits 后立即调用 `model_runner.sample`（`srt/managers/tp_worker.py:598` 的方法体内，`:675` 与 `:686` 两处调用点），`ModelRunner.sample` 委托给 `srt/layers/sampler.py:109` 的 `Sampler`。

批内每个请求可以有&#8203;**不同的采样参数**&#8203;，`SamplingBatchInfo`（采样信息的批形态）把逐请求的温度、top-k、top-p、惩罚打包成批张量，`Sampler.forward`（`sampler.py:141`）按其内容选择核函数路径。

## 11.2 采样主路径

`Sampler.forward` 的分支（`sampler.py:141–420`）按复杂度递进：

1. **贪婪/纯 argmax**&#8203;：`need_top_p_sampling` 与 `need_top_k_sampling` 均为假时直接取 argmax（`sampler.py:203` 的判定）；
2. **top-k / top-p**&#8203;：CUDA 上用 flashinfer 的 `top_k_top_p_sampling_from_probs`，其他平台按 `is_hip` / `is_musa` / `is_xpu` 分派（`sampler.py:1–60` 的平台导入块）；ROCm 上还可走 `aiter` 的 `greedy_sample`，源码注释记录了一个已知坑：该 kernel 在全 NaN/inf logit 行会返回越界 token id（`sampler.py:58` 起的注释），需要防御性修正——这是「测试表达可观察契约、注释记录已知边界」的实例；
3. **顺序过滤路径**&#8203;：`top_k_renorm_prob` → `top_p_renorm_prob`（`sampler.py:370–400`）。

与采样并行的还有：`min_p` 采样、逐请求的自定义 logit processor（`Req.custom_logit_processor` 字段，`srt/managers/schedule_batch.py:999` 构造参数可见）、惩罚项（repetition/frequency/presence）在 `SamplingBatchInfo` 内累积。这些都发生在 **logits → 概率** 之间。

## 11.3 结构化输出：grammar 的介入点

受限解码（`json_schema` / regex / EBNF，`--grammar-backend xgrammar`）不是采样后的校验，而是&#8203;**采样前的掩码**&#8203;：

- `srt/constrained/grammar_manager.py:30` 的 `GrammarManager` 在调度器内维护每请求的 FSM（xgrammar、outlines 等后端，`srt/constrained/base_grammar_backend.py:373` 的工厂分发）;
- 每个 decode 步，FSM 依据当前已生成 token 序列计算合法 token 集，转成位掩码注入采样；
- `Sampler.forward` 中 `sampling_info.grammars is not None` 的分支应用掩码（`apply_grammar_mask` 一族），使非法 token 概率为 −inf。

掩码的时机与 overlap 调度有耦合：第 6 章已看到 `event_loop_overlap` 中 *Run sample of the current batch — It depends on the result of the last batch (e.g., grammar), so we run it after the last batch is processed* 的注释（`srt/managers/scheduler.py:2004`）——**带 grammar 的批必须等上一批结果落账后才能采样**&#8203;，否则掩码基于过期的 token 历史。这是 overlap 优化在正确性面前的显式让步，`is_disable_overlap_for_batch`（`srt/managers/scheduler.py:2015`）里 `need_grammar_sync` 分支同样是这个约束的体现。

## 11.4 延迟采样：把采样推迟一拍

`TpModelWorker.forward_batch_generation` 中有一条专门路径（`srt/managers/tp_worker.py:668` 起的条件分支）：

```python
# srt/managers/tp_worker.py:645 附近（节选）
if (
    self.enable_overlap
    and not self.enable_spec
    and (
        forward_batch.sampling_info.grammars is not None
        or (
            envs.SGLANG_ENABLE_DELAY_SAMPLE.get()
            and not forward_batch.is_prefill_only
        )
    )
):
    def sample_batch_func():
        batch_result.next_token_ids = self.model_runner.sample(
            logits_output, forward_batch
        )
        ...
        return batch_result
    batch_result.delay_sample_func = sample_batch_func
    return batch_result
```

即：&#8203;**采样不在此刻执行，而是打包成 `delay_sample_func`**&#8203;，由第 6 章 overlap 循环末尾的 `launch_batch_sample_if_needed` 在上一批结果处理完之后调用。收益（源码注释与结构一致）：logits 在 GPU 上，采样这段 GPU 工作可以塞进「CPU 处理上一批结果」的窗口；代价：本批 token 的可见性又延后一拍，与 grammar 同步约束共同构成 overlap 模式的时序边界。

## 11.5 本章收束

- 采样参数是批张量（`SamplingBatchInfo`），同一批内逐请求异构；路径按 need_top_k/p 与平台分派。
- 结构化输出是采样前掩码而非事后校验；FSM 状态推进要求「先落账上一批、再掩码这一批」，这是 overlap 与 grammar 的时序契约。
- 延迟采样把采样作为一拍内最后一个 GPU 动作调度，最大化 CPU/GPU 重叠；投机解码与 prefill-only 是明确排除项。
- 下一章：token 已经选出，看它如何流回用户的屏幕。
