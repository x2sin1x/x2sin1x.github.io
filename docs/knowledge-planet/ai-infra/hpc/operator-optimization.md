---
title: "算子优化与融合"
date: 2026-09-29T10:30:00+08:00
weight: 20
---

# 算子优化与融合

> 模型大部分时间花在少数几个矩阵乘上，但**吃掉 GPU 利用率的，恰恰是其余那几百个小算子**。本篇讲怎么评估、改写和融合它们。

## 优化的第一步：算出上限

拿到一个慢算子，先别写代码，先做两道算术（[Roofline](/knowledge-planet/ai-infra/hardware/chip-architecture)）：

1. **运算强度** $I=N_{\text{flop}}/N_{\text{byte}}$：这个算子每个字节换来几次运算？
2. **可达性能** = $\min(P, I\times\beta)$：理论时间多少？

然后 profile 实测。**实测时间 ÷ 理论时间就是优化空间**——一个实测 3 ms、理论 0.1 ms 的 elementwise 算子，问题不在算法在访存模式；而一个已经贴近理论值的算子，再优化也是白费劲。这个"先算上限再看实测"的顺序，比任何技巧都值钱。

## Triton 与 CUDA：两条写 kernel 的路

| 维度 | CUDA C++ | Triton |
| ---- | ---- | ---- |
| 抽象层级 | 线程级：显式管 warp、寄存器、shared memory | tile 级：操作整块 tensor，编译器管线程与流水 |
| 上限 | 最高（一切皆可调） | 接近 CUDA（Tile 化 GEMM/Attention 类） |
| 上手成本 | 高 | 低（Python 语法，NumPy 心智） |
| 动态 shape | 手动处理 | 天然支持（tile 边界自动 mask） |

选择经验：**探索性/中等复杂度算子用 Triton**（Inductor 生成的就是 Triton），**极致性能或特殊硬件路径用 CUDA/CUTLASS**。Triton 之于 CUDA，类似 Numpy 之于 C——它把"线程划分、访存合并、流水线调度"这些机械但易错的活交给编译器，代价是牺牲一部分控制力。

## 一个算子优化的工具箱

按投入产出排序：

1. **访存合并（coalescing）**：warp 内连续访问。修复一次 stride 访问 = 免费拿回最多 32 倍带宽。
2. **避免 bank conflict**：shared memory 的 padding/重排。
3. **tiling + 复用**：数据先进 shared memory，寄存器里做最内层乘加。
4. **vectorized load**：用 128-bit load（`float4`）替代标量 load，减少指令数。
5. **occupancy 权衡**：寄存器用得多 → 每 SM 驻留 warp 少 → 藏延迟能力弱。`__launch_bounds__` 与 `-maxrregcount` 显式约束；用 Nsight Compute 的 occupancy 面板看瓶颈。
6. **warp 原语**：`__shfl_sync` 让 warp 内线程直接交换寄存器（归约不再过 shared memory）；cooperative groups 提供更高层的组抽象与跨 block 同步（grid sync）。
7. **异步与流水**：cp.async/TMA 让"搬运下一块数据"与"计算当前块"重叠——双缓冲是标准写法。

工具是 **Nsight Compute**：它的 Speed Of Light 面板直接给出 SM 吞吐与显存吞吐各达到峰值的百分比，Memory Workload Analysis 给出实际带宽与 L2 命中率——**这两个数字就能把"算力受限还是带宽受限"判掉**，再看 Source Counter 对到行。

## 算子融合：为什么有用，边界在哪

融合 = 把多个算子合成一个 kernel。收益公式很朴素：每个 kernel 都要把中间结果写 HBM 再读回来，融合掉一次往返就省 $2\times$ 中间张量字节的流量，还省一次 launch。

两个经典案例：

