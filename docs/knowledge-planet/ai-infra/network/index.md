---
title: "网络与通信"
date: 2026-09-29T10:00:00+08:00
weight: 3
---

# 网络与通信

[分布式系统](/knowledge-planet/ai-infra/distributed/)章回答了"多机协作需要什么流量"——梯度同步的 allreduce、MoE 的 all-to-all、KV Cache 的 P2P 传输。本章回答下一个问题：&#8203;**这些流量用什么网络承载才跑得动**&#8203;。判断口诀：换一种互联技术文章还成立的内容（算法与架构）归分布式系统章，离开具体协议就不成立的内容（链路与协议）归本章。

本章节内容：

1. [RDMA 与高性能网络](/knowledge-planet/ai-infra/network/rdma-highspeed-network)——为什么训练网络绕过内核：RDMA 原理、IB Verbs、RoCE v2 的 ECN/PFC 拥塞控制。
2. [NCCL 与通信优化](/knowledge-planet/ai-infra/network/nccl-tuning)——集合通信库的实战：算法选型、环境变量调优、拓扑感知、通信计算重叠与故障诊断。

阅读前提：[集合通信](/knowledge-planet/ai-infra/distributed/collective-communication)篇的通信量模型与 [超节点](/knowledge-planet/ai-infra/distributed/supernode)篇的 Scale-up/Scale-out 分界。读完本章，你应当能解释"为什么训练流量不能走 TCP"、诊断一次 NCCL hang，并给出跨机通信优化的工程清单。
