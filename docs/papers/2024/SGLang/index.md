---
title: "SGLang"
date: 2024-06-06
tags:
  - LLM Serving
  - KV Cache
  - Structured Output
categories:
  - arXiv
description: "SGLang 的核心创新 RadixAttention 首次把 KV cache 当作树形 LRU 缓存来管理：请求产生的所有共享前缀自动收进一棵 radix tree，配合最长共享前缀优先调度把命中率推向理论最优，在 agent、few-shot、多轮对话等多调用任务上报告最高 6.4x 吞吐提升。"
---

# SGLang：让 KV cache 第一次被当作缓存来管理

Lianmin Zheng, Liangsheng Yin, Zhiqiang Xie, Chuyue Sun, Jeff Huang, Cody Hao Yu, Shiyi Cao, Christos Kozyrakis, Ion Stoica, Joseph E. Gonzalez, Clark Barrett, Ying Sheng · arXiv 2024（v2）

[Paper](https://arxiv.org/abs/2312.07104v2) · [Code](https://github.com/sgl-project/sglang)

大语言模型的使用方式正在从"一次问答"变成"一段程序"：agent 要多轮规划与调用工具，self-consistency 和 Tree-of-Thought 要并行或树状地发起多次生成，RAG 与 JSON 模式则要求结构化的输入输出。论文把这类多调用、带控制流、输入输出结构化的程序统称为 LM Programs。问题在于，底层推理引擎是为单次请求优化的：一个请求结束时它的 KV cache 就被丢弃，于是 system prompt、few-shot 示例、多轮对话历史这些共享前缀，在不同调用、不同请求之间被一遍遍重算。

SGLang 的核心创新 RadixAttention 针对的正是这一点：请求结束后不释放 KV cache，而是把"token 序列 → 缓存张量"的映射收进一棵 radix tree，按 LRU 策略自动复用与淘汰，再配一个最长共享前缀优先的缓存感知调度器，把命中率推向理论最优——论文声称这是第一个把 KV cache 当作树形 LRU 缓存管理的方案。围绕它，前端一组嵌入 Python 的生成与并行原语让程序"自觉"提供复用机会，压缩有限状态机则让结构化输出一次前向解码多个 token。在 Llama-2 7B/70B、Mixtral-8x7B 与 LLaVA 模型的 agent、few-shot、多轮对话等基准上，论文报告相对 vLLM 等系统最高 6.4x 的吞吐提升和最高 3.7x 的延迟下降。

## Quick Start

需要说明：论文发表后，SGLang 已从"前端 DSL + 运行时"的定位演进为一个通用的高性能 serving 框架，当前仓库的重心是 OpenAI 兼容的推理服务，prefix caching（即 RadixAttention 的延续）作为核心特性默认内置。下面的安装与服务启动命令依据[官方文档](https://docs.sglang.io/get_started/install.html)核对（2026-09-28，要求 CUDA 13），未在本文环境中实测——启动会下载模型并占用 GPU。

```bash
pip install --prerelease=allow sglang

# 启动一个 OpenAI 兼容的本地服务（默认端口 30000）
python3 -m sglang.launch_server --model-path qwen/qwen2.5-0.5b-instruct --host 0.0.0.0
```

```bash
# 同一服务内自动获得前缀缓存与结构化输出支持
curl -s http://localhost:30000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen/qwen2.5-0.5b-instruct", "messages": [{"role": "user", "content": "Hello"}]}'
```

## Why RadixAttention?

先看 KV cache 在推理里的角色。生成每个 token 时，attention 需要用到之前所有 token 的 key/value 中间张量；这部分计算只取决于前缀 token 本身，与前缀之后是谁在提问无关。于是只要两个请求共享同一段前缀——同一个 system prompt、同一组 few-shot 示例、同一次对话的前几轮、甚至对同一张图片的多个提问——后到的请求本可以直接复用先算好的 KV cache，省掉整段 prefill。

主流引擎却把这笔账算丢了。vLLM、TGI、TensorRT-LLM 这类系统把优化目标放在单个请求的延迟和吞吐上，对 workload 本身没有认知：请求结束，KV cache 释放，下一个请求从零开始 prefill。它们的个别前缀共享（比如固定 system prompt）需要手工配置，覆盖不了程序执行中动态出现的共享——一个 agent 模板加上任意深度的对话分叉，构成的是一棵树，而不是一条固定的公共前缀。

一个自然的想法是给缓存做"语义匹配"：不要求前缀逐字相同，只要意思相近就复用。这条路存在精度风险——同期的 PromptCache 尝试非前缀的模块化复用，论文在相关工作中指出其准确率最多可下降 43%。复用必须是逐字前缀级、无损的，问题才成立。

于是问题收敛成一个系统设计题：**既然 KV cache 只依赖前缀 token，能否把它当成一种普通的缓存资源来管理——自动发现、自动复用、自动淘汰，而不是靠开发者预先声明哪些前缀值得共享？**

## How RadixAttention Works

### 关键洞察：KV cache 就是一种可缓存的中间结果

论文的判断是：程序执行中反复出现的共享前缀，天然构成一棵树；只要有一个能把"token 序列 → KV cache 张量"的映射按前缀组织起来的数据结构，复用就可以变成默认行为，而不再是一份需要维护的配置。这把 KV cache 从"每个请求的私有工作区"重新定义为"整个服务生命周期的公共缓存"，与 CPU 缓存、CDN 在概念上站到了同一层。

### 为什么 radix tree 改变了权衡

旧方案里，复用范围由人工枚举决定：声明一个 system prompt 可共享，就只共享它；程序里新出现的共享模式（few-shot 示例下的多个问题、同一问题的多个分支）完全不可见。radix tree 的边的标签是任意长度的 token 序列，任何一次插入都自动与已有请求找最长公共前缀、在分歧处分裂节点——多级共享被数据结构本身自动覆盖，无需任何声明。缓存命中从此成为运行时的属性，而不是程序员的负担。

### 工作循环：插入、匹配、分裂、逐出

RadixAttention 的运行时围绕四个动作循环：

1. **插入：** 一个请求完成后，它的完整 prompt 与生成结果被合并成树上的新边和叶子节点。每个节点带引用计数，标记有多少个正在运行的请求依赖这条路径。
2. **匹配：** 新请求到来时沿树做最长前缀匹配，命中的路径直接复用已有 KV cache，只对未命中的尾部做 prefill。前端的 `fork` 原语会先发送共享前缀作为 hint，确保并行分叉的前缀先于分支落进树里——这是前端与运行时协同设计的第一个落点。
3. **分裂：** 当新请求与某个已有节点共享前缀但在此分叉时，节点被一分为二，两边各自共享公共祖先的缓存。
4. **逐出：** 显存有限，缓存采用 LRU 策略且优先逐出叶子——祖先节点因此能活到自己也变成叶子为止，公共前缀获得最长寿命。关键在于缓存与运行请求共享同一块显存池：等待的请求足够多时，系统宁可全部逐出缓存去扩大 batch size，缓存永远不挤占运行内存。

![RadixAttention 的九个时刻：新请求沿树匹配前缀直接复用缓存，在分歧处分裂节点，内存不足时优先逐出叶子节点](https://arxiv.org/html/2312.07104v2/example_radix_attn.svg)

> 来源：原论文 Figure 3。读图重点：两级聊天会话共享 system prompt、few-shot 批量提问共享题干、self-consistency 共享问题前缀——这些不同形态的共享都被同一棵树自动接住。

这个设计天然可扩展到分布式：张量并行下每张 GPU 持有自己那片 KV cache 分片，树操作完全相同、无需同步；数据并行下，每个 worker 维护子树，路由器维护一棵追踪所有子树的 meta-tree，按请求与各 worker 的共享前缀亲和度派发请求。论文在四个 worker 的 MMLU 实验中观察到线性扩展与接近最优的命中率，弱一致分布式缓存的同步开销很小。

### 缓存感知调度：命中率也是调度问题

有了缓存，"按什么顺序执行请求"就直接决定命中多少。若调度器在无关请求间频繁切换，缓存会被反复冲刷（thrashing）。SGLang 的缓存感知调度在批处理场景把等待队列按已匹配前缀长度排序，最长共享前缀优先。

这不仅是启发式。论文证明了 Theorem 3.1：当缓存容量不小于最大请求长度时，按 radix tree 的深度优先顺序访问请求可以取得最优缓存命中率——因为每条树的边对应的 KV cache 至少要算一次，DFS 恰好让每条边算一次、算完整个子树前一直命中——而最长共享前缀优先正好等价于 DFS。在线场景下请求到达会打断 DFS，但调度器仍在近似这一顺序。代价是贪心：论文明确指出这种调度可能导致请求饥饿，与公平调度的融合留作未来工作。

### 配套机制

RadixAttention 解决复用，SGLang 的另外两个部件解决"机会从哪来"与"输出怎么快"：

- **前端语言与流式解释器：** `gen`（生成并支持 regex 约束）、`select`（从候选中选概率最高项）、`fork`/`join`（并行分叉与汇合）嵌入 Python。它不只是让程序好写（同等程序用 OpenAI API 风格接口要写约 2.1x 的代码量），更通过流式解释器和 fork hint 主动为运行时制造可复用的前缀结构。
- **压缩有限状态机：** 对结构化输出，把正则约束转成的 FSM 中"只有一个出边的连续路径"压缩为单条边——固定字符串 `{"summary": "` 在原 FSM 里要走多个 token，压缩后一次前向即可整段解码，配套 retokenization 处理分词伪影，FSM 预处理在整批请求间复用。
- **API speculative execution：** 对只开放 API 的黑盒模型（如 GPT-4），前两条机制都碰不到推理过程；SGLang 让第一次生成越过 stop 条件多生成几步，后续 `gen` 原语直接匹配复用这些输出，用少量浪费换取省掉整个 API 调用的输入 token 费用。

## Results

实验设置决定了这组对比的口径：模型为 Llama-2 7B/70B、Mixtral-8x7B、LLaVA-v1.5-7B（图像）与 LLaVA-NeXT-34B（视频），float16；主硬件是 AWS G5 实例的 NVIDIA A10G（24GB），7B 单卡、大模型张量并行，另有 A100（80GB）实验。基线分两层：编程系统 Guidance v0.1.8（llama.cpp 后端）与 LMQL v0.7.3（Hugging Face Transformers 后端），以及推理引擎 vLLM v0.2.5（论文脚注说明：因 RadixAttention 已作为实验特性部分合入新版 vLLM，故选用较早版本对比）；除非特别说明，所有系统都关闭会改变计算结果的优化，保证输出一致。吞吐口径是"程序实例/秒"，即批处理下单位时间完成的完整程序数。

![Llama-2-7B 上九类工作负载的端到端吞吐：SGLang 在 agent、few-shot、JSON 解码等多调用任务上明显高于 vLLM、Guidance、LMQL](https://arxiv.org/html/2312.07104v2/e2e_throughput_llama_7b.svg)

> 来源：原论文 Figure 5。读图重点：收益集中在存在前缀共享或多调用并行的任务上，直接验证 RadixAttention"利用多调用结构"的主张。

结果上，SGLang 把端到端吞吐最高提高 6.4x、延迟最高降低 3.7x。收益来源与任务结构一一对应：MMLU 复用 5-shot 示例的缓存，HellaSwag 复用"few-shot 示例 + 题干"两级前缀，agent 类任务复用模板与历史调用，多轮对话复用对话历史，多模态下 SGLang 直接以输入图像的哈希作为树键，复用对同一图片多次提问的缓存。这些基准上的缓存命中率在 50%-99% 之间，缓存感知调度平均达到理论最优命中率的 96%。

![RadixAttention 消融：去掉树结构、改回先来先到或随机调度、关闭前端并行或 hint，任一部件缺失都会掉性能](https://arxiv.org/html/2312.07104v2/cache_hit_and_ablation.svg)

> 来源：原论文 Figure 8(c)。读图重点：完整优化与任一单项退化之间的差距，把收益归因到 RadixAttention 的每个组成部分，而非笼统的"加缓存"。

消融实验把功劳拆到了每个部件：去掉树结构退化为表式缓存、改回先来先到或随机调度、关闭前端并行与 hint，任何一个都会掉性能——前端与运行时必须协同设计。开销方面，在一个毫无复用机会的 ShareGPT 负载上，RadixAttention 的数据结构管理只占总时间的 0.3% 以下（100 个请求 74.3 秒中仅 0.2 秒），论文因此默认开启它。配套机制各有一份账：压缩 FSM 把 JSON 解码吞吐提高 1.6x，且 FSM 预处理必须跨请求复用，否则吞吐会低 2.4x；API speculative execution 在 GPT-3.5 的字段抽取任务上把输入 token 成本降低约三倍。生产侧，SGLang 部署在 Chatbot Arena 服务开源模型：一个月实测 Vicuna-33B 缓存命中率 74.1%、LLaVA-NeXT-34B 52.4%，Vicuna-33B 的首 token 延迟平均下降 1.7x。

证据的边界也要说清。收益与输出长度强相关：多轮对话输出较短时加速明显，输出长达 256-512 token 时几乎无加速——缓存复用省的是 prefill，而解码时间占主导。缓存感知调度可能饥饿请求；同样的贪心也体现在内存分配上，等待的请求足够多时缓存会整体让位给 batch size。最后，这条路线只覆盖逐字前缀复用，跨"语义相似"前缀的复用仍因精度风险（前述最高 43% 的准确率下降）留在无损边界之外。

## Conclusion

**RadixAttention 证明的是：KV cache 可以像普通缓存一样被自动管理，LM Programs 的多调用结构本身就是一种可被系统利用的优化信号。** 树形 LRU 让前缀复用从人工配置变成数据结构的默认行为，缓存感知调度用一条 DFS 定理把"什么顺序执行请求"也纳入复用问题，压缩 FSM 则把约束解码从逐 token 变成按 FSM 边走。三者的共同前提是前端与运行时协同设计——程序知道自己会怎么被调用，运行时才知道该缓存什么。

**它改变的是看待推理引擎的方式：缓存命中率开始与算子效率平起平坐。** 这条思路的延续——prefix caching、缓存感知负载均衡——如今已是主流 serving 框架的标配（vLLM 也随后将 RadixAttention 思路合入为实验特性），SGLang 本身则从一个论文原型长成了工业界广泛使用的推理后端。对今天设计推理系统的人而言，值得追问的问题从"单请求多快"多了一条："程序结构里还有多少共享，正在被引擎白白重算？"

## Resources

- [Paper（arXiv 2312.07104v2）](https://arxiv.org/abs/2312.07104v2)
- [Code（sgl-project/sglang）](https://github.com/sgl-project/sglang)
- [官方文档](https://docs.sglang.io/)

## Citation

```bibtex
@misc{zheng2024sglang,
  title         = {SGLang: Efficient Execution of Structured Language Model Programs},
  author        = {Lianmin Zheng and Liangsheng Yin and Zhiqiang Xie and Chuyue Sun and Jeff Huang and Cody Hao Yu and Shiyi Cao and Christos Kozyrakis and Ion Stoica and Joseph E. Gonzalez and Clark Barrett and Ying Sheng},
  year          = {2024},
  eprint        = {2312.07104},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI}
}
```
