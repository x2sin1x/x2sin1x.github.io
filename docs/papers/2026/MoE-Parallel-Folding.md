---
title: "MoE Parallel Folding"
date: 2026-03-02
tags:
  - AI Infrastructure
  - Distributed Training
  - MoE
categories:
  - arXiv
description: "让 Attention 层与 MoE 层各自持有独立的并行映射，把 EP 从 DP 的子集中解放出来折叠进 NVLink 域，配合支持 token-dropping 与 token-dropless 的统一 token dispatcher：Mixtral 8x22B 在 H100 上达到 49.3% MFU，扩展至 1024 GPU 与 128K 上下文，已随 Megatron-Core 开源。"
---

# MoE Parallel Folding：Attention 和 MoE 层，本就不该共用同一套并行图

Dennis Liu, Zijie Yan, Xin Yao, Tong Liu, Vijay Korthikanti, Evan Wu, Shiqing Fan, Gao Deng, Hongxiao Bai, Jianbin Chang, Ashwath Aithal, Michael Andersch, Mohammad Shoeybi, Jiajie Yao, Chandler Zhou, David Wu, Xipeng Li, June Yang · NVIDIA

[Paper](https://arxiv.org/abs/2504.14960v3)（arXiv 2504.14960v3，2025-04-21 首发于 arXiv，本文依据 2026-03-02 更新的 v3 于 2026-09-28 核对） · [Code](https://github.com/NVIDIA/Megatron-LM)（已合入 Megatron-Core）

MoE 用稀疏激活换参数规模：每个 token 只过 Top-K 个专家，模型可以堆到数千亿参数而计算量可控。但这份稀疏性恰恰是训练系统的噩梦——MoE 模型的计算/参数比远低于 dense 模型，dense 模型那套"TP 开小了显存爆、开大了通信贵"的 3D 并行配方直接照搬过来两头不讨好；而以往方案把 expert parallelism（EP）当作 data parallelism（DP）的子集来组织，EP 的度数被 DP 封顶，专家一多就无路可走。

MoE Parallel Folding 的做法是把"并行映射"这件事从模型级常量降级为逐层选择：Attention 层走 TP×CP×DP×PP 四维组，MoE 层另立一套 ETP×EP×EDP×PP 四维组，两者的模型并行维度可以自由折叠，层间转换只需一次 reshape、零通信。论文在 NVIDIA Eos 集群的 H100 上把 Mixtral 8x22B 训到 49.3% MFU、Qwen2-57B-A14B 训到 39.0% MFU，强扩展到 1024 GPU、上下文扩展到 128K 仍保持高性能，方法已随 Megatron-Core 开源。

## Quick Start

方法已合入[官方仓库](https://github.com/NVIDIA/Megatron-LM)（Megatron-Core，本文依据 main 分支与 core_v0.19.2，2026-09-28 核对，未实测训练）。最短探索路径是官方 Mixtral 示例脚本，它已经用上 EP 与分布式优化器：

```bash
git clone https://github.com/NVIDIA/Megatron-LM && cd Megatron-LM
# 需先准备 checkpoint、tokenizer 与预处理数据；单机 8 卡起步，多机改 MASTER_ADDR/NNODES
bash examples/mixtral/train_mixtral_8x7b_distributed.sh <checkpoint> <tokenizer_model> <data_path>
```

与本文方法对应的两个关键旋钮都在 `pretrain_gpt.py` 的参数里：`--expert-tensor-parallel-size`（ETP，缺省跟随 TP；设为 1、同时拉大 `--expert-model-parallel-size` 即论文中"EP 优先于 ETP"的折叠配置）与 `--moe-token-dispatcher-type flex`（论文的灵活 dispatcher）。生产集成路径就是 Megatron-Core 本身——这篇论文的工程载体，配置细节见官方 `examples/moe` 与论文附录 A 的逐模型最优映射表。

## Why MoE Parallel Folding?

先看 MoE 训练在并行什么。一条 Transformer 里有两类层：Attention 层对整条序列做稠密计算，序列内部有数据依赖；MoE 层对单个 token 独立算 FFN，路由器把每个 token 发给 Top-K 个专家。EP 的流水线因此是三段式：按专家分组 permutation 排列 token，一次 All-to-All 把 token 送到专家所在的 GPU，专家计算完再逆置换还原。专家之间互不通信，这让 EP 在 MoE 层天然比 TP 便宜。

问题在于以往框架只给 MoE 一套被 Attention 绑定的并行图。EP 组被放在 DP 组内部，EP 的最大度数被 DP 度数封顶——想要 64 路 EP，就得先有 64 路 DP 冗余；而 MoE 层被迫沿用 Attention 的 TP 配置时，就出现了论文反复命中的困境：TP 开小，MoE 参数和激活塞不下；TP 开大，模型并行通信膨胀，算力被搬运吃掉。具体有多惨，论文在同一框架内做了横向对比：纯 FSDP 在四个 MoE 模型上 MFU 全部低于 10%，最大的 Llama3-8x70B 直接 OOM；FSDP+EP 好转但通信无法与计算充分重叠；TP+EP+DP 进一步改善，可大 TP 的激活通信又把 MFU 拖回来，Llama3-8x70B 仍然 OOM。即便是支持 5D 并行的 Megatron-Core 基线，因为 Attention 和 MoE 层耦合在同一套映射里，配置仍是次优的。

病根不在任何一个并行维度的调参，而在"一张并行图管所有层"这个约束本身：Attention 按序列切、MoE 按 token 派发，两种计算模式的通信形状不同，最优的分组方式没有理由相同。

> **能不能让 Attention 和 MoE 层各选各的并行映射，还不用为此付出额外交际代价？**

## How MoE Parallel Folding Works

### 关键洞察：层间转换只是一次 reshape

答案藏在 MoE 的计算性质里：专家对每个 token 独立计算，token 是哪个序列、哪个子序列的，专家根本不关心。所以无论 Attention 层把输入按 batch（DP）还是按序列（TP/CP）切开，进入 MoE 层时都只需要把序列/子序列摊平成一个 token batch——一次 reshape，零显式通信。既然层间没有通信障碍，两层就没有理由共享任何并行组。

### 设计

![Figure 1：并行映射对比。以往方案中 EP 组嵌套在 Attention 的 DP 组内，度数被 DP 封顶；MoE Parallel Folding 把 MoE 层的模型并行维度（EP/ETP）折叠到 Attention 层的任意子组上，两层各自组网](https://arxiv.org/html/2504.14960v3/images/MoE_Parallel_Folding-mapping-switch.png)

> 来源：论文 Figure 1。读图重点：EP 的度数上限不再由 DP 决定，MoE 层的模型并行可以与 Attention 的 TP/CP/DP 任意子组重叠——"折叠"指的就是这种组关系的重写。

1. **双四维并行组：** Attention 层组网为 TP×CP×DP×PP，MoE 层为 ETP×EP×EDP×PP（Expert-TP 与 Expert-DP 是 MoE 层自己的张量与数据并行）。唯一约束是 PP 组在两层间必须一致，否则流水线无法衔接。收益有二：MoE 层可以独立选最优映射——例如用通信更省的 EP 替换 ETP；同时模型并行通信被折叠进更紧凑的 GPU 组，尽量贴在 NVLink 高带宽域内。
2. **统一 token dispatcher：** 任意折叠组合下的数值正确性由它兜底。前向流程为：路由 permutation → EP 组 All-to-All-V → ETP 组 AllGather-V（组内共享激活）→ 专家 FFN 计算 → ETP 组 ReduceScatter-V → EP 组 All-to-All-V → 逆 permutation；反向以 RS/AG 镜像。它同时支持 token-dropping 与 token-dropless 两种范式，张量形状动态、与序列长度解耦。dropping 策略上，论文用子序列级 dropping 替代全序列级——不必跨卡 gather 全序列 logits，省通信还缓解负载不均，且经验上不伤收敛。
3. **与现有栈的组合：** dispatcher 消除了序列长度依赖，CP/SP、PP、分布式优化器都能照常叠加；论文附录 A 给出每个实验模型调出的最优映射，可直接当配置参考。

![Figure 2：TP=2、ETP=2 的四卡示例中 token dispatcher 的前向数据流：All-to-All-V 跨 EP 组换 token，AllGather-V/ReduceScatter-V 在 ETP 组内聚散激活](https://arxiv.org/html/2504.14960v3/images/dispatcher.excalidraw.png)

> 来源：论文 Figure 2。读图重点：GPU (0,1)(2,3) 是 ETP 组、(0,2)(1,3) 是 EP 组——同一批 GPU 在 MoE 层内同时身兼两种身份，这正是折叠后的组形态。

精度方面，论文用 Mixtral 8x7B 做了 token-dropless 训练验证（TP2/CP2/PP2/EP8/ETP1，40B tokens），训练与验证 loss 曲线与未折叠的 MCore v0.9 对齐，说明折叠不改变收敛结果。

## Results

实验设置：NVIDIA Eos 集群，DGX H100 节点（单卡 BF16 峰值 989.5 TFLOP/s，节点内 NVLink 450 GB/s、节点间 InfiniBand 400 Gbps），PyTorch 2.5.0 + CUDA 12.6，全局 batch 256、序列长 4096。四个模型覆盖粗细两档粒度：粗粒度的 Mixtral 8x22B 与 Llama3-8x70B（由 Llama3-70B upcycling 而来），细粒度的 Qwen2-57B-A14B 与 Mixtral-8x22B-G8T8（Mixtral 重参数化为 64 专家）。所有基线都实现在 Megatron-Core 内，且各自取调参后的最优配置。为压掉 dropless 训练的负载抖动，MFU 对比统一采用 capacity factor=1 的 token dropping。

下表根据原论文 Table 1 与 Table 3 整理，数值为 BF16 训练 MFU：

| 模型（粒度） | GPU 数 | FSDP | FSDP+EP | TP+EP+DP | MCore | MCore w/ Folding |
| --- | --- | --- | --- | --- | --- | --- |
| Mixtral-8x22B（粗） | 128 | 4.3% | 23.4% | 36.6% | 46.3% | **49.3%** |
| Llama3-8x70B（粗） | 256 | OOM | 19.6% | OOM | 38.8% | **41.6%** |
| Qwen2-57B-A14B（细） | 64 | 9.9% | 25.4% | 23.1% | 35.3% | **39.0%** |
| Mixtral-8x22B-G8T8（细） | 128 | 2.2% | 9.0% | 8.7% | 17.1% | **28.8%** |

Folding 对细粒度 MoE 的收益最醒目：G8T8 上相对 MCore 基线从 17.1% 提到 28.8%。消融给出了原因——细粒度 MoE 激活专家多、dispatch 通信量大、专家 hidden size 小导致 GEMM 效率低，当 ETP×EP 超过 8（跨节点）时通信占 MoE 层时延的 70% 以上，此时"EP 优先于 ETP、模型并行尽量小"的策略收益最大；折叠还让 CP×EP 组贴回 NVLink 域，避免 All-to-All 摔进节点间网络。

![Figure 3：强扩展实验，GPU 数增至 1024；各并行策略的 MFU 随规模变化，Folding 配置在所有规模下保持最高](https://arxiv.org/html/2504.14960v3/images/scaling.png)

> 来源：论文 Figure 3。读图重点：Llama3-8x70B 从 128 卡扩到 16 倍规模，Folding 的 MFU 仅从 43.7% 降到 41.5%——扩展性瓶颈被压平是折叠的核心价值。

两个方向的扩展都稳：上下文扩展实验中，batch 总 token 数不变、序列拉长到 128K，Qwen2-57B-A14B 的 MFU 从 38.7% 降到 35.9%，Mixtral 8x22B 从 47.6% 降到 42.9%。精度之外还测了速度上限：FP8 delayed scaling 下 Mixtral 8x22B 在 128 卡达到 631.7 TFLOPS（相对 BF16 无折叠 1.26x、有折叠 1.30x）。

边界要说清楚：所有 MFU 对比基于 token dropping（CF=1），dropless 训练的性能抖动问题被绕开而非解决；证据止于 loss 曲线对齐与吞吐，没有下游任务精度评估；对比基线全部在 Megatron-Core 内复现，代表的是"同一框架内的映射选择"收益，与框架外的实现（如 Megablocks）没有直接对比；Eos 集群的网络条件（NVLink + 400G IB）也意味着结论对低带宽互联环境的迁移需要谨慎。

## Sources

- [MoE Parallel Folding arXiv v3](https://arxiv.org/abs/2504.14960v3)，2025-04-21 首发、2026-03-02 更新，本文于 2026-09-28 核对
- [NVIDIA Megatron-LM 仓库](https://github.com/NVIDIA/Megatron-LM)，方法已合入 Megatron-Core（本文核对 main 分支与 core_v0.19.2，2026-09-18 发布）
- [官方 Mixtral 训练示例](https://github.com/NVIDIA/Megatron-LM/blob/main/examples/mixtral/train_mixtral_8x7b_distributed.sh)，Quick Start 命令依据该脚本核对

## Conclusion

**MoE Parallel Folding 证明了并行映射的最优解是逐层的，不是逐模型的。** 层间一次零通信的 reshape 解锁了两张独立的并行图，EP 从 DP 的子集里被解放出来折叠进 NVLink 域，统一 dispatcher 再兜住任意组合的数值正确性——四个模型、两个粒度上 MFU 全面领先，1024 卡与 128K 上下文下依然成立。

**它改变的是配置 MoE 训练时的提问方式。** 与其问"这个模型该用什么并行度"，不如先问"这个层类型的计算按什么单位切、通信落在哪个网络域"——前一个问题只有一个答案，后一个问题允许 Attention 和 MoE 给出不同答案。对设计下一代 MoE 系统（尤其细粒度专家和超长上下文）的读者来说，"每层一张并行图"是一个已经开源验证、可以直接借用的出发点。

## Citation

```bibtex
@misc{liu2025moeparallelfolding,
  title         = {MoE Parallel Folding: Heterogeneous Parallelism Mappings for Efficient Large-Scale MoE Model Training with Megatron Core},
  author        = {Dennis Liu and Zijie Yan and Xin Yao and Tong Liu and Vijay Korthikanti and Evan Wu and Shiqing Fan and Gao Deng and Hongxiao Bai and Jianbin Chang and Ashwath Aithal and Michael Andersch and Mohammad Shoeybi and Jiajie Yao and Chandler Zhou and David Wu and Xipeng Li and June Yang},
  year          = {2025},
  eprint        = {2504.14960},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG},
  url           = {https://arxiv.org/abs/2504.14960}
}
```