- **LayerNorm+残差+激活**：三个带宽受限算子串行时读写字节是各自 3–4 倍中间量的总和；融合后中间量全程留在寄存器/共享内存。Transformer 每层都有，累积收益巨大。
- **Softmax 粘在矩阵乘后面**：见[芯片架构](/knowledge-planet/ai-infra/hardware/chip-architecture)篇的"一等公民"讨论。

**融合的边界**（对应题库"operator-decomposing 与 operator-fusion 的边界"）：

- 拆（decompose）的理由：把大算子拆成可复用的小块，或让 shape/布局对齐（如把 conv 拆成 im2col+GEMM）。
- 不融合的理由：① 融合后寄存器/shared memory 溢出，occupancy 崩掉，反而变慢；② 中间结果要被复用多次时，重算比读写贵；③ 编译器 guard 与代码膨胀——每个动态 shape、每种 dtype 组合都实例化一个 kernel。
- 工程判断：**融合带宽受限的相邻小算子几乎稳赚；融合计算受限的矩阵乘通常是零或负收益**。

## 动态 shape：优化工程的结构性难题

batch、序列长度、专家路由都是动态的，而 kernel/CUDA Graph/编译缓存都偏爱静态 shape。常见对策：

- **分桶（bucketing）**：shape 分桶 padding 到桶边界，桶内静态化（CUDA Graph 可用）；代价是 padding 的无效计算。
- **kernel 缓存按 shape 实例化**：编译器（Inductor/TensorRT）对每个 shape 编译一份；shape 空间大时编译时间与缓存内存爆炸——"编译时间过长"问题的根源与解法（限制 guard、Triton 的 shape 泛化、`dynamic=True` 的 symbolic shape）。
- **Mask 代替分支**：Triton 的边界 mask 让一个 kernel 覆盖一片 shape，牺牲少量无效计算换取无重编译。

## 小结

- 优化顺序：先算 Roofline 上限 → profile 实测 → 定位差距 → 用对工具。
- Triton 管易用性（tile 抽象、动态 shape），CUDA/CUTLASS 管上限；Inductor 已经替大部分算子走了 Triton。
- 融合的收益来自省掉中间张量的 HBM 往返，对带宽受限算子稳赚，对计算受限算子通常无益。
- 动态 shape 用分桶/泛化/mask 化解，代价分别是无效计算、编译时间与缓存内存。

## 思考题

1. 一个 elementwise 算子读写各 1 GB，H100 上理论时间多少？实测 4 ms 时瓶颈在哪类问题里找？
2. 为什么把两个 10 GB/s 的算子融合后不一定是 10 GB/s？举一个融合反而变慢的场景。
3. decode 阶段（shape 稳定）和 prefill 阶段（shape 变化大）分别适合 CUDA Graph 还是 shape 泛化？为什么？

::: details 参考答案

1. 2 GB ÷ 3.35 TB/s ≈ 0.6 ms；实测 4 ms 说明只用了 15% 带宽——查 coalescing、vectorized load、launch 配置（grid 太小没吃满 SM）。
2. 融合后寄存器压力增大导致 occupancy 下降、或 mask/分支引入 warp divergence；典型反例是融合两个各自已经计算受限的 GEMM，或中间结果需被多次复用导致重算。
3. decode 适合 CUDA Graph：shape 静态、kernel 小而多、launch 开销占比高；prefill 适合 shape 泛化（Triton mask/符号 shape），因为 shape 空间大，为每个 shape 录图不现实且 padding 浪费大。

:::

## 参考资料

- NVIDIA, [Nsight Compute 文档](https://docs.nvidia.com/nsight-compute/)（Speed Of Light 与 Occupancy 章节）
- OpenAI, [Triton 官方教程](https://triton-lang.org/main/getting-started/tutorial.html)（fused softmax 即本章案例）
- PyTorch, [TorchInductor 设计](https://dev-discuss.pytorch.org/t/inside-the-pytorch-2-0-compiler-episode-1/1000)（官方开发者论坛系列）

