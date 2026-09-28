---
title: "附录 C 术语表"
---

# 附录 C 术语表

> 只收录正文使用的术语。同一概念全书只用一个中文译名，首次出现给出英文原名。

## 运行时结构

- **SRT（SGLang Runtime）**&#8203;：`python/sglang/srt` 下的推理服务运行时，本卷主体。
- **TokenizerManager（TM）**&#8203;：主进程内的分词与请求状态管理器（第 5 章）。
- **Scheduler**&#8203;：调度子进程，拥有等待队列、chunked_req 与运行批（第 6 章）。
- **DetokenizerManager**&#8203;：反分词子进程，做增量文本化（第 12 章）。
- **PrefillAdder**&#8203;：prefill 装批器，按 token 预算从等待队列挑选请求（第 7 章）。
- **ModelRunner**&#8203;：单 GPU 进程内的模型执行门面（第 10 章）。

## 调度

- **prefill（预填充）**&#8203;：对输入 prompt 做一次前向、填满 KV cache；对应 `ForwardMode.EXTEND`。
- **decode（解码）**&#8203;：每步每序列生成一个 token；对应 `ForwardMode.DECODE`。
- **chunked prefill（分块预填充）**&#8203;：把超长 prompt 的 prefill 切成多个 chunk 跨多拍执行，`chunked_req` 是其暂存槽（第 7 章）。
- **retract（收回）**&#8203;：KV 池不足时把部分 decode 请求收回等待队列重新 prefill（第 6 章）。
- **overlap scheduling（重叠调度）**&#8203;：把上一批结果处理与下一批 GPU 前向重叠的循环模式（第 6 章）。
- **future map**&#8203;：overlap 下管理「下一拍才可见 token 槽位」的账本（第 6 章）。
- **forward batch**&#8203;：一次前向所需的纯张量视图（第 8 章）。

## 内存与缓存

- **RadixCache（基数树前缀缓存）**&#8203;：把 KV 槽位按 token 前缀组织成树以复用（第 9 章）。
- **KV 池 / token 池**&#8203;：存放 KV cache 的显存池，槽位编号即 `device_indices`（第 9 章）。
- **`req_to_token` 表**&#8203;：请求行 → KV 槽位序列的映射表（第 8、9 章）。
- **lock ref（树节点锁）**&#8203;：请求对命中前缀的持有计数，锁住的 token 不可淘汰（第 9 章）。
- **evict（淘汰）**&#8203;：从叶子释放可淘汰缓存槽位（第 9 章）。
- **HiCache**&#8203;：KV 的主机（CPU）第二层缓存（第 9 章）。
- **pinned memory（锁页内存）**&#8203;：调度流预置、前向流异步拷贝的主机内存（第 8 章）。

## 执行与采样

- **CUDA Graph 重放**&#8203;：decode 批的静态形状图执行路径（第 10 章）。
- **attention backend（注意力后端）**&#8203;：按硬件/架构可插拔的注意力实现（第 10 章）。
- **MLA（Multi-head Latent Attention）**&#8203;：DeepSeek 系列的潜变量注意力，拥有独立池类与后端分支（第 9、10 章）。
- **grammar / 受限解码**&#8203;：用 FSM 位掩码在采样前约束合法 token（第 11 章）。
- **delay sampling（延迟采样）**&#8203;：把采样推迟到上一批结果处理后的 overlap 优化（第 11 章）。

## 并行与集群

- **DP / TP / PP / EP**&#8203;：数据、张量、流水线、专家并行（第 13 章）。
- **attention-DP / DP attention**&#8203;：注意力维度独立做数据并行的混合模式（第 6、13 章）。
- **EPLB（专家负载均衡）**&#8203;：依据专家路由记录重均衡 EP 布局（第 10、13 章）。
- **PD 分离（prefill/decode disaggregation）**&#8203;：prefill 与 decode 用不同实例承载（第 14 章）。
- **bootstrap room**&#8203;：PD 分离中请求跨实例接力的凭证（第 14 章）。
- **PREBUILT**&#8203;：decode 实例上「KV 已就绪」的前向模式（第 14 章）。
- **缓存感知路由（cache-aware routing）**&#8203;：网关按跨实例前缀树匹配选实例（第 15 章）。
- **KV 事件**&#8203;：SRT 发布的缓存增删事件流，供网关维护影子树（第 9、15 章）。
