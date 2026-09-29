---
title: "集群调度"
date: 2026-09-29T10:30:00+08:00
weight: 10
---

# 集群调度

> 一个千卡训练作业就是一千个必须同时就位的"仪式"：任何一张卡缺席，大家都等。**把这种全员到齐的作业调度好，是 AI 集群与通用云集群的根本差异**。

## AI 负载的调度特殊性

训练作业有三个与 Web 服务截然不同的调度特征：

1. **Gang scheduling（全员或全不）**（题库 173）：DDP/TP 的集体通信要求所有 rank 同时在线——部分启动的作业只会集体 hang 到超时。调度器必须**原子地**分配整组资源，经典实现是 Volcano 的 PodGroup 与 gang 插件。
2. **拓扑敏感（题库 175）**：TP 组必须在超节点内、PP 跨相邻机、DP 可跨轨道——调度不只是"找到 N 张空卡"，而是"找到网络拓扑正确的 N 张卡"（匹配原则见[超节点](/knowledge-planet/ai-infra/distributed/supernode)篇）。
3. **长时运行 + 可抢占错峰**（题库 176）：训练跑数天到数月，但 checkpoint/restart 让它**可迁移**——这给了调度器用低优先级作业填空、高优先级作业抢占回填的机会。

## Slurm 与 Kubernetes：两套世界

**Slurm** 是 HPC 出身的作业调度器，AI 训练的传统主力（题库 171）。一个最小 sbatch 脚本的骨架：

```bash
#!/bin/bash
#SBATCH --job-name=llm-train
#SBATCH --nodes=16 --ntasks-per-node=8     # 16 机 × 8 卡
#SBATCH --gres=gpu:8
#SBATCH --cpus-per-task=8
#SBATCH --time=72:00:00
srun torchrun --nnodes=$SLURM_JOB_NUM_NODES \
    --nproc-per-node=8 train.py
```

要点：`srun`/`torchrun` 的组合负责把 rank 环境变量（`RANK`/`WORLD_SIZE`/`MASTER_ADDR`）注入每个进程；`--exclusive` 保证独占节点。Slurm 的优势是 gang 语义原生、HPC 生态成熟；劣势是容器与云原生集成弱。

**Kubernetes + Volcano/调度器扩展**（题库 172）是平台化的主流：原生 kube-scheduler 没有 gang 语义，Volcano 补上 PodGroup/queue/preemption，配合 **NVIDIA GPU Operator**（题库 134）自动管理驱动、device plugin、容器运行时（nvidia-container-toolkit）与监控组件。其他常见件：`topology-aware` 调度插件（读 CRD 里的 NVLink/IB 拓扑给打分）、DLRMs 类项目的 queue 层（多租户配额）。

**容器与底层（题库 301–305）**在这一层交汇：容器运行时（runc/containerd）管理 cgroup/namespace——GPU 作业的设备暴露靠 device plugin 与 `nvidia-container-runtime`；**CNI** 决定 Pod 网络（训练 Pod 常用 hostNetwork 直取 RDMA 网卡，绕过 overlay 网络的性能损失）；**CSI** 把分布式文件系统挂成 PV（checkpoint 与数据集的挂载点）；etcd 是 K8s 的状态存储，其一致性保证是调度决策可靠性的地基。

## 抢占与回填：让集群跑满

高利用率的核心机制（题库 174/176/177）：

- **优先级 + 抢占**：高优先级作业可以夺走低优先级的资源；被抢的低优先级作业**靠 checkpoint 恢复**——这正是训练侧把"可恢复性"做成一等能力的原因（[容错](/knowledge-planet/ai-infra/distributed/fault-tolerance)与[训练 Infra](/knowledge-planet/ai-infra/training/training-infra)篇的联合兑现）。
- **回填（backfill）**：大作业排队等整组资源时，允许小作业"借"未来才需要的资源跑——前提是不推迟大作业的启动。这让碎片时间的利用率显著上升。
- **碎片整理（defragmentation，题库 226）**：长时间运行后小空隙散落各处、凑不出大作业的整组资源。手段：定期 drain 重排（结合可迁移性）、调度时避免产生新碎片（拓扑打包约束）、弹性作业（动态调整 DP 度数填空隙）。

## 多集群与成本（题库 178–180）

- **异构 GPU 管理**：新旧卡混部（H100/A100/910B）时，调度器按卡型过滤 + 按作业声明匹配；并行策略随卡型变（不同卡的 NVLink 域大小不同，TP/PP 布局要重算）。
- **多集群联邦**：大作业绑单集群（网络拓扑不可跨），联邦层的价值在**队列聚合与配额仲裁**——跨集群只是提交入口的统一，不是运行的分布（跨 AZ 训练的网络账见[RDMA]篇）。
- **成本核算（cost accounting）**：按"卡时 × 单价"给每个作业记账，区分预留（guaranteed）与抢占（spot）价差——回填与抢占的经济意义就是让 spot 资源占比最大化。utilization 监控（题库 177）用 [profiling 章](/knowledge-planet/ai-infra/profiling/)的指标口径，但聚合到天/周粒度看趋势。

## 小结

- AI 调度三特征：gang 原子性、拓扑正确性、可抢占性——最后一个依赖训练侧的可恢复能力。
- Slurm 赢在 gang 原生，K8s + Volcano + GPU Operator 赢在平台生态；CNI/CSI/device plugin 是 GPU 作业的三大基建件。
- 抢占 + 回填 + 碎片整理是利用率的三大杠杆，本质都是"用可恢复性换填空能力"。
- 成本核算让调度决策显性化：spot 占比、碎片率、排队时间是可以上 OKR 的数字。

## 思考题

1. 为什么 gang scheduling 不能用"重试"来替代？写出一个 hang 场景的时间线。
2. 回填的约束是什么？如果大作业的预计启动时间估算错了，会发生什么？
3. 你要把 8 卡 A100 作业迁到 H100 集群，除了换卡型声明，并行配置里哪些数字必须重算？

::: details 参考答案

1. 部分启动的 rank 会阻塞在集合通信（如 barrier/allreduce），直到 NCCL 超时（默认 30 分钟）才失败——期间已分配的卡全部空转，重试循环放大浪费。时间线：rank 0-63 启动 → rank 64 容器拉起失败 → 前 64 rank 卡在 init_process_group → 30 min 后超时 → 释放重来。
2. 约束是"不推迟任何高优先级作业的准确启动时间"（EFT, earliest-start-time-first 的守恒条件）；估算错了（大作业实际更早需要资源）会触发对小作业的二次抢占——所以回填策略偏好"能快速跑完/能快速恢复"的小作业。
3. TP 度数受新卡 NVLink 域大小影响（如 8→18 卡域）；PP 的 stage 划分随 TP 变化重算；DP 度数 = 总卡数/(TP×PP) 联动；ZeRO/微调显存账随 HBM 大小变化可放宽——本质是[并行策略](/knowledge-planet/ai-infra/parallelism/)章的决策框架在新约束下重跑一遍。

:::

## 参考资料

- Slurm 官方文档，[sbatch/srun 手册](https://slurm.schedmd.com/sbatch.html)
- Volcano, [gang scheduling 文档](https://volcano.sh/en/docs/)；NVIDIA, [GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/)
- Meta AI, [Llama 3 Herd of Models](https://arxiv.org/abs/2407.21783)（大规模训练的调度与容错协同）

