---
title: "torch.compile：Dynamo → Inductor → Triton"
date: 2026-09-29T10:30:00+08:00
weight: 20
---

# torch.compile：Dynamo → Inductor → Triton

> 一行 `model = torch.compile(model)`，平均 1.3–2 倍加速。它背后是 PyTorch 2.0 以来最重要的工程栈：**Dynamo 抓图，AOTAutograd 做微分，Inductor 编译，Triton 出 kernel**。

## 四级流水：从 Python 到 Triton

1. **TorchDynamo（抓图）**：用 CPython 的 frame evaluation API 在字节码层面拦截 Python 函数，把 PyTorch 操作段"抽"成 FX Graph。它解决了 TorchScript trace/script 的老大难：动态控制流不炸、Python 语义保留——遇到解释不了的部分就**图断裂（graph break）**，把那段退回 eager。
2. **AOTAutograd（预微分）**：在编译期对抓到的图做一次联合前向-反向追踪，生成反向图——这样编译器能对前向+反向整体做优化，而不是只优化前向。
3. **Inductor（编译）**：PyTorch 2.x 的默认编译器后端。对图做归一化与模式匹配融合，然后：GPU 上生成 **Triton** kernel（pointwise/reduction 融合矩阵乘外壳），CPU 上生成 C++。它内置了自动调优（对生成的 Triton kernel 做配置搜索，结果缓存）。
4. **Triton（出 kernel）**：tile 抽象的 kernel 语言（见[算子优化](/knowledge-planet/ai-infra/hpc/operator-optimization)篇对比），融合后的 pointwise 链、reduction、softmmu 类 kernel 都由它生成。

一次编译的完整形态：`torch.compile(model, mode="max-autotune")` 会额外尝试把 GEMM 走 CUTLASS/Triton 模板调优——速度上限更高，编译时间也更长。

## 模式对比：jit.trace / jit.script / torch.compile

| 维度 | `torch.jit.trace` | `torch.jit.script` | `torch.compile` |
| ---- | ---- | ---- | ---- |
| 抓图方式 | 跑一遍记录算子 | 解析 Python 源码子集 | 字节码拦截 |
| 控制流 | 只固化当次路径 | 支持（要写 TorchScript 方言） | 原生 Python 语义 |
| 动态 shape | 炸（固化 shape） | 手动标注 | 支持（symbolic shape/guard） |
| 优化深度 | 少量 | 少量 | 图级融合 + kernel 生成 |

结论：新项目一律 `torch.compile`；jit 系列只剩维护旧代码的价值。

## Guard 与重编译：编译时间的账

Dynamo 对每个图生成 **guard**（对输入 shape、dtype、设备、Python 值的断言）；调用时先查 guard，命中就走缓存的编译产物，miss 就重编译。由此得到三条工程法则：

- **shape 多变 = 编译次数多**：prefill 的任意序列长度会触发大量重编译。对策：`torch.compile(dynamic=True)`（符号 shape，一个 kernel 覆盖一族 shape）、输入 padding 到固定档位、或限制 `cache_size_limit`。
- **首轮编译慢是常态**：编译分钟级，服务上线要预热（[推理引擎](/knowledge-planet/ai-infra/inference/engine-landscape)篇的 warmup 一节）。
- **graph break 会稀释收益**：`torch._dynamo.explain()` 报告断裂点；常见元凶是数据依赖的 Python 控制流、打印/随机数、`.item()` 之类同步操作。

## mode 与推理优化

- `mode="reduce-overhead"`：叠加 **CUDA Graph**（见[CUDA 编程](/knowledge-planet/ai-infra/hpc/cuda-programming)篇）——静态 shape 下的 decode 场景，launch 开销直接消失，是 vLLM 类引擎 v0 compile 路线的同款思路。
- `mode="max-autotune"`：kernel 级模板搜索，训练大模型追求最后几个百分点时用。
- 推理专用：`torch.compile` 与 `torch.inference_mode()` 组合，AOTAutograd 跳过反向图，编译更快。

::: details 量化与 compile 怎么配合

`torch.ao` 的 PTQ 流程（见[量化基础](/knowledge-planet/ai-infra/quantization/quantization-basics)篇）产生的量化图可以直接进 compile：Inductor 认识 quantize/dequantize 模式并做**量化算子融合**（quant+conv+relu 合一个 kernel）。INT8/FP8 推理在 compile 栈下的另一条路是 `torch.export` 导出静态图后交给 AOTInductor/Runtime——脱离 Python 进程运行，是部署侧的编译终点。

:::

## 小结

- 编译栈四级流水：Dynamo 抓图（字节码级、可回退）→ AOTAutograd 预微分 → Inductor 图编译 → Triton kernel 生成。
- jit.trace/script 的历史问题（控制流、动态 shape）被 compile 的 guard 机制系统性地解决。
- guard/重编译决定了 compile 的工程形态：shape 分桶、预热、graph break 定位是日常功课。
- `reduce-overhead`（CUDA Graph）与 `max-autotune`（kernel 搜索）是两个最常用的加速档位。

## 思考题

1. 训练脚本里 loss 有 `if loss.item() > 100: ...`：compile 后会发生什么？怎么改？
2. 为什么 `dynamic=True` 的 kernel 通常比静态 shape 编译慢 10–20%？
3. reduce-overhead 模式在哪个负载下反而劣化？

::: details 参考答案

1. `.item()` 触发 GPU→CPU 同步且结果参与 Python 控制流 → graph break（或为两种路径各编译一份）。改：把阈值逻辑移出编译区，或用 tensor 比较构造 mask 代替 Python 分支。
2. 符号 shape 让 tile 大小、循环边界在运行期确定：编译器无法做形状特化的常量折叠与最优 tile 选择，mask/边界处理也多出指令。
3. 动态 shape 或频繁 graph break 的负载：CUDA Graph capture 需要静态 shape，shape 一变就 re-capture，开销反超收益；另一个是显存极紧的场景（capture 需要静态内存池）。

:::

## 参考资料

- PyTorch, [Introduction to torch.compile](https://pytorch.org/tutorials/intermediate/torch_compile_tutorial.html)（官方教程）
- PyTorch 官方博客，[Inside the PyTorch 2.0 Compiler](https://dev-discuss.pytorch.org/t/inside-the-pytorch-2-0-compiler-episode-1/1000) 系列（Dynamo/AOTAutograd/Inductor 逐级拆解）
- Anyscale 博客，[Producing PyTorch 2.0 performance with torch.compile](https://www.anyscale.com/blog/accelerating-large-language-models-with-pytorch-2-and-flash-attention)（工程实测）

