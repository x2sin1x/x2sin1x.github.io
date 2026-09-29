---
title: "RDMA 与高性能网络"
date: 2026-09-29T10:30:00+08:00
weight: 10
---

# RDMA 与高性能网络

> [万卡集群](/knowledge-planet/ai-infra/distributed/large-scale-cluster)篇说跨机梯度同步动辄 GB 级。这种流量走 TCP 会怎样？——内核协议栈的拷贝与中断把 CPU 打满，延迟抖动几个数量级。&#8203;**训练网络的答案是绕过内核：RDMA。**

## 为什么 TCP 不行

TCP 收发一个包要经历：系统调用 → 内核协议栈解析 → 数据从网卡拷到内核再拷到用户态（两次拷贝）→ 上下文切换与中断。100 Gbps 线速下，每秒千万级包的中断和拷贝会把 CPU 打满，单包延迟几十微秒起步且抖动很大。

对训练这是致命的：allreduce 的带宽项假设"网络给多少吃多少"，而 TCP 给不了稳定的满带宽；同步 collective 更怕长尾——一千条流里最慢的那条决定所有人的等待时间。

**RDMA（Remote Direct Memory Access）把协议栈从数据路径上整个摘掉**&#8203;：网卡直接读写远端应用注册好的内存，不经内核、零拷贝、CPU 全程不参与数据搬运。延迟从几十 µs 降到 1–2 µs，且抖动极小。

## 三种承载：IB、RoCE、iWARP

| 维度 | InfiniBand | RoCE v2 | iWARP |
| ---- | ---- | ---- | ---- |
| 链路 | 专用 IB 交换机/线缆 | 以太网（UDP/IP 封装） | 以太网（TCP 封装） |
| 拥塞控制 | 链路层信用制，天然无损 | 依赖 ECN/PFC（下节） | 借用 TCP 拥塞控制 |
| 典型场景 | 专用训练集群（多数万卡集群） | 复用以太网的训练集群 | 少见 |
| 成本 | 交换机与网卡均专用 | 复用以太网生态，但要求网络"无损" | 复用 TCP 栈 |

万卡集群的主流选择是 IB 或 RoCE v2；两者性能接近，分歧主要在运维生态——IB 是封闭体系但"开箱无损"，RoCE 复用以太网但要把以太网**调教成无损网络**。

## RoCE 的无损化：PFC 与 ECN

以太网天生允许丢包，而 RDMA 协议不容丢包（重传代价极高），所以 RoCE 要求网络提供"不丢包"保证，核心是两个机制：

- **PFC（Priority-based Flow Control）**：逐优先级的"停一停"信令。下游交换机缓冲将满时，通知上游对相应优先级停发。它保证不丢，但会带来两个新问题：**PFC 死锁**（环形依赖的停发互相等待）与**hoarding**（一条慢流堵住端口，同队列的无辜流被一起停住）。
- **ECN（Explicit Congestion Notification）**：交换机在缓冲超过水线时给包打标记，接收端通过 CNP 报文通知发送端降速。PFC 是"快满了别发"的硬保险，ECN 是"快满了请减速"的软调节——**健康网络的调优目标是让 ECN 早于 PFC 生效，PFC 只兜底不干活**。

一个反复出现的模式：&#8203;**incast（多对一汇聚）是训练网络的头号杀手**&#8203;。allreduce 尾部所有卡同时收数据，瞬时 N 对 1 的流量模式极易触发缓冲溢出——这正是轨道优化组网（[万卡集群](/knowledge-planet/ai-infra/distributed/large-scale-cluster)篇）与 NCCL 调优（下一篇）要共同解决的问题。

## 内存注册与 Verbs

RDMA 网卡读写的是**虚拟地址**，前提是应用先把内存"注册"给网卡：锁定物理页、建立虚拟地址→物理地址的映射表（MTT）、拿到本地/远程键（lkey/rkey）。此后收发只需提交"这段内存、那个远端、用这个 key"的描述符（Work Request）。

