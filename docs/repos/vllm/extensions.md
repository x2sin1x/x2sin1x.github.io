---
title: 扩展点全景
weight: 140
---

# 扩展点全景

> 本章回答：不修改 vLLM 本体的情况下，外部代码可以从哪些位置注入行为——硬件平台、启动时插件、跨引擎 KV 传输与结构化输出。这四个扩展点分别对应"换硬件、加代码、跨引擎、约束输出"四类需求。

## Platform：换硬件

`Platform`（`vllm/platforms/interface.py:135`）是硬件抽象基类，内置实现有 `cuda.py`、`rocm.py`、`tpu.py`、`xpu.py`、`cpu.py` 等。它声明设备能力与差异：设备名查询（`get_device_name`，`:490`）、算子可用性、平台专属配置。进程启动时 `platforms/__init__.py` 按 CUDA 环境变量与可用性探测选定唯一的当前平台，此后全库通过平台单例询问设备能力。`pre_register_and_update`（`:538`）钩子允许平台在模型注册前做一次性调整。

与第 9 章的 attention 注册表配合，第三方硬件的接入路径是：Platform 声明设备 → 平台专属 attention 后端 `register_backend` 注册 → 层实现按平台分发算子。

## Plugin：启动时注入

`load_general_plugins()`（`vllm/plugins/__init__.py:77`）按 Python entry points 发现插件组（模型、平台、general 三类），受 `VLLM_PLUGINS` 环境变量白名单控制（`:40`）。插件的典型用途：注册自定义模型架构、注册平台、注册 API 端点——仓库测试目录里就放着 `vllm_add_dummy_model`、`vllm_add_dummy_platform` 等示例插件（`tests/plugins/`）。插件在引擎构造前加载，因此能参与所有注册表的初始化。

## KV Connector：跨引擎的 KV 流动

这是四个扩展点中与调度器耦合最深的一个。`KVConnectorBase_V1`（`vllm/distributed/kv_transfer/kv_connector/v1/base.py:178`）定义了外部 KV 来源/去向的协议，两种角色由 `KVConnectorRole`（`:136`）区分（Scheduler 侧与 Worker 侧各一个实例）。

核心钩子是 `get_num_new_matched_tokens()`（`:475`）：调度器询问"除了本地已计算的 token，你还能从外部给我多少 token 的 KV？"返回值直接参与第 6 章的调度决策。引擎侧的接入点在第 7 章 `allocate_slots` 的布局里也出现过：`ext_comp` 段位就是为外部 KV 预留的。

实现清单展示了这个接口的覆盖面：

- **P/D 分离**：Prefill 与 Decode 部署在不同引擎实例，靠 Connector 搬运 KV——快照中有 `nixl/`、`mooncake/`、`hf3fs/` 等生产级传输实现；
- **KV 离线存储**：`lmcache_connector.py` 的 `LMCacheConnectorV1`（`:68`）、`OffloadingConnector`（`offloading_connector.py:52`）把 KV 卸载到 CPU/远端缓存；
- **组合**：`MultiConnector`（`multi_connector.py:133`）把多个 Connector 叠成查找链。

调度器为 Connector 留有专门状态：请求的 `WAITING_FOR_REMOTE_KVS` 状态（`scheduler.py:891` 一带可见）、抢占时 `_request_blocks_can_be_freed` 的传输保护（第 6 章）、以及 `KVConnectorMetadata` 随 `SchedulerOutput` 下发——Connector 的元数据流动完全搭在既有调度骨架上，而不是另起一套。

## 结构化输出：约束每一次采样

`StructuredOutputManager`（`vllm/v1/structured_output/__init__.py:36`）让输出遵循 JSON Schema / 正则 / 文法。机制分两半：

1. **编译**：请求到达时 `grammar_init`（EngineCore 侧调用，`vllm/v1/engine/core.py:1070`）把 schema 编译成增量文法状态机；后端可选 xgrammar、outlines、guidance、lm-format-enforcer（`backend_xgrammar.py` 等四个文件）。编译是异步的——调度器通过 `WAITING_FOR_STRUCTURED_OUTPUT_GRAMMAR` 状态（`vllm/v1/request.py:117`）等编译完成再排程；
2. **执行**：每步 `grammar_bitmask()`（`:314`）为批内所有受约束请求生成词表位掩码，在 GPU 上与 logits 相与，非法 token 概率归零。`EngineCore.step()` 在 GPU 前向的同时**并发**计算这个 bitmask（第 5 章），把它与 logits 处理器串联。

::: mermaid
flowchart TB
    P["Platform<br/>platforms/interface.py:135"] -->|"设备能力"| REG["各注册表<br/>模型 / attention / 连接器"]
    PL["Plugin<br/>plugins/__init__.py:77"] -->|"启动时注册"| REG
    KVC["KVConnectorBase_V1<br/>kv_connector/v1/base.py:178"] -->|"get_num_new_matched_tokens"| SCHED["Scheduler"]
    KVC -->|"KV 数据搬运"| WORKER["Worker / 传输后端"]
    SO["StructuredOutputManager<br/>structured_output/__init__.py:36"] -->|"bitmask"| SMP["Sampler 的 logits 处理器"]
:::

## 本章收束

- 四个扩展点作用于四个不同时机：Platform 与 Plugin 在启动期，KV Connector 在每步调度期，结构化输出在每步采样期；
- KV Connector 是唯一深入调度决策的扩展点，其状态机（等待远端 KV、传输中禁止抢占）由调度器原生承载；
- 结构化输出把"生成约束"从文本后处理挪到 logits 位掩码，保证约束从不被违反。

下一章总结部署形态：这套系统以什么进程拓扑在生产环境运行，以及如何观测它。
