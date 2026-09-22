---
title: "专家并行"
date: 2026-09-22T18:00:00+08:00
weight: 50
---

# 专家并行

> MoE 把"每个参数都参与每个 token"改成"少数专家服务每个 token"。**专家并行解决的是：专家放不下、也住不开。**

## MoE 的账先算清楚

以 DeepSeek-V3 为例：256 个路由专家 + 1 个共享专家、每 token 激活 8 个路由专家。总参数 $\Psi_{\text{total}}\approx671\text{B}$，激活参数每 token 仅约 37B——**容量与计算解耦**：

- 权重显存/并行切分：按**总**参数算（所有专家都要驻留）；
- 计算量：按**激活**参数算，$6ND$ 中的 $N$ 换成 $N_{\text{act}}$。

同一模型，"存"是 dense 的 7 倍难，"算"只有 dense 的 1/5——这就是 MoE 的 Infra 契约：**用显存和通信换算力**。

## 机制：all-to-all 两轮

专家按哈希/配置切到 $e$ 张卡。每层的 MoE 子层前后各一次 all-to-all：

::: mermaid
flowchart LR
    T0["卡0 的 token<br/>（部分要去卡2的专家）"] -- "dispatch<br/>all-to-all" --> E0["专家卡0"] & E2["专家卡2"]
    T1["卡1 的 token"] -- "dispatch" --> E1["专家卡1"] & E2
    E0 & E1 & E2 -- "combine<br/>all-to-all" --> O["token 回到原卡"]
:::

- **dispatch**：每个 token 按 router 的选择发给持有目标专家的卡；
- **combine**：专家输出加权合并送回原卡。

通信量每层 $2\times$（被选中的 token×激活维），与 TP 同量级但**语义更重**：token 离开本地处理后必须回来，前向路径上不可省略。

## 两大系统难题

1. **负载不均**：router 偏爱某些专家（热点专家卡成瓶颈、冷门专家空转），M 以上需辅助负载均衡损失 + 容量因子（capacity factor）限流丢 token——丢 token 率是 MoE 训练的敏感指标；
2. **EP 度数与通信**：EP 越大，专家切得越细、单卡显存越省，但 all-to-all 跨的卡越多。[超节点](/knowledge-planet/ai-infra/hardware/supernode)篇的结论在这里兑现：**DeepSeek-V3 用 8 卡 EP（域内）做预填充、更大 EP 靠超节点带宽**；CM384 这类 384 卡超节点的卖点正是大 EP 通信余量。

::: details 深入推导：all-to-all 通信模型与 DeepSeek-V3 的 EP 配置

**all-to-all 成本**。$e$ 卡、每卡发出 $m/e$ 给每张卡（理想均衡）：带宽项 $T \approx \frac{m}{e\cdot\beta_{\text{link}}}$？——精确模型：每卡同时向 $e-1$ 卡各发 $m/e$，链路是全双工的，每卡总收发各 $m(1-1/e)$，$T\approx \frac{m(1-1/e)}{\beta_{\text{e2e}}}$，其中 $\beta_{\text{e2e}}$ 是每卡的端到端可用带宽。与 allreduce 不同，**all-to-all 无法用树形结构省流量**（每个 token 的目的地不同），通信量是刚性的。

**DeepSeek-V3 的两级 EP**。预填充：节点内 EP=8（NVLink 域，重叠友好）；解码：EP=40（跨节点，稀疏专家使得单专家批大）。论文报告 MoE 层通信与计算的重叠设计（Dispatch/Combine 与 FFN 计算 overlap）是利用率的关键。INT8 量化通信（原论文训练精度细节）进一步减半流量——**算法（MoE 稀疏激活）与系统（通信重叠+压缩）共同决定 MoE 的实际性价比**。

**为何不用 TP 切专家**。单个专家是普通 FFN，可以再 TP——DeepSeek 细粒度专家（每专家更小）+ 更多专家数的设计选择了"专家数换专家粒度"，让 EP 而非 TP 成为专家维度的主要切法，因为 all-to-all 可以和计算重叠而 TP allreduce 不行。

（据 Zoph et al. 2022 ST-MoE、DeepSeek-AI 2024 V3。）

:::

## 思考题

1. 671B 参数的 MoE、64 张 H100（80 GB）：纯权重 BF16 放得下吗？EP 最小多少？
2. 容量因子 1.25 意味着什么？设太高和设太低各会发生什么？
3. 为什么 MoE 的 $6ND$ 用激活参数算而显存用总参数算？这个解耦对 scaling law 意味着什么？

::: details 参考答案

1. 权重 $2\times671\text{GB}=1.34\ \text{TB}$，64 卡总显存 5.1 TB 放得下但单卡 $21\ \text{GB}$ 的权重+其余状态——EP=64 恰好可行；若考虑激活/优化器（训练态）需配合 ZeRO/TP。EP 最小度数由"单卡要装的专家参数"决定：$\lceil 1.34\ \text{TB}/(\text{可用显存})\rceil$。
2. 每个专家的缓冲按平均值 ×1.25 预留：设太低（如 1.0）→ 热点专家溢出、token 被丢弃，训练信号损失且 router 被迫绕行；设太高 → 缓冲浪费显存、padding 计算增多，利用率下降。它是吞吐-质量的调节阀。
3. 计算发生在激活路径（$6N_{\text{act}}D$），存储责任在全部参数（$16\Psi_{\text{total}}$ 训练态）。解耦让"模型容量增长"与"单 token 成本"分离——MoE 可以用亚线性的计算成本买线性的容量增长，这是它优于 dense scaling 的经济内核，但代价是显存与通信的复杂账。

:::

## 小结

- MoE = 容量（总参数）与计算（激活参数）解耦；EP 解决专家的放置与调度。
- 每层两轮 all-to-all（dispatch/combine），通信量刚性、无法用树省流量，但可与计算重叠。
- 负载均衡（辅助损失 + capacity factor）决定训练质量，是 MoE 特有的新故障面。
- 大 EP 是超节点（Scale-up 带宽）的直接受益者，DeepSeek-V3 的两级 EP 是教科书配置。

## 参考资料

- Shazeer et al., [Outrageously Large Neural Networks (Sparsely-Gated MoE)](https://arxiv.org/abs/1701.06538)（arXiv 1701.06538）
- Fedus et al., [Switch Transformers](https://arxiv.org/abs/2101.03961)（arXiv 2101.03961）
- Zoph et al., [ST-MoE: Designing Stable and Transferable Sparse Expert Models](https://arxiv.org/abs/2202.08906)（arXiv 2202.08906）
- DeepSeek-AI, [DeepSeek-V3 Technical Report](https://arxiv.org/abs/2412.19437)（arXiv 2412.19437）
- DeepSeek-AI, [DeepSeekMoE](https://arxiv.org/abs/2401.06066)（细粒度专家，arXiv 2401.06066）
