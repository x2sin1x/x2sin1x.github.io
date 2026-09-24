---
title: 附录 C：术语表
weight: 120
---

# 附录 C：术语表

> 只收录正文使用过的术语；一个概念全系列只用一个译名，首次出现时标注英文原名。

| 术语 | 英文 | 含义 |
| --- | --- | --- |
| 分离式架构 | disaggregated architecture | 把 Prefill 与 Decode 部署到不同集群，经高速网络交换中间结果（KVCache / hidden states） |
| KVCache | KV cache | 注意力机制中 key/value 张量的缓存；Mooncake 缓存与搬运的基本单位（语义层） |
| 传输引擎 | Transfer Engine (TE) | Mooncake 的高性能数据搬运框架，支持 RDMA、TCP、NVMeoF、GPU-IPC 等多种 transport |
| 段 | segment | 一个节点对外暴露的内存区间集合，TE 的远端寻址单位 |
| 分片 | slice | TE 内最小传输单元，由 `slice_size` 切分而来，承载重试与状态机 |
| 批次 | batch | 一次提交的一组传输请求，共享一个 `BatchID` 用于状态查询 |
| 拓扑 | topology | 本机网卡（HCA）与 CPU/GPU 的亲和关系，用于多网卡选择 |
| 段描述符 | segment descriptor | 段的元数据：协议、buffer 列表、设备拓扑；存于元数据服务 |
| 元数据服务 | metadata service | 段名字 → 段描述符的注册中心，支持 etcd / HTTP |
| TENT | TENT | TE 的新一代实现（环境变量 `MC_USE_TENT` 启用），本系列主线为默认经典实现 |
| 主节点 | Master | Mooncake Store 的元数据权威：对象索引、副本分配、租约、配额 |
| 副本 | replica | 一个对象在某介质上的完整拷贝，类型有 MEMORY / NOF_SSD / LOCAL_DISK / DFS |
| 放置策略 | placement policy | 决定副本落在哪些段的算法（Random / FreeRatioFirst 等 5 种） |
| 租约 | lease | Master 授予读方的时限承诺，防止数据在传输窗口内被淘汰 |
| 卸载 | offload | 把内存副本迁移到 SSD / DFS 等慢介质 |
| 回载 | load | 把卸载到慢介质的数据读回内存 |
| 热缓存 | hot cache | 客户端节点本地的 DRAM 读缓存，按访问频率准入（count-min sketch） |
| 淘汰 | eviction | 容量压力下删除对象元数据并回收存储 |
| 两阶段写 | two-phase put | PutStart（分配）→ 数据直传 → PutEnd（提交）/ PutRevoke（回滚） |
| PD 分离 | P/D disaggregation | Prefill 与 Decode 分离部署；Mooncake 为其提供 KVCache 传输与共享 |
| 热备 | hot standby | 备机持续消费 oplog 保持热状态，主机故障时接管 |
| 操作日志 | oplog | 快照之间的元数据增量日志，用于 Master 恢复 |
| 张量并行 | tensor parallel (TP) | 单层权重按张量切分到多卡；`pub_tensor_with_tp` 等接口处理其分片 |
