---
title: "主流量化方法：GPTQ、AWQ 与 SmoothQuant"
date: 2026-09-29T10:30:00+08:00
weight: 20
---

# 主流量化方法：GPTQ、AWQ 与 SmoothQuant

> [量化基础](/knowledge-planet/ai-infra/quantization/quantization-basics)篇讲了原理与定标，本篇拆解工业界三大算法的核心思想——它们本质上是**三个不同的"保护敏感权重"策略**。

## 共同的敌人：异常值

直接把权重四舍五入到 4 bit，PPL 会爆炸。根因是**异常值（outlier）**：少数权重/激活通道的数值范围远超均值，定标后被压到底部量化级里，误差被放大。三大算法的分野就在于从哪个角度处理异常值。

## GPTQ：逐层误差补偿

GPTQ（Frantar et al., 2022）把量化当**压缩感知式重构**问题：逐层最小化 $\|WX - \hat{W}X\|^2$（量化前后对该层输入输出的差异）。做法：

1. 用校准数据取每层输入 $X$ 的二阶统计量（Hessian $H=2XX^\top$）。
2. **逐列量化**：每次量化一列权重，随即用 Hessian 的逆**把该列引入的误差补偿到尚未量化的列**上（OBS/OBQ 的贪心近似）。
3. 全层量化完后误差已被"摊薄"进所有列。

特点：**权重量化的天花板**（4/3/2 bit 都能压），需要校准但数据量小（128 条样本即可），一次成型（one-shot，无训练）。代价是量化过程本身要跑 GPU 数小时（大模型），且对激活异常值无能为力——它只修权重。

## AWQ：按激活重要度缩放

AWQ（Lin et al., 2023）的洞察：**不到 1% 的权重通道承载了大部分激活能量，保护它们比均匀保护更重要**。做法：

1. 观察激活分布，找出每个输入通道的缩放系数 $s$。
2. 对权重做等价变换 $y = (W \cdot \text{diag}(1/s))\cdot(\text{diag}(s)\cdot x)$——数学上完全等价，但把"重要通道"的权重量化误差转移到了不重要的通道（重要通道权重变大，占的量化级更精细）。
3. 缩放系数不靠搜索穷举（AutoAWQ 用解析式近似最优）。

特点：**激活感知但只动权重**，前向零开销（缩放被吸收进权重），4 bit 下精度与 GPTQ 相当且对生成质量更稳，量化速度快得多。vLLM/TensorRT-LLM 的默认路线之一。

## SmoothQuant：把激活也压进 INT8

前两者的局限：激活的异常值没法像权重那样提前吸收——激活是运行时数据。**W8A8**（权重与激活都 INT8）才是让 INT8 GEMM 真正跑上 Tensor Core 的路线，而它的拦路虎正是激活异常值。SmoothQuant（Xiao et al., 2023）的解法：

- 与 AWQ 同款的等价变换，但方向相反：$s<1$ 时把激活的异常值**平滑掉**（除以 $s$），把难度**迁移给权重**（乘 $s$）——权重好量化，让它多吃点。
- 迁移强度由超参 $\alpha$ 控制（$\text{diff} = \alpha\cdot s_{\text{act}}$ 的通道缩放）。

特点：得到真正的 W8A8 静态图，TTFT 显著受益（prefill 是计算受限，INT8 GEMM 提速）。FP8（Hopper 原生支持，见[量化基础]篇）普及后，W8A8 路线的性价比进一步提升。

## 谱系的另一端：GGUF 与 k-means

