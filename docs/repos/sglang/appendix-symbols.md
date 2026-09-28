---
title: "附录 B 核心符号速查"
---

# 附录 B 核心符号速查

> 符号按黄金路径顺序排列。路径缩写约定见第 2 章（`srt/…` = `python/sglang/srt/…`），行号锚定 commit `65824258549671404188450748b90ab7cacab2ae`。

## 入口与进程

| 符号 | 职责 | 位置 | 相关章节 |
| --- | --- | --- | --- |
| `run_server` | CLI 模式分派 | `python/sglang/launch_server.py:19` | 3 |
| `launch_server` | SRT 服务器总装 | `srt/entrypoints/http_server.py:2871` | 3 |
| `Engine._launch_subprocesses` | 拉起三进程 | `srt/entrypoints/engine.py:1065` | 3 |
| `lifespan` | FastAPI 运行时装配 | `srt/entrypoints/http_server.py:281` | 3、4 |
| `generate_request`（HTTP） | `/generate` 路由 | `srt/entrypoints/http_server.py:915` | 4 |
| `OpenAIServingChat` | OpenAI 协议翻译 | `srt/entrypoints/openai/serving_chat.py:265` | 4 |

## 请求与状态

| 符号 | 职责 | 位置 | 相关章节 |
| --- | --- | --- | --- |
| `GenerateReqInput` | 原生请求对象 | `srt/managers/io_struct.py:177` | 4、5 |
| `TokenizerManager.generate_request` | 请求总入口（async generator） | `srt/managers/tokenizer_manager.py:854` | 5 |
| `TokenizerManager.handle_loop` | 结果事件循环 | `srt/managers/tokenizer_manager.py:2332` | 5 |
| `_handle_batch_output` | meta 组装与流式唤醒 | `srt/managers/tokenizer_manager.py:2347` | 5、12 |
| `TokenizedGenerateReqInput` | 下行 ZMQ 消息 | `srt/managers/io_struct.py:1041` | 5 |
| `Req` | 单请求调度状态 | `srt/managers/schedule_batch.py:999` | 8 |

## 调度

| 符号 | 职责 | 位置 | 相关章节 |
| --- | --- | --- | --- |
| `Scheduler.event_loop_normal` | 同步主循环 | `srt/managers/scheduler.py:1906` | 6 |
| `Scheduler.event_loop_overlap` | 重叠主循环 | `srt/managers/scheduler.py:1941` | 6 |
| `get_next_batch_to_run` | 选批决策汇总 | `srt/managers/scheduler.py:3641` | 6 |
| `update_running_batch` | decode 批维护与 retract 触发 | `srt/managers/scheduler.py:4191` | 6 |
| `get_new_batch_prefill` | prefill 装批入口 | `srt/managers/scheduler.py:3804` | 7 |
| `PrefillAdder` / `add_one_req` | 装批与预算 | `srt/managers/schedule_policy.py:621` / `:1347` | 7 |
| `ScheduleBatch.retract_decode` | 收回请求 | `srt/managers/schedule_batch.py:3291` | 6 |
| `prepare_for_extend` / `prepare_for_decode` | 批张量化 | `srt/managers/schedule_batch.py:2722` / `:3551` | 8 |
| `ForwardMode` | 前向语义枚举 | `srt/model_executor/forward_batch_info.py:193` | 8 |
| `ForwardBatch` | 执行期张量视图 | `srt/model_executor/forward_batch_info.py:488` | 8 |
| `BatchTokenIDOutput` / `BatchStrOutput` | 上行 ZMQ 消息 | `srt/managers/io_struct.py:1526` / `:1627` | 12 |

## 内存与缓存

| 符号 | 职责 | 位置 | 相关章节 |
| --- | --- | --- | --- |
| `RadixCache.match_prefix` | 前缀命中 | `srt/mem_cache/radix_cache.py:354` | 9 |
| `RadixCache.insert` | 前缀写回 | `srt/mem_cache/radix_cache.py:414` | 9 |
| `RadixCache.cache_unfinished_req` | chunk/在途写回 + 锁切换 | `srt/mem_cache/radix_cache.py:502` | 9 |
| `RadixCache.evict` | 叶子优先淘汰 | `srt/mem_cache/radix_cache.py:553` | 9 |
| `inc_lock_ref` / `dec_lock_ref` | 树节点锁 | `srt/mem_cache/radix_cache.py:583` | 9 |
| `MHATokenToKVPool` | KV 物理池 | `srt/mem_cache/memory_pool.py:1971` | 9 |
| `ReqToToken.alloc/free` | 请求行槽位 | `srt/mem_cache/memory_pool.py:317` / `:360` | 8、9 |

## 执行与采样

| 符号 | 职责 | 位置 | 相关章节 |
| --- | --- | --- | --- |
| `TpModelWorker.forward_batch_generation` | 执行门面 | `srt/managers/tp_worker.py:598` | 8、10 |
| `ModelRunner.forward` / `_forward_raw` | 前向与分派 | `srt/model_executor/model_runner.py:1706` / `:1856` | 10 |
| `ATTENTION_BACKENDS` | 注意力后端注册表 | `srt/layers/attention/attention_registry.py:40` | 10 |
| `Sampler` | 采样 | `srt/layers/sampler.py:109` | 11 |
| `GrammarManager` | 受限解码 FSM 管理 | `srt/constrained/grammar_manager.py:30` | 11 |

## 输出与集群

| 符号 | 职责 | 位置 | 相关章节 |
| --- | --- | --- | --- |
| `process_batch_result` | 结果分派 | `srt/managers/scheduler.py:4765` | 12 |
| `process_batch_result_decode` | decode 账本结算 | `srt/managers/scheduler_components/batch_result_processor.py:921` | 12 |
| `stream_output` | 攒批发往 Detokenizer | `srt/managers/scheduler_components/output_streamer.py:119` | 12 |
| `DetokenizerManager.event_loop` | 反分词循环 | `srt/managers/detokenizer_manager.py:179` | 12 |
| `DataParallelController` | DP 请求分发 | `srt/managers/data_parallel_controller.py:140` | 13 |
| `PrefillBootstrapQueue` | PD bootstrap | `srt/disaggregation/prefill.py:156` | 14 |
| `CacheAwarePolicy` | 缓存感知路由 | `sgl-model-gateway/src/policies/cache_aware.rs` | 15 |
