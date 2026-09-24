---
title: "DualMap"
date: 2026-09-24
tags:
  - LLM Serving
categories:
  - ICLR
description: "用两个独立哈希函数把每个请求映射到两个候选实例，以 power of two choices 同时保住 KV cache 复用与负载均衡，在相同 TTFT SLO 下将有效请求容量提高至最高 2.25x。"
---

# DualMap：一次哈希写两个答案，缓存亲和与负载均衡不再二选一

Ying Yuan, Pengfei Zuo, Bo Wang, Zhangyu Chen, Zhipeng Tan, Zhou Yu · 华为 & 华中科技大学 · ICLR 2026

[Paper](https://arxiv.org/abs/2602.06502v1) · [OpenReview](https://openreview.net/forum?id=zCadrJ32Xn) · [Code](https://github.com/ASISys/DualMap)

多轮对话和 agent 应用的请求天然共享 prompt 前缀，context caching 把这些前缀的 KV cache 存下来复用，可以省掉重复 prefill，直接压低 time-to-first-token（TTFT）。但这给分布式调度出了难题：cache affinity 要求把同前缀请求送到已存有对应 KV cache 的实例上，load balancing 要求把请求均匀摊到所有实例上。在单一映射空间里，这两个目标互相拆台——prompt-aware 的哈希把热门前缀全堆到一个实例，Least Loaded 则把本可命中缓存的请求散落各处。Mooncake、Preble 这类现有系统只能把请求分成两拨，一拨走 prompt-aware、一拨走 load-aware，得到的只是 trade-off 曲线上的一个中间点，而不是两个目标同时达成。

DualMap 换了一种映射结构：用两个独立的哈希函数把每个请求映射到两个候选实例，再根据系统状态从中选一。共享前缀的请求总是落在同一个候选对里，缓存复用有了保底；power of two choices 又保证不同前缀均匀散布全集群，负载均衡有了理论界。配合 SLO-aware routing、hotspot-aware rebalancing 和 dual-hash-ring scaling 三个机制，论文在 Mooncake 真实 trace、Qwen2.5-7B/14B、8 实例集群上报告：相同 5s TTFT SLO 约束下，有效请求容量相对 SOTA 调度最高提升 2.25x。

## Quick Start

截至 2026-09-24，官方 [DualMap](https://github.com/ASISys/DualMap) 仓库提供了基于 vLLM（>=0.4.2）的完整实验代码，全量实验需要约 8 卡 GPU 和大容量 DRAM。以下命令依据当前 README 核对，未在本文环境中下载模型或占用 GPU 实测。

数据预处理（处理 Mooncake 开源 trace）：

```bash
conda create -n dualmap python=3.10 -y
conda activate dualmap
cd DualMap && pip install -r ./requirements.txt

python evaluation/run/process_dataset.py \
  --model_path ./models/Qwen/Qwen2.5-7B-Instruct \
  --origin_dataset_file ./evaluation/dataset/toolagent_trace.jsonl \
  --processed_dataset_file ./evaluation/dataset/mooncake/processed_toolagent_trace.jsonl
```

然后用 vLLM 在 8 个端口分别拉起 8 个推理实例，最后由全局调度器接入：

```bash
python ./start_up.py \
  --replicas_ip_port "127.0.0.1:8081,...,127.0.0.1:8088" \
  --model_path "./models/Qwen/Qwen2.5-7B-Instruct" \
  --model_name "Qwen2.5-7B-Instruct" \
  --qps 10 \
  --global_scheduler_type "cache_affinity" \
  --ttft_slo 5
```

论文中的 DRAM-based KV-cache 管理模块可用 LMCache 或 Mooncake 直接替换，接口以[官方仓库](https://github.com/ASISys/DualMap)当前说明为准。

## Why DualMap?

先看清两个极端各自输在哪。Cache Affinity 用 prompt-aware 函数把同前缀请求固定到同一实例，缓存命中最大化，但真实负载的前缀热度是倾斜的：热门前缀把一个实例压垮，其余实例闲置，尾延迟失控。Least Loaded 只看各实例当前负载（如待 prefill 的 token 数），负载接近完美均衡（CV≈0），却把共享前缀的请求散落到各处，KV cache 大量 miss，重新计算推高所有人的 TTFT。

论文在 8 实例集群、Qwen2.5-7B 上量化了这条鸿沟：Conversation 数据集上 Cache Affinity 的缓存命中率是 Least Loaded 的 1.21x；在 Tool&Agent 数据集上，前者逼近理论上界，后者贴近下界。而作为中间路线的 Min TTFT（Mooncake 的调度策略）和 Preble 也只是落在两者之间——它们在单一映射空间内，对一部分请求走 prompt-aware、对另一部分走 load-aware，无法同时逼近两个坐标轴的最好值。

![Figure 1：Tool&Agent 数据集上各调度策略的缓存命中率与负载均衡系数（CV）的 Pareto 分布，Cache Affinity 与 Least Loaded 分居两端，Min TTFT 与 Preble 只能取中间点](https://arxiv.org/html/2602.06502v1/motivation_pareto-cache-loadbalance-toolagent.svg)

> 根据原论文 Figure 1(b) 重制引用。读图重点：横纵两轴分别是负载均衡与缓存命中，所有单映射策略只能在这条 Pareto 曲线上移动，没有谁能逼近右上角。

更隐蔽的失败来自 Min TTFT 一类的"逐请求最优"：它为每个请求估计两个候选路径的 TTFT 再取小者，但请求到达会改变系统状态，负载一波动，调度决策就在 cache-aware 和 load-aware 之间来回震荡，反复制造本可避免的 cache miss，重新计算的开销反过来又恶化 TTFT。每一步都局部最优，系统层面却在退步。

问题于是可以复述成一个具体形态：**能不能设计一种映射，一次就同时编码缓存位置和负载分散两个目标？**

## How DualMap Works

### 关键洞察：用两次哈希代替一次折中

DualMap 对每个请求的前缀用两个独立哈希函数 $f_1$、$f_2$ 各算出一个候选实例，请求只会落在这对候选 $\{I_1, I_2\}$ 之内。这一个结构同时给了两个保证：

- **缓存亲和有保底。** 同前缀的 $m$ 个请求总是映射到同一对候选，缓存命中率的下界是 $\max(0, 1-2/m)$，与 Cache Affinity 的 $\max(0, 1-1/m)$ 只差一个候选位。$m$ 稍大，两者几乎重合。
- **负载均衡有理论界。** power of two choices（PoTC）的经典结论（Mitzenmacher, 2002）：$m$ 个请求、$n$ 个实例、每个请求看 $d$ 个候选取负载较低者时，最大负载满足 $\max_i L(I_i) \le m/n + \log\log n/\log d + \mathcal{O}(1)$。$d=1$ 时偏离项是 $\Theta(\sqrt{m\log n/n})$，随规模增长；$d=2$ 就降到 $\log\log n$ 量级。

而 $d$ 也不是越大越好：$d=3, 4$ 对偏离项的改善已经边际递减，候选集每扩一位，共享前缀的请求就多一处被分散的去向，缓存局部性被稀释——"全局收集所有实例信息再选最优"等价于 $d=n$，负载上几乎不再改善，缓存复用却退化成 Least Loaded。**$d=2$ 是这个问题的甜点。**

![DualMap 系统总览：全局调度器对每个请求做双重哈希得到两个候选实例，经 SLO-aware routing 选定其一；热点实例通过 hotspot-aware rebalancing 把排队请求迁移到各自的备份候选；扩缩容由 dual-hash ring 支持局部重映射](https://arxiv.org/html/2602.06502v1/DaulMap-overview.svg)

> 来源：论文 Figure 2。读图重点：每个请求的可行域从"全集群"收缩到"一对候选"，调度器的全部决策——路由、迁移、扩缩——都只发生在这对候选之内。

### 机制一：SLO-aware routing

两个候选之间怎么选？DualMap 的原则是**能保缓存就保缓存**：默认选缓存复用更高的候选，直到该实例的排队负载会使预期 TTFT 超出 SLO，才切换到 load-aware 选择较空闲的那个；两个候选命中率相同时，恒选负载较低者。与 Min TTFT 的区别在于目标函数——DualMap 不追求单请求最优延迟，而是把"缓存复用"设为默认态、"负载均衡"设为 SLO 受威胁时的例外态，震荡和重复计算因此大幅减少。切换判据是预计算的 `ttft_slo_threshold`：给定 TTFT SLO，算出一张 GPU 在时限内最多能处理多少待 prefill token。

哈希键的长度本身也是个问题：键太长会超出实际共享前缀，把同源请求打散；太短则让无关请求撞车。DualMap 维护一棵前缀热度树，用滑动窗口统计各前缀的流量占比 $\rho$，热点前缀（$\rho > 2/n$，$n$ 为实例数）向下分裂以拉长哈希键，热度退去再收缩合并。真实数据说明这步不可或缺：Conversation 数据集 95% 的请求用 2 个 block 作哈希键即可，而 Tool&Agent 里 37.8% 的请求因两个异常热门的前缀被拉长到 13 个 block。

### 机制二：hotspot-aware rebalancing

PoTC 均衡的前提是请求近似随机，前缀倾斜会击穿这个假设。DualMap 借鉴 Cuckoo hashing——每个键本就有两个槽位——把过载实例上排队的请求迁移到它的备份候选，但不做递归驱逐，只做单轮批量迁移。是否迁移由收益决定：$B_r^{(i\to j)} = \mathrm{TTFT}_{r,i} - \mathrm{TTFT}_{r,j}$，即请求 $r$ 留在源实例 $i$ 与迁往备份 $j$ 的预期 TTFT 之差，只有收益为正且目标确实空闲的请求才动身，按收益降序迁移直到队列有望满足 SLO。因为迁移始终发生在候选对内部，缓存亲和不会被牺牲，调度复杂度也与集群规模无关。

### 机制三：dual-hash-ring scaling

静态哈希把前缀焊死在实例上，扩缩容会触发全局重映射，缓存命中率瞬间崩塌。DualMap 把双重哈希架在一致性哈希环上：逻辑空间 $[0, M)$ 中每个实例按标识占据锚点，请求的前缀经两个哈希函数落在环上，各取顺时针最近的实例为候选。映射只取决于环上的相对位置，增删实例只影响环上局部区段的请求，绝大多数前缀的映射路径原样保留，扩缩容因此轻量且不抖动。论文的弹性实验里，4 实例过载时在第 74 秒扩到 8 实例，SLO 达标率随即回到 90%；负载回落后再缩回 4 实例，全程保持在 90% 以上。

## Results

实验设置：DualMap 作为独立全局调度层部署在 vLLM 之上，8 实例集群，每实例一块 Ascend NPU（7B 用 910B4、14B 用 910B3）加 DRAM 缓存，Qwen2.5-7B/14B，float16。负载来自 Mooncake 的两份真实 trace：Conversation（4000 请求，前缀缓存占比 40%）和 Tool&Agent（8000 请求，占比 59%，含明显的倾斜前缀）。对比 Cache Affinity、Least Loaded、Min TTFT（Mooncake 调度）与 Preble，SLO 统一为 TTFT < 5s。

主结果：

![Figure 3：四种负载下各策略的 effective request capacity 与 goodput；DualMap 在含倾斜前缀的 Tool&Agent 工作负载上优势最大](https://arxiv.org/html/2602.06502v1/slo_satisfaction_ttft_5_big.svg)

> 来源：论文 Figure 3。读图重点：横轴 QPS 增大时，各 baseline 的 SLO 达标率快速滑落，DualMap 的曲线最平缓——缓存复用减少了总计算量，负载均衡又消掉了热点排队，两个收益叠加。

- **有效请求容量**：Tool&Agent 上 DualMap 相对最佳 baseline 提升最高 125%（即 2.25x）；Conversation 上提升 40.6%-80%。
- **Goodput**（满足 SLO 约束下可持续的最大请求率）：Tool&Agent 上比最佳 baseline 高 16.7%-48%，Conversation 上高 14.3%-40%。
- **延迟**：高 QPS 下相对最佳 baseline，P50 TTFT 降低 55.4%-97.4%，P90 TTFT 降低 82.3%-97%；E2E 延迟趋势与 TTFT 一致。
- **两个目标各自到位**：缓存命中率达到 Cache Affinity 理论上界的 62.5%（Conversation）和 96.4%（Tool&Agent），同时负载均衡度显著优于所有 baseline。

消融实验（Conversation，Qwen2.5-14B）验证了每个机制的贡献：把候选间选择换成 min-TTFT 策略，缓存命中率立刻因震荡选择下滑；SLO-aware routing 相对 min-ttft 选择降低 P50/P90 TTFT 23.5%/18.5%；再叠加 hotspot-aware rebalancing，P90 TTFT 进一步降低 11.3%。

边界也要说清楚。调度开销本身很小——每次路由约 0.6ms、KV cache 查询约 0.2ms、一轮再平衡 2.2-2.5ms，元数据每实例约 146KB（7B 模型），且这些开销不随集群规模增长；但基于 Vidur 模拟器的 8→32 实例近线性 goodput 扩展性结果来自仿真而非真实集群。实验硬件是 Ascend NPU，缓存模块依赖 DRAM，TTFT 估计在显存竞争引发 decode 瓶颈时的鲁棒性被论文放在附录讨论；对比对象也未包含调度设计相似的 Dynamo。工程落地前，这些条件值得逐一对照自己的环境。

## Sources

- [DualMap arXiv v1](https://arxiv.org/abs/2602.06502v1)，2026-02 提交，本文于 2026-09-24 核对
- [ICLR 2026 OpenReview 页面](https://openreview.net/forum?id=zCadrJ32Xn)，论文已被接收为 ICLR 2026 Poster，本文于 2026-09-24 核对
- [Official DualMap repository](https://github.com/ASISys/DualMap)，用于核对 2026-09-24 的安装与使用入口

## Conclusion

DualMap 证明了一件事：cache affinity 与 load balancing 的冲突不是两个目标之间的权重问题，而是映射空间的结构问题。把"每个请求一个去处"改成"每个请求一对候选"，power of two choices 的负载理论界和前缀绑定的缓存保底就能同时成立，SLO-aware 的候选间选择、候选对内的热点迁移和哈希环上的局部重映射再把这对候选用好。

它改变看待调度问题的方式也在于此：与其在"保缓存"和"保均衡"之间调权重，不如先问映射空间本身能不能同时容下两个目标。对做推理服务调度的读者来说，"两次哈希 + 状态感知选择"是一个成本极低、又带理论保证的起步模板。
