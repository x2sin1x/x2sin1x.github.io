---
title: "第 2 章 仓库地图"
---

# 第 2 章 仓库地图

> 本章回答：SGLang 的目录如何按职责划分？模块间的依赖方向是什么？读者在追调用链时应该从哪里进、在哪里找证据？快照规模：Python 6953 个文件约 227 万行，Rust 564 个文件约 25 万行。

## 2.1 路径约定

全书代码引用的路径以仓库根为基准，其中 `srt/…` 是 `python/sglang/srt/…` 的缩写。例如 `srt/managers/scheduler.py:1906` 指向 `python/sglang/srt/managers/scheduler.py` 第 1906 行。

## 2.2 顶层目录

```text
python/sglang/            主 Python 包（本卷主体）
  launch_server.py        服务器 CLI 入口
  srt/                    SRT 推理运行时（第 3–12 章的范围）
  lang/                   前端 DSL（早期编程接口）
  cli/                    sglang serve 等 CLI 命令
  kernels/                自带算子（AOT 编译、JIT）
  multimodal_gen/         多模态生成
  bench_one_batch_server.py / bench_serving.py   基准工具
sgl-model-gateway/        Rust 路由网关（第 15 章）
experimental/sgl-router/  旧一代 Rust 路由器（已被 gateway 取代）
rust/                     Rust 服务端实验（sglang-server、grpc、radix-tree 等）
test/                     回归测试（含大量 CI 用例）
benchmark/                性能与压测脚本
docs/                     项目文档（用户侧）
```

依赖方向是单向的：`sgl-model-gateway` 与 `experimental/sgl-router` 都通过 HTTP/gRPC 消费 SRT 的接口（负载统计、KV 事件），不反向导入 SRT 代码；`rust/sglang-server` 是把 API server 搬进 Rust 的实验分支，由环境变量 `SGLANG_RUST_SERVER` 开关（`srt/entrypoints/http_server.py:2871` 附近的分支逻辑可证）。

## 2.3 SRT 内部结构

`srt/` 是本卷的主战场，按职责可归为五组：

```text
srt/
├── entrypoints/      对外接口层：HTTP、gRPC、Engine Python API、OpenAI/Anthropic/Ollama 兼容
├── managers/         进程层：TokenizerManager、Scheduler、DetokenizerManager、DP controller
│   └── scheduler_components/   Scheduler 的拆分组件（输入接收、输出流式、指标等）
├── model_executor/   执行层：ModelRunner、ForwardBatch、CUDA graph runner
├── mem_cache/        内存层：RadixCache、KV 内存池、分配器、HiCache（主机缓存）
├── layers/           模型组件层：注意力后端、Sampler、量化、MoE、LogitsProcessor
├── models/           模型定义（LLaMA、Qwen、DeepSeek、Gemma 等数百个模型类）
├── disaggregation/   PD 分离（第 14 章）
├── speculative/      投机解码
├── server_args.py    服务参数定义与校验（配合 arg_groups/）
└── arg_groups/       按命名空间拆分的参数定义（schedule、memory、parallel…）
```

一句话职责（依赖自上而下）：

| 模块 | 职责一句话 |
| --- | --- |
| entrypoints | 把网络协议翻译成内部请求对象，把内部结果翻译回协议 |
| managers | 拥有请求生命周期状态，决定「哪个请求、哪一步、何时执行」 |
| model_executor | 把一个 ForwardBatch 变成一次 GPU 前向 |
| mem_cache | 决定「KV 放哪、何时复用、何时丢弃」 |
| layers | 前向中每个数学操作的实现与硬件适配 |

## 2.4 状态容器的位置

追代码时最有用的问题是「谁拥有这个可变状态」。SRT 的关键状态分布是：

- **请求元状态**&#8203;（`Req` 对象：input/output ids、finish 状态）由 TokenizerManager 和 Scheduler 各持有一份视图，跨进程靠 `rid` 对齐；
- **GPU KV 槽位**&#8203;由 `req_to_token_pool`（请求行 → token 槽位表）与 `token_to_kv_pool_allocator`（槽位分配）持有，属于 Scheduler 进程（`srt/mem_cache/memory_pool.py:317` 的 `alloc`、`:360` 的 `free`）;
- **批张量**&#8203;（input_ids、seq_lens、out_cache_loc）在 `ScheduleBatch` 与 `ForwardBatch` 之间单向流动，第 8 章展开。

## 2.5 测试在哪里

`test/` 目录按功能划分（`test/srt/` 下的调度、缓存、各模型回归用例；`test/registered/` 为 CI 注册用例）。以本书涉及的核心机制为例：

- 前缀缓存：`test/srt/test_radix_cache.py` 一族；
- 调度与 retract：`test/srt/test_schedule_conservativeness.py` 等；
- 网关路由策略：`sgl-model-gateway/e2e_test/`。

阅读建议：SRT 的测试大多是「启动一个真实服务再打请求」的端到端形态，适合验证行为契约，不适合逐函数定位；逐函数定位优先看调用点。

## 2.6 本章收束

- 仓库三层结构：Python 运行时（SRT）、Rust 网关、周边工具，依赖单向。
- SRT 内部五层：接口 → 进程/调度 → 执行 → 内存 → 模型组件，这正是后续章节的推进顺序。
- 关键可变状态：请求状态在两个进程各有一份视图；KV 槽位状态只属于 Scheduler 进程。
- 下一章进入启动流程，看这三个进程是如何被拉起来的。
