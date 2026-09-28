---
title: "第 3 章 启动与进程拓扑"
---

# 第 3 章 启动与进程拓扑

> 本章回答：`sglang serve` 之后发生了什么？三个进程如何建立、如何用 ZMQ 连接、启动失败的传播路径是什么？本章是后续所有「进程 A 发给进程 B」叙述的地基。

## 3.1 入口分派

CLI 入口最终落到 `python/sglang/launch_server.py:19` 的 `run_server`。它按配置分派四种模式：

```python
# python/sglang/launch_server.py:19 起（节选）
def run_server(server_args):
    """Run the server based on the gRPC flags and server_args.encoder_only."""
    ...
    if cfg.encoder_only:
        # For encoder disaggregation
        ...
    elif cfg.smg_grpc_mode:
        # Legacy SMG gRPC server ...
        from sglang.srt.entrypoints.grpc_server import serve_grpc
        asyncio.run(serve_grpc(server_args))
    elif cfg.use_ray:
        # Ray mode: HTTP mode with Ray backend.
        ...
    else:
        # Default mode: HTTP mode.
        from sglang.srt.entrypoints.http_server import launch_server
        launch_server(server_args)
```

默认（也是本书覆盖的）分支是最后一支：HTTP 模式。`launch_server` 位于 `srt/entrypoints/http_server.py:2871`，其文档字符串（第 1 章引用过）定义了三进程结构。

## 3.2 进程的拉起

`launch_server` 的第一步是调用 `Engine._launch_subprocesses`（`srt/entrypoints/engine.py:1065`）。该方法完成：

1. **配置与校验**&#8203;：`configure_logger`、`server_args.resolve_once()`、`check_server_args()`，以及自动探测 reasoning/tool-call 解析器（`resolve_auto_parsers`）；
2. **端口分配**&#8203;：`PortArgs.init_new(server_args)` 为进程间通信预留端口；
3. **启动 Scheduler 进程**&#8203;：`_launch_scheduler_processes(server_args, port_args, run_scheduler_process_func)`——TP 并行时会拉起多个 rank 进程（第 13 章）；
4. **启动 Detokenizer 进程并创建 TokenizerManager**&#8203;（主进程内）。

多节点（`node_rank >= 1`）时行为不同：非零节点不运行 Tokenizer，只等 rank 0 的 `ShutdownReq` 广播来停机（`srt/entrypoints/engine.py:1194` 附近的日志可证）。

::: mermaid
flowchart TB
    subgraph main["主进程"]
        CLI["sglang serve / launch_server"]
        HTTP["FastAPI HTTP server"]
        TM["TokenizerManager"]
    end
    subgraph sched["Scheduler 进程（每 TP rank 一个）"]
        S["Scheduler 事件循环"]
        MR["ModelRunner / GPU"]
    end
    subgraph detok["Detokenizer 进程"]
        D["DetokenizerManager 事件循环"]
    end
    CLI --> HTTP
    CLI --> TM
    CLI -->|"spawn"| S
    CLI -->|"spawn"| D
    S --- MR
    TM -->|"ZMQ: TokenizedGenerateReqInput"| S
    S -->|"ZMQ: BatchTokenIDOutput"| D
    D -->|"ZMQ: BatchStrOutput"| TM
:::

## 3.3 启动失败如何传播

启动期错误有两个值得注意的传播机制，源码注释给出了明确意图（`srt/entrypoints/engine.py:1112` 起）：

- **上下文快照回滚**&#8203;：`publish(server_args, role="tokenizer")` 之前先 `snapshot_context()`，启动失败时 `restore_context(context_before_publish)`，让调用方 catch 到错误时拿到的仍是发布前的上下文；
- **看门狗**&#8203;：`launch_server` 返回的 `subprocess_watchdog` 负责监控子进程退出。Scheduler 进程内部还有软看门狗（`soft_watchdog`，见第 5 章与第 12 章的事件循环代码），事件循环卡死超时即自杀，让 watchdog 级联重启。

这两个机制解释了一个源码可见的行为约定：&#8203;**任何一步失败都要把系统带回可重试或可观测的状态，而不是留下半初始化的进程**&#8203;。

## 3.4 HTTP 服务的生命周期

进程拉起后，`_setup_and_run_http_server` 挂载 FastAPI 应用。`srt/entrypoints/http_server.py:281` 的 `lifespan` 协程完成运行时装配：

- 按模式初始化单/多 Tokenizer（`is_single_tokenizer_mode` 分支）；
- 构造所有 OpenAI 兼容 handler（`OpenAIServingChat`、`OpenAIServingCompletion`、`OpenAIServingEmbedding` 等，`http_server.py:307–338`）；
- 按需启动 Prometheus 指标、OpenTelemetry 追踪、原生 gRPC 服务器；
- 启动 `_wait_and_warmup` 预热线程（先 `/generate` 一发再宣告就绪——Rust server 分支的注释还解释了不预热会出现「首个真实请求付 >60s 冷启动代价」的问题）。

`lifespan` 的 `finally` 块依次停 sidecar、停 gRPC、关 tool server、join 预热线程——优雅停机的顺序与装配顺序相反。

## 3.5 ZMQ 通道

三进程间的消息类型定义在 `srt/managers/io_struct.py`：下行有 `TokenizedGenerateReqInput`（`:1041`），上行有 `BatchTokenIDOutput`（`:1526`）与 `BatchStrOutput`（`:1627`）。通道拓扑是固定的「1 → 1 → 1」，但在注意力 DP（attention-DP）与多 Tokenizer 模式下会扩展为多路；Scheduler 侧用 `request_receiver.recv_requests()` 统一收包（`srt/managers/scheduler.py:2063` 的 `ingest_requests`），屏蔽了拓扑差异。

机制解释（依据上述代码结构）：把「协议处理」与「调度执行」拆进程、用 ZMQ 解耦，代价是每次请求都要经历两次序列化往返，但换来了两个收益——调度循环不被 asyncio 事件循环阻塞，以及 Python GIL 下 tokenizer/detokenizer 的 CPU 工作与调度器并行。

## 3.6 本章收束

- 启动链：`run_server` → `launch_server` → `Engine._launch_subprocesses` → 三个进程 → FastAPI lifespan 装配 handler 与预热。
- 进程间只有三条 ZMQ 通道：请求下行、token ID 上行、文本上行，消息类型集中在 `io_struct.py`。
- 启动失败通过上下文回滚 + 双层看门狗收敛为可观测错误。
- 下一章看请求进来后最先碰到的代码：HTTP 路由与 OpenAI 兼容层。