编程接口是 **Verbs**：最底层是 QP（Queue Pair，每端一对发送/接收队列）上的 post_send/poll_cq；NVIDIA 封装的 NCCL/IBVerbs 层以及 GDS、UCX 都构建在其上。两个工程要点：

1. **注册开销是一次性的，但很贵**（大内存注册要 pin 页、建大表），所以框架在启动时一次性注册大块内存池反复使用——DataLoader 的 `pin_memory` 与 NCCL 的 buffer 池都是这个思路。
2. **QP 状态机与建链**：万卡规模的 allreduce 要在数千对 QP 上做连接管理，NCCL 的 bootstrap（下一篇）专门解决"怎么发现拓扑并建满这些连接"。

## 跨 AZ 与长距离

同一训练任务跨可用区（AZ）部署时：单向物理延迟（光纤传播约 5 µs/km，AZ 间通常 1–3 ms）直接进入所有 collective 的延迟项；带宽往往降档；且跨 AZ 流量可能计费。工程结论：&#8203;**训练域内（同步密集的 DP/TP/PP）绝不跨 AZ**；能跨的只有异步的数据管道（数据预取、checkpoint 异步上传）与超大规模下的粗粒度流水（如 DisbMoE 式的跨 AZ MoE，靠把通信藏进计算）。

## 小结

- 训练网络的核心诉求是**低延迟、满带宽、零抖动**，TCP 的内核路径给不了，RDMA 用内核旁路 + 零拷贝解决。
- IB 靠专用网络天然无损；RoCE v2 靠 PFC（兜底）+ ECN（调节）把以太网调教成无损——PFC 频繁触发说明调优失败。
- 内存注册是 RDMA 编程的前提，框架用"启动时注册大内存池"摊销开销。
- 集散比（incast）是训练流量的固有形态，是组网与通信库共同优化的靶心。

## 思考题

1. 一次 64 卡 allreduce，若走 25 Gbps TCP（每卡一条流），单包延迟 50 µs，估算同步 1 GB 梯度的时间；换成 400 Gbps RDMA（1.5 µs 延迟）呢？
2. 为什么 PFC 死锁在 CLOS 组网里依然可能发生？运维上最常见的触发条件是什么？
3. 你的集群 8 卡机内 NVLink 900 GB/s、机间 RoCE 200 Gbps，DP=64 的梯度同步放在哪一层？如果 NCCL 报 PFC 频繁触发告警，先查什么？

::: details 参考答案

1. TCP：1 GB ÷ 3.125 GB/s ≈ 320 ms，且长尾抖动另计；RDMA：1 GB ÷ 25 GB/s ≈ 40 ms。差 8 倍——还不算 TCP 的 CPU 消耗对数据加载的挤占。
2. CLOS 消除了稳态死锁（上行/下行分离），但服务器双上联、跨 Pod 长距互联、非对称链路故障后路由收敛期间可能形成环形依赖；最常见触发是链路故障/维护导致 ECMP 路由不对称。
3. 64 卡 DP 梯度同步通信量大但可重叠，优先用机间网络 + bucket 重叠（见[数据并行](/knowledge-planet/ai-infra/parallelism/data-parallelism)篇）。PFC 频繁触发先查：ECN 水线配置是否低于 PFC 水线、是否有 incast（NCCL 算法是否该换 Tree/分层）、以及是否存在慢节点（NIC 降速、光模块故障）。

:::

## 参考资料

- NVIDIA, [RDMA and RoCE Solutions for GPU Clusters](https://docs.nvidia.com/networking/display/mlnxofedv531001/rdma-and-rosce-solutions) 系列文档
- Linux Foundation, [InfiniBand Architecture Specification](https://www.infinibandta.org/)（IBTA 规范）
- Alibaba HPN 团队，[Alibaba HPN: A Data Center Network Architecture for Large Language Model Training](https://dl.acm.org/doi/10.1145/3651890.3672234)（SIGCOMM 2024，双平面组网与 RDMA 实战）
