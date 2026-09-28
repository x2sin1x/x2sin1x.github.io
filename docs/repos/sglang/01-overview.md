---
title: "第 1 章 定位与心智模型"
---

# 第 1 章 定位与心智模型

> 本章回答：SGLang 的仓库里到底住着几个系统？我们常说的「SGLang 服务」指哪一个？一次生成请求的端到端路径长什么样？这是全书后续章节的坐标系。

## 1.1 一个仓库，三个系统

从仓库顶层目录看，SGLang 并不是一个单一的推理引擎，而是至少三个可以独立服役的系统：

1. **SRT（SGLang Runtime）**&#8203;：`python/sglang/srt/` 下的推理服务运行时，也是本卷的主角。它把一个模型权重变成一个多进程、支持流式与并发批处理的 HTTP/gRPC 推理服务。
2. **路由网关**&#8203;：`sgl-model-gateway/`（Rust）与 `experimental/sgl-router/`，负责把请求分发到多个 SRT 实例，实现负载均衡、缓存感知路由与 KV 事件订阅。
3. **前端 DSL 与周边工具**&#8203;：`python/sglang/lang/`（早期的前端编程语言）、`benchmark/`、`test/`、`rust/`（Rust 实现的服务端实验）等。

本卷的分析范围以 SRT 为主，网关在第 15 章单独展开。这样取舍的依据是依赖方向：网关消费 SRT 暴露的负载统计与 KV 事件接口，理解 SRT 是理解网关行为的前提。

## 1.2 SRT 的核心问题

SRT 解决的问题是：&#8203;**在 GPU 显存有限的约束下，把并发生成请求尽量高效地塞进每一次前向计算**&#8203;。它的一切关键设计都可以还原为三个互相牵制的量：

- **单次前向能容纳多少 token**&#8203;（`max_prefill_tokens`、`chunked_prefill_size`，见第 7 章）；
- **同时能跑多少条序列**&#8203;（`max_running_requests`、KV 池大小，见第 9 章）；
- **每条序列为未来的输出 token 预留多少空间**&#8203;（`retract_decode` 的触发条件，见第 6 章）。

srt/arg_groups/fields/schedule.py:98 中调度策略默认值是 `"fcfs"`，可选 `lpm`（最长前缀匹配）、`hrrn` 等；srt/arg_groups/fields/schedule.py:71 中 `max_prefill_tokens` 默认 16384。这些是调度器的初始约束，真正的动态决策在运行时完成。

## 1.3 黄金路径：一次请求的端到端旅程

SRT 默认形态是一个多进程结构。`srt/entrypoints/http_server.py:2871` 的 `launch_server` 文档字符串直接给出了官方定义：

> The SRT server consists of an HTTP server and an SRT engine. …
> 1. TokenizerManager: Tokenizes the requests and sends them to the scheduler.
> 2. Scheduler (subprocess): Receives requests from the Tokenizer Manager, schedules batches, forwards them, and sends the output tokens to the Detokenizer Manager.
> 3. DetokenizerManager (subprocess): Detokenizes the output tokens and sends the result back to the Tokenizer Manager.

即：HTTP 服务与 TokenizerManager 同进程，Scheduler 与 DetokenizerManager 各占一个子进程，进程间用 ZMQ 通信。这条结构是全书的主轴：

::: mermaid
sequenceDiagram
    participant C as 客户端
    participant H as HTTP (FastAPI)
    participant T as TokenizerManager
    participant S as Scheduler 子进程
    participant M as ModelRunner (GPU)
    participant D as Detokenizer 子进程

    C->>H: POST /generate 或 /v1/chat/completions
    H->>T: GenerateReqInput
    T->>S: TokenizedGenerateReqInput (ZMQ)
    Note over S: 入等待队列，调度为 prefill/decode batch
    S->>M: forward_batch_generation
    M-->>S: logits / next_token_ids
    S->>D: BatchTokenIDOutput (ZMQ)
    D->>T: BatchStrOutput (ZMQ，增量反分词)
    T-->>H: 流式/整段结果
    H-->>C: SSE 流或 JSON
:::

后续章节沿这条链展开：第 4、5 章覆盖上半程（HTTP 与 TokenizerManager），第 6–9 章覆盖调度与内存（Scheduler 的两难权衡），第 10–12 章覆盖执行与输出（ModelRunner、采样、反分词），第 13–15 章覆盖多机与生态。

## 1.4 与同类系统的一个关键差异点

源码直接可见、也是 SGLang 最具辨识度的机制是 **RadixCache 前缀缓存**&#8203;：所有请求的 KV cache 按前缀组织成一棵基数树（radix tree），公共前缀（系统提示词、few-shot、多轮对话历史）只计算一次，命中后直接复用树中已有的 KV 物理槽位。srt/mem_cache/radix_cache.py:354 的 `match_prefix` 与第 9 章将展开的 `insert` / `evict` / `inc_lock_ref` 构成了这一机制的全部核心。它与调度深度耦合——`PrefillAdder` 决定「下一个请求要不要现在 prefill」时，预算计算就要考虑树中可淘汰的 token 数量（见第 7 章）。

## 1.5 事实、解释与推断的边界

本系列严格区分三类叙述，并在正文中用固定措辞标注：

- **「源码显示」**&#8203;：代码、配置或测试直接可见的事实；
- **「机制解释」**&#8203;：对多处事实的归纳，例如「chunked prefill 的目的是让长 prompt 的 prefill 不阻塞 decode」属于此类，依据是 `chunked_req` 在调度循环中的处理方式；
- **「可以推断」**&#8203;：合理但项目未直接声明的结论，例如某设计动机，会明确标注。

涉及性能数字的部分，本卷一律不引用（快照仓库中 benchmark/ 目录的数字依赖特定硬件与版本，复现口径不在本书范围内）。

## 1.6 本章收束

- SGLang = SRT 运行时（Python，本卷主体）+ Rust 路由网关 + 前端 DSL 与工具链；三者通过 HTTP/gRPC 与 ZMQ 接口衔接。
- SRT 的默认进程形态是「HTTP + TokenizerManager | Scheduler | DetokenizerManager」三进程，ZMQ 串联。
- 全书的黄金路径是 `/generate` 请求从 TokenizerManager 进入 Scheduler，经 prefill/decode 批调度、RadixCache 命中、ModelRunner 前向、采样、增量反分词后流式返回。
- 下一章先建立仓库地图，让这条链上的每个符号都能对应到一个目录。
