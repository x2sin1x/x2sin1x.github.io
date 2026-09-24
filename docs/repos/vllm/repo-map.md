---
title: 仓库地图与模块边界
weight: 30
---

# 仓库地图与模块边界

> 本章回答：约 170 万行 Python（另有 Rust、CUDA、C++）的 vLLM 仓库由哪些顶层区域组成，每个模块一句话职责是什么，依赖方向朝哪边流动。

## 顶层区域一览

```text
vllm/                  Python 包主体（约 3150 个文件）
├── entrypoints/       所有外部入口：CLI、离线 LLM、OpenAI 兼容 API、渲染器
├── engine/            引擎配置工具与兼容壳（arg_utils、旧版 async_llm_engine）
├── config/            全部配置类型（VllmConfig 及其子配置）
├── v1/                V1 引擎本体：调度、KV 管理、worker、采样、投机解码
├── distributed/       并行与通信：parallel_state、自定义 allreduce、KV 传输
├── model_executor/    模型执行：模型实现、层实现、权重加载、量化
├── models/            新一代模型实现（deepseek_v32、kimi_k3、qwen4_exp 等）
├── multimodal/        多模态输入处理与注册表
├── platforms/         硬件平台抽象（cuda、rocm、tpu、xpu、cpu）
├── plugins/           插件加载机制
├── renderers/         prompt 渲染：聊天模板 + tokenizer + 多模态占位
├── tokenizers/        tokenizer 实现（含 Rust 绑定封装）
├── compilation/       torch.compile 包装与 CUDA Graph 管理
├── kernels/           Triton / Aiter 等算子
├── inputs/            ProcessorInput 等输入数据结构
├── vllm_flash_attn/   内嵌 FlashAttention 绑定
├── lora/ reasoning/ tool_parsers/ structured-output 相关支撑模块
└── utils/ usage/ profiling/ logging_utils/ 通用工具与遥测
csrc/                  CUDA/C++ 算子源码（约 320 个文件）
rust/                  Rust 重写面：server、tokenizer、engine-core-client 等
tests/                 约 2230 个测试文件
benchmarks/ examples/ docs/   基准、示例与文档
```

## 核心模块与依赖方向

::: mermaid
flowchart LR
    E["entrypoints<br/>入口与协议"] --> ENG["v1/engine<br/>AsyncLLM / LLMEngine"]
    ENG --> C["v1/engine/core<br/>EngineCore"]
    C --> S["v1/core/sched<br/>Scheduler"]
    C --> X["v1/executor<br/>执行器"]
    S --> KV["v1/core + kv_*<br/>KVCacheManager"]
    X --> W["v1/worker<br/>GPUModelRunner"]
    W --> ATT["v1/attention<br/>attention 后端"]
    W --> ME["model_executor<br/>模型与层实现"]
    ME --> M["model_executor/models<br/>+ models/"]
    W --> D["distributed<br/>parallel_state / allreduce"]
    C --> CFG["config<br/>VllmConfig"]
    S --> SO["v1/structured_output<br/>文法约束"]
    S --> SD["v1/spec_decode<br/>投机解码"]
    C --> KVT["distributed/kv_transfer<br/>KV Connector"]
:::

依赖方向整体是单向的：入口层 → 引擎编排层 → 调度/执行层 → 模型与算子层。`config/` 是被所有人依赖的叶子模块；`distributed/` 被 Worker 与 EngineCore 双向使用（TP 通信组在两侧都要初始化）。

值得点名的几个模块：

- **`v1/engine/`**：`async_llm.py`（在线服务引擎）、`llm_engine.py`（离线同步引擎，`vllm/entrypoints/llm.py:343` 被引用）、`output_processor.py` 与 `detokenizer.py`（API 进程侧的输出恢复）。注意旧的 `vllm/entrypoints/openai/api_server.py` 已改为转发壳，新位置在 `vllm/entrypoints/launchers/api_server/`（`api_server.py:23` 的 DeprecationWarning）。
- **`v1/core/`**：调度器与 KV 元数据。`kv_cache_manager.py` 是 Scheduler 的 KV 账本，`block_pool.py` 是物理块池。
- **`v1/worker/gpu_model_runner.py`**：单文件 7500+ 行，是全仓库最重的文件——持久批次管理、attention metadata 构建、CUDA Graph 分发都住在这里。
- **`model_executor/`**：`models/` 子目录是各模型的前向实现；`layers/` 是可替换的算子层（`layers/quantization/` 存放全部量化方法）；`model_loader/` 是权重加载框架。
- **`rust/`**：与 Python 并行的 Rust 实现面（server、tokenizer、engine-core-client 等 15 个 crate），是快照中的进行时工作，正文只在入口章节提及，不作为主证据。

## tests 目录与源码的对应

测试目录结构基本镜像源码，几个值得作为"可观察契约"阅读的位置：

- `tests/v1/core/test_scheduler.py`——调度行为的细粒度断言；
- `tests/v1/core/test_prefix_caching.py`——前缀缓存命中与淘汰契约；
- `tests/v1/engine/test_output_processor.py`——流式输出语义；
- `tests/v1/worker/test_gpu_model_runner.py`——模型执行路径。

## 本章收束

- 仓库的骨架是"入口 → 引擎 → 调度 → 执行 → 模型"的单向依赖链，`config/` 与 `distributed/` 是两个横向公共模块；
- 找任何功能先问"它在 EngineCore 进程还是 Worker 进程"，目录归属基本由进程归属决定；
- `vllm/entrypoints/openai/api_server.py` 已是转发壳，新入口代码在 `entrypoints/launchers/`——读旧文章时注意这一漂移。

下一章进入入口层，看三类入口如何收敛到同一个 `EngineClient` 接口。
