---
title: 定位与总体架构
weight: 10
---

# 定位与总体架构

> 本章回答：Mooncake 解决什么问题、由哪些组件构成、一次推理请求如何与它发生交互。它是后续所有章节的地图。

## 问题与约束

大模型推理由两个阶段组成：**Prefill**（一次性处理整段 prompt，计算密集）与 **Decode**（逐 token 生成，访存密集）。把两者放在同一批 GPU 上，会互相抢资源；但简单地把集群劈成两半，又会产生新的问题——Prefill 完成的 KVCache 需要以极低的延迟搬运到 Decode 节点，同时重复 prompt 的 KVCache 应该被缓存复用。

Mooncake 的回答是：把 **KVCache 的存储与搬运**从推理引擎中抽出来，做成独立的分布式基础设施。官方 README 对其的概括是：*以 KVCache 为中心的分离式架构，分离 Prefill 与 Decode 集群，并利用 GPU 集群中闲置的 CPU、DRAM、SSD 资源构建分离式 KVCache 池*（来源：仓库 README「Overview」一节；"Kimi 在满足 SLO 的前提下多处理 75% 请求"出自同一节及 FAST'25 论文，属项目方报告的数据，非本文复现结论）。

## 三大组件

源码以 monorepo 组织，核心组件与顶层目录一一对应：

| 组件 | 目录 | 一句话职责 |
| --- | --- | --- |
| Transfer Engine（TE） | `mooncake-transfer-engine/` | 异构网络/加速器上的高性能数据搬运框架，RDMA 一键多网卡聚合 |
| Mooncake Store | `mooncake-store/` | 分布式 KVCache 池：Master 管元数据，客户端在段间直传数据 |
| Mooncake EP & PG | `mooncake-ep/`、`mooncake-pg/` | 弹性 MoE（专家并行）服务与进程组抽象 |

三个组件的协作关系（仅呈现源码与官方设计文档能支持的关系）：

::: mermaid
flowchart LR
    subgraph Inference["推理引擎（vLLM / SGLang 等）"]
        PD["Prefill / Decode 实例"]
    end
    subgraph Store["Mooncake Store"]
        SC["客户端 SDK"] 
        MS["Master 服务"]
        SEG["数据段（各节点 DRAM/SSD）"]
    end
    subgraph TE["Transfer Engine"]
        MT["MultiTransport 路由"]
        RDMA["RDMA / TCP / NVMeoF …"]
    end
    PD -->|"Put / Get KVCache"| SC
    SC -->|"元数据 RPC（gRPC）"| MS
    SC -->|"读写副本数据"| MT
    MT --> RDMA --> SEG
:::

关键分工是：**Master 只管元数据，不碰数据**。客户端从 Master 拿到"对象在哪个段的哪个 buffer"，随后用 Transfer Engine 与持有数据的节点直连传输。这决定了后文两条主线的形状：控制面走 `master_client_` 的 gRPC 调用，数据面走 `transfer_engine_` 的批次传输。

## 两条端到端主线

本系列沿两条真实调用链展开，它们分别对应 TE 与 Store 的核心价值：

**主线一（数据面，[第 4 章](/repos/mooncake/te-transfer)）**：

```text
allocateBatchID → submitTransfer → MultiTransport::selectTransport
→ RdmaTransport::submitTransferTask → 按 slice_size 切分 → selectDevice 选 NIC
→ WorkerPool 异步投递 → getTransferStatus 轮询 / 重试
```

**主线二（缓存面，[第 5 章](/repos/mooncake/store-client)）**：

```text
Client::Put → master PutStart（分配副本与 buffer 描述符）
→ TransferWrite（数据面写入各副本）→ PutEnd（提交）
Client::Get → master GetReplicaList（查副本 + 授租约）
→ 本地热缓存? → TransferRead（从副本直读）→ 校验 → 填充热缓存
```

## 一个重要的源码事实：两代实现并存

阅读 TE 源码时会撞上两套并存的实现：经典的 `MultiTransport` 路径，以及命名空间 `tent` 下的新一代实现。`TransferEngine` 用 `use_tent_` 标志分流（`mooncake-transfer-engine/src/transfer_engine.cpp:461`）：

```cpp
if (getenv("MC_USE_TENT") || getenv("MC_USE_TEV1")) {
    use_tent_ = true;
}
```

即：**默认走经典实现，设置 `MC_USE_TENT` 环境变量才切换到 TENT**（事实，见该文件与 `docs/source/design/tent/`）。本系列主线沿默认的经典路径追踪，涉及 TENT 处会明确指出，不把两代实现拼成一条调用链。

## 失败边界与本章收束

- Mooncake 是基础设施库，不含模型权重加载、采样等推理逻辑；推理引擎侧的集成是它的全部消费方式（[第 8 章](/repos/mooncake/integration)）。
- README 中的性能数字（75% 吞吐提升等）来自项目方与论文，本文不独立复现；正文凡涉及数字均标注来源口径。

读完本章应能复述：Mooncake = TE（搬数据）+ Store（管 KVCache）+ EP/PG（MoE 服务）；Master 管元数据、数据直传；源码存在经典 TE 与 TENT 两代实现，默认走前者。下一章先看仓库地图，建立目录级的方位感。
