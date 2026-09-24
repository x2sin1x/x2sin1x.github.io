---
title: 并行策略与执行器后端
weight: 120
---

# 并行策略与执行器后端

> 本章回答：一个 EngineCore 如何驱动多个 GPU Worker——TP/PP/DP/EP 各自在哪一层切开模型，通信组如何建立，执行器后端如何选择进程模型。

## 四种并行，四个切面

vLLM 的并行配置集中在 `ParallelConfig`，各维度作用于系统不同层次：

| 维度 | 切什么 | 落点 |
|---|---|---|
| TP（张量并行） | 每层的权重矩阵 | 层实现内部（`model_executor/layers/linear.py`） |
| PP（流水线并行） | 按层深度切开模型 | Worker 的 `execute_model` 边界（`gpu_worker.py:1198`） |
| DP（数据并行） | 不切模型，复制引擎 | EngineCore 层（DP rank 各一套调度） |
| EP（专家并行） | MoE 的专家分布 | `fused_moe` 层与 all-to-all 通信 |

**TP** 是最常用的一维：注意力头的 QKV、MoE 的专家权重按 rank 切分，前向中经 all-reduce 汇聚。通信原语由 `GroupCoordinator`（`vllm/distributed/parallel_state.py:424`）提供，并针对小消息实现了自定义 allreduce（`distributed/device_communicators/`）——decode 批次极小，NCCL 的延迟劣势明显，这是 vLLM 自建通信内核的原因。

**PP** 的接缝就在上一章看到过：非首 rank 在 `Worker.execute_model` 里 `irecv_tensor_dict` 收中间张量，执行完再 `isend_tensor_dict` 发往下游（`gpu_worker.py:1246`/`:1283` 一带），发送句柄由下一步执行前统一 wait——流水线重叠不阻塞 GPU 忙循环。

**DP** 是 EngineCore 层的并行：每个 DP rank 拥有独立的 Scheduler 与完整副本的模型；`EngineCore._init_data_parallel`（`vllm/v1/engine/core.py:1454`）协调多个 EngineCore 的启动，API 进程按负载（各 rank 的排队请求数，经 `publish_dp_lb_stats` 发布，`core.py:1483`）路由请求。

## initialize_model_parallel：通信组的拓扑

`initialize_model_parallel()`（`parallel_state.py:1967`）在 torch.distributed 之上切分通信组，其 docstring 给出标准例子：8 卡、TP=2、PP=4 时，张量组是 `[g0,g1],[g2,g3],...`，流水线组是 `[g0,g2,g4,g6],[g1,g3,g5,g7]`。之后任何代码都用 `get_tp_group()`（`:1547`）等取回自己所属的组——通信组的"身份"就此冻结进每个进程。

## 执行器后端：Worker 进程怎么来

EngineCore 不亲自管理 GPU 进程，而是把这件事交给 `Executor`（`vllm/v1/executor/abstract.py:41`）。`get_class()`（`:52`）按 `distributed_executor_backend` 分派：

::: mermaid
flowchart TB
    EC["EngineCore<br/>model_executor"] --> X["Executor 接口<br/>execute_model / sample_tokens / collective_rpc"]
    X --> U["UniProcExecutor<br/>Worker 在进程内"]
    X --> M["MultiprocExecutor<br/>每 GPU 一个子进程"]
    X --> R["RayDistributedExecutor / V2<br/>跨节点"]
    X --> E["ExecutorWithExternalLauncher<br/>外部拉起"]
:::

- **UniProcExecutor**：单 GPU 部署，Worker 与 EngineCore 同进程，`execute_model` 是直接函数调用；
- **MultiprocExecutor**（`vllm/v1/executor/multiproc_executor.py:111`）：单机多卡默认选项。它为每个 GPU 拉起 `WorkerProc` 子进程，通过 `WorkerProcHandle`（`:573`）与 ZMQ 通道通信；`execute_model()`（`:340`）把调用翻译成 `collective_rpc("execute_model", unique_reply_rank=output_rank)`——所有 rank 并行执行，只有 output rank（通常是 TP rank 0，负责采样）返回结果；
- **RayDistributedExecutor**（及其 V2 形态，`abstract.py:64-72`）：多机部署，把 Worker 放进 Ray actor。

执行器还负责 Worker 的生命周期：`MultiprocExecutor.__init__` 挂上 `weakref.finalize(self, self.shutdown)`（`:121`），保证 EngineCore 崩溃后子进程被回收。

## collective_rpc：统一的远端调用

注意到 `execute_model` 与 `sample_tokens`（`:353`）都翻译成 `collective_rpc`——这是执行器的统一抽象：向所有 Worker 广播一个方法调用并聚合结果，附带超时（`VLLM_EXECUTE_MODEL_TIMEOUT_SECONDS`）、KV/EC 输出聚合器。Worker 的任何运维操作（保存分片状态、LoRA 加载、profile 开关）都复用同一条 RPC 通道，EngineCore 侧的对应方法们（`core.py:1011` 起的 `add_lora`、`save_sharded_state` 等）只是薄转发。

## 本章收束

- 四种并行的切面不同：TP 在层内、PP 在 Worker 边界、DP 在 EngineCore、EP 在 MoE 专家分布；
- `initialize_model_parallel` 决定通信组拓扑，之后进程只凭 `get_tp_group()` 使用身份；
- 执行器是 EngineCore 与 Worker 进程模型之间的可替换件：uni / mp / ray / external_launcher 四种后端共享 `collective_rpc` 抽象。

下一章看让 decode 更快的一类特殊机制：投机解码。
