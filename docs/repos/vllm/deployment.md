---
title: 部署形态与可观测性
weight: 150
---

# 部署形态与可观测性

> 本章回答：前十章的组件在生产中以什么进程拓扑组装，健康与性能如何观测，故障会在哪里暴露。

## 常见部署拓扑

把前面的组件组装起来，得到三种典型部署形态：

::: mermaid
flowchart TB
    subgraph S1["单机单卡（最简）"]
        A1["API 进程<br/>AsyncLLM + InprocClient/MPClient"] --> E1["EngineCore 进程"]
        E1 --> W1["Worker（UniProcExecutor）<br/>GPU 0"]
    end
    subgraph S2["单机多卡（TP）"]
        A2["API 进程"] --> E2["EngineCore 进程"]
        E2 --> M["MultiprocExecutor"]
        M --> W2["Worker × N<br/>GPU 0..N-1"]
    end
    subgraph S3["多机（TP + PP / DP）"]
        A3["API 进程 ×1"] --> E3["EngineCore 进程"]
        E3 --> R["RayDistributedExecutor"]
        R --> W3["Worker（跨节点 Ray actor）"]
    end
:::

三条部署轴相互正交，可以按需叠加：

- **API 进程数**：`--api-server-count` 支持多个 API 进程共享一组 EngineCore（`entrypoints/cli/serve.py:68` 附近的参数处理），协议处理与渲染是纯 CPU 工作，可以独立扩容；
- **DP**：`--data-parallel-size` 起 N 套 EngineCore，各带自己的调度与模型副本；API 侧按各 rank 的排队长度做负载均衡（第 5 章提到的 `publish_dp_lb_stats`，`vllm/v1/engine/core.py:1483`）；
- **执行器后端**：单机默认 MultiprocExecutor，跨机用 Ray（`vllm/v1/executor/abstract.py:64`）。

## 生命周期控制

部署态需要的启停原语都挂在 `EngineClient` 上，由 EngineCore 逐级转发到 Worker：

- **睡眠与唤醒**：`AsyncLLM.sleep()`（`vllm/v1/engine/async_llm.py:1096`）/`wake_up()`——让引擎释放显存给其他进程（如权重更新后的重新加载），`level` 参数区分释放 KV 还是连同模型权重；
- **profile 开关**：`start_profile`/`stop_profile`（`:1067`）包装 torch profiler；
- **准停**：`pause_generation`/`resume_generation`（`:914`），对应调度器的 `PauseState`；
- **健康检查**：`check_health()`（`:1062`）——AsyncLLM 侧仅检查内部错误标志，真正的存活由 ZMQ 通道的活性保证。

## 指标体系

可观测性三件套各归其位：

1. **Prometheus 指标**：`vllm/v1/metrics/loggers.py` 定义 `StatLoggerBase`（`:49`），`output_handler` 每步调用 `record()`（`async_llm.py` 的 output 循环末尾）喂入迭代统计（TTFT、每步 token 数、缓存命中）与调度统计（队列长度、KV 使用率，`SchedulerStats` 由 `run_busy_loop` 的 `_maybe_publish_request_counts` 主动推送，`core.py:1483`）。指标注册在 `v1/metrics/prometheus.py`，桶配置在 `buckets.py`；
2. **KV 事件流**：调度器周期性从 `KVCacheManager.take_events()`（`vllm/v1/core/kv_cache_manager.py:716`）取块存储/移除事件，经 `EventPublisherFactory`（`vllm/v1/core/sched/scheduler.py:20` 的导入）对外发布——供外部缓存网关感知哪些前缀已缓存；
3. **结构化日志**：`log_stats` 系列方法输出吞吐统计行，供日志管道采集。

指标插件化：`load_stat_logger_plugin_factories()`（`v1/metrics/loggers.py:79`）允许插件注入自定义 stat logger，与第 13 章的 plugin 机制同源。

## 故障会在哪里暴露

结合进程模型，故障有明确的暴露面：

- **Worker 崩溃**（CUDA OOM、非法访存）：`MultiprocExecutor` 的 RPC 超时（`VLLM_EXECUTE_MODEL_TIMEOUT_SECONDS`，`multiproc_executor.py:348`）触发，EngineCore 报错退出，API 进程经 ZMQ 感知 `EngineCoreProc` 死亡并返回 5xx——进程隔离保证了 API 不会僵死；
- **EngineCore 崩溃**：`BackgroundResources.validate_alive()`（`core_client.py:543`）在读消息时校验 ZMQ 帧，死连接转化为 `AsyncLLM.errored` 状态，健康检查随之失败；
- **抢占风暴**：KV 使用率长期顶着 watermark、频繁 recompute——这是调度层症状，只能靠 Prometheus 的 KV usage 与抢占计数发现，需要扩容或调 `gpu_memory_utilization`。

值得注意的是 vLLM 不做引擎内的请求持久化：进程崩溃即丢失全部在途请求，重试语义留给客户端——这是"调度器状态全部在内存"设计的直接代价。

## 本章收束

- 部署 = API 进程数 × DP 规模 × 执行器后端三个正交选择，组件不因形态改变职责；
- 观测三件套：Prometheus（每步统计）、KV 事件流（外部网关）、结构化日志；指标与事件都从调度器/输出处理器单点流出；
- 故障暴露面与进程边界一致：Worker 死于执行超时、EngineCore 死于调度异常、API 进程只优雅降级。

至此正文章节结束。附录提供按读者目标组织的阅读路径、核心符号速查与术语表。
