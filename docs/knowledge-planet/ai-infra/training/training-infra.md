---
title: "训练 Infra：数据管道、恢复与实验管理"
date: 2026-09-29T10:30:00+08:00
weight: 70
---

# 训练 Infra：数据管道、恢复与实验管理

> 模型代码只占训练系统的一小部分。本篇收拢训练的"外围"工程：**数据怎么流进来、中断后怎么继续、实验怎么管、长上下文与多模态带来什么新问题**。

## 数据管道：让 GPU 永远有下一批数据

数据管道的目标只有一个：**GPU 的等待时间为零**。分层结构（对应题库 154/166）：

1. **读取层**：对象存储/分布式文件系统（选型见[数据管道与存储选型](/knowledge-planet/ai-infra/storage/data-pipeline)篇）。
2. **处理层**：解码、增强、tokenize——CPU 密集，靠 `DataLoader` 的 worker 并行（`num_workers` 的经验值：每 GPU 4–8 个，瓶颈在 CPU 核数与内存带宽；配 `pin_memory=True` 让 H2D 拷贝走 DMA）。
3. **传输层**：异步预取（`prefetch_factor`），让第 $n$ 步训练与第 $n{+}k$ 批预处理重叠。

诊断瓶颈的标准方法（题库 166）：看 GPU 的 step 间隙（profiler 时间线上 kernel 之间的空洞）；再分别压测"只读不训"与"只训不读"——两者的差值就是管道欠的债。图像多模态训练的经典坑是 **CPU 解码跟不上**，解法是 GPU 解码（DALI，见[存储章](/knowledge-planet/ai-infra/storage/data-pipeline)）或更激进的预 token 化/预编码（把图像预先处理成 feature 存储，训练时零解码）。

**全局 shuffle**（题库 222）：万亿 token 预训练要求样本全局随机，而数据是按分片存储的。两阶段方案：粗粒度 shuffle（把分片序列全局打乱，启动时一次）+ 细粒度 shuffle（worker 内 buffer 池随机采样）。纯 in-memory 全局 shuffle 对 TB 级数据不现实，账本是"随机性够用"与"IO 可行"的折中。

## 恢复一致性：checkpoint 之后的那点事

容错的存储视角见[存储章](/knowledge-planet/ai-infra/storage/checkpoint-storage)，这里讲**恢复流程的正确性**（题库 153）：

- **必须恢复的状态**不止模型与优化器：数据加载器的位置（epoch/step/分片游标）、随机数状态（数据增强、dropout 的种子链）、学习率调度器、EMA 权重——漏掉任何一项都造成"恢复成功但实验作废"。
- **非确定性**：即使全部状态对齐，cudnn benchmark、atomics、异步 reduce 的浮点顺序都会让恢复后的 loss 曲线有小抖动。验收标准不是 bit-exact，而是**统计等价**（loss 曲线在若干步内重合）。
- **恢复时间账**：万卡集群重启 + 加载 TB 级 checkpoint + 重新 warmup 的全程要几十分钟——恢复频率与恢复时间的乘积是真实的产能税（[容错](/knowledge-planet/ai-infra/distributed/fault-tolerance)篇的最优间隔公式在此兑现）。

## 实验管理：大规模训练的可观测三件套

题库 160 的清单，按"出了事能不能回答"组织：

1. **指标**：loss/grad-norm/学习率按 step 记录，MFU/吞吐按小时聚合（口径见[性能指标](/knowledge-planet/ai-infra/profiling/metrics)篇）——回答"训练健康吗"。
2. **环境与配置**：git commit、数据版本、超参、硬件拓扑快照——回答"这个结果怎么复现"。
3. **异常留证**：异常样本 dump（loss 尖刺时的 batch）、NCCL/驱动日志归档——回答"上周那次中断为什么发生"。

工具（Weights & Biases/TensorBoard/自研）是次要的，**记录粒度与留存策略**才是重点：万卡训练每 step 记录的聚合开销必须压到毫秒级（异步上报），而原始日志要留到模型发布后数年。

## 两个前沿负载的 Infra 挑战

**长上下文训练（100K+ token，题库 158）**：激活的平方项爆炸（score 矩阵）、序列并行的通信、attention kernel 的分块——技术清单散见各篇（[序列并行](/knowledge-planet/ai-infra/parallelism/sequence-parallelism)、[FlashAttention](/knowledge-planet/ai-infra/hpc/attention-kernels)），Infra 层的组合结论是：**CP（context parallel）+ FA + selective 重算**是当前的长上下文标准配方，数据侧则要按长度分桶避免 batch 内 padding 浪费。

**多模态训练（题库 155）**：三重新增——数据管道新增图像/视频解码（CPU 瓶颈位移，见上文）、显存账新增视觉编码器（ViT 的激活与文本模型不同构，并行切分要分别规划）、以及**多阶段混合训练**（图文对齐 → 指令微调）的数据配比与热切换。工程上最常见的错误是把视觉塔与语言塔的并行配置绑死——两者该独立选 TP/PP 再拼接。

## 小结

- 数据管道三层各自可压测，"只读不训 vs 只训不读"的差值就是优化空间；全局 shuffle 靠两阶段折中。
- 恢复一致性 = 全部随机性状态 + 统计等价验收；恢复时间是产能税，进入容错的间隔公式。
- 实验管理三件套回答三个问题：健康吗、能复现吗、为什么坏；粒度与留存比工具重要。
- 长上下文与多模态不是单点优化，而是并行/kernel/数据管道的重新组合。

## 思考题

1. `num_workers=8` 后 GPU 利用率仍只有 60%：给出你的下一步诊断动作（至少三个）。
2. 恢复时漏了 dropout 的 RNG 状态，后果是什么量级？bit-exact 为什么本来就不该是目标？
3. 预 token 化（预先 tokenize 存储）牺牲了什么，换来了什么？什么场景不值得？

::: details 参考答案

1. ① 压测"只训不读"得到 GPU 上限时间，算出管道欠债比例；② 检查 CPU 利用率与 worker 内解码热点（py-spy）；③ 看 H2D 拷贝与 pinned memory（是否 pageable 拷贝）；④ 检查存储端吞吐（分片是否打散、是否命中缓存）。
2. dropout mask 全变 → 恢复后模型走上一条统计上等价但路径不同的轨迹；单次实验影响不大，但对"恢复后 loss 应与中断前衔接"的回归测试是致命的。bit-exact 本来就不可达（非确定性 reduce/atomics），验收标准应是统计等价。
3. 牺牲：数据版本与 tokenize 逻辑的耦合（改词表要重处理全量数据）、存储占用（存 token 比存原文大）。换来：训练时零 CPU tokenize、IO 更规整。不值得的场景：实验期频繁换 tokenizer/数据配比的阶段。

:::

## 参考资料

- PyTorch, [DataLoader 文档](https://pytorch.org/docs/stable/data.html)（worker/prefetch/pin_memory 语义）
- Li et al., [MegaScale](https://arxiv.org/abs/2402.15627)（数据管道与训练诊断实践）
- Meta AI, [The Llama 3 Herd of Models](https://arxiv.org/abs/2407.21783)（长上下文与多模态训练的 Infra 章节）

