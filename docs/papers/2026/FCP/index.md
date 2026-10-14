---
title: "FCP"
date: 2026-05-08
tags:
  - AI Infrastructure
  - Distributed Training
categories:
  - MLSys
description: "把每条序列切成固定大小的块、允许块落在任意 GPU 上，用 LPT 装箱均衡负载、用二部图匹配规划无拥塞通信，在长尾序列分布下同时拿到单卡高 MFU 与全局负载均衡：256 GPU 上近线性扩展，attention MFU 提高 1.13x-2.21x。"
---

# FCP：把 ring 从 context parallelism 的必需品降级为一种特例

Yilong Zhao, Xiaonan Nie, Kan Zhu, Shuang Ma, Zhichao Lai, Hongxiang Hao, Yang Zhou, Baris Kasikci, Ion Stoica · MLSys 2026

[Paper](https://arxiv.org/abs/2605.08524v1)（arXiv 2605.08524v1，2026-05-08 提交，本文于 2026-09-28 核对）

长上下文和多模态把 foundation model 预训练的序列越拉越长——一张 1080p 图片对应数千个 patch token，一分钟 30 fps 的视频可以膨胀到百万 token 级别。Context parallelism（CP）因此成了标配：把每条序列切开分给多张 GPU 并行算 attention。但真实预训练语料的序列长度呈长尾分布，从几千 token 到 512K 不等，而现有 CP 设计都默认序列长度是均匀的：要么把所有序列均匀切分，短序列被切碎到打不满 TensorCore 还白白增加通信；要么把长短序列分给不同的 GPU 组，长尾序列把负载均衡彻底打乱。

FCP 换了一种切法和一种放法：把每条序列切成固定大小的块，块可以落到集群里的任意 GPU 上——为此它放弃了所有人默认的 ring 通信拓扑，改用任意点对点通信，再用负载感知装箱和无拥塞的通信规划把灵活性变成实际收益。论文在最多 256 张 NVIDIA GPU 上测得近线性扩展，attention MFU 相对 Ring Attention、ByteScale、WLB-LLM 和 MagiAttention 四个基线提高 1.13x-2.21x。

## Why FCP?

先看现有 CP 是怎么工作的。以最主流的 ring attention 为例：每条序列被均匀切成与 GPU 数量相关的若干块（ring attention 切成 2N 块，每张 GPU 拿两块，按 Zig-Zag 顺序配对），然后所有 GPU 围成一个环，每一步从邻居拉来一份 KV、和本地 Q 算一段 attention、再把 KV 传给下一个邻居。双缓冲让通信和计算重叠，Zig-Zag 让 causal mask 下每张 GPU 的计算量和通信量完全一样。这套机制在"所有序列一样长"的世界里近乎完美。

问题出在真实语料不是那个世界。论文从内部预训练任务里统计的序列长度分布近似 lognormal，长尾延伸到 512K：既有大量塞不满一张 GPU 的短文本，也有比它长几个数量级的视频或长文档样本。这个分布从两个方向击穿 ring attention 的假设。

第一是计算效率。现代 GPU 的 TensorCore 需要足够大的输入才能打满：以 Hopper 为例，989 TFLOPs 的 BF16 峰值算力配 4.8 TB/s 的显存带宽，意味着每个从显存读出的元素要被复用约 412 次才够本，而 attention kernel 内部的复用远没有这么容易。ring attention 对每条序列一视同仁地切 2N 块，短序列自然被切成极小的块——论文实测，块长低于 2K token 时 attention MFU 明显下滑，512 token 的块只能用到单卡 MFU 的 25%。更亏的是通信：小于 4K 的序列本可以整个留在一张 GPU 上零通信，在朴素 CP 下它们却贡献了约一半的通信量。为了并行而并行，把算力换成了搬运。

第二是负载不均衡。attention 的计算量随序列长度二次增长，而按长度分组的方案（以 ByteScale 为代表）只按长度线性地给每组分配 GPU 数量。一条 64K 序列的计算量是 4K 序列的 256 倍，却只分到 16 倍的计算资源——组内没有别的序列可以帮它摊平，落后者的长度就是整个集群的长度。这类方案在论文的真实分布下测得最高 70% 的负载不均衡。WLB-LLM 干脆在两种策略之间按在线性能模型切换，但这只是在一口锅里二选一，没有扩大搜索空间：计算效率和负载均衡依然是一个非此即彼的权衡。

![Figure 5：两类现有 CP 设计。(a) balance-optimized 的 ring attention 把每条序列切成固定块数、Zig-Zag 配对，负载完美均衡但短序列被切成碎块；(b) efficiency-optimized 的方案按长度把序列分给不同 GPU 组，组内计算高效但组间失衡](https://arxiv.org/html/2605.08524v1/existing-pattern.drawio.svg)

> 来源：论文 Figure 5。读图重点：两种设计分别在 G（怎么切）和 M（怎么放）两个自由度上做了简化，代价分别落在计算效率和负载均衡上——这是同一枚硬币的两面。

把两条失败摆在一起，问题就浮出来了：

> **能不能既让每个计算块大到打满硬件，又让负载在整个集群里精确均衡？**

两类现有方案在这道题上各让一半，是因为它们共享一个更深的默认假设——序列必须沿一个固定的 ring 对称切分和轮转。FCP 的第一步，就是质疑这个假设本身。

## How FCP Works

### 关键洞察：ring 不是高效通信的必要条件

ring 拓扑之所以无处不在，是因为它的通信模式对称、邻居固定，容易实现通信与计算的重叠。但"重叠"真正需要的只是：每个阶段的通信时间不超过计算时间。论文算了一笔账：在 Hopper GPU 加 50 GB/s 的 ConnectX-7 InfiniBand 上，只要 22 GB/s——不到线速的一半——就能把一个块的通信完全藏进它的计算里。而且块越大，这个要求越低：块内计算量随块长二次增长，通信量只线性增长。

这就是 FCP 全部的杠杆：既然任意点对点通信在带宽上完全付得起，那么"块必须沿 ring 对称摆放"这个约束就可以整个拆掉，把切分（G）和放置（M）两个自由度还给调度算法。剩下的工作是把灵活性兑现成性能——依次解决怎么放、怎么传、怎么接入现有框架三件事。

### 设计

![Figure 6：FCP 系统总览。Block Distributor 决定块的切分与放置，Communication Planner 依据块间依赖构建二部图并求解无拥塞的通信计划，Transparent Reshuffler 在 attention 模块边界处现场重排数据布局](https://arxiv.org/html/2605.08524v1/fcp-design.drawio.png)

> 来源：论文 Figure 6。读图重点：三个组件分别对应"放哪里、按什么顺序传、如何不打扰现有并行方案"三个问题，缺一环灵活性都无法落地。

1. **Block Distributor（块分发器）：** 每条序列不管多长都切成固定大小的块（评测中取 4K token），块足够大以保证单块就能打满硬件，短序列不足一块时用 varlen kernel 打包计算。然后做多维装箱：把每个块按内存和计算两个维度归一化后降序排列，贪心地放到当前最闲、且内存不超限的 GPU 上——这是经典 Longest Processing Time 调度的一个变体，复杂度只有 O(K log N)。序列内部的 causal 不均衡仍交给 Zig-Zag 配对处理，于是通信均衡也被归约成计算均衡。相对 ring attention，它改的是"块数随序列长度变化、块大小恒定"，长尾被装箱吸收而不是被切碎或孤立。
2. **Communication Planner（通信规划器）：** 任意放置意味着任意 GPU 之间都可能要传块，无序的拉取会让多张 GPU 同时涌向同一个源节点。FCP 把每次传输建模成二部图上的一条边（N 个发送节点对 N 个接收节点），一轮"每张 GPU 至多发一块、至多收一块"的无拥塞通信恰好对应图上的一个匹配；由二部图边着色理论，整个图可以分解成 Δ 个匹配（Δ 是最大度），这就是最优的子阶段数。论文用 Hopcroft-Karp 算法在 O(N^2.5) 时间内求解，每 batch 只算一次，数百 worker 规模下秒级完成、可在 CPU 上大规模并行。在此之上，块级的拉-算-推三个阶段被拆成交错的子阶段流水，让通信始终有计算可以隐藏。
3. **Bottom-up coalescer 与 Transparent Reshuffler（合并器与透明重排器）：** 前者把连续若干个块级子阶段（默认 16 个）合并成更大的执行单元——调度粒度和执行粒度就此解耦，块可以小到适合装箱，kernel 可以大到适合跑满。后者负责部署透明性：进入 attention 模块前把用户提供的序列布局现场重排成 FCP 需要的布局，退出后还原，dataloader、RoPE 和 FSDP、TP、EP、SP 等现有并行方式都不用改；重排通信被安排在流水线首尾、与不依赖远端块的本地计算重叠。

![Figure 8：无拥塞求解器示例。依据块放置得到的跨 GPU 依赖构建二部图（如序列 B 的第 1 块要从 GPU 2 传到 GPU 0 和 GPU 1，产生 2→0、2→1 两条边），每次最大匹配即一轮无拥塞通信](https://arxiv.org/html/2605.08524v1/fcp-communicate.drawio.svg)

> 来源：论文 Figure 8。读图重点：每一轮匹配里每张 GPU 恰好进出各一个块，网络永远不会有热点；最大度 Δ 决定轮数下界，分解恰好达到这个下界。

工程实现上，FCP 约 4K 行 Python，对 FlashAttention 3 kernel 做了少量修改；用 CUDA Green Context 把少量 SM（GPU-X 上 6 个、GPU-Y 上 8 个）划给纯搬运的通信流，其余 SM 专心计算；配合 NCCL 的 group P2P 原语和感知网络拓扑的通信路径，多缓冲流水进一步压掉流水线气泡。

## Results

实验设置：Llama-3-70B 的模型配置（8 个 KV head、64 个 QO head、head dim 128），序列从内部预训练 trace 中采样（最长 512K，即前文的长尾分布），每 GPU 固定 32K token、causal mask，弱扩展。硬件是两个匿名化的工业界与学术界集群（GPU-X 与 GPU-Y，算通比分别为 5920 和 2500），规模最多 256 卡。基线是 Ring Attention（TransformerEngine 实现）、ByteScale（按长度分组）、WLB-LLM（用 oracle 切换作为其上界版本）和开源的 MagiAttention。

证据分三层。负载均衡层：FCP 把计算与通信的不均衡率始终压在 5% 以内，而 ByteScale 在长尾分布下最高 70%，MagiAttention 因只优化计算、通信不均衡最高 17%。单卡效率层：假设负载完全均衡时，FCP 的 attention MFU 稳定在 90% 以上（其中已扣除让给通信的那几个 SM）。合起来的最终结果如下图：

![Figure 11：真实长尾数据集上 attention 模块级 MFU 的弱扩展（每 GPU 32K token）；FCP 在所有 GPU 规模下高于全部四个基线，且随规模扩大差距拉开](https://arxiv.org/html/2605.08524v1/fig-eval-mfu.svg)

> 来源：论文 Figure 11。读图重点：16 卡时各方案差距很小——规模小时没有多少调度余地；随着 CP 度数增大，Ring Attention 因短序列过度切分而下滑，ByteScale 因组间失衡下滑更快，FCP 保持近线性。这也是全文 1.13x-2.21x MFU 提升的出处。

消融实验（128 卡 GPU-X）把每个组件的贡献单独拆开，数值为相对上一步的提升：

| 配置 | Forward MFU | Backward MFU |
| --- | --- | --- |
| 基线（无块级流水） | 0.29 | 0.37 |
| + 块级流水线 | 0.48（+64%） | 0.46（+24%） |
| + 无拥塞求解器 | 0.62（+29%） | 0.59（+28%） |
| + 自底向上合并 | 0.70（+10%） | 0.69（+17%） |
| + 透明重排器 | 0.75（+7%） | 0.74（+7%） |

> 根据原论文 Table 2 重绘。块级流水线和无拥塞求解器合计贡献了最大的一块收益——灵活性必须靠通信规划兑现。

泛化性方面：换到采用 FlashAttention 4 的 GPU-Y 集群，FCP 仍全面领先，达到单卡 FA4 MFU 的 70% 以上（差距主要来自让给通信的 SM 和更高的算术强度要求）；在合成的弱长尾和双峰分布下结论不变；块大小 4K 是均衡与效率的甜点，2K 到 6K 之间的差异约 7%，说明该超参数不算脆弱。

边界同样要交代。FCP 的任意点对点通信在多包合并后近似 all-to-all 流量，这要求 fat-tree 或 rail-optimized 的 InfiniBand/RoCE 网络，论文明确指出在 torus 拓扑（如 TPU v3 集群）上性能受限；方法目前只处理 causal 和 non-causal mask，不规则稀疏 mask 留作未来工作；出于保密，GPU 型号与集群规模匿名，基线中 WLB-LLM 是作者重实现的 oracle 版本而非官方代码直跑。此外，截至 2026-09-28 核对时，论文与 arXiv 页面均未提供 FCP 的官方开源实现，想复现需要自行搭建。

## Sources

- [FCP arXiv v1](https://arxiv.org/abs/2605.08524v1)，2026-05-08 提交，MLSys 2026，本文于 2026-09-28 核对
- [MagiAttention 开源仓库](https://github.com/SandAI-org/MagiAttention/)，论文中作为对照的并发开源工作

## Conclusion

**FCP 证明了 CP 的调度不必在计算效率和负载均衡之间二选一。** 固定块长保住了单卡 MFU，任意放置加 LPT 装箱保住了全局均衡，二部图匹配的通信规划和块级流水线再把任意拓扑的通信代价藏进计算——256 卡上近线性扩展和 1.13x-2.21x 的 MFU 提升为这条链路闭环。

**它改变的是对 ring 的定位。** ring attention 长期被当作 CP 的定义本身，FCP 说明它只是任意点对点通信约束最严的一个特例；拆掉这个约束后，CP 调度回到了两个被充分研究的经典问题——装箱和匹配。对做分布式训练系统的读者来说，"先质疑通信拓扑假设，再谈调度算法"是一个可以迁移到其他集合通信场景的思考顺序。

## Citation

```bibtex
@misc{zhao2026fcp,
  title         = {Unleashing Scalable Context Parallelism for Foundation Models Pre-Training via FCP},
  author        = {Yilong Zhao and Xiaonan Nie and Kan Zhu and Shuang Ma and Zhichao Lai and Hongxiang Hao and Yang Zhou and Baris Kasikci and Ion Stoica},
  year          = {2026},
  eprint        = {2605.08524},
  archivePrefix = {arXiv},
  primaryClass  = {cs.DC},
  note          = {MLSys 2026},
  url           = {https://arxiv.org/abs/2605.08524}
}
```
