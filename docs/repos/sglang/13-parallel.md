---
title: "第 13 章 并行体系：DP / TP / PP / EP"
---

# 第 13 章 并行体系：DP / TP / PP / EP

> 本章回答：SGLang 的四种并行各自由谁持有、在代码哪里分派？单机多卡与多机是如何被统一抽象的？本章对四种并行各给出「谁在管、边界在哪」的最小叙述。

## 13.1 四种并行的分层

按源码结构，SGLang 的并行可以放进三个层：

| 并行 | 层 | 持有者 | 证据锚点 |
| --- | --- | --- | --- |
| 数据并行（DP） | 进程间 | `DataParallelController` | `srt/managers/data_parallel_controller.py:140` |
| 张量并行（TP） | 进程内/间 | Scheduler 每个 rank 一个进程，层内集合通信 | 第 3 章 `_launch_scheduler_processes` |
| 流水线并行（PP） | 进程间 | `scheduler_pp_mixin`、`PPProxyTensors` | `srt/managers/scheduler_pp_mixin.py`、`srt/managers/tp_worker.py:613` 附近分支 |
| 专家并行（EP） | 层内 | MoE 层与 EPLB | `model_executor/moe_ep_setup.py`、`model_runner.py` 的 `eplb_manager` |

注意 DP 与 TP 的组合方式：DP 是&#8203;**请求级**&#8203;复制（每个 DP rank 是完整的调度器 + 模型副本），TP 是&#8203;**层内**&#8203;切分（一次前向跨 rank 集合通信）。两者可叠加（DP×TP），注意力部分还可细分为 attention-TP/CP，调度循环中的 `require_mlp_sync`、`dp_attn_adapter` 分支（第 6 章 `get_next_batch_to_run` 尾部可见）即为此存在。

## 13.2 DP：DataParallelController

`srt/managers/managers/data_parallel_controller.py` 的类文档一句话：*A controller that dispatches requests to multiple data parallel workers*（`:140`）。它持有到各 DP rank scheduler 的 ZMQ 连接，按 `LoadBalanceMethod`（`:87` 的枚举）分发：

```python
# srt/managers/data_parallel_controller.py:172 附近（节选）
dispatch_lookup = {
    LoadBalanceMethod.ROUND_ROBIN: self.round_robin_scheduler,
    LoadBalanceMethod.FOLLOW_BOOTSTRAP_ROOM: self.follow_bootstrap_room_scheduler,
    LoadBalanceMethod.TOTAL_REQUESTS: self.total_requests_scheduler,
    LoadBalanceMethod.TOTAL_TOKENS: self.total_tokens_scheduler,
}
self.dispatching = dispatch_lookup[self.load_balance_method]
```

四个内置策略对应三类信息：无状态轮询（ROUND_ROBIN）、会话粘性（FOLLOW_BOOTSTRAP_ROOM，配合 PD 分离的 bootstrap room，第 14 章）、负载反馈（TOTAL_REQUESTS / TOTAL_TOKENS，依赖各 rank 上报的负载——第 12 章输出链中 `load_publisher.publish_load_stat` 就是数据源）。

规模弹性上还有 `max_dp_size >= launch_dp_size` 的断言（`data_parallel_controller.py:180`）与 elastic EP 的扩缩分支，支持运行期增加 DP rank（弹性并行）。

## 13.3 TP：rank 组与集合通信

TP 在启动期由 `_launch_scheduler_processes` 为每个 TP rank 拉起一个 Scheduler 进程（第 3 章）。运行期的协作点：

- **权重加载**&#8203;：`model_loader/` 按 rank 切分权重（列/行并行由各层声明）；
- **前向集合通信**&#8203;：`srt/distributed/` 封装 NCCL/RCCL 的组通信，MoE 层的 all-to-all、注意力层的 all-reduce 都在这里；
- **调度一致性**&#8203;：TP rank 们跑同样的调度循环，输入广播自 rank 0（`ingest_requests` 的注释说明 recv 在 `pp_rank == 0 and attn_tp_rank == 0` 的 rank 上进行，`srt/managers/scheduler.py:2063` 附近），因此每个 rank 做出&#8203;**相同的调度决策**——这是无锁协同的根基。

## 13.4 PP 与 EP

流水线并行把层切到多个 rank，一个 microbatch 依次流过；`scheduler_pp_mixin.py` 管理 microbatch 的搬运，`PPProxyTensors`（`tp_worker.py:613` 附近 `forward_batch_generation` 的 `pp_proxy_tensors` 参数）是 stage 间传递的中间激活容器。第 6 章已见其调度痕迹：chunked req 在 PP 下的 max_running_requests 特例注释（`srt/managers/scheduler.py:3860` 附近）。

专家并行是 MoE 层的专家切分，与 EPLB（专家负载均衡）配套：第 10 章见过的 `get_global_expert_distribution_recorder().with_forward_pass(...)` 记录每步专家路由，`eplb_manager.on_forward_pass_end()` 据此推进重均衡计数（`srt/model_executor/model_runner.py:1794` 附近）。

## 13.5 多机协同的心智模型

::: mermaid
flowchart TB
    Tok["TokenizerManager"] --> DPC["DataParallelController"]
    DPC -->|"按负载/会话分发"| R0["DP rank 0<br/>(Scheduler × TP group)"]
    DPC --> R1["DP rank 1<br/>(Scheduler × TP group)"]
    DPC --> R2["DP rank n<br/>(Scheduler × TP group)"]
    subgraph R0S["DP rank 0 内部"]
        S0["Scheduler (tp rank 0)"] ---|"相同决策"| S1["Scheduler (tp rank 1)"]
    end
:::

要点：&#8203;**请求级并行交给 DP 控制器，张量级并行交给 TP 组内一致的调度**&#8203;；PP 与 EP 是模型维度的纵深切分。分层正交，因此单机单卡的黄金路径（第 6–12 章）在每层并行下依然成立，只是多了同步点。

## 13.6 本章收束

- DP 是进程级请求分发，四种策略在 `dispatch_lookup`；TP 是 rank 组内一致调度，输入广播保证决策相同。
- PP 的载体是 `PPProxyTensors` 与 scheduler 的 PP mixin；EP 的载体是 MoE 层 + EPLB 的记录/重均衡闭环。
- 本书黄金路径描述的是「一个调度器内部」的逻辑，叠加任何并行都只是在其外围加同步点。
- 下一章把 TP/DP 组合推到极端：prefill 与 decode 用不同实例承载。
