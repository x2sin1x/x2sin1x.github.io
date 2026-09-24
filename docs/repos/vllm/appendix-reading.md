---
title: 附录 A：推荐阅读路径
weight: 160
---

# 附录 A：推荐阅读路径

不同读者带着不同问题进入 vLLM 源码。下表按读者目标组织章节与源码入口，避免按目录顺序平铺。

## 我想理解"为什么它快"

| 顺序 | 材料 | 回答什么 |
|---|---|---|
| 1 | [第 1 章：定位与总体架构](/repos/vllm/overview) | 进程模型与请求生命周期 |
| 2 | [第 6 章：调度器](/repos/vllm/scheduler) | 连续批处理与统一 token 视角 |
| 3 | [第 7 章：PagedAttention 与 KV Cache](/repos/vllm/kv-cache) | 块池、前缀缓存、淘汰 |
| 4 | [第 8 章：GPUModelRunner](/repos/vllm/model-runner) | 持久批次与 CUDA Graph |

配合源码：`vllm/v1/core/sched/scheduler.py` 的 `schedule()` 与开头注释；`vllm/v1/core/kv_cache_utils.py` 的 `hash_block_tokens`；`vllm/v1/worker/gpu_model_runner.py` 的 `_update_states`。

## 我想贡献调度或 KV 相关代码

1. 先按上面路径建立模型；
2. [第 5 章：AsyncLLM 与 EngineCore](/repos/vllm/engine-core)——搞清状态归属进程；
3. [第 9 章：Attention 后端体系](/repos/vllm/attention)——KV 形状如何被后端改写；
4. 测试即契约：`tests/v1/core/test_scheduler.py`、`tests/v1/core/test_prefix_caching.py`、`tests/v1/kv_offload/`。

## 我想做服务化集成（网关、PD 分离、KV 缓存）

| 顺序 | 材料 | 回答什么 |
|---|---|---|
| 1 | [第 4 章：三类入口](/repos/vllm/entrypoints) | EngineClient 协议与渲染边界 |
| 2 | [第 10 章：采样与流式输出](/repos/vllm/sampling-output) | 流式语义与背压契约 |
| 3 | [第 13 章：扩展点全景](/repos/vllm/extensions) | KV Connector 协议 |
| 4 | [第 14 章：部署形态与可观测性](/repos/vllm/deployment) | 指标与 KV 事件流 |

源码入口：`vllm/distributed/kv_transfer/kv_connector/v1/base.py`（Connector 协议）、`vllm/v1/distributed/kv_events.py`（事件发布）、`vllm/entrypoints/launchers/api_server/`（服务装配）。

## 我想适配新硬件或新模型

1. [第 9 章：Attention 后端体系](/repos/vllm/attention)——能力声明协议；
2. [第 13 章：扩展点全景](/repos/vllm/extensions)——Platform 与 Plugin 注册时机；
3. [第 11 章：模型加载与量化](/repos/vllm/model-loading)——层实现与量化 config 协议；
4. 源码入口：`vllm/platforms/interface.py`、`vllm/plugins/__init__.py`、`vllm/model_executor/layers/quantization/`。

## 我想做投机解码研究

1. [第 6 章](/repos/vllm/scheduler) 与 [第 12 章：投机解码](/repos/vllm/spec-decode)——统一调度模型如何吸收草稿 token；
2. 源码入口：`vllm/v1/spec_decode/`（提案者家族）、`vllm/v1/sample/rejection_sampler.py`（验证）、`vllm/v1/worker/gpu_model_runner.py` 的 `take_draft_token_ids`。

## 排查生产问题

直接读 [第 14 章：部署形态与可观测性](/repos/vllm/deployment)，再按症状跳转：吞吐低读 [第 6 章](/repos/vllm/scheduler)（预算与抢占），延迟毛刺读 [第 8 章](/repos/vllm/model-runner)（CUDA Graph 与 padding），KV 相关读 [第 7 章](/repos/vllm/kv-cache)。
