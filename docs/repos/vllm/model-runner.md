---
title: GPUModelRunner：把调度结果变成一次前向
weight: 80
---

# GPUModelRunner：把调度结果变成一次前向

> 本章回答：Worker 进程收到 `SchedulerOutput` 后如何把它变成 GPU 上的一次前向——持久批次的增量更新、attention metadata 的构建、CUDA Graph 的分发，以及执行后的记账。

## Worker：模型侧的壳

每个 GPU 对应一个 `Worker`（`vllm/v1/worker/gpu_worker.py:183`）。它的 `execute_model()`（`:1198`）主要处理流水线并行的边界：非首rank先 `irecv_tensor_dict` 接收上游的中间张量，非末rank执行完 `isend_tensor_dict` 发给下游；中间则把工作原样交给 `GPUModelRunner.execute_model()`。Worker 还拥有 KV Cache 的**实际张量**——`initialize_from_config()`（`:774`）按 EngineCore 传来的 `KVCacheConfig` 在显存里分配块张量。

## 持久批次：只为增量干活

`GPUModelRunner`（`vllm/v1/worker/gpu_model_runner.py:479`）单文件 7500+ 行，核心设计是**持久批次**：批内请求的元数据常驻 CPU/GPU 结构，每步只做增量增删，而不是每步重建。

```python
def _update_states(
    self, scheduler_output: "SchedulerOutput"
) -> Callable | None:          # gpu_model_runner.py:1192
```

`_update_states()` 按 `SchedulerOutput` 增量同步三样东西：

1. **`InputBatch`**（`vllm/v1/worker/gpu_input_batch.py:90`）：采样参数、温度、惩罚系数等按请求槽位存储的 CPU/GPU 张量，`add_request`（`:347`）/`remove_request`（`:525`）维护槽位复用；
2. **`BlockTable`**（`vllm/v1/worker/block_table.py:57`）：每请求的 KV 块号表——正是调度器账本的 GPU 侧镜像，attention kernel 靠它做块寻址；
3. **位置与序列元数据**：query/context 长度等随新 token 增长。

engine step 由此分两半：调度器每步把请求移入/移出批次（增量、便宜），模型只看"当前批次状态 + 本步新增 token"。

## 一次 execute_model 的主线

`execute_model()`（`:4149`）沿以下顺序推进：

::: mermaid
sequenceDiagram
    participant S as SchedulerOutput
    participant MR as GPUModelRunner
    participant M as 模型 forward
    participant K as attention kernel
    S->>MR: execute_model()
    MR->>MR: _update_states() 增量同步批次
    MR->>MR: 构建输入张量 / padding 判定
    MR->>MR: attention metadata builder.build()
    alt 命中 CUDA Graph
        MR->>M: replay 捕获好的图
    else 常规路径
        MR->>M: 直接 forward
    end
    M->>K: 按块表读写 KV Cache
    K-->>M: attention 输出
    M-->>MR: logits（或中间张量）
    MR->>MR: _bookkeeping：记录采样输入/块表更新
:::

关键一步是 attention metadata：`AttentionMetadataBuilder` 把块表、序列长度、滑动窗口等编译成所选 attention kernel 期望的布局（如 FlashAttention 的 `FlashAttentionMetadata`，`vllm/v1/attention/backends/flash_attn.py:508`）。同一份 `SchedulerOutput`，不同后端产出不同 metadata——这是"调度与 kernel 解耦"的接缝。

## CUDA Graph：小批次的延迟杀手

decode 阶段每步只算极少的 token，kernel launch 开销占比剧增。vLLM 用 CUDA Graph 把整次前向录制成图，之后按批次形状直接 replay：

- 捕获尺寸列表来自 `compilation_config.cudagraph_capture_sizes`（`gpu_model_runner.py:773`）；
- 运行时分发由 `CudagraphDispatcher`（`:886` 创建，实现于 `vllm/v1/cudagraph_dispatcher.py`）完成：`execute_model` 内部调用 `_determine_batch_execution_and_padding()` 判定批次描述，再把实际 batch padding 到最近的捕获尺寸后 replay；
- 多模态编码器有独立的 `EncoderCudaGraphManager`（`:597`）。

代价是**形状刚性**：图按固定形状捕获，实际批次必须 padding（白白多算的 token）和做形状分派；这也是为什么 `"FULL" vs "PIECEWISE"` 的 cudagraph 模式选择成为 `compilation_config` 的重要开关。

## 执行后的记账与采样分离

前向结束后 `_bookkeeping_sync()`（`:3667`）记录本步每个请求新算的 token 位置、更新块表偏移，并打包成 `ModelRunnerOutput` 回传 EngineCore。值得注意快照中 `execute_model` 与采样是**可分离**的两步：EngineCore 的 `step()` 里若 `model_output` 为空会改调 `executor.sample_tokens()`（`vllm/v1/engine/core.py:647`），对应 Worker 的 `sample_tokens()`（`:4530`）——这服务于异步调度：前向可以比采样调度领先一步排队。

## 本章收束

- Worker 的本质是"持久批次 + 增量更新"：`_update_states` 只同步 `SchedulerOutput` 的差量；
- 块表是调度器 KV 账本的 GPU 侧镜像，attention kernel 通过它寻址分页 KV；
- CUDA Graph 换来小批次延迟，付出 padding 与形状分派的代价；
- 前向与采样可拆为两步，为异步调度留出重叠空间。

下一章看 attention 这个接缝的另一半：后端如何被注册、声明能力与被选中。
