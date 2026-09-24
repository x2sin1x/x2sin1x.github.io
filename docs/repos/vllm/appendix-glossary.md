---
title: 附录 C：术语表
weight: 180
---

# 附录 C：术语表

只收录正文使用的术语。同一概念全系列只用一个译名，首次出现附英文原名。

| 术语 | 英文 | 释义 |
|---|---|---|
| 引擎核心 | EngineCore | 独立进程中的调度大脑，持有 Scheduler 与 KV 账本（`vllm/v1/engine/core.py`） |
| 调度器 | Scheduler | 每个 engine step 决定调度哪些请求、各推进多少 token 的组件 |
| 步 | step | 调度器的一次"调度 + 执行 + 收账"循环，一次前向 |
| 连续批处理 | continuous batching | 请求随到随进、随完随走的批次组织方式，无需等待整批结束 |
| 分页注意力 | PagedAttention | 把 KV Cache 按固定大小块管理、支持非连续显存的注意力实现 |
| 块 | block | KV Cache 的分配单位，固定 token 数（默认 16），是第 7 章的核心概念 |
| 块池 | BlockPool | 空闲块队列 + hash 索引 + 引用计数，物理 KV 块的所有者 |
| 块表 | block table | 每请求的块号序列，调度器账本在 GPU 侧的镜像 |
| 前缀缓存 | prefix caching | 内容寻址（`BlockHash`）复用相同前缀 KV 的机制 |
| 命中 | cache hit | 请求前缀与已缓存块哈希匹配，可跳过计算 |
| token 预算 | token budget | 单步全局可调度的 token 上限（`max_num_scheduled_tokens`） |
| 分块预填充 | chunked prefill | 超预算的 prompt 被切成多步逐步送入模型 |
| 抢占 | preemption | 显存不足时把运行中请求踢出、释放块、重入等待队列（重算式） |
| 计算令牌数 | `num_computed_tokens` | 请求已完成计算（含缓存命中）的 token 计数器，调度的统一视角 |
| 采样参数 | sampling params | 温度、top-k/top-p、惩罚、stop 条件等生成控制参数 |
| logits 处理器 | logits processor | 在采样前修改 logits 分布的插件（含结构化输出约束） |
| 位掩码 | grammar bitmask | 结构化输出每步生成的词表掩码，非法 token 概率归零 |
| 增量反词元化 | incremental detokenization | 只解码新 token、维护 UTF-8 残片的文本重建方式 |
| 流式收集器 | RequestOutputCollector | 每请求一个的覆盖式输出队列，实现流式背压 |
| 持久批次 | persistent batch | 常驻 Worker 的批次元数据，每步只做增量增删 |
| 注意力元数据 | attention metadata | attention kernel 所需的块表、序列长度等输入布局 |
| CUDA 图 | CUDA Graph | 把整次前向录制成图并按形状 replay 的延迟优化 |
| 执行器 | Executor | EngineCore 与 Worker 进程模型之间的可替换件（uni/mp/ray） |
| 通信组 | process group | torch.distributed 意义上的进程集合（TP/PP/DP 组） |
| 张量并行 | TP，tensor parallel | 按层内权重矩阵切分到多卡 |
| 流水线并行 | PP，pipeline parallel | 按层深度切分，中间张量在 rank 间传递 |
| 数据并行 | DP，data parallel | 复制多套引擎，各自调度、按负载路由请求 |
| 专家并行 | EP，expert parallel | MoE 专家分布到不同卡 |
| 提案者 | proposer | 投机解码中产生草稿 token 的组件（n-gram / Eagle / Medusa / MTP） |
| 拒绝采样 | rejection sampling | 投机解码的验证算法，保证输出分布与自回归采样一致 |
| KV 连接器 | KV Connector | 跨引擎/跨层缓存搬运 KV 的扩展协议（P/D 分离、LMCache 等） |
| 分离式部署 | P/D disaggregation | Prefill 与 Decode 引擎实例分离、经 Connector 传递 KV 的架构 |
| 平台 | Platform | 硬件抽象（CUDA/ROCm/TPU/XPU/CPU），声明设备能力 |
| 插件 | plugin | 经 entry points 在启动期注册模型/平台/端点的外部代码 |
| 结构化输出 | structured output | 用 JSON Schema/正则/文法约束生成内容的机制 |
| 量化配置 | quantization config | 每种量化方案（fp8/AWQ/…）提供替换层的配置类 |
| 加载器 | model loader | 按 load_format 分派的权重装载组件 |
| 块事件 | KV cache events | 块存储/移除的对外事件流，供外部网关感知缓存状态 |
