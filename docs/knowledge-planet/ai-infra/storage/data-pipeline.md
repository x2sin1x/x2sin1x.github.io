---
title: "数据管道与存储选型"
date: 2026-09-29T10:30:00+08:00
weight: 20
---

# 数据管道与存储选型

> 训练状态是"写多读少且顺序"，训练数据是"读多写少且随机"——两种负载需要的存储完全不同。本篇讲数据侧：**文件系统怎么选、缓存怎么做、解码怎么不拖后腿**。

## 负载画像决定选型

先给数据负载画像（题库 162 的方法论）：**读放大**（一个 epoch 读几遍）、**随机度**（样本是否打散）、**单样本大小**（文本 KB 级 vs 图像 MB 级 vs 视频 10 MB+）。三种负载、三种答案：

| 负载特征 | 合适的存储 | 理由 |
| ---- | ---- | ---- |
| 海量小文件随机读（原始文本/图像） | **对象存储 + 打包格式**（WebDataset/Parquet/TFRecord） | 小文件直读会被元数据 QPS 打死；打包成 100 MB 级 shard 顺序读 |
| 高吞吐顺序流（预 tokenize 后的 token 流） | 分布式文件系统（Lustre/3FS/JuiceFS）或对象存储直读 | 顺序大块读，聚合带宽就是一切 |
| 需 POSIX 语义/频繁覆盖（训练临时产物） | 分布式 FS 或本地 NVMe | 随机写与元数据操作 |

**打包分片（sharding，题库 168）**是数据管道的枢纽设计：按 shard 打包后，读取顺序化、缓存友好、并行度高；全局 shuffle 则在 shard 间打乱 + shard 内 buffer 洗牌两阶段完成（见[训练 Infra]篇）。shard 大小的权衡：越大越顺序（好读）、但 shuffle 粒度越粗、失败重试重读越多——经验值 100 MB–1 GB。

## 缓存：三级水位

数据通常跑多个 epoch、被多个任务复用，缓存按"离 GPU 的距离"分层（题库 163）：

1. **节点本地 NVMe/内存**：热 shard 的本地副本。容量有限，靠 LRU（题库 284 的 bloom filter 可加速"是否已缓存"判断）与任务亲和调度（同一任务的 worker 调度到有缓存的节点）提高命中。
2. **集群共享缓存**（Alluxio 类）：跨任务共享热数据，适合多任务读同一数据集的组织。
3. **源站对象存储**：最终真相，吞吐大但延迟高。

缓存策略的核心账：**命中率 ×（源站延迟 - 本地延迟） vs 缓存成本**。训练场景的特殊性：数据集内样本被读概率几乎均匀（全量遍历），LRU 优化空间小——**预取与预加载（任务启动前批量预热）往往比运行时缓存更有效**。

## GPU 解码与 DALI

图像/视频多模态训练的经典瓶颈是 CPU 解码（题库 167/208）：JPEG 解码单核 ~50 张/s，一 GPU 一秒要上千张——CPU 核数成为硬约束。**DALI（NVIDIA Data Loading Library）把解码/增强搬上 GPU**：NVJPEG/NVDEC 硬件解码 + GPU 上的 resize/crop/normalize，pipeline 全程不回 CPU。适用判断：**CPU 已经加满 worker 还喂不饱时**再上 DALI（它吃 GPU 算力与显存，且增加 pipeline 复杂度）；文本为主、预 tokenize 完成的 LLM 训练用不上它。

更彻底的方案是**数据预处理前移**：训练前一次性把图像编码成 feature/token、把文本 tokenize 成二进制 token 流——训练时零解码、纯顺序读。代价是"改增强策略就要重处理全量数据"（[训练 Infra]篇思考题 3 的权衡）。

## 诊断：bottleneck 在哪一层

数据管道的分段压测法（题库 166 的展开）：

1. **基线**：只训练（dummy data）→ GPU 上限吞吐 $T_{\max}$。
2. **只读**：完整数据管道但不训练 → 管道吞吐 $T_{\text{pipe}}$。
3. 逐步启用：+GPU 解码、+预取、+缓存，看 $T_{\text{pipe}}$ 爬升到哪。

诊断工具分层：网络层（iperf3 对比节点间吞吐）、存储层（fio 压测本地盘、对象存储 SDK 的单流/并发基准）、处理层（py-spy 看 worker 内解码热点）、总线层（nvidia-smi 的 H2D 带宽，pageable vs pinned 的差距能到 3 倍）。**大文件的 external sort 类需求（题库 282）在数据侧的对应物**是：样本级排序用外部归并（shard 内排序 + shard 间归并），避免全量进内存。

## 元数据管理（题库 170）

万亿样本的元数据（路径、长度、质量分、去重指纹）本身就是数十亿行的表：

- **格式**：Parquet（列存、谓词下推、按长度列直接构建分桶）是主流。
- **索引**：按"长度桶/领域/质量分"建多级分区，训练时按配比采样直接定位——比全量扫描快几个数量级。
- **去重**：MinHash/LSH 指纹的存储与查询是分布式哈希/一致性哈希（题库 283）的直接应用场景。

## 小结

- 选型从负载画像出发：随机小文件 → 打包 shard + 对象存储；顺序 token 流 → 分布式 FS；POSIX 需求 → 分布式 FS/本地盘。
- 打包分片是管道枢纽，shard 大小平衡顺序性与 shuffle 粒度；训练场景预加载常优于运行时缓存。
- CPU 解码瓶颈的解法梯度：多 worker → GPU 解码（DALI）→ 预处理前移。
- 分段压测定位瓶颈，元数据用列存 + 多级分区管理。

## 思考题

1. 一个 10 TB 图像集（1000 万张，每张 1 MB）：原始小文件 vs 打包 512 MB shard，随机读 QPS 会差多少量级？为什么？
2. 你把 DALI 接进 pipeline 后 GPU 利用率反而下降，可能的原因？
3. 多 epoch 训练下"全局 shuffle"为什么不能只靠 shard 内洗牌？

::: details 参考答案

1. 差 3–5 个量级。原始小文件：每次读都有元数据查询 + 小 IO，单客户端几十至几百 QPS；shard：一次顺序读 512 MB 可解析上千样本，QPS 限制从元数据变成带宽。这就是 WebDataset/Parquet 存在的理由。
2. GPU 解码吃掉了训练/GEMM 的算力与显存带宽（多模态训练里 GPU 同时做解码与计算，互相挤占）；或 DALI pipeline 的 GPU 解码本身成了新瓶颈（NVDEC 利用率/显存不足），预取缓冲被掏空。
3. shard 内洗牌只保证 shard 内随机；跨 epoch 时若 shard 顺序固定，同一 shard 的样本总在同一时间窗出现（样本与训练阶段相关，损失梯度有偏）。必须每 epoch 重排 shard 顺序（或全局混洗分片序列）。

:::

## 参考资料

- NVIDIA, [DALI 文档](https://docs.nvidia.com/deeplearning/dali/user-guide/docs/)（GPU decode pipeline）
- WebDataset, [设计文档](https://github.com/webdataset/webdataset)（shard 格式与随机读）
- DeepSeek-AI, [3FS](https://github.com/deepseek-ai/3FS)（高吞吐文件系统设计）；Penedo et al., [FineWeb 数据集报告](https://arxiv.org/abs/2406.17557)（大规模数据管道工程实践）

