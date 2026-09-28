---
title: "附录 A 推荐阅读路径"
---

# 附录 A 推荐阅读路径

> 按「你想干什么」选择入口，而不是按目录顺序硬读。每条路径给出最小阅读集与对应源码文件。

## 路径一：快速理解整体（半天）

目标：建立能复述的心智模型。

1. 第 1 章（定位与黄金路径图）；
2. 第 3 章（三进程拓扑）；
3. 第 6 章（调度循环四种动作）；
4. 对照源码通读 `srt/managers/scheduler.py:1906–2082` 的两个事件循环。

## 路径二：核心机制深挖（三到五天）

目标：能沿调用链解释一次请求的每个跳转。

1. 第 4、5 章（入口与 TokenizerManager）；
2. 第 7、8 章（PrefillAdder 预算与批张量化）；
3. 第 9 章（RadixCache 全生命周期），对照 `srt/mem_cache/radix_cache.py:354–619`；
4. 第 10、11、12 章（执行、采样、回程）；
5. 每章末「本章收束」作为自测清单。

## 路径三：调度与性能调优（两天）

目标：理解每个调优参数改了哪段代码的行为。

- `chunked_prefill_size` / `max_prefill_tokens` → 第 7 章（`srt/arg_groups/fields/schedule.py:52` 与 `:71`）；
- `schedule_policy`（fcfs/lpm/hrrn…）→ 第 7 章 `policy.calc_priority`；
- `retraction_policy` / `schedule_conservativeness` → 第 6 章 retract 流程；
- `stream_interval` → 第 12 章（`srt/arg_groups/fields/serving.py:255`）;
- overlap 调度 → 第 6 章 6.5 节的张量保全机制。

## 路径四：扩展开发（三天）

目标：为 SGLang 贡献一个后端/模型/策略。

- 注意力后端：第 10 章 + `srt/layers/attention/attention_registry.py`（注册装饰器）与 `base_attn_backend.py`（接口）；
- 前缀缓存变体：第 9 章 + `srt/mem_cache/base_prefix_cache.py`（接口）；
- 模型接入：第 8 章（ForwardMode 与批张量约定）+ `srt/models/` 现有实现；
- 网关策略：第 15 章 + `sgl-model-gateway/src/policies/factory.rs`。

## 路径五：生产运维（一天）

目标：知道系统在过载/故障下的行为边界。

1. 第 6 章 6.3 节（retract：过载时先变慢不崩溃）；
2. 第 3 章 3.3 节（看门狗与失败传播）；
3. 第 12 章 12.6 节（输出侧已知竞态）；
4. 第 14 章（PD 分离的传输失败边界）；
5. 第 15 章（负载与 KV 事件的采集点，用于监控接入）。
