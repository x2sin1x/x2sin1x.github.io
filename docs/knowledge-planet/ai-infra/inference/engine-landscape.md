---
title: "推理引擎版图"
date: 2026-09-29T10:30:00+08:00
weight: 100
---

# 推理引擎版图

> 前面的机制篇（KV Cache、batching、调度、P/D 分离）讲了"应该怎么设计"，本篇看"各家做了什么"：**vLLM、TensorRT-LLM、SGLang、llama.cpp** 的取舍与选型，以及散落在引擎层的公共优化点。

## 四个代表性引擎

| 引擎 | 核心取向 | 关键技术 | 适用场景 |
| ---- | ---- | ---- | ---- |
| vLLM | 通用 + 吞吐 | PagedAttention、continuous batching、prefix caching | 开源生态默认项，研究与服务首选 |
| TensorRT-LLM | NVIDIA 极致性能 | 静态图编译 + kernel 库 + in-flight batching | NVIDIA 卡上的延迟/吞吐上限 |
| SGLang | 高吞吐 + 灵活编程 | RadixAttention（前缀树 KV 复用）、结构化生成 | 多轮对话、agent、复杂前端逻辑 |
| llama.cpp | CPU/端侧 | GGUF k-quants、量化矩阵乘、无 GPU 依赖 | 本地/边缘/嵌入式 |

**vLLM**：PagedAttention 把 KV Cache 按页管理（见[KV Cache]篇），配合 continuous batching 把吞吐做成了开源标杆；生态最广，量化/投机/分离式方案都最先适配。

**TensorRT-LLM**：路线与 vLLM 相反——**编译时**把模型图优化成引擎（层融合、kernel 选择、量化图），运行时高度确定性。in-flight batching 即 continuous batching 的 TRT 版。性能上限最高，代价是灵活性低（新模型适配滞后）、调试困难。

**SGLang**：RadixAttention 用前缀树管理 KV，多请求共享前缀天然命中（见[Prefix Caching]篇）；叠加结构化生成的 frontend DSL，在 agent/多轮场景常跑出最高有效吞吐。

**llama.cpp**：逆向路线——**不依赖 CUDA 生态**，量化矩阵乘在 CPU/Metal/各 NPU 上跑，GGUF 块定标（见[主流量化方法]篇）兼顾精度与内存。端侧推理与"无卡验证"的默认工具。

选型的经验法则：**先看约束再看榜单**——硬件（NVIDIA 深度 vs 通用）、模型（主流 LLM vs 私有结构）、延迟/吞吐偏重、工程团队的调试深度，四项定引擎；benchmark 只在真实负载与长度分布下才有意义（题库 112 的警告：合成长度分布会误导引擎排名）。

## 引擎层的公共优化点

这些点每个引擎都要处理，也是面试高频散点：

- **Warmup（题库 109）**：首请求的延迟包含 CUDA context 初始化、kernel 编译/JIT（TensorRT build、torch.compile）、显存池建立。生产服务的标准做法是启动后用真实 shape 的假请求预热——**warmup 不是测性能，是把一次性成本挪出 SLO 视野**。
- **Multi-stream（题库 110）**：prefill 与 decode、计算与采样/通信放不同 CUDA stream 并发（见[CUDA 编程]篇 stream 节）；P/D 分离架构里 KV 传输与计算的重叠也靠 stream/事件编排。
- **Padding 与 packing（题库 111）**：batch 内序列长度不齐是 prefill 的隐形杀手。padding 按最长对齐（浪费算力）；packing 把多条序列拼进同一行（attention 用块对角 mask 隔离），SFT 训练与 prefill 引擎都会用——利用率差距可达数倍（[后训练]篇算过这笔账）。
- **Debug 模式（题库 115）**：引擎的可用性设计——逐层输出对比（与 HF 参考实现对齐数值）、调度决策日志（为什么这个请求被抢占）、KV 页级统计。没有这三样的引擎，线上问题只能靠猜。

## 延迟分布：别只看平均

延迟评估的正确姿势（题库 112）：**分位数 + 长度分箱**。TTFT/TPOT 都按 P50/P90/P99 报告，并按输入/输出长度分箱——长请求的 P99 才是 SLO 的真实约束。常见指标陷阱：平均 TTFT 被大量短请求稀释；吞吐（tokens/s）在高并发下漂亮但 P99 崩坏；goodput（满足 SLO 的有效吞吐，见[性能指标]篇）才是服务口径。

## 端侧与移动端（题库 108）

移动端的约束排序是**内存 > 能耗 > 延迟**：模型必须全量驻留内存（7B INT4 约 3.5 GB，手机上限附近），所以端侧模型选择先于引擎选择；执行上 llama.cpp 类方案（量化 GEMM、内存映射加载 `mmap` 权重按需换页）是主流；硬件路线拼的是 NPU 支持（QNN/CoreML/NNAPI 的算子覆盖）。一个有用的判断：**端侧推理的瓶颈通常是内存带宽而非算力**——与服务器 decode 同款 Roofline 结论（[芯片架构]篇），只是带宽更小 10 倍。

## 小结

- vLLM 求通用吞吐、TRT-LLM 求单硬件上限、SGLang 求前缀复用与结构化生成、llama.cpp 求无 GPU 依赖——选型从约束出发。
- warmup/multi-stream/packing/debug 是所有引擎的公共课，也是机制篇落到工程的具体位置。
- 延迟按分位数与长度分箱报告，goodput 是服务口径的最终指标。
- 端侧排序是内存 > 能耗 > 延迟，瓶颈结论与服务器 decode 同构。

## 思考题

1. 你的负载 90% 请求命中同一个 2K token 系统提示：哪个引擎机制受益最大？量化收益。
2. TRT-LLM 性能上限高于 vLLM，什么情况下反而该选 vLLM？
3. 多 stream 并发 decode 的两个 stream 会争什么资源？为什么有时并发反而变慢？

::: details 参考答案

1. Prefix/Radix caching：2K 前缀只算一次，后续请求 TTFT 省掉约 2K token 的 prefill（7B 模型约 100+ ms 的计算与带宽）；命中率 90% 意味着系统 prefill 算力需求近似降一个量级（见[Prefix Caching]篇账本）。
2. 模型/量化方案不在 TRT 支持列表（适配滞后）、需要频繁改模型与实验（编译周期长）、多硬件/云环境（TRT 绑 NVIDIA 且版本敏感）、以及调试深度不足的团队。
3. 争 SM 与显存带宽：两个 decode stream 各自的 GEMM 都是带宽受限，并发只是让它们分抢同一带宽——总吞吐不变甚至因调度开销下降。multi-stream 的正确用法是让**异质**任务（计算 vs 拷贝/通信）并发，而非同质 decode。

:::

## 参考资料

- vLLM, [官方文档](https://docs.vllm.ai/) 与 Kwon et al., [Efficient Memory Management for LLM Serving with PagedAttention](https://arxiv.org/abs/2309.06180)（arXiv 2309.06180）
- NVIDIA, [TensorRT-LLM 文档](https://nvidia.github.io/TensorRT-LLM/)；Zheng et al., [SGLang](https://arxiv.org/abs/2312.07104)（arXiv 2312.07104）
- Gerganov, [llama.cpp](https://github.com/ggerganov/llama.cpp)（GGUF 与后端架构）

