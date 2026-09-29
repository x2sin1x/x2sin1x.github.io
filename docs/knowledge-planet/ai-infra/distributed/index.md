---
title: "分布式系统"
date: 2026-09-29T10:00:00+08:00
weight: 2
---

# 分布式系统

一颗芯片的算力、显存、带宽都有物理上限，而大模型的需求没有。&#8203;**把多颗芯片组织成一台"逻辑上的大计算机"，就是分布式系统要回答的问题**&#8203;：卡与卡怎么协作（集合通信）、机柜怎么焊成一台机器（超节点）、机柜怎么扩展成数据中心（万卡集群），以及规模变大之后故障如何成为常态（容错）。

本章节内容：

1. [集合通信](/knowledge-planet/ai-infra/distributed/collective-communication)——多卡协作的基本语言：allreduce、allgather、reduce-scatter 与 Ring 算法。
2. [超节点](/knowledge-planet/ai-infra/distributed/supernode)——Scale-up：把一个机柜焊成一台机器，NVL72 与 CM384 两条路线。
3. [万卡集群](/knowledge-planet/ai-infra/distributed/large-scale-cluster)——Scale-out：从机柜到数据中心，胖树与轨道优化组网。
4. [容错与 Checkpoint](/knowledge-planet/ai-infra/distributed/fault-tolerance)——规模越大故障越日常，checkpoint/restart 的账本。

本章回答的是"机器如何组成一台计算机"这一**静态能力**；任务如何用好这台计算机（调度、多租户、成本）见[平台与调度](/knowledge-planet/ai-infra/platform/)章，流量的协议与链路细节见[网络与通信](/knowledge-planet/ai-infra/network/)章。
