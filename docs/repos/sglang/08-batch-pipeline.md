---
title: "第 8 章 从 Req 到 ForwardBatch：批数据流水线"
---

# 第 8 章 从 Req 到 ForwardBatch：批数据流水线

> 本章回答：调度器选中一批请求后，数据要经历几次形态转换才到达 GPU？每次转换解决什么问题？prefill 与 decode 两条路径的张量差异在哪里？

## 8.1 三级数据结构

一个请求到 GPU 前经历三级形态，定义位置：

- `Req`（`srt/managers/schedule_batch.py:999`）：单请求的 Python 视图——`origin_input_ids`、`output_ids`、`sampling_params`、前缀命中信息 `prefix_indices`、最后命中的树节点 `last_node`；
- `ScheduleBatch`（`schedule_batch.py:2335`）：一批 Req 的容器，负责张量化与内存分配；
- `ForwardBatch`（`srt/model_executor/forward_batch_info.py:488`）：一次前向所需的&#8203;**纯张量**&#8203;视图，ModelRunner 只看它。

关键设计（可从字段注释直接读到）：`ForwardBatch` 的 GPU 张量字段是从 `ScheduleBatch` **借用**&#8203;的（`forward_batch_info.py:507` 的注释 `=== Borrowed from ScheduleBatch: GPU tensors ...`），并标注了跨流（cross-stream）克隆语义——这是第 6 章 overlap 张量保全的根源。

## 8.2 ForwardMode：一次前向的语义

`srt/model_executor/forward_batch_info.py:193`：

```python
class ForwardMode(IntEnum):
    EXTEND = auto()        # prefill：序列前缀的 KV 已算好（如系统提示词）
    DECODE = auto()        # 每序列一个 token
    MIXED = auto()         # chunked prefill 下 extend 与 decode 混合
    IDLE = auto()          # 无序列可跑（注意力 DP 下部分 worker 空转）
    TARGET_VERIFY = auto() # 投机解码：目标模型验证草稿
    DRAFT_EXTEND_V2 = auto()  # 投机解码：草稿模型扩展
    PREBUILT = auto()      # PD 分离 decode 端：KV 已就绪
    SPLIT_PREFILL = auto() # PD 复用的分层切块 prefill
    DLLM_EXTEND = auto()   # 扩散式 LLM
```

`is_extend()` 与 `is_decode()` 两个谓词贯穿全书调度代码（第 6 章的 `get_next_batch_to_run` 即用它们分派）。

## 8.3 prefill 路径：prepare_for_extend

`srt/managers/schedule_batch.py:2722` 的 `prepare_for_extend` 把 prefill 批张量化：

```python
# srt/managers/schedule_batch.py:2722（节选）
def prepare_for_extend(self):
    self.forward_mode = ForwardMode.EXTEND
    ...
    input_ids = [r.get_fill_ids()[len(r.prefix_indices) :] for r in reqs]
    extend_num_tokens = sum(len(ids) for ids in input_ids)
    seq_lens = [r.extend_range.end for r in reqs]
    prefix_lens = [len(r.prefix_indices) for r in reqs]
    ...
    # Stay on pinned CPU; H2D is deferred to forward stream via
    # resolve_forward_inputs.
    pinned_input_ids = flatten_arrays_to_pinned_cpu(input_ids, _pin)
    ...
    # Allocate memory
    out_cache_loc, req_pool_indices_tensor, req_pool_indices_cpu = alloc_for_extend(
        self
    )
```

逐项解释：

- **输入裁剪**&#8203;：`get_fill_ids()[prefix:]` 只计算前缀之后的部分——命中 RadixCache 的部分不进前向（第 7 章预算的落地）；
- **`seq_lens`**&#8203;：包含命中前缀在内的总长度（KV 已在池中），attention backend 据此定位；
- **`out_cache_loc`**&#8203;：`alloc_for_extend` 从 KV 分配器为本 chunk 的每个 token 分配的槽位，是本章与第 9 章的接口；
- **pinned memory + 延迟 H2D**&#8203;：输入张量先落在锁页内存，真正的拷贝推迟到前向流上的 `resolve_forward_inputs`（第 6 章 overlap 流程可见其调用）——调度流与前向流解耦的实现细节。

## 8.4 decode 路径：prepare_for_decode

decode 批的每拍更新在 `srt/managers/schedule_batch.py:3551` 的 `prepare_for_decode`：每条序列追加一个 token，为它分配一个 KV 槽位（`out_cache_loc` 长度等于 batch size），`seq_lens` 张量原地加一。与 prefill 相比，decode 批形状固定、每次只变化一列——这正是 decode 能用 CUDA Graph 重放（第 10 章）而 prefill 通常不能的形状学原因。

## 8.5 全景时序

::: mermaid
flowchart LR
    subgraph S["Scheduler（调度流）"]
        Req["List[Req]"] --> SB["ScheduleBatch<br/>prepare_for_extend / prepare_for_decode"]
        SB -->|"alloc_for_extend<br/>→ out_cache_loc"| Pool["KV 池分配器"]
    end
    SB --> MB["ForwardBatch.init_new<br/>(srt/model_executor/…)"]
    MB --> MR["ModelRunner.forward<br/>（前向流）"]
    Pool -.->|"req_to_token 表"| MR
:::

`ForwardBatch.init_new` 由 `tp_worker.forward_batch_generation`（`srt/managers/tp_worker.py:598`）调用，把 ScheduleBatch 折叠成张量包后交给 `ModelRunner.forward`（第 10 章）。`req_to_token` 表（第 9 章）是两者共享的「请求行 → KV 槽位」映射，attention backend 前向时按 `req_pool_indices` 查表定位每个请求的历史 KV。

## 8.6 本章收束

- 三级形态 Req → ScheduleBatch → ForwardBatch，是「语义状态 → 调度张量 → 执行张量」的逐级提纯；GPU 代码只见第三级。
- prefill 输入按前缀裁剪，decode 每拍一列，形状差异决定了两者能否图重放。
- `out_cache_loc` 与 `req_to_token` 表是调度与执行共享内存状态的接缝；pinned memory + 延迟 H2D 是双流调度的细节。
- 下一章补齐这条流水线中最有辨识度的部分：`out_cache_loc` 背后的 RadixCache 与 KV 内存池。
