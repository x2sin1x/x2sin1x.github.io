---
title: "第 14 章 PD 分离（Prefill/Decode disaggregation）"
---

# 第 14 章 PD 分离（Prefill/Decode disaggregation）

> 本章回答：为什么要把 prefill 与 decode 拆到不同实例？KV cache 如何从 prefill 实例搬到 decode 实例？请求的「接力」如何在两个调度器之间完成？

## 14.1 动机与形态

PD 分离的动机可以从第 7 章的权衡直接推出：prefill 是计算密集型（吃 GPU 算力），decode 是访存密集型（吃 KV 带宽），两者在同一实例上互相干扰。SGLang 的解法是让一个实例只做 prefill（`disaggregation_mode = "prefill"`）、另一个只做 decode（`"decode"`），KV cache 通过专门的传输通道从前者流向后者。

模式定义在 `srt/disaggregation/utils.py:89` 的 `DisaggregationMode` 枚举。第 6 章调度循环中的两处分支是其运行期痕迹：`get_next_batch_prefill` 中 `DisaggregationMode.PREFILL` 下用 `req_to_token_pool.available_size()` 做额外的批满判断（`srt/managers/scheduler.py:3977`），`run_batch` 中 prefill 实例会 `maybe_send_cached_prefix_chunk(req)` 提前发送已缓存前缀的 KV（`srt/managers/scheduler.py:4375`，注释：*PD prefill: early-send cached prefix KV, overlapping the suffix forward*）。

## 14.2 组件与接力流程

`srt/disaggregation/prefill.py` 与 `decode.py`（3199 行）分别承载两端。核心组件（类与定义位置均源码可见）：

- `PrefillBootstrapQueue`（`srt/disaggregation/prefill.py:156`）：prefill 端为待处理请求预先建立到 decode 端的连接（bootstrap）；
- `CommonKVManager` / `CommonKVSender` / `CommonKVReceiver`（`srt/disaggregation/common/conn.py`，`decode.py:46` 的导入可见）：KV 传输的通用抽象，支持不同传输后端（NIXL、Mooncake 等在 `disaggregation/` 下的适配）；
- `bootstrap_room`：请求级接力凭证，`GenerateReqInput` 的 `bootstrap_host/port/room` 字段（第 5 章）在两个实例间传递。

::: mermaid
sequenceDiagram
    participant C as 客户端
    participant P as Prefill 实例
    participant X as KV 传输 (CommonKVSender/Receiver)
    participant D as Decode 实例

    C->>P: 请求（含 bootstrap 参数）
    P->>P: bootstrap：预建连接，进 PrefillBootstrapQueue
    P->>P: prefill 前向，KV 写入本地池
    P->>X: 发送 KV（layer 粒度，边算边发）
    X->>D: 接收 KV，写入 decode 端 KV 池
    D->>D: PREBUILT 模式：KV 就绪即入 decode 批
    D->>C: 后续流式输出
:::

## 14.3 decode 端的 PREBUILT 模式

接力在 decode 端的形态是新的 `ForwardMode.PREBUILT`（`srt/model_executor/forward_batch_info.py:211` 的注释：*Used in disaggregated decode worker — Represent a batch of requests having their KV cache ready to start decoding*）。第 6 章的 `ForwardMode` 枚举可见它独立于 EXTEND/DECODE；第 12 章 `process_batch_result` 的 `is_prebuilt` 分支（`srt/managers/scheduler.py:4791`）则是其输出侧处理点。

decode 端调度器不再做 prefill，其「入批」的判据从「PrefillAdder 预算」变成「KV 是否已完整到达」。`decode.py` 中 `CommonKVReceiver.query_prefill_dp_ranks`（`:1154` 附近）用于在多 prefill 实例间按 room 查询来源。

## 14.4 失败与恢复边界

源码可见的边界处理：

- **传输未完成不编排**&#8203;：`decode.py` 对 KV receiver 的完成状态轮询（`:1154` 附近调用族），未就绪请求滞留等待队列；
- **prefill 端重试**&#8203;：`prefill.py:110` 的 `should_force_retry(req)` 定义了强制重试条件；
- **元数据缓冲管理**&#8203;：`prefill.py:139` 的 `maybe_release_metadata_buffer` 在失败/异常路径释放传输元数据，防泄漏；
- **会话粘性**&#8203;：第 13 章的 `FOLLOW_BOOTSTRAP_ROOM` 分发策略保证多轮请求跟随原 room，避免 KV 重复传输（机制解释，依据 bootstrap room 在两章间的一致使用）。

## 14.5 与单机路径的关系

PD 分离没有引入第三种调度循环：prefill 实例复用黄金路径的 prefill 半程，decode 实例复用 decode 半程，唯一的新抽象是「KV 到达」这一异步事件（`PREBUILT` + KV receiver 轮询）。源码结构（`disaggregation/` 目录的 mixin 形态：`ScheduleBatchDisaggregationDecodeMixin` 等，`srt/managers/schedule_batch.py:2335` 可见）表明分离能力是&#8203;**混入**&#8203;调度器而非替换调度器。

## 14.6 本章收束

- PD 分离把第 7 章的 prefill/decode 争抢从「同实例内的调度权衡」升级为「物理隔离」，KV 传输层（CommonKV*）是桥。
- 接力凭证是 bootstrap room；KV 按 layer 粒度边算边发，decode 端以 KV 就绪为入批条件（PREBUILT）。
- 失败边界集中在传输侧：连接预建、重试条件、元数据释放。
- 下一章看这些实例之上的一层：Rust 路由网关如何选择实例。