- **GGUF（llama.cpp 生态）**：面向 CPU/端侧的权重格式，量化级别 k-quants（Q2_K…Q8_0）按**块**定标（每 32/256 个权重一个 scale+offset），超块再存二级统计——比逐张量定标精细得多，是"小卡/无卡跑大模型"的主力。其 Q4_K_M 级别是社区公认的"速度/质量甜点"（题库 120）。
- **k-means / 非均匀量化**（题库 124）：把"均匀切量化级"换成"按权重分布聚类"。对权重呈钟形分布（多数值集中、少数离群）的Tensor 特别合身——量化级按密度分配。代价是硬件不支持非均匀的 dequant 路径，常见于端侧/NPU 自定义实现。二值化网络（BNN，题库 125）是谱系极限：1 bit 权重 + XNOR-popcount，学术价值大于当前工业价值——精度损失使它只在特定小型网络存续。

## 选型速查

| 目标 | 推荐 | 一句话理由 |
| ---- | ---- | ---- |
| 4 bit 权重，GPU 服务 | AWQ 或 GPTQ | 成熟、引擎支持好；AWQ 量化快，GPTQ 极限更高 |
| INT8 全量化（W8A8） | SmoothQuant / FP8 | 唯一能吃满 INT8/FP8 Tensor Core 的路线 |
| CPU/端侧 | GGUF k-quants | 块定标 + 无 GPU 依赖 |
| 极限压缩研究 | GPTQ 2-bit / AQLM 类 | 误差补偿框架的极限 |

量化后精度损失的定位流程（题库 123，见[量化基础]篇的校准节）：先二分定位层（逐层 swap 回 FP16 跑 PPL）→ 再定位算子（该层的 matmul vs softmax）→ 最后看是权重误差还是激活 clip（对比校准统计与真实分布）。

## 小结

- 三大算法都是"异常值"的应答：GPTQ 用 Hessian 补偿摊薄权重误差，AWQ 用等价缩放保护重要通道，SmoothQuant 把激活难度转移给权重。
- W4A16（AWQ/GPTQ）省显存带宽、W8A8（SmoothQuant/FP8）换计算提速——目标不同，选型即答案。
- GGUF 的块定标是端侧路线，k-means 是非均匀定标的谱系延伸。
- 精度损失定位的通用循环：层二分 → 算子归因 → 分布对比。

## 思考题

1. AWQ 与 SmoothQuant 都用等价缩放，方向为何相反？各利用了什么不对称性？
2. GPTQ 的误差补偿为什么需要 Hessian（$XX^\top$）而不是一阶统计量？
3. 你要把 70B 模型部署到 2 张 80 GB 卡上做长上下文服务：选哪条量化路线？KV Cache 要不要量化？

::: details 参考答案

1. AWQ：$s>1$ 放大重要权重——利用"权重可离线自由变换、激活是模型输出不可动"的不对称；SmoothQuant：$s<1$ 压小激活——利用"激活有难缠的异常值而权重量化容错高"的不对称。本质是同一个自由度（通道缩放的等价重分配），从两端各取所需。
2. 目标函数 $\|WX-\hat W X\|^2 = \text{tr}(\Delta W \, H \, \Delta W^\top)$ 的二阶项就是 $H=2XX^\top$——补偿要走"该误差经过输入分布后造成的输出误差"，一阶统计量丢失了通道相关性。
3. 权重 70B×0.5 B=35 GB（W4）→ 2 卡可容纳且给 KV 留足空间，选 AWQ/GPTQ；KV Cache 必须量化（FP8/BF16→INT8 减半），长上下文下 KV 是显存霸主（见[KV Cache](/knowledge-planet/ai-infra/inference/kv-cache)篇），只压权重不压 KV 达不到目的。

:::

## 参考资料

- Frantar et al., [GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers](https://arxiv.org/abs/2210.17323)（arXiv 2210.17323）
- Lin et al., [AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration](https://arxiv.org/abs/2306.00978)（arXiv 2306.00978）
- Xiao et al., [SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models](https://arxiv.org/abs/2211.10438)（arXiv 2211.10438）
- llama.cpp, [GGUF 与 k-quants 说明](https://github.com/ggerganov/llama.cpp/blob/master/docs/build.md) 与 [PR #1684](https://github.com/ggerganov/llama.cpp/pull/1684)（k-quants 原始说明）

