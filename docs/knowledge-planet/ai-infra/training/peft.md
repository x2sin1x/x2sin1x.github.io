---
title: "参数高效微调"
date: 2026-09-22T18:00:00+08:00
weight: 30
---

# 参数高效微调

> 全量微调 70B 要一个集群，LoRA 微调 70B 只要一张卡。&#8203;**PEFT 的本质是：把"学什么"和"存什么"解耦。**

## 全量微调为什么贵

全量微调的显存账是[显存层次](/knowledge-planet/ai-infra/hardware/memory-hierarchy)篇的 $(2+2+12)\Psi$——优化器状态占了 12 字节/参数的大头，因为它要为**每个参数**维护动量与方差。但微调任务往往只需要在少数能力维度上做调整：&#8203;**能否只训练一小部分参数，却达到接近全量的效果？**

## LoRA：低秩增量假设

LoRA（Low-Rank Adaptation）的核心假设：微调引起的权重变化 $\Delta W$ 是低秩的。于是冻结原权重 $W$，为每个目标层注入一对小矩阵：

$$W' = W + \Delta W = W + BA,\quad B\in\mathbb{R}^{d\times r},\ A\in\mathbb{R}^{r\times k},\ r\ll\min(d,k)$$

::: mermaid
flowchart LR
    x["输入 x"] --> W["W（冻结）"]
    x --> A["A（r×k，可训）"]
    A --> B["B（d×r，可训）"]
    W --> add(("+"))
    B --> add
    add --> y["输出"]
:::

**账目**&#8203;：$r=16$ 时，$d=k=4096$ 的层可训参数从 $16.8\text{M}$ 降到 $131\text{K}$（128 分之一），整个 70B 模型只训约 $0.1\%\sim1\%$ 的参数。由此连锁省下：优化器状态 $12\Delta\Psi$ 字节（几乎消失）、梯度 $2\Delta\Psi$、checkpoint 只存 $BA$（MB 级，切换任务=换一个几十 MB 的文件）。单卡 80 GB 微调 70B（QLoRA）由此成为可能。

**推理零开销**&#8203;：部署时 $BA$ 合并进 $W$，结构与原模型完全一致——这是它统治落地侧的关键。

## QLoRA：4 bit 基座 + LoRA 增量

QLoRA 再砍一刀：把冻结的基座量化到 4 bit（NF4 数据类型），LoRA 增量保持 BF16。70B 模型基座 $4\times70\times10^9=35\ \text{GB}$，加上 LoRA 训练态与激活，单卡可训。代价是基座前向需要反量化计算（约 10~30% 额外开销）。&#8203;**QLoRA 证明了：微调质量的瓶颈在数据而非基座精度**&#8203;——这个结论改变了小团队微调大模型的经济学。

## 机制对比

| 方法 | 可训参数 | 额外推理开销 | 适用场景 |
| ---- | ---- | ---- | ---- |
| 全量微调 | $100\%$ | 无 | 数据充足、追求上限 |
| LoRA | $0.1\%\sim1\%$ | 合并后无 | 通用默认选择 |
| QLoRA | 同 LoRA | 反量化开销 | 单卡/少卡场景 |
| Prefix/P-tuning | $<0.1\%$（KV 前缀） | 每步读取前缀 | 极小数据、多任务 |
| Adapter | $0.5\%\sim8\%$ | 串行小层，有延迟 | 多任务服务 |

::: details 深入推导：LoRA 的初始化、秩的选择与多任务服务

**初始化**&#8203;：$A$ 用高斯初始化、$B$ 置零，保证训练起点 $BA=0$、模型行为与基座完全一致。反过来（$B$ 高斯、$A$ 置零）梯度会流经零矩阵导致 $A$ 学不动，这是实现中最常见的错误之一。

**梯度与秩**&#8203;：$\Delta W$ 被约束在秩 $\le r$ 的子空间。对损失 $L$，$\partial L/\partial B = (\partial L/\partial W')A^\top$，梯度天然限制在 $A$ 张成的低维空间里。经验上：简单风格任务 $r=8\sim16$ 足够；领域知识密集或长输出推理任务升到 $r=64\sim256$，并把 LoRA 加到所有线性层（而非仅注意力投影）效果更稳。

**多任务服务账**&#8203;：$n$ 个任务全量微调需要 $n\times 2\Psi$ 字节权重；LoRA 只需 $n\times 2r(d+k)$ 字节（70B 模型、$r=16$ 约 160 MB/任务）。推理时动态换装或用 S-LoRA 式统一分页服务数千个 LoRA——&#8203;**PEFT 把"模型即服务"变成了"模型 + 插件即服务"**&#8203;。

（据 Hu et al. 2021、Dettmers et al. 2023。）

:::

## 思考题

1. 70B 模型、$r=16$、给所有 1024 个线性层加 LoRA（$d=k=8192$ 层占多数），可训参数量级是多少？QLoRA 下单卡 80 GB 够吗？
2. 为什么 LoRA 合并后推理零开销，而 Adapter 每层都有额外延迟？
3. 你的任务是让模型学会一个新的编程语言语法，选 $r$ 与放置层的原则是什么？

::: details 参考答案

1. $1024\times(8192+8192)\times16\times1\ \text{字节口径换参数} = 1024\times2\times8192\times16 \approx 2.7\times10^8\approx 0.27\text{B}$，占 70B 的 0.4%。QLoRA 下基座 35 GB + LoRA 训练态（0.27B 参数约 4.3 GB 含优化器）+ 激活——80 GB 单卡勉强可行，配合梯度检查更稳。
2. LoRA 的 $BA$ 数学上可折叠进原权重（$W'=W+BA$ 预先算好）；Adapter 是新插入的串行计算图节点，无法折叠，每层多两次小矩阵乘与内存往返，decode 时逐层累积延迟。
3. 新语法是模式性知识，中低秩（$r=16\sim32$）够用；优先覆盖注意力投影（学习新格式关联）+ MLP 层（存储事实性语法规则），用验证集上 loss 曲线判断是否升秩。

:::

## 小结

- PEFT = 低秩/少量参数假设 + 冻结基座，把优化器状态这个显存大头直接消掉。
- LoRA 靠"可合并"实现推理零开销，成为默认；QLoRA 把基座压到 4 bit，单卡微调 70B。
- 多任务场景 LoRA 增量以 MB 计，模型服务变成"基座 + 插件"模式。
- 秩与放置层是仅有的两个关键超参：难度高、知识密则升秩、全层放置。

## 参考资料

- Hu et al., [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)（arXiv 2106.09685）
- Dettmers et al., [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314)（arXiv 2305.14314）
- Dettmers et al., [8-bit Optimizers via Block-wise Quantization](https://arxiv.org/abs/2110.02861)（arXiv 2110.02861）
- Hugging Face，[PEFT 文档](https://huggingface.co/docs/peft)
