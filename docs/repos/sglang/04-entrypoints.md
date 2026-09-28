---
title: "第 4 章 HTTP 入口与 OpenAI 兼容层"
---

# 第 4 章 HTTP 入口与 OpenAI 兼容层

> 本章回答：一个 `/v1/chat/completions` 请求如何变成内部的 `GenerateReqInput`？流式响应在哪里被组装？OpenAI 兼容层与原生 `/generate` 接口是什么关系？

## 4.1 两层入口

SRT 对外有两层接口：

1. **原生接口**&#8203;：`/generate`（`srt/entrypoints/http_server.py:915`）、`/encode`、`/classify` 等，暴露 SRT 的全部能力（logprobs、hidden states、自定义采样掩码等）；
2. **兼容接口**&#8203;：`srt/entrypoints/openai/` 下的 OpenAI 协议族（`/v1/chat/completions`、`/v1/completions`、`/v1/responses`…），以及 Anthropic、Ollama 兼容层。

兼容层不是简单转发：`srt/entrypoints/http_server.py:281` 的 `lifespan` 中，每个兼容 endpoint 都绑定了一个 `OpenAIServing*` 对象，它们在内部把 OpenAI 格式的请求翻译成 `GenerateReqInput`，调用与 `/generate` 相同的 `TokenizerManager.generate_request`。

机制解释：这种「协议适配器 + 单一引擎入口」的结构意味着协议差异（消息格式、工具调用、多轮状态）全部在 `OpenAIServing*` 内消化，调度器与执行层完全不感知协议。

## 4.2 /generate 路由

原生入口非常薄（`srt/entrypoints/http_server.py:910` 附近）：

```python
@app.api_route("/generate", methods=["POST", "OPTIONS"])
async def generate_request(obj: GenerateReqInput, request: Request):
    ...
    async def stream_results() -> AsyncIterator[bytes]:
        ...
```

`GenerateReqInput`（`srt/managers/io_struct.py:177`）是原生协议的核心对象，支持批量（`is_single` 为 False 时 `rid` 是列表）。校验由 FastAPI 的 Pydantic 模型完成；自定义异常处理器把校验错误转成 SGLang 风格的 JSON 错误体（`http_server.py:556` 与 `:613`）。大体积请求（多模态可达数十 MB）走 `ORJSONRequest`（`http_server.py:453` 的类定义），用 orjson 替换 stdlib json 解析，并在裸 NaN/Infinity 与超范围整数上返回 400。

## 4.3 OpenAIServingChat：把消息翻译成 prompt

`srt/entrypoints/openai/serving_chat.py:265` 的 `OpenAIServingChat` 是 OpenAI 协议的主翻译官。它的职责链：

1. 应用 chat template 把 `messages` 数组渲染成 prompt 文本（模板来自 `TemplateManager`）；
2. 解析推理模型的前后缀标记（reasoning parser）；
3. 采样参数从 OpenAI 语义映射到 `SamplingParams`；
4. 按 `stream` 标志分流到非流式或流式生成器。

流式分支入口在 `serving_chat.py:1876` 的 `_handle_streaming_request` → `:1904` 的 `_generate_chat_stream`。它消费 TokenizerManager 的流式输出，把每个 delta 包装成 OpenAI 的 `chat.completion.chunk` 事件序列（role delta → content/reasoning delta → tool call delta → finish → `[DONE]`）。

## 4.4 一个最小心智模型

把第 3、4 章合起来，请求在进入调度器之前经历了这样的变换：

::: mermaid
flowchart LR
    A["OpenAI /chat/completions"] --> B["OpenAIServingChat<br/>模板渲染 + 参数映射"]
    C["/generate"] --> D["直接使用 GenerateReqInput"]
    B --> E["GenerateReqInput"]
    E --> F["TokenizerManager.generate_request<br/>(srt/managers/tokenizer_manager.py:854)"]
    D --> F
:::

值得注意的边界：兼容层在本层做的是&#8203;**文本级**&#8203;工作（模板、格式、协议），不做任何与 GPU 或调度相关的决策；它也不缓存对话状态——多轮对话的历史由客户端每次重发，服务端靠 RadixCache 复用公共前缀的 KV（第 9 章），这是无状态协议与有状态缓存的配合点。

## 4.5 本章收束

- 两层入口共享同一个引擎入口 `TokenizerManager.generate_request`；OpenAI/Anthropic/Ollama 兼容层是纯协议适配器。
- `/generate` 是薄路由，校验交给 Pydantic，异常统一转 JSON。
- 流式响应对兼容层是 SSE 事件重组，对原生层是直接透传 TokenizerManager 的流式片段。
- 下一章进入 TokenizerManager 本体：请求如何被分词、发出、等待、流式回传。
