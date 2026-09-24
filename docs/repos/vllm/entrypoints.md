---
title: 三类入口：LLM、OpenAI Server 与 CLI
weight: 40
---

# 三类入口：LLM、OpenAI Server 与 CLI

> 本章回答：用户可以通过哪些入口使用 vLLM，三类入口如何收敛到同一个 `EngineClient` 接口，入口层各自做了哪些不可省略的前置工作。

## EngineClient：入口层的共同契约

三个入口最终都指向同一个抽象：`EngineClient`（`vllm/engine/protocol.py:43`）。它声明了 `add_request`、`generate`、`abort`、`check_health` 等接口；两个实现分别是离线同步的 `LLMEngine` 与在线异步的 `AsyncLLM`。入口层的选择只决定"用哪个实现、做多少协议加工"，不触碰调度与执行。

::: mermaid
flowchart TB
    CLI["vllm serve<br/>entrypoints/cli/serve.py"] --> RS["run_server<br/>launchers/api_server/entry.py"]
    PY["from vllm import LLM<br/>entrypoints/llm.py"] --> LE["LLMEngine<br/>v1/engine/llm_engine.py"]
    SERVE["FastAPI 路由<br/>chat_completion/serving.py"] --> BAC["build_async_engine_client<br/>launchers/api_server/entry.py:36"]
    RS --> BAC
    BAC --> AL["AsyncLLM<br/>v1/engine/async_llm.py:80"]
    LE --> CORE["EngineCoreClient"]
    AL --> CORE
:::

## 离线入口：LLM 类

`LLM`（`vllm/entrypoints/llm.py:67`）是离线批量推理的门面。它的 `__init__` 做三件事：把用户参数解析成 `VllmConfig`、通过 `LLMEngine.from_engine_args()`（`llm.py:343`）拉起引擎、记录 usage 遥测上下文。`generate()`（`llm.py:419`）则是同步循环——它内部就是反复调用 `LLMEngine.step()`（`vllm/v1/engine/llm_engine.py:305`）直到所有请求完成。

`LLMEngine` 是 V1 中离线路径的编排者：它同样持有 `EngineCoreClient`，只是用阻塞式调用代替事件循环。离线与在线因此共享同一套 EngineCore 逻辑，差异只被压缩在客户端封装层。

## 在线入口：vllm serve 与 FastAPI

`vllm serve` 命令（`vllm/entrypoints/cli/serve.py`）把 CLI 参数交给 `run_server`（`vllm/entrypoints/launchers/api_server/entry.py:160`），后者最终调用 `build_async_engine_client()`（`entry.py:36`）。这个 async 上下文管理器先处理多进程启动方式（forkserver 预导入 `vllm.v1.engine.async_llm`），再构造 `AsyncEngineArgs` 并委托 `from_engine_args` 拉起 `AsyncLLM`。

FastAPI 应用由 `build_app` 组装，路由集中在 `entrypoints/launchers/api_server/routers.py:12` 的 `register_api_routers()` 中注册。业务处理器按模态拆分：chat 补全在 `entrypoints/openai/chat_completion/serving.py`，其 `OpenAIServingChat`（`:118`）继承 `GenerateBaseServing`；后者在构造时直接持有 `engine_client` 并暴露 `renderer` 与 `input_processor`（`entrypoints/generate/base/serving.py:155`），所有模态共享同一条 `engine_client.generate()` 下行路径。

## 入口层的前置工作：渲染与输入处理

入口层在把请求交给引擎前，必须完成协议 → 引擎输入的转换：

1. **prompt 渲染**：`renderers/` 模块把 OpenAI 协议的 messages 数组套用聊天模板、调用 tokenizer、插入多模态占位。渲染结果附带多模态特征（`mm_features`）；
2. **输入处理**：`InputProcessor`（`vllm/v1/engine/input_processor.py:41`）校验并固化 `EngineCoreRequest`——它拥有独立的 `process_inputs()`（`:324`），使这部分工作可以脱离事件循环并发执行；
3. **准入检查**：`GenerateBaseServing` 在创建请求前调用 `engine_client.check_admission(n)`（`serving.py:186`），配合 `AsyncLLM.check_admission`（`async_llm.py:307`）实现服务端准入控制。

这三步都在 **API 进程**完成。EngineCore 收到的 `EngineCoreRequest` 已是 token id 列表 + 采样参数 + 多模态特征的扁平结构，不需要再访问 tokenizer。

## 一个容易误读的边界

`LLM` 与 `AsyncLLM` 不是"同步版和异步版的同一层"。`AsyncLLM` 额外承担了流式输出分发（`_run_output_handler` 后台任务，`async_llm.py:791`）、多引擎（DP）输出路由与 `RequestOutputCollector` 管理；`LLMEngine` 则在 `step()` 返回完整 `RequestOutput` 列表。若在事件循环里误用 `LLM`，它的阻塞 step 会卡死整个循环——这也是文档建议在线场景用 `AsyncLLM` 的原因（`entrypoints/llm.py:176` 附近的类注释）。

## 本章收束

- 三类入口收敛于 `EngineClient` 协议；离线用 `LLMEngine`（同步 step 循环），在线用 `AsyncLLM`（事件循环 + 后台 output handler）；
- `vllm serve` 的启动链是 `cli/serve.py → run_server → build_async_engine_client → AsyncLLM`，注意 `entrypoints/openai/api_server.py` 已是弃用的转发壳；
- 渲染、tokenize、多模态预处理、准入检查都发生在 API 进程，EngineCore 只消费扁平的 token 序列。

下一章穿过进程边界，看 `AsyncLLM` 与 `EngineCore` 之间到底跑了什么消息。
