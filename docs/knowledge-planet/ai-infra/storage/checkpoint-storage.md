---
title: "Checkpoint 存储与加载"
date: 2026-09-29T10:30:00+08:00
weight: 10
---

# Checkpoint 存储与加载

> [容错](/knowledge-planet/ai-infra/distributed/fault-tolerance)篇算过：万卡训练的 checkpoint 超过 10 TB、每几分钟写一次。**写入时间拖训练、恢复时间烧产能**——本篇讲怎么把这本账做平。

## 格式：从 pickle 到 safetensors 到 DCP

- **torch.save（pickle）**：最早的格式。致命缺陷：加载需要**任意代码执行**（安全风险）且必须整体读入（不支持懒加载、不能流式）。
- **safetensors**（HuggingFace）：只存张量头 + 裸数据——加载零拷贝（mmap）、无代码执行风险、按张量名随机访问。已是 HF 生态的默认格式，单模型存储的事实标准。
- **DTensor/DCP（PyTorch Distributed Checkpoint）**：面向**分布式**的格式——存的是"每个 rank 的分片 + 全局元数据"，保存/加载时自动重分片。**换并行布局也能加载**（TP=8 训练的 checkpoint 直接以 TP=4 加载），这是与文件级格式（safetensors）的本质区别，训练侧的默认选择。

格式选择的经验线：**训练中频繁存 → DCP；发布给社区/推理服务 → safetensors**。

## 写入：TB 级状态的时间账

写入时间 $T = M/B_{\text{write}}$，问题在于分母怎么凑：

1. **聚合带宽**：单节点 NVMe 只有 3–7 GB/s，写入 10 TB 要半小时——不可接受。解法是**多节点并发写**（每个 rank 写自己的分片到不同节点），聚合带宽 = 单盘带宽 × 节点数。DeepSeek 的 3FS 把这一思路做成文件系统：多机并发 + RDMA 直达，checkpoint 写入达 TB/s 级。
2. **同步 vs 异步**：同步 checkpoint 会把训练暂停 $T$；异步方案（Megatron/DeepSpeed 的 async save）把当前步状态**先复制到侧缓冲**（GPU 内存充裕时）或直接微批化地分块搬运，训练继续跑。代价是侧缓冲显存/内存，以及"写的是上一步快照"的语义。
3. **快照一致性**：分布式下各 rank 必须写**同一逻辑步**的状态——写前做一次 barrier/版本号约定，否则恢复时 optimizer state 与 model 对不上步。

## 加载：恢复时间也是产能税

恢复时间 = 作业调度 + 容器拉起 + **权重加载** + warmup。加载侧的三个手段：

- **重分片加载**：DCP 按新布局读取，省掉"先按旧布局加载再全量 reshard"的中间峰值（那个峰值常是 OOM 元凶）。
- **按需/懒加载**：推理服务用 safetensors 的 mmap 只加载用到的张量（多 LoRA 适配器共享底座时省大显存）。
- **预加载流水**：上一个 checkpoint 从对象存储流式拉取与容器启动重叠（题库 164 的"高效加载"本质是流水线化）。

多节点同步（题库 165）的要点：恢复时各 rank 按全局元数据只取自己的分片，**对象存储按名字空间组织**（step/layer/rank），加上"最新完整 checkpoint"的原子指针（写入完成后才更新）避免读到半成品。

## 存储选型的一页账

| 介质 | 带宽 | 用途 |
| ---- | ---- | ---- |
| 本地 NVMe | 3–7 GB/s/盘 | 第一级缓冲，本地快照 |
| 分布式文件系统（3FS/Lustre/JuiceFS） | 聚合 TB/s 级 | 训练主存储 |
| 对象存储（S3/OSS） | 单流 ~1 GB/s，聚合高、单流慢 | 归档、跨集群、发布 |

典型拓扑：**rank → 本地 NVMe → 异步聚合到分布式 FS → 关键里程碑异步归档对象存储**。每层的保存间隔与带宽预算（题库 169 的"云与本地差异"）：对象存储单流慢、不适合直接承接万卡同步写入，但容量/成本/持久性最优。

## 小结

- 格式演进 = pickle（可执行、整体读）→ safetensors（安全、mmap）→ DCP（分布式分片、可重分片）。
- 写入靠**聚合带宽**（多节点并发）+ **异步化**（侧缓冲快照）；恢复靠重分片加载 + 懒加载 + 流水预取。
- 分布式一致性要点：同一逻辑步 + 原子版本指针。
- 存储拓扑三级化：本地 NVMe 缓冲 → 分布式 FS 主力 → 对象存储归档。

## 思考题

1. 12 TB checkpoint、要求 5 分钟内写完：需要多大的聚合写带宽？64 节点每节点 2 盘 NVMe（每盘 5 GB/s）够吗？
2. 为什么"换并行布局加载"（TP8→TP4）用文件级格式做不到，DCP 可以？
3. 异步 checkpoint 写的是"上一步"快照，这引入的语义差异是什么？什么故障会放大它？

::: details 参考答案

1. $12\text{ TB}/300\text{ s}\approx 40\text{ GB/s}$。64×2×5=640 GB/s 聚合，绰绰有余——瓶颈实际会移到网络（每节点 10 GB 出口 × 64 = 640 GB/s 需要网络也匹配）与文件系统的元数据处理。
2. 文件级格式把张量按**保存时的物理分片**固化；DCP 存"逻辑张量 → 分片映射"的元数据，加载时按新布局重新路由读取并按需 gather/scatter——本质是把 reshard 做进了 IO 层。
3. 故障窗口多了一个 checkpoint 间隔的工作量（容错篇的 $E[\text{loss}]=t_{\text{ck}}+\dots$ 里的项变大）；对"中断后必须精确续训"的合规场景（如数据已删除的流式训练），还可能造成样本重复/丢失，需要数据游标配合。

:::

## 参考资料

- HuggingFace, [safetensors 文档](https://huggingface.co/docs/safetensors/index)
- PyTorch, [Distributed Checkpoint (DCP) 文档](https://pytorch.org/docs/stable/distributed.checkpoint.html)
- DeepSeek-AI, [3FS — A High-Performance Distributed File System](https://github.com/deepseek-ai/3FS) 与相关设计分享（TB/s 级 checkpoint 写入）

