---
title: "DSpark"
date: 2026-09-23
tags:
  - Speculative Decoding
categories:
  - ICML
description: "在并行 drafter 后接极轻的顺序修正模块增强块内连贯性，并按前缀验证通过概率与引擎负载动态决定验证长度，同时改好生成与调度两侧。"
---

# DSpark：既要猜得连贯，也要把验证算力花在刀刃上

Xin Cheng, Xingkai Yu, Chenze Shao, et al. · arXiv 2026

[Paper](https://arxiv.org/abs/2607.05147v1) · [Code](https://github.com/deepseek-ai/DeepSpec) · [Models](https://huggingface.co/collections/deepseek-ai/deepspec) · [DeepSeek-V4-Pro-DSpark](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-DSpark)

Speculative decoding 的承诺很诱人：让小型 drafter 先猜一段 token，再由大模型一次验证，便能把多次串行生成压缩成一个 round。DFlash 一类 parallel drafter 又进一步把“猜”的过程并行化。但并行预测的每个位置看不到同一 block 中实际采样出的前序 token，越往后的猜测越容易互相冲突；而在高并发服务中，target model 若仍把这些低胜率后缀全部送进验证，浪费的不只是几次计算，而是整个 batch 的宝贵容量。

DSpark 同时改了生成和调度两侧：先在重型并行 backbone 后接一个极轻的顺序修正模块，让 block 内 token 重新产生依赖；再预测每个前缀能通过验证的概率，结合当前引擎负载决定每个请求究竟值得验证多长。论文在 Qwen3 离线实验中将平均 accepted length 相对 DFlash 提高 16.3%-18.4%；部署到 DeepSeek-V4 实时流量后，在相同总吞吐下，V4-Flash 的单用户生成速度提高 60%-85%，V4-Pro 提高 57%-78%。前者证明 drafter 更准，后者才是完整系统收益。

## Quick Start

截至 2026-09-23，官方 [DeepSpec](https://github.com/deepseek-ai/DeepSpec) 仓库提供了训练、评测代码以及 Qwen3、Gemma4 的 Eagle3 / DFlash / DSpark checkpoints。下面是依据仓库当前文档核对的 Qwen3-4B 最短评测路径；这些命令未在本文环境中下载模型或占用 GPU 实测。

```bash
git clone https://github.com/deepseek-ai/DeepSpec.git
cd DeepSpec
python -m pip install -r requirements.txt

CUDA_VISIBLE_DEVICES=0,1,2,3 python eval.py \
  --target_name_or_path Qwen/Qwen3-4B \
  --draft_name_or_path deepseek-ai/dspark_qwen3_4b_block7
```

这条路径默认使用 4 张可见 GPU；官方训练配置默认按单机 8 卡编写。若要从头准备 Qwen3-4B 的默认 target cache，仓库估算需要约 38 TB 存储，因此多数读者更适合先用已发布 checkpoint 做评测。DeepSeek-V4-Pro-DSpark 的 vLLM 部署则面向专用多 GPU 硬件，应直接参考其[官方模型页](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-DSpark)，不能把它视为普通单卡 Quick Start。

## Why DSpark?

一次 speculative decoding round 包含两件事：drafter 提出长度为 $\gamma$ 的候选序列，target model 并行检查它；从开头连续匹配的 token 被接受，遇到第一次拒绝便停止。最终分布仍由 target model 决定，所以 drafter 不必独立生成完美答案，但必须让“每轮接受的 token 数”足以抵消起草和验证的额外成本。

自回归 drafter 知道自己刚刚生成了什么，因此候选序列较连贯，代价是 draft latency 随 $\gamma$ 近似线性增长。Parallel drafter 只做一次前向，能够用更深的网络同时预测整块 token，却付出了独立性代价：当上下文同时允许 “of course” 和 “no problem” 时，两个位置各自对多种延续取平均，可能拼出 “of problem” 或 “no course”。单个位置看似合理，组合起来却不是任何一种合理模式。

![Qwen3-4B 上 Eagle3、DFlash 与 DSpark 在数学、代码和对话任务中的逐位置条件接受率；DFlash 的后缀衰减明显，而 DSpark 缓解了下降](https://arxiv.org/html/2607.05147v1/position_cond_accept.svg)

> 来源：原论文 v1 Figure 2。图中是“给定此前位置已通过后的当前位置接受率”，不是整个前缀存活率；它隔离出了各位置本身的预测质量。读图重点：parallel DFlash 的速度优势伴随明显 suffix decay，DSpark 用少量顺序依赖缓解了这一问题。

更长的 draft block 还会在服务端制造第二重浪费。结构化数学题可能有很长的可预测前缀，开放式对话的后续表达却有许多同样合理的分支；若对每个请求固定验证相同长度，低置信度后缀会占据 target batch，挤掉原本可以服务的新请求。在低并发时多验证几个 token 可能物有所值，在引擎接近饱和时，同一选择却可能拖垮总吞吐。

问题因此不只是“怎样一次猜更多”：**能否用接近并行生成的成本恢复 block 内连贯性，同时让验证长度随候选质量和系统负载一起变化？**

## How DSpark Works

### 关键洞察：并行负责重计算，顺序只负责消歧

DSpark 没有在自回归与并行生成之间二选一。它先让多层 parallel backbone 完成绝大部分表示计算，再用一个轻量 sequential head 根据已经采样的前序 token 修正下一位置 logits。顺序路径仍存在，但它只承担“让这一块候选落到同一个生成模式”这一小部分工作。

论文用一个简单关系概括 speculative decoding 的权衡：

$$
L = \frac{T_{\text{draft}} + T_{\text{verify}}}{\tau}
$$

这里 $L$ 是平均每个输出 token 的延迟，$T_{\text{draft}}$ 与 $T_{\text{verify}}$ 分别是每轮起草、验证时间，$\tau$ 是每轮平均接受长度。自回归 drafter 往往有较高的 $\tau$，但 drafting 随 block 变长；纯并行 drafter 压低了 $T_{\text{draft}}$，却容易让后缀接受率下滑。DSpark 的半自回归结构提高 $\tau$，置信度调度则削减没有回报的 $T_{\text{verify}}$，两部分恰好作用于公式的不同位置。

### 设计

![DSpark 解码周期：并行 backbone 产生整块表示，轻量顺序 head 生成候选与置信度，调度器裁掉低价值后缀后交给 target model 验证](https://arxiv.org/html/2607.05147v1/model_arch.svg)

> 来源：原论文 v1 Figure 1。读图重点：DSpark 总是先生成完整 draft block，再由 scheduler 选择要送进 target model 的前缀；调度节省的是验证算力，并不消除整块 drafting 的固定成本。

1. **Parallel backbone：** DSpark 复用 DFlash 式五层 backbone，一次前向为整个 block 产生 hidden states 与基础 logits。重型表示计算仍然并行，draft cost 因而不会像完整自回归 drafter 那样随候选长度线性增加。
2. **Sequential head：** 默认的 Markov head 用 rank-256 低秩转移矩阵，根据刚采样的 token 给下一位置 logits 添加 transition bias。它不重复 backbone 的深层计算，只沿 block 做便宜的逐 token 修正；论文也测试了 RNN head，但额外收益有限、部署复杂度更高，最终生产系统选择 Markov 版本。
3. **Confidence head：** 对第 $k$ 个位置，head 估计“此前 token 已通过时，该 token 也会通过”的条件概率 $c_k$。长度为 $k$ 的整段前缀存活概率就是 $\prod_{i=1}^{k} c_i$。原始置信度不能直接当概率使用，论文以 Sequential Temperature Scaling 做事后校准，将约 3%-8% 的 ECE 降到约 1%；ROC-AUC 落在 0.81-0.90，说明它也具备区分高、低风险候选的能力。
4. **Hardware-aware prefix scheduler：** 调度器不使用固定阈值，而是把候选前缀的预期接受 token 数与引擎实测的 steps/s 结合起来，在全 batch 中分配验证预算。它按前缀存活概率比较每次“再多验证一个 token”的价值，并保证每个请求只保留合法前缀；生产实现使用延迟两步的容量估计，以适配异步调度、ZOS 与 CUDA Graph。被裁掉的只是 draft proposal，保留下来的 token 仍由 target model 按标准流程验证，因此不会改变输出分布。

两部分训练目标也各自对应其职责。Token prediction loss 训练 drafter 模仿 target 的后续分布，二元 acceptance labels 训练 confidence head 预测每个位置能否通过。校准与引擎吞吐 profile 则在训练后完成，使同一个 drafter 可以针对具体硬件和服务负载调整验证策略。

## Results

### 先看 drafter：少量顺序依赖是否真的有用？

离线实验使用 Qwen3-4B/8B/14B 与 Gemma4-12B 作为 target，在 130 万条 Open-PerfectBlend prompts 上分别训练 Eagle3、DFlash 和 DSpark，并覆盖数学、代码、对话任务。所有模型运行在 non-thinking、temperature 1.0 设置；Eagle3 的 test-time training horizon 为 7，DFlash 与 DSpark 的 block size 为 7。DFlash / DSpark 使用五层 backbone，Eagle3 为单层。最重要的是，这组实验**关闭了 confidence scheduler**并强制固定长度，因此测到的是 draft quality，不是动态调度收益；accepted length 还包含 target model 生成的 bonus token。

| Target model | DSpark 相对 Eagle3 的宏平均 accepted length 提升 | DSpark 相对 DFlash 的提升 |
|---|---:|---:|
| Qwen3-4B | +30.9% | +16.3% |
| Qwen3-8B | +26.7% | +18.4% |
| Qwen3-14B | +30.0% | +18.3% |

> 来源：原论文 v1 Table 1。这里比较的是每轮平均接受长度，不是端到端 latency 或 serving throughput；三种 drafter 使用同一训练框架与数据，以减少实现差异带来的干扰。

收益不是平均数掩盖出来的。以 Qwen3-4B 为例，DSpark 在数学、代码、对话上的领域平均 accepted length 分别为 5.57、5.12 和 3.49；开放式对话确实更难预测，也正说明固定验证长度为何不经济。方法还迁移到 Gemma4-12B，但论文没有为它给出与三个 Qwen3 尺度相同的汇总提升百分比。

随着 proposal length 增长，顺序修正的作用更加明显。在 $\gamma=7$ 时，DSpark 相对 DFlash 在数学、代码、对话上分别提高约 16%、15%、18%；到 $\gamma=15$ 时，优势扩大到 30%、26%、22%。代价并未同比增长：batch size 128 下，draft length 从 4 扩到 16，完整 round latency 相对 DFlash 只增加 0.2%-1.3%。这组结果直接支持论文的架构判断：不必把整个 drafter 改回自回归，一点放在末端的顺序性已经能显著修复 suffix decay。

置信度也确实能识别低价值后缀。在静态阈值诊断中，剪枝将 Qwen3-4B 的 token acceptance rate 从对话的 45.7% 提高到 95.7%，数学从 76.9% 提高到 92.5%，代码从 67.6% 提高到 92.0%。但更高 acceptance rate 本身不等于更高吞吐：阈值过严会留下太少 token，所以生产系统还需要把置信度与实时引擎容量一起优化。

### 再看服务系统：更准的草稿能否转化成更好的吞吐？

论文将最大 draft length 为 5 的 DSpark-5 部署到 DeepSeek-V4-Flash（preview）与 DeepSeek-V4-Pro（preview）的生产 serving engine，并用实时用户流量与原生产方案 MTP-1 比较。MTP-1 每轮只预测一个额外 token；静态 MTP-3/5 虽能提高单请求速度，却会因验证开销在高并发下损害总吞吐，因此没有成为此前的生产默认方案。

![DeepSeek-V4-Flash 与 V4-Pro 实时流量下，DSpark-5 和 MTP-1 的总输出吞吐与单用户生成速度 Pareto 前沿](https://arxiv.org/html/2607.05147v1/online_service.png)

> 来源：原论文 v1 Figure 7。散点是实时生产流量遥测，实线是拟合后的 performance frontier。读图重点：DSpark 把总吞吐与单用户速度的权衡曲线整体向外推；该结论限定于论文所用 DeepSeek-V4 preview 引擎、流量与配置。

| 生产设置 | 中等 SLA 下的总吞吐提升 | 相同总吞吐下的单用户速度提升 |
|---|---:|---:|
| V4-Flash，80 tok/s/user | +51% | +60%-85% |
| V4-Pro，35 tok/s/user | +52% | +57%-78% |

调度行为解释了这条 Pareto frontier。在生产环境常见的中等并发区间，scheduler 会利用尚未饱和的 target capacity，把每请求验证预算从 MTP-1 的静态 2 个 token 扩到约 4-6 个；并发继续升高后，它会平滑缩短前缀，避免低置信度 token 占满 batch。换句话说，空闲时它用更多验证换单用户速度，繁忙时则主动让出容量保总吞吐。

论文还报告了两个很醒目的数字：V4-Flash 在 120 tok/s/user SLA 下总吞吐名义提升 661%，V4-Pro 在 50 tok/s/user 下提升 406%。它们不应被理解为 DSpark 的常规“数倍加速”：在如此严格的 SLA 下，MTP-1 已接近性能悬崖，只能维持很小的并发 batch。这两个点证明的是 DSpark 扩展了可实现的交互速度边界，而更有代表性的稳态比较仍是表中的中等 SLA 与 matched-throughput 结果。

证据边界同样清楚。离线实验比较 Eagle3 与 DFlash 时关闭了 scheduler，线上实验则比较 DSpark-5 与既有生产 baseline MTP-1，不能把两组数字直接相乘。更根本的限制是：scheduler 只能裁掉送往 target 的后缀，parallel backbone 仍已为完整 $\gamma$-token block 付出一次固定成本；对于天然难预测、接受率很低的请求，这部分 drafting compute 无法回收。

## Conclusion

**DSpark 的核心不是让 speculative decoding 一味猜得更长，而是让每一段额外计算都有足够的预期回报。** 半自回归 drafter 用很小的串行成本修复 parallel drafting 的后缀衰减，置信度调度器再根据候选质量和系统负载决定哪些 token 值得验证；离线 accepted length 与 DeepSeek-V4 实时服务曲线分别验证了这两层改动。

**这项工作把 speculative decoding 从单纯的生成架构问题，推进成了生成与资源分配的联合问题。** “可以起草多少 token”只是模型能力，“此刻应该验证多少 token”则是系统决策。DSpark 已证明两者联合优化能在所测模型与生产环境中移动 Pareto frontier；如何避免低接受率请求的固定 drafting 成本，仍是下一步需要解决的问题。

## Sources

- [DSpark arXiv v1](https://arxiv.org/abs/2607.05147v1)，2026-07-06 提交的当前版本，本文于 2026-09-23 核对
- [Official DeepSpec repository](https://github.com/deepseek-ai/DeepSpec)，用于核对代码、评测入口、硬件默认值与已发布 checkpoints
- [Official DeepSpec model collection](https://huggingface.co/collections/deepseek-ai/deepspec)
- [DeepSeek-V4-Pro-DSpark model page](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-DSpark)，用于核对生产模型与 vLLM 部署入口

## Citation

```bibtex
@misc{cheng2026dsparkconfidencescheduledspeculativedecoding,
  title        = {DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation},
  author       = {Xin Cheng and Xingkai Yu and Chenze Shao and Jiashi Li and Yunfan Xiong and Yi Qian and Jiaqi Zhu and Shirong Ma and Xiaokang Zhang and Jiasheng Ye and Qinyu Chen and Chengqi Deng and Jiping Yu and Damai Dai and Zhengyan Zhang and Yixuan Wei and Yixuan Tan and Wenkai Yang and Runxin Xu and Yu Wu and Zhean Xu and Xuanyu Wang and Muyang Chen and Rui Tian and Xiao Bi and Zhewen Hao and Shaoyuan Chen and Huanqi Cao and Wentao Zhang and Anyi Xu and Huishuai Zhang and Dongyan Zhao and Wenfeng Liang},
  year         = {2026},
  eprint       = {2607.05147},
  archivePrefix = {arXiv},
  primaryClass = {cs.AI},
  url          = {https://arxiv.org/abs/2607.05147}
}
```
