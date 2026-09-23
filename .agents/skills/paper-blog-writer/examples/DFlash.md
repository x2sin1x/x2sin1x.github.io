# DFlash：让 diffusion 做它更擅长的并行起草

Jian Chen, Yesheng Liang, Zhijian Liu · ICML 2026

[Paper](https://arxiv.org/abs/2602.06036v2) · [Code](https://github.com/z-lab/dflash) · [Models](https://huggingface.co/collections/z-lab/dflash) · [Original project page](https://z-lab.ai/projects/dflash/)

大语言模型一次只生成一个 token：后一个 token 必须等前一个 token 出来。Speculative decoding 试图把这条串行链缩短，让小型 draft model 先猜一段，再由 target model 一次并行验证；但 EAGLE-3 这样的强 baseline 连“猜”本身仍是自回归的，实际加速通常停在约 2-3x。

DFlash 换了一种分工：用轻量 block diffusion model 在一次前向中并行起草一整块 token，再让它读取 target model 已经算出的上下文特征。论文在 Qwen3 非思考模式的多项任务上报告平均 4.9x 的自回归 baseline 加速，相对同为 16-token drafting budget 的 EAGLE-3 平均提高 2.4x；单项结果最高超过 6x，同时仍由 speculative verification 保持 lossless 输出。

## Quick Start

截至 2026-09-23，官方仓库已提供 `dflash` 包、本地 Transformers/MLX 路径，以及面向 SGLang、vLLM 等 OpenAI-compatible server 的入口。下面展示当前官方 CLI 对 Qwen3 DFlash checkpoint 的最短本地路径；该命令依据官方文档核对，未在本示例环境下载模型或占用 GPU 实测。

```bash
pip install "dflash[local]"

dflash generate transformers \
  --model Qwen/Qwen3-8B \
  --draft z-lab/Qwen3-8B-DFlash-b16 \
  "How many positive whole-number divisors does 196 have?"
```

生产服务的后端支持与启动参数变化更快，应以[官方仓库](https://github.com/z-lab/dflash)当前说明为准。

## Why DFlash?

Speculative decoding 的基本流程并不复杂。Draft model 先提出若干候选 token，target model 再并行检查；猜对的连续前缀被接受，第一次猜错的位置回到 target model 的结果。因此最终质量不需要交给 drafter 保证，drafter 真正要优化的是两件事：一次能猜对多长，以及为这批猜测付出多少时间。

自回归 drafter 在这两件事之间很难取巧。多猜一个 token，就多一次串行前向；为了压低 drafting latency，EAGLE-3 只能采用很浅的单层结构，而容量受限又让 acceptance length 很快饱和。增加 speculation budget 并不会免费换来更多被接受的 token。

Diffusion 看上去正好能并行生成，但直接替换同样行不通。DiffuSpec、SpecDiff-2 等方案使用约 7B 参数的 drafter，显存和 drafting cost 都偏高；把 diffusion model 缩小，则会失去足够的预测能力。DFlash 论文中的反例很直观：一个没有 target conditioning 的五层 block diffusion drafter，在四个数学任务上通常只有约 2-3x 加速。

问题因此变得具体：**能否让 diffusion drafter 足够小、足够快，同时又知道 target model 接下来大概率会说什么？**

## How DFlash Works

### 关键洞察：答案的一部分已经在 target model 里

Target model 完成 prefill 或一次 verification 后，不只产生下一个 token 的 logits。它的多层 hidden features 还编码了语义、长程依赖，以及关于多个未来 token 的信息。让小 drafter 从零推理很难，但让它读取这些已经计算出的上下文，任务就从“独立回答”变成了“沿着 target model 的思路快速补全”。

这也是 DFlash 对 diffusion model 的重新定位：它不必在端到端生成质量上击败 autoregressive LLM，只需要成为一个快而准、且最终会被验证的 block drafter。

### 为什么 diffusion 改变了速度与容量的权衡

自回归 drafting 的成本大致随候选 token 数线性增长，因为每个 token 都需要下一次前向。Block diffusion 则在一次前向中同时预测一个 block 的所有 masked positions；在适中的 block size 下，drafting cost 对 token 数不再呈同样的线性增长。

于是模型容量的选择空间变了。DFlash 可以使用多层 drafter 提高 acceptance length，而不必为每个候选 token 重复运行这些层。论文测得，五层 DFlash 一次起草 16 个 token 的 latency 仍低于单层 EAGLE-3 起草 8 个 token。更深、猜得更多，反而用时更少。

### 设计

![DFlash 推理流程：target model 的多层 hidden features 经融合后注入每一层 draft model 的 KV cache，draft model 再并行预测一个 token block](https://z-lab.ai/assets/projects/dflash/method.png)

> 来源：DFlash 官方项目页，对应论文 Figure 2。读图重点：target context 不是只在 draft model 入口出现一次，而是作为持久条件进入每一层；这一点使“更深的 drafter”不会迅速丢失 target signal。

1. **Feature Fusion：** 从 target model 由浅到深均匀选择若干层 hidden features，拼接后通过轻量 projection，得到紧凑的 target context feature。
2. **KV Injection：** 将融合特征直接投影到每一层 drafter 的 Key/Value，并保存在 KV cache 中跨 drafting iteration 复用。EAGLE-3 风格的 input fusion 只在第一层输入 target feature，层数增加后信号会逐渐稀释；逐层注入让 acceptance length 能随深度继续增长。
3. **Parallel Drafting：** Drafter 以最后一个已验证 token 和持久 target context 为条件，通过单步 block diffusion 并行预测下一块 token；target model 随后统一验证。

训练也围绕同一个推理接口展开。DFlash 随机采样干净的 anchor token，将后续位置遮住并要求 drafter 并行预测；多个 block 用 sparse attention 在一次 forward/backward 中训练，从而避免不同 block 互相泄漏信息。

## Results

论文在 Qwen3-4B/8B/Coder、LLaMA-3.1-8B，数学、代码和对话任务上评测 acceptance length 与端到端 decoding speedup。Qwen3 主实验使用 Transformers，默认在 NVIDIA H200 上运行；核心 baseline 是 vanilla autoregressive decoding 和 EAGLE-3。对 EAGLE-3 同时报告 tree size 16 与 60，其中 16 与 DFlash block size 16 对齐 drafting budget。

![Qwen3-8B 的数学、代码与对话任务中，DFlash 相对自回归 baseline 的加速普遍高于 EAGLE-3](https://arxiv.org/html/2602.06036v2/dflash_speedup.svg)

> 来源：原论文 v2 Figure 1。读图重点：在图示 Qwen3-8B 与 Transformers 设置中，DFlash 跨任务保持更高的端到端 speedup；这张图不能单独代表其他模型、硬件或 serving backend。

| 设置 | DFlash 相对自回归 baseline 的平均加速 | 相对 EAGLE-3(16) 的平均提升 |
|---|---:|---:|
| Qwen3，thinking off，temperature = 0 | 4.9x | 2.4x |
| Qwen3，thinking off，temperature = 1 | 4.1x | 2.2x |

> 来源：原论文 v2 Table 1 与 Section 5.1。读表重点：DFlash 的优势同时出现在 greedy decoding 和 sampling，而不是只依赖确定性输出；这些数值是跨表中任务的平均结果，不代表每个任务都达到相同比例。

这个结果背后的两个因素可以由消融分开看到。逐层 KV injection 比只在输入层融合 target features 得到更高 acceptance length；在 acceptance length 接近时，block diffusion 又因并行 drafting 获得更高 speedup。换句话说，DFlash 不是只把 draft 猜得更准，也不是只把 draft 算得更快，而是同时改变了质量和成本两侧。

收益还延伸到其他设置：thinking mode 下论文报告约 4.5x 和 3.9x 的自回归 baseline 加速；在单张 B200、SGLang 与 concurrency 1-32 的 serving 实验中，Qwen3-8B 最高达到 5.1x。不过，这些数字来自不同模型、硬件和后端，不能横向拼成一个统一的“5x”承诺。

证据也有明确边界。论文没有与其他 diffusion speculative decoding 方法做直接实验比较，理由是当时缺少开源实现；基础 drafter 在超过其 4K 训练上下文后 acceptance length 会下降，需要少量长上下文微调恢复。最优层数与 block size 也依赖部署负载：更深会提高 acceptance length，却不一定带来最高端到端 speedup。

## Conclusion

**DFlash 证明，diffusion model 不必承担最终回答，才能发挥并行生成的价值。** 把它限制在 drafting 阶段，再用 target hidden features 提供高质量条件，系统便能同时降低 drafting latency、提高 acceptance length，并让 autoregressive verification 保住输出质量。

**更值得记住的是一种角色重分配：强模型负责思考与验收，小 diffusion adapter 负责并行补全。** 论文已经证明这种分工在所测模型和系统上有效；能否在更多硬件、长上下文与动态 serving 负载下维持优势，仍需要继续验证。

## Sources

- [DFlash arXiv v2](https://arxiv.org/abs/2602.06036v2)，2026-05-28 修订的 ICML 2026 camera-ready 版本
- [Z Lab DFlash project page](https://z-lab.ai/projects/dflash/)，本文风格参考来源
- [Official DFlash repository](https://github.com/z-lab/dflash)，用于核对 2026-09-23 的使用入口
- [Official model collection](https://huggingface.co/collections/z-lab/dflash)

## Citation

```bibtex
@inproceedings{chen2026dflash,
  title     = {DFlash: Block Diffusion for Flash Speculative Decoding},
  author    = {Chen, Jian and Liang, Yesheng and Liu, Zhijian},
  booktitle = {Proceedings of the International Conference on Machine Learning},
  year      = {2026}
}
```
