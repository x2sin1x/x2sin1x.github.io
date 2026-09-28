---
title: "第 10 章 ModelRunner 与模型执行"
---

# 第 10 章 ModelRunner 与模型执行

> 本章回答：`ModelRunner.forward` 如何决定走 CUDA Graph 还是 eager？注意力后端如何选择与接入？前向内部还有什么必须知道的机制？

## 10.1 入口与主干

`ModelRunner`（`srt/model_executor/model_runner.py`）是「一个 GPU 进程内模型执行」的门面，由 `TpModelWorker` 持有（`srt/managers/tp_worker.py`，第 6 章 `run_batch` → `model_worker.forward_batch_generation`）。主前向入口在 `srt/model_executor/model_runner.py:1706`：

```python
# srt/model_executor/model_runner.py:1706（节选）
def forward(
    self,
    forward_batch: ForwardBatch,
    ...
) -> ModelRunnerOutput:
    ...
    with (
        canary_ctx,
        step_span_ctx,
        get_global_expert_distribution_recorder().with_forward_pass(...)
        as recorder_outputs,
    ):
        output = self._forward_raw(
            forward_batch, pp_proxy_tensors, reinit_attn_backend, split_forward_count
        )
        ...
```

`_forward_raw`（`:1856`）是真正的分派器，主干分支（按源码顺序）：

1. **decode CUDA Graph 重放**&#8203;：`can_run_graph` 为真时直接 `self.decode_cuda_graph_runner.execute(...)` 返回——静态形状路径，跳过一切动态装配；
2. **eager 前的规范化**&#8203;：`_prepare_eager_forward_batch` 处理 DP/MLP 同步填充与注意力 TP 归一化（`model_runner.py:1901` 调用处注释说明 decode graph 路径不经过这里）；
3. **prefill CUDA Graph（piecewise）**&#8203;：可运行时走分段图；
4. **eager 前向**&#8203;：其余情况。

`can_run_graph` 的判定组合了 `forward_batch.forward_mode.is_cuda_graph`、graph runner 存在性、以及 runner 自己的形状检查——decode 批形状固定（第 8 章），所以这是 decode 的快路径，prefill 因形状动态通常落到 eager 或分段图。

## 10.2 注意力后端：注册表与选择

注意力后端是 SGLang 最主要的硬件适配面。注册表在 `srt/layers/attention/attention_registry.py:40`：

```python
# srt/layers/attention/attention_registry.py:40
ATTENTION_BACKENDS = {}

def register_attention_backend(name):
    def decorator(fn):
        ATTENTION_BACKENDS[name] = fn
        return fn
    return decorator

@register_attention_backend("flashinfer")
def create_flashinfer_backend(runner):
    ...
    if not runner.use_mla_backend:
        from sglang.srt.layers.attention.flashinfer_backend import (
            FlashInferAttnBackend,
        )
        ...
        return FlashInferAttnBackend(...)
    else:
        from sglang.srt.layers.attention.flashinfer_mla_backend import (
            FlashInferMLAAttnBackend,
        )
        return FlashInferMLAAttnBackend(runner)
```

同文件还注册了 `triton`、`trtllm_mha`、`fa4`、`flashmla`、`aiter` 等数十个后端（同目录下每个 `*_backend.py` 一个家族）。选择发生在 ModelRunner 初始化阶段，结果存在 `self.attn_backend` 与 `self.decode_attn_backend`（`model_runner.py:1023–1024`）；选择依据是 CLI 参数（`--attention-backend`）、模型架构（是否 MLA）、平台（CUDA/ROCm/NPU）与投机解码需求的交集，`attention_registry.py:435` 附近还有按硬件能力缩小候选集的校验。

所有后端实现 `AttentionBackend`（`srt/layers/attention/base_attn_backend.py`）约定：init forward metadata、按 `ForwardMode` 提供 attention 计算入口。前向代码只见接口，不见具体 kernel——这就是新增硬件支持的主要扩展点。

## 10.3 KV 的读与写

前向期间注意力层做两件与内存池相关的事：

- **读**&#8203;：按 `forward_batch.req_pool_indices` 与 `seq_lens` 从 `req_to_token` 表取出历史 KV 槽位，再在 `MHATokenToKVPool` 的张量中索引（MLA/混合线性注意力等架构读法不同，由各自池类适配）；
- **写**&#8203;：把本步新算出的 K/V 写入 `out_cache_loc` 指定的槽位（第 8 章分配的地址）。

读写的槽位编号全部来自调度器（第 9 章的树与分配器），ModelRunner 不做任何内存决策——职责边界与第 2 章的分层完全一致。

## 10.4 CUDA Graph 的取舍

图重放（`srt/model_executor/runner_backend/` 下的 `full_cuda_graph_backend.py`、`breakable_cuda_graph_backend.py`、`tc_piecewise_cuda_graph_backend.py`）与 eager 的取舍在源码层面表现为：

| 维度 | 图重放 | eager |
| --- | --- | --- |
| CPU 启动开销 | 一次重放调用 | 每层每 op 的调度开销 |
| 形状 | 固定（按 batch 桶预捕获） | 任意 |
| 内存 | 需要为捕获保留静态缓冲 | 动态分配 |
| 适用 | decode 主路径 | prefill、动态形状、调试 |

`cuda_graph_config.py` 与 `model_executor/cuda_graph_buffer_registry.py` 管理捕获配置与缓冲生命周期；`graph_memory_usage.py` 提供图内存的核算。

## 10.5 执行层的辅助机制

`model_runner.py:1706` 的 `forward` 签名周围还能看到一组横切机制，各司其职：

- **性能剖析**&#8203;：`step_span_ctx`（步骤级 span）、profiler 管理、`dumper` 调试器；
- **MoE 专家分布记录**&#8203;：`get_global_expert_distribution_recorder().with_forward_pass(...)` 记录路由到的专家（供 EPLB 专家均衡，`:1794` 附近 `eplb_manager.on_forward_pass_end()`）;
- **弹性 EP**&#8203;：`_maybe_rebalance_after_rank_fault` 支持专家并行 rank 故障后的重均衡（`:1778` 附近分支）；
- **canary 管理**&#8203;：数值校验的前向探针（`canary_ctx`）。

这些机制都以「可选上下文管理器」方式挂进前向主干，主干逻辑（图重放/规范化/分派）保持清晰——这是本章最值得借鉴的代码组织。

## 10.6 本章收束

- `forward` → `_forward_raw` 的三分支：decode 图重放、prefill 分段图、eager；形状固定性决定路径。
- 注意力后端是注册表多态：`ATTENTION_BACKENDS` 字典 + 工厂函数，按架构/硬件/特性交集选择。
- ModelRunner 只消费调度器给定的内存地址，不做内存决策；前向的横切机制全部以可选上下文挂载。
- 下一章：前向输出 logits 之后，token 是如何被「选」出来的。
