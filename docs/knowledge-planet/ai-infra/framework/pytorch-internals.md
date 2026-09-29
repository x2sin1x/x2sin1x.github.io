---
title: "PyTorch 内部机制"
date: 2026-09-29T10:30:00+08:00
weight: 10
---

# PyTorch 内部机制

> 会用 PyTorch 与会调 PyTorch 之间隔着一层内部机制。本篇讲五个地基：autograd、dispatch、Module、CachingAllocator 与混合精度——分布式 hang、显存碎片、kernel launch 失败这些疑难杂症的病根都在这里。

## Autograd：动态图是怎么反向的

前向时每个算子都返回一个持有 `grad_fn` 的张量，`grad_fn` 串成一条从输出回溯到叶子的链；`loss.backward()` 从根出发按**拓扑序**执行各节点的 `grad_fn`，把梯度经 `AccumulateGrad` 累加进叶子的 `.grad`。三个推论：

- **动态图**：图在前向时按代码执行路径即时构建，控制流（if/while）天然支持——这是与静态图（TF1、TensorRT）的本质区别。
- **`.grad` 是累加而非覆盖**：所以每个 step 前要 `optimizer.zero_grad()`；梯度累积（见[数据并行](/knowledge-planet/ai-infra/parallelism/data-parallelism)篇）正是"故意多次 backward 再统一 step"。
- **梯度检查点**：前向丢弃中间激活、反向时重算——用约 30% 的重计算换大显存（[显存优化](/knowledge-planet/ai-infra/training/memory-optimization)篇细账）。

## Dispatch：一次 `a.add(b)` 的旅程

PyTorch 是一个多后端系统（CPU/CUDA/XLA/各种自定义加速器），dispatch 层负责把一次张量操作路由到正确的实现：

```
Tensor.add → dispatcher → (设备/布局/dtype 等key) → CUDA kernel 注册的实现
```

理解 dispatch 的三个实用价值：**hook 机制**挂在 dispatch/autograd 的关键节点上（前向 hook 看输入输出、反向 hook 看梯度、`register_buffer` 之外的 profiling 装点都靠它）；**扩展算子**（`torch.library.custom_op` 注册自定义 op，让 autograd/profiler/compile 都认得它）；**读懂报错**——"no kernel is registered for this dtype" 这类错误说的就是 dispatch 表查空了。

## Module：`__call__` 与 forward 的区别

`model(x)` 走的是 `Module.__call__`（实际是 `_call_impl`），forward 只是它调用的一步。区别在于 `__call__` 会在前后插入 **hook**、处理 `_backward_hooks`、编译标记等。所以：直接调 `model.forward(x)` 会**静默跳过所有 hook**——测试代码、profiling 场景下最经典的 bug 来源。

## CachingAllocator：显存为什么"只增不减"

PyTorch 不每次向驱动要显存，而是自持一个内存池：释放的显存块回到池里按 size 分裂/合并复用，`torch.cuda.memory_reserved()` 与实际使用 `memory_allocated()` 之间的差就是池化余量。由此推出全部常见现象：

- **显存只增不减是特性不是泄漏**：池子按历史峰值驻留；真泄漏的判据是 `memory_allocated` 持续单调上涨。
- **碎片**：长短生命周期张量交错分配时，池里剩的都是用不上的小洞——大 batch 训练里碎片可占 10–20%。缓解：`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`（按段虚拟地址管理，碎片显著减少）、或开训前用 `torch.cuda.empty_cache()` 让池子归零（注意它本身不省已分配显存，只是把缓存还给驱动）。
- **OOM 排查顺序**：`memory_allocated`（真用了）→ `memory_reserved`（池持有）→ 碎片（allocated 低但 reserved 高且 OOM）。

## 混合精度：AMP 的账

`torch.cuda.amp` 用 BF16/FP16 做前向与反向（快在算力与带宽双收益），权重主副本保持 FP32。FP16 路线需要 **GradScaler**：loss 乘大系数放大梯度、避免下溢，优化器 step 前再 unscale 并跳过 inf/nan 的 step。BF16 与 FP32 同指数位，天然无下溢问题——**A100 以后 BF16 是默认选择，GradScaler 可省**。混合精度的数值稳定性细节（loss scaling 在分布式下的处理）见[数据并行](/knowledge-planet/ai-infra/parallelism/data-parallelism)篇。

::: details 深入一点：自定义 CUDA 算子怎么接进这套体系

三步：① 写 CUDA kernel 并编译（`torch.utils.cpp_extension` 或独立构建）；② 用 `torch.library.custom_op` 注册为 PyTorch 算子，声明 schema（dtype/设备）；③ 注册 autograd 公式（`register_autograd`：前向调 kernel、反向再写一个 kernel 或复用 autograd 可分解的操作）。做完这三步，autograd、profiler、torch.compile 都把这个算子当"自己人"。完整 worked example 见[算子优化](/knowledge-planet/ai-infra/hpc/operator-optimization)篇与题库 004。

:::

## 小结

- autograd 是动态构建的计算图，`.grad` 累加、检查点重算都是它的直接推论。
- dispatch 路由一切操作，hook 与自定义算子扩展都挂在它上面；`__call__` 才是完整入口，绕过它 hook 失效。
- CachingAllocator 解释"显存只增不减"与碎片；`expandable_segments` 是现代默认解。
- BF16 时代 AMP 的核心复杂度（loss scaling）已在退场，但数值账仍然要会算。

## 思考题

1. 训练中 `memory_allocated` 稳定但每 epoch 上涨一次后回落，`reserved` 持续涨：诊断是什么？动作是什么？
2. 为什么 `find_unused_parameters=True` 依赖 autograd 图，而它拖慢训练？
3. grad hook 与 forward hook 各在 dispatch 链的哪一段？想监控"每个 Module 的输入均值"该用哪个？

::: details 参考答案

1. 典型碎片 + 池驻留：数据长度变化导致不同 size 的块交错。动作：开 `expandable_segments`、把变长 tensor 的分配改为预分配复用，必要时 epoch 边界 `empty_cache()`。
2. 它在每个 backward 后对图做 unused 检测，并把"有未用参数"的标记经 allreduce 广播（挂起图遍历），通信与计算双开销；根因是 DDP 默认假设所有参数都参与反向（见[数据并行]篇）。
3. forward hook 在 dispatch 完成后、模块输出处触发；grad hook 在 autograd 节点（grad_fn）上。监控输入均值用 forward hook——拿的是真实输入张量。

:::

## 参考资料

- PyTorch, [A Gentle Introduction to torch.autograd](https://pytorch.org/tutorials/beginner/blitz/autograd_tutorial.html) 与 [CUDA 内存管理文档](https://pytorch.org/docs/stable/notes/cuda.html#memory-management)
- PyTorch, [The PyTorch Dispatcher](https://pytorch.org/blog/how-dispatch-works/) 与 `torch.library` 文档
- PyTorch, [Expanding Segments allocator](https://pytorch.org/docs/stable/notes/cuda.html#optimizing-memory-usage-with-pytorch-cuda-alloc-conf)（`PYTORCH_CUDA_ALLOC_CONF` 说明）

