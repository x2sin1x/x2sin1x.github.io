---
title: "CUDA 编程模型"
date: 2026-09-29T10:30:00+08:00
weight: 10
---

# CUDA 编程模型

> [芯片架构](/knowledge-planet/ai-infra/hardware/chip-architecture)篇讲了硬件有什么，本篇讲怎么指挥它：CUDA 的线程层次、内存层次与同步机制，是读懂和写出一切高性能 kernel 的地基。

## 线程层次：Grid → Block → Warp → Thread

一次 CUDA kernel 启动会派出一个 **grid**，grid 由若干 **block** 组成，block 内是若干线程（硬件上再划成 32 线程的 warp 锁步执行）。两级层次对应两级资源分配：

- **block 是资源分配单位**：一个 block 整体分到一个 SM 上（运行期间不再拆开），占用该 SM 的一份 shared memory 和寄存器配额。
- **warp 是调度单位**：SM 的 warp 调度器每 clock 从就绪 warp 里挑一个发射指令。

这直接解释了两个最基本的 kernel 设计问题：block 数量要远大于 SM 数量（让调度器随时有活干）；每个 block 的线程数取 128–1024（必须能整除 32，且不要大到一个 block 就吃光 SM 资源）。

## 内存层次：问题几乎总是"数据从哪来"

| 存储 | 容量/卡 | 延迟 | 谁可见 |
| ---- | ---- | ---- | ---- |
| 寄存器 | 每 SM 256 KB 量级 | 0 clock | 单线程 |
| shared memory | 每 SM 228 KB（Hopper） | ~30 clock | block 内共享 |
| L2 | 50 MB | ~200 clock | 全卡 |
| HBM | 80–180 GB | ~400+ clock | 全卡 |

寄存器与 shared memory 是程序员真正能调度的资源，核心结论只有一条：**能进 shared memory 的复用数据就别反复去 HBM 拿**。经典例子是 tiled 矩阵乘：把 $A$、$B$ 切成 tile 装入 shared memory，每个 tile 被重复使用 $t$ 次，HBM 流量降为原来的约 $1/t$，运算强度随之提高 $t$ 倍——这就是为什么手写 tiled GEMM 能比 naive 版快几十倍，也是 CUTLASS/Triton 自动帮你做的事。

两个必知的 shared memory 陷阱：

- **Bank conflict**：shared memory 物理上分 32 个 bank，同 warp 的线程若有两个以上访问同一 bank 的不同地址，访问串行化（广播同一地址例外）。矩阵按列访问天然冲突，靠 padding 一列绕开。
- **访存合并（coalescing）**：warp 的 32 个线程访问连续地址才合成一次 HBM 传输；跨步访问把一次传输拆成 32 次，带宽利用率掉 32 倍。

## 同步与流：stream/event 才是并发的主战场

- **block 内同步**用 `__syncthreads()`；跨 block 只能靠 kernel 边界（或 cooperative groups，见下）。
- **stream** 是 GPU 上的任务队列，不同 stream 的 kernel 可以并发。多 stream 的典型用法：一个 stream 跑计算，另一个 stream 同时做 H2D 拷贝或通信（推理引擎的多 stream、框架的通信 stream 都是这个模式）。
- **event** 是 stream 中的标记点，用于计时与跨 stream 依赖。同步语义要记牢：`cudaStreamSynchronize` 阻塞 CPU 等整条 stream，`cudaDeviceSynchronize` 等全部——滥用会把并发退回串行。
- **CUDA Graph**：把一串 kernel 启动及依赖关系录制（capture）成一张图，之后一次 launch 重放。收益来自把成百上千次 kernel launch 的 CPU 开销（每次约 5–10 µs）压缩成一次图重放。**约束是图是静态的**：shape 不能变，所以动态 shape 场景（不同 batch/seq len）要么按 shape 分桶各录一张图，要么放弃（见[算子优化](/knowledge-planet/ai-infra/hpc/operator-optimization)篇的动态 shape 困境）。推理引擎的 decode 阶段 shape 稳定，是 CUDA Graph 的最佳舞台。

::: details 深入一点：GPU 藏着多少并发

以 H100 为例：132 个 SM × 每 SM 64 个 warp 槽位 = 8448 个 warp 可驻留。每个 warp 32 线程 → 最多 27 万线程同时在片上。**这么大的并发不是为了"算得快"，而是为了把访存延迟藏起来**：一个 warp 等 HBM 时调度器立刻切到别的 warp。由此推出 occupancy 的直觉：每个 warp 占的寄存器越多，SM 能驻留的 warp 越少，藏延迟的能力越弱——register 压力与 occupancy 的权衡见下一篇。

:::

## 资源管理：CUDA 的错误处理与 RAII

CUDA 的错误分两级：**launch 错误**（同步返回，如配置非法）与**执行错误**（异步，在下次同步时才爆出来）。工程惯例：

1. 每个 CUDA 调用包一层检查宏（`cudaGetLastError()` + `cudaPeekAtLastError()`），异步错误用同步点定位到"最近一次同步以来的某个 kernel"。
2. device 内存、stream、event、graph 都是 C 资源——用 RAII 封装（析构时 `cudaFree`/`cudaStreamDestroy`），异常路径才不泄漏；host pinned 内存用 `cudaHostAlloc` 并同样封装。
3. 多 GPU 场景记得 `cudaSetDevice` 与 device 上下文绑定，一切句柄都是 per-device 的。

## 小结

- 线程层次（grid/block/warp）对应资源分配与调度两级现实：block 吃 SM 资源，warp 是调度单位。
- 内存层次的工程核心是把复用搬进 shared memory：tiled 化、coalescing、避开 bank conflict。
- stream/event 组织并发，CUDA Graph 把 launch 开销一次付清但 shape 必须静态。
- 资源管理靠 RAII 与分层错误检查，异步错误要在同步点定位。

## 思考题

1. 一个 kernel 用 64 KB shared memory/block、每线程 40 个寄存器：H100 上一个 SM 最多驻留几个 block？大概多少 occupancy？
2. 你要给 decode 阶段加 CUDA Graph，但 batch size 随负载变化（1–64）。设计一个可行的 capture 方案。
3. 为什么 `__syncthreads()` 放在"部分线程可能提前 return"的代码后面会死锁？正确的写法是什么？

::: details 参考答案

1. 228 KB / 64 KB = 3 个 block。寄存器：65536 寄存器/SM ÷ 40 ≈ 1638 线程 ≈ 51 warp，但 3 block ×（如 256 线程）= 24 warp——瓶颈在 shared memory，occupancy ≈ 24/64 = 37%。想提高就得减 shared memory 用量或换小 block。
2. 按 batch 桶分图：为 {1, 2, 4, …, 64} 各 capture 一张图（推理时 padding 到桶边界），或用 Graph 的条件节点/动态参数更新（CUDA 12.4+ 的 graph update）改张量指针而保留拓扑。代价是显存×桶数，这正是 vLLM 类引擎限制并发桶的原因。
3. `__syncthreads()` 要求 block 内所有线程到齐；有线程 return 了就永远凑不齐。正确写法：把条件收敛成"所有线程都算完条件，统一 return"，或把同步移到任何 return 路径之前。

:::

## 参考资料

- NVIDIA, [CUDA C++ Programming Guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)（官方文档，执行模型与 Graph 章节）
- NVIDIA, [Hopper Tensor Core Features](https://developer.nvidia.com/blog/hopper-features/)（架构特性）
- Xiao & Feng, [CUDA-Graphs 相关优化实践](https://pytorch.org/blog/cuda-graphs/)（PyTorch 官方博客）

