---
title: "负载特征与性能归因"
date: 2026-09-29T10:30:00+08:00
weight: 30
---

# 负载特征与性能归因

> [工具篇](/knowledge-planet/ai-infra/profiling/tools)教了怎么拿到 profile，本篇教怎么**从 profile 到结论**：负载特征怎么提取、时间去哪了怎么归因、性能回归怎么自动化——profiling 的终点是"下一步改什么"。

## 提取负载特征：训练与推理各一组指纹

**训练侧的特征五元组**（每次 profile 先填这张表）：

| 特征 | 指标 | 健康区间 | 恶化方向 |
| ---- | ---- | ---- | ---- |
| 计算 | MFU | 40–55%（一线） | 气泡↑、重算↑ |
| 通信 | comm-exposed 占比 | 5–15% | TP 跨机、overlap 失败 |
| 显存 | 峰值/容量、碎片率 | <85% 且碎片 <10% | OOM 风险、empty_cache 滥用 |
| 流水 | 气泡率 | 接近理论 $\frac{p-1}{M+p-1}$ | 负载不均、micro-batch 过小 |
| IO | step 间隙 | ≈0 | 数据管道欠债 |

**推理侧的特征组**：TTFT/TPOT 分位数（P50/90/99）× 长度分箱、batch 水位（实际并发 vs 上限）、KV Cache 水位与命中率、prefix cache 命中率。两组特征都按"**先和理论模型对表，再看与实测的差值**"的方法论读（[性能指标](/knowledge-planet/ai-infra/profiling/metrics)篇给了全部公式）。

## 工具的分工与读法

一张速查表（题库 181–189 的落位）：

- **nvidia-smi dmon/pmon**：dmon 看全卡指标流（util/mem/freq），pmon 看每进程占用——快速判断"卡在空转还是有活干"。
- **Nsight Systems**：时间线——**看并发与间隙**：kernel 之间的洞（launch 开销/同步等待）、NCCL 与计算是否重叠、多 stream 是否真的并行。
- **Nsight Compute**：单 kernel 深挖——Speed Of Light 面板判断算力/带宽受限，配合 Roofline（[高性能计算]章）定位优化空间。
- **PyTorch Profiler**：框架层——op 级耗时、memory timeline（显存随步的变化，抓泄漏与碎片）、record_shapes 配合动态 shape 分析。
- **perf/eBPF**（题库 187）：CPU 侧——DataLoader worker 的解码热点（py-spy/perf）、内核路径（网络 softirq 占比过高说明包处理问题）、以及 GPU 之外被忽视的 host 开销。

**读时间线的三个固定动作**：① 找最大的时间块（ Pareto）；② 找间隙与串行化（并发失败的地方最隐蔽）；③ 对齐多卡/多进程时间线看长尾（最慢的 rank 决定集体，[容错]篇的 straggler 账）。

## 通信与显存的专项 breakdown

**通信 breakdown（题库 192）**：把 comm-exposed 拆成三段分别归因——

1. **量**：通信量是否比理论大？（bucket 配置、重复同步、不必要的 allgather）
2. **率**：实测带宽是否达到 NCCL 基线？（走错通道、PFC 风暴，见[NCCL](/knowledge-planet/ai-infra/network/nccl-tuning)篇诊断表）
3. **叠**：是否与计算重叠？（时间线上 NCCL kernel 旁有没有计算 kernel）

三段各自的修法完全不同——不拆开的"通信占比 20%"是个无法下手的数字。

**显存 breakdown（题库 184）**：PyTorch Profiler 的 memory timeline + `memory_summary` 把峰值拆成权重/梯度/优化器/激活/缓冲——与[显存优化](/knowledge-planet/ai-infra/training/memory-optimization)篇的 $16\Psi$ 公式对表，多出来的部分通常是碎片与通信缓冲。算子级耗时（题库 193）用 op 表按"总时间 × 频次"排序，注意区分"单个慢"与"调用次数多"两类问题——解法一个在 kernel 优化，一个在融合与调度。

## 性能回归的自动化（题库 195）

优化会腐烂：框架升级、驱动更新、代码合入都可能悄悄吃掉性能。回归检测的闭环：

1. **基准集**：固定模型 × 配置 × 输入的微型负载（分钟级），覆盖训练单步、prefill、decode 三类。
2. **指标与阈值**：单步时间/MFU/TTFT 的移动基线（最近 N 次的统计区间），超界告警——用相对阈值而非绝对值（机器噪声）。
3. **定位挂钩**：回归触发时自动附上 profiler 快照与二分信息（哪个 commit/哪个组件），把"发现"直接推进到"归因"。
4. **长跑巡检**：小时级混合负载监控慢漂移（碎片、泄漏、缓存劣化）——分钟级基准测不出的东西。

这套系统的成本极低（复用 CI 机时），却是性能资产唯一的保险——没有它，每次"顺手改一下"都是无对账的支出。

## 小结

- 特征先行：训练五元组、推理分位数×分箱，每个指标都配理论对照区间。
- 工具按"时间线→单 kernel→host 侧"分工，读时间线的固定动作是找大块、找间隙、对齐长尾。
- 通信 breakdown 拆"量/率/叠"三段，显存 breakdown 对表 $16\Psi$——拆开才能归因。
- 性能回归自动化是优化的保险：基准集 + 相对阈值 + 归因挂钩 + 长跑巡检。

## 思考题

1. MFU 从 48% 掉到 41%，五元组里你会先看哪两个特征？为什么？
2. 时间线上 NCCL kernel 旁有计算 kernel，但 comm-exposed 仍然高——还可能差在哪？
3. 设计回归基准时，为什么"分钟级微型负载"比"复跑完整训练"更好？漏掉了什么，怎么补？

::: details 参考答案

1. 先看 comm-exposed 与气泡率——两者是 MFU 漂移最常见的主因（配置漂移、拓扑变化、负载数据长度分布变化都会先体现在这两处）；显存与 IO 通常表现为突发故障而非渐变劣化。
2. 带宽项没问题但**量**大了（bucket 过碎导致小消息 allreduce 频次高），或**率**在长尾上掉（偶发 PFC/慢节点让部分 step 的通信时长抖动）——看通信时间的分布而不只看均值。
3. 好处：快（能进 CI/每 commit 跑）、可控（变量固定）、便宜（复用机时）。漏掉的是长周期效应——数据管道波动、碎片累积、热漂移（降频）；用小时级长跑巡检与生产聚合指标（MFU 周趋势）补上。

:::

## 参考资料

- PyTorch, [Profiler 文档](https://pytorch.org/tutorials/recipes/recipes/profiler_recipe.html)（memory timeline 与 export_chrome_trace）
- NVIDIA, [Nsight Systems/Compute 文档](https://docs.nvidia.com/nsight-systems/)
- Li et al., [MegaScale](https://arxiv.org/abs/2402.15627)（大规模训练的诊断系统设计）；HolisticTraceAnalysis 项目（多 rank 时间线聚合）

