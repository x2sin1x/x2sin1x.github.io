---
title: "第 15 章 Rust 路由网关"
---

# 第 15 章 Rust 路由网关（sgl-model-gateway）

> 本章回答：SRT 实例之上为什么还需要一层路由？缓存感知路由如何工作？网关与 SRT 之间交换哪些运行时信息？

## 15.1 定位

`sgl-model-gateway/`（Rust）在多实例部署中位于 SRT 之前：客户端打网关，网关按策略挑实例、转发请求、回传响应。它对 SRT 的消费面有三类（均可从源码找到入口）：

1. **请求代理**&#8203;：HTTP/OpenAI 协议转发（`src/routers/`）；
2. **负载信息**&#8203;：订阅每个 SRT 实例的负载统计——SRT 侧的发布点在第 12 章输出链中出现过（`load_publisher.publish_load_stat`，`srt/managers/scheduler.py:4775` 附近）；
3. **KV 事件**&#8203;：订阅 radix 树的增删事件——SRT 侧的产生点在第 9 章 `evict` 中的 `kv_events.record_remove(x)`（`srt/mem_cache/radix_cache.py:578`）与 `kv_events_publisher` 组件（`srt/managers/scheduler_components/kv_events_publisher.py`）。

与旧一代路由器的关系：`experimental/sgl-router/` 是早期实现，网关的 `bindings/python`（`sglang_router` 包）是其生产化后继；第 2 章的依赖方向（网关只消费 SRT 接口）在此再次成立。

## 15.2 路由策略

策略目录 `sgl-model-gateway/src/policies/`：

```text
policies/
├── cache_aware.rs      缓存感知（前缀树匹配 + 负载混合）
├── round_robin.rs      轮询
├── power_of_two.rs     两随机取一较优
├── consistent_hashing.rs / prefix_hash.rs   一致性/前缀哈希
├── bucket.rs / random.rs / manual.rs        桶、随机、手工指定
├── tree.rs             前缀树数据结构
└── registry.rs / factory.rs                 注册与工厂
```

`mod.rs:14–34` 的导出清单显示 `CacheAwarePolicy`、`PowerOfTwoPolicy`、`RoundRobinPolicy` 是主要公开策略。

**缓存感知路由**&#8203;是与 SGLang 核心机制协同最深的一层：网关维护一棵跨实例的前缀树（`tree.rs`），把每个请求的前缀与各实例已缓存的前缀匹配——命中某实例树深的请求优先路由到该实例，使其在 SRT 内直接命中 RadixCache（第 9 章）；同时约束单实例过载（负载项参与打分）。机制解释：这是把「前缀复用」的优化从实例内延伸到集群级，代价是网关要维护一份与实例树近似同步的影子树，同步延迟可能导致误路由（路由错只损失缓存收益，不损失正确性——因为 SRT 的 RadixCache miss 时仍会重算，这是正确性与收益的分离点）。

## 15.3 数据流

::: mermaid
flowchart LR
    C["客户端"] --> GW["sgl-model-gateway<br/>策略选择"]
    GW -->|"HTTP 代理"| A["SRT 实例 A"]
    GW --> B["SRT 实例 B"]
    A -->|"负载统计 (load_publisher)"| GW
    B -->|"负载统计"| GW
    A -->|"KV 事件 (kv_events_publisher)"| GW
    B -->|"KV 事件"| GW
:::

闭环：&#8203;**请求去程**&#8203;按策略选实例；&#8203;**回程信息**&#8203;（负载 + KV 事件）持续修正策略状态。KV 事件的发布是可选能力（SRT 侧按配置开启），网关侧对应 `experimental/sgl-router/sgl-kv-indexer/` 等索引组件（第 2 章清单可见其独立 crate）。

## 15.4 网关侧的可扩展性

网关自带三类扩展面（目录可直接看到）：

- **中间件**&#8203;（`src/middleware.rs`）：鉴权、限流等横切处理；
- **WASM 插件**&#8203;（`src/wasm/` 与 `examples/wasm/` 下的 auth、logging、ratelimit 三个示例）：以 WASM guest 形式注入自定义逻辑；
- **多语言绑定**&#8203;（`bindings/python`、`bindings/golang`）：把网关嵌入非 Rust 编排环境。

## 15.5 本章收束

- 网关是 SRT 集群化的前置层，消费两类回程信息：负载统计与 KV 事件，两者的产生点都在本书黄金路径上。
- 缓存感知路由把第 9 章的前缀复用延伸到集群级：跨实例影子树 + 负载约束打分；错误路由的代价是收益损失而非正确性损失。
- 扩展面：中间件、WASM 插件、Python/Go 绑定。
- 全书正文到此完成；附录提供阅读路径、符号速查与术语表。
