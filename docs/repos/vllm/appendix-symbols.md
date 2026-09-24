---
title: 附录 B：核心符号速查
weight: 170
---

# 附录 B：核心符号速查

正文引用过的关键符号，按进程归属分组。行号以快照 commit `bbc4ddeca9ece9851aad26f03afc4bab37c6e8df` 为准。

## API 进程

| 符号 | 职责 | 定义位置 | 主要调用者 | 章节 |
|---|---|---|---|---|
| `EngineClient` | 引擎抽象协议 | `vllm/engine/protocol.py:43` | 所有入口 | 4 |
| `build_async_engine_client` | 服务端引擎的 async 工厂 | `vllm/entrypoints/launchers/api_server/entry.py:36` | `vllm serve` | 4 |
| `LLM` | 离线推理门面 | `vllm/entrypoints/llm.py:67` | Python 用户 | 4 |
| `AsyncLLM` | 在线异步引擎 | `vllm/v1/engine/async_llm.py:80` | OpenAI server | 5 |
| `_run_output_handler` | 输出恢复后台任务 | `vllm/v1/engine/async_llm.py:791` | `AsyncLLM` 自身 | 5 |
| `OutputProcessor` | 输出反序列化与流式分发 | `vllm/v1/engine/output_processor.py:464` | output handler | 5, 10 |
| `RequestOutputCollector` | 每请求流式队列（覆盖写） | `vllm/v1/engine/output_processor.py:51` | `AsyncLLM` | 5, 10 |
| `IncrementalDetokenizer` | 增量反词元化 | `vllm/v1/engine/detokenizer.py:31` | `OutputProcessor` | 10 |

## EngineCore 进程

| 符号 | 职责 | 定义位置 | 主要调用者 | 章节 |
|---|---|---|---|---|
| `EngineCoreClient` | 客户端抽象 | `vllm/v1/engine/core_client.py:80` | `AsyncLLM`/`LLMEngine` | 5 |
| `MPClient` / `InprocClient` | 跨进程 / 进程内实现 | `core_client.py:556` / `:343` | 同上 | 5 |
| `EngineCore` | 调度大脑 | `vllm/v1/engine/core.py:111` | — | 5 |
| `EngineCore.step` | 一步调度+执行+收账 | `core.py:633` | busy loop | 5 |
| `EngineCoreProc.run_busy_loop` | EngineCore 主循环 | `core.py:1470` | 进程入口 | 5 |
| `preprocess_add_request` | 请求预处理 | `core.py:1049` | input 队列 | 5 |
| `Scheduler` | 调度器 | `vllm/v1/core/sched/scheduler.py:79` | `EngineCore` | 6 |
| `Scheduler.schedule` | 每步调度决策 | `scheduler.py:557` | `EngineCore.step` | 6 |
| `Scheduler.update_from_output` | 消费执行结果 | `scheduler.py:1967` | `EngineCore.step` | 6 |
| `_preempt_request` | 抢占重算 | `scheduler.py:1539` | `schedule` | 6 |
| `SchedulerOutput` | 每步施工图纸 | `vllm/v1/core/sched/output.py:232` | `schedule` 产出 | 6, 8 |
| `Request` | 调度视角的请求 | `vllm/v1/request.py:60` | EngineCore 全程 | 5, 6 |
| `KVCacheManager` | KV 账本 | `vllm/v1/core/kv_cache_manager.py:131` | `Scheduler` | 7 |
| `KVCacheManager.get_computed_blocks` | 前缀缓存查找 | `kv_cache_manager.py:264` | `schedule` | 7 |
| `KVCacheManager.allocate_slots` | 块分配 | `kv_cache_manager.py:371` | `schedule` | 7 |
| `BlockPool` | 物理块池 | `vllm/v1/core/block_pool.py:134` | `KVCacheManager` | 7 |
| `hash_block_tokens` | 块内容哈希 | `vllm/v1/core/kv_cache_utils.py:649` | 块登记 | 7 |
| `FreeKVCacheBlockQueue` | 空闲块队列 | `kv_cache_utils.py:246` | `BlockPool` | 7 |
| `KVCacheSpec` | 缓存形状声明 | `vllm/v1/kv_cache_interface.py:156` | 各 attention 层 | 7, 9 |
| `StructuredOutputManager` | 文法约束管理 | `vllm/v1/structured_output/__init__.py:36` | `EngineCore` | 13 |
| `grammar_bitmask` | 每步位掩码 | `structured_output/__init__.py:314` | `EngineCore.step` | 13 |

## Worker 进程

| 符号 | 职责 | 定义位置 | 主要调用者 | 章节 |
|---|---|---|---|---|
| `Executor` | 执行器抽象 | `vllm/v1/executor/abstract.py:41` | `EngineCore` | 12 |
| `Executor.get_class` | 后端选择 | `abstract.py:52` | 引擎构造 | 12 |
| `MultiprocExecutor` | 单机多卡执行器 | `vllm/v1/executor/multiproc_executor.py:111` | 默认多卡 | 12 |
| `Worker` | 单 GPU 容器 | `vllm/v1/worker/gpu_worker.py:183` | 执行器 | 8 |
| `Worker.execute_model` | PP 边界 + 前向 | `gpu_worker.py:1198` | 执行器 | 8 |
| `GPUModelRunner` | 持久批次与执行 | `vllm/v1/worker/gpu_model_runner.py:479` | `Worker` | 8 |
| `_update_states` | 批次增量同步 | `gpu_model_runner.py:1192` | `execute_model` | 8 |
| `InputBatch` | 请求元数据槽位 | `vllm/v1/worker/gpu_input_batch.py:90` | runner | 8 |
| `BlockTable` | 块表的 GPU 镜像 | `vllm/v1/worker/block_table.py:57` | runner | 8 |
| `Sampler.forward` | 采样管线 | `vllm/v1/sample/sampler.py:72` | runner | 10 |
| `AttentionBackend` | 后端抽象 | `vllm/v1/attention/backend.py:58` | 注册表 | 9 |
| `get_attn_backend` | 后端选择 | `vllm/v1/attention/selector.py:105` | 引擎初始化 | 9 |
| `FlashAttentionBackend` | 主力后端示例 | `vllm/v1/attention/backends/flash_attn.py:283` | 选择器 | 9 |
| `take_draft_token_ids` | 取回草稿 token | `gpu_model_runner.py:4836` | `EngineCore.post_step` | 12 |

## 横向扩展点

| 符号 | 职责 | 定义位置 | 章节 |
|---|---|---|---|
| `Platform` | 硬件抽象 | `vllm/platforms/interface.py:135` | 13 |
| `load_general_plugins` | 插件发现 | `vllm/plugins/__init__.py:77` | 13 |
| `KVConnectorBase_V1` | KV 传输协议 | `vllm/distributed/kv_transfer/kv_connector/v1/base.py:178` | 13 |
| `get_num_new_matched_tokens` | 外部 KV 查询钩子 | 同上 `:475` | 13 |
| `GroupCoordinator` | 通信原语 | `vllm/distributed/parallel_state.py:424` | 12 |
| `initialize_model_parallel` | 通信组拓扑 | 同上 `:1967` | 12 |
| `get_model_loader` | 加载器分派 | `vllm/model_executor/model_loader/__init__.py:123` | 11 |
| `NgramProposer` | n-gram 提案者 | `vllm/v1/spec_decode/ngram_proposer.py:12` | 12 |
| `EagleProposer` | Eagle 提案者 | `vllm/v1/spec_decode/eagle.py:10` | 12 |
