---
title: "AI 编译器：XLA、TVM、MLIR 与 TensorRT"
date: 2026-09-29T10:30:00+08:00
weight: 30
---

# AI 编译器：XLA、TVM、MLIR 与 TensorRT

> torch.compile 只是编译器大家庭的一支。本篇横向看四条技术路线：**XLA（框架内编译）、TVM（调度搜索）、MLIR（编译器基建）、TensorRT（部署引擎）**，以及它们对同一批问题的不同答案。

## 四条路线的定位

| 路线 | 代表 | 核心思想 | 典型用户 |
| ---- | ---- | ---- | ---- |
| 框架内编译 | XLA（TF/JAX）、Inductor | 框架图 → HLO/自定义 IR → 融合 + 代码生成 | 训练/推理一体 |
| 调度搜索 | TVM（Ansor/MetaSchedule） | 把"怎么算"与"怎么调度"解耦，自动搜索调度 | 专有硬件、算子库 |
| 编译器基建 | MLIR | 多层 IR 与 dialect 框架，造编译器用的脚手架 | 芯片厂商、新后端 |
| 部署引擎 | TensorRT / ONNX Runtime | 吃训练后的静态图，做推理极致优化 | 服务部署 |

## XLA 与 HLO

XLA（Accelerated Linear Algebra）是 TF/JAX 的编译后端，中间表示是 **HLO**（High Level Optimizer IR）——算子级的有向图，每个节点是带 shape/layout 的运算。XLA 的主要优化：**算子融合**（pointwise 链与归约合并成 kLoop/kElementwise 类融合 kernel）、布局选择、常量折叠。它与 PyTorch 栈的设计理念差异（题库 017 的核心）：**TF 的 `tf.function` 是"显式声明你要编译"，trace 出静态图**——控制流要改写成 `tf.while` 这类图原语；**`torch.compile` 是"默认保持 Python 语义，能编译多少编译多少"**。前者优化更彻底、约束更硬；后者开发体验好、上限略低。JAX 的成功证明了一条折中路线：纯函数 + 显式变换（jit/vmap/pmap），静态图但写起来像 NumPy。

## TVM：把调度变成可搜索的

TVM 的独门思路是 **计算与调度解耦**：同一份计算描述（`A[i,j] = sum(B[i,k]*C[k,j])`）可以套用不同 **schedule**（tiling 方式、循环顺序、并行策略）。早期靠专家写 schedule template；**Ansor/MetaSchedule 把它变成自动搜索**——在调度空间里枚举/学习，按目标硬件实测反馈选最优。这条路线对**碎片化硬件**最有价值：新加速卡只要有代码生成后端，就能靠搜索获得接近手写的算子，不必雇专家手写 CUDA——国内大量 NPU 生态走的就是这条路。代价是搜索时间（小时级/算子）与缓存管理。

## MLIR：编译器的编译器

MLIR 本身不编译模型，而是提供**多层 IR + 可扩展 dialect** 的基础设施：`linalg`（结构化算子）、`tosa`（算子集规范）、`func/llvm`（通往 LLVM 代码生成）……每一层做一类降低（lowering）。它的价值在"为新的硬件后端添加编译器支持"（题库 040）：芯片厂商不必从零造编译器，实现关键几层 lowering 即可复用上游优化。IREE、各大 NPU 工具链、甚至 PyTorch 的 `torch-mlir` 都建在其上。理解 MLIR 的关键词是 **pass 管理与 progressive lowering**：优化以 pass 为单位（见题库 039 的通用机制——每个 pass 图变换一次、可控可测），IR 逐层从高级语义降到机器码。

## TensorRT 与 ONNX Runtime：部署侧

**TensorRT** 是 NVIDIA 的推理引擎：吃 ONNX（或框架导出的图），做图优化（层融合、精度标定）、kernel 选择（对每层从内置实现库挑选并可 auto-tune）、显存规划。扩展机制是 **plugin**：引擎不认识的算子用 `IPluginV2DynamicExt`/`IPluginV3` 接口写自定义 kernel 挂进去——部署侧的自定义算子开发基本等于写 plugin（流程：实现接口 → 序列化配置 → builder 注册 → 校验，见题库 035/098）。**ONNX Runtime** 的定位是跨平台执行引擎：ONNX 图 + 可插拔 **execution provider**（CUDA/TensorRT/OpenVINO/各种 NPU 的 EP），同一份模型在不同后端上执行——它赢在覆盖面，TensorRT 赢在单后端深度。

**路线对比的收束**（题库 041）：TorchDynamo 代表"从 Python 动态图向上抓"，TVM/MLIR 代表"从硬件向下建"，TensorRT 代表"部署时一次性深度特化"——工业界的现实是**组合**：PyTorch 训练 → export/ONNX → TensorRT/自定义引擎部署，中间可能穿插 TVM 搜出的算子。

::: details 编译器的通病与药方（编译时间、动态 shape、控制流）

三个问题所有路线都有，只是程度不同：**编译时间过长**——TVM 搜索与 Inductor autotune 都是分钟到小时级，药方是缓存（按硬件+shape 缓存）、并行搜索、约束搜索空间；**动态 shape**——为每个 shape 特化最优但爆炸，药方是 symbolic shape（编译一族）或分桶；**控制流**——静态图表达不了数据依赖分支，药方是子图切分（控制流留在 host，线性段交给编译器）或把分支编译成算子（select/where）。理解了这三组矛盾，任何新编译器发布都能快速定位它站在哪。

:::

## 小结

- XLA/HLO 是框架内编译的标杆，`tf.function` 与 `torch.compile` 是"显式静态"与"尽力编译"两种理念的对照。
- TVM 把调度变成可搜索空间，是碎片化硬件获得算子库的捷径；MLIR 是造编译器的脚手架，新后端靠多层 lowering 复用生态。
- TensorRT/ONNX Runtime 是部署侧两极：单后端深度 vs 跨平台广度；自定义算子在 TRT 世界里 = 写 plugin。
- 所有编译器共享三组矛盾：编译时间、动态 shape、控制流——识别矛盾位置比记住 API 更长效。

## 思考题

1. JAX 代码里 `lax.scan` 为什么比 Python while 循环对 XLA 友好？
2. 你要为一款新 NPU 提供编译器支持，用 MLIR 和用 TVM 各自的工作量与收益是什么？
3. TensorRT 的 plugin 与 PyTorch 的 custom op 在"谁管反向"上的区别？

::: details 参考答案

1. `lax.scan` 是 HLO 原语：循环体是静态子图，XLA 可整体编译优化；Python while 是 host 侧控制流，只能切成多段图反复 launch，优化机会被打碎。
2. MLIR：前期投入大（实现 dialect 与多层 lowering），但优化链路可复用、上限高，适合长期产品化的自研硬件；TVM：接入快（写 codegen + 跑搜索），短期见效，但整体架构受制于 TVM 的抽象，深度定制困难。
3. TRT plugin 只管前向——推理引擎没有反向；PyTorch custom op 必须注册 autograd 公式才能参与训练（见[PyTorch 内部机制](/knowledge-planet/ai-infra/framework/pytorch-internals)篇）。

:::

## 参考资料

- XLA 官方文档，[XLA Architecture](https://openxla.org/xla/architecture)（HLO 与编译管线）
- TVM 官方文档，[MetaSchedule](https://tvm.apache.org/docs/tutorial/meta_schedule.html) 与 Ansor 论文（OSDI 2020）
- MLIR 官方文档，[Language Reference](https://mlir.llvm.org/docs/LangRef/) 与 [Pass Management](https://mlir.llvm.org/docs/PassManagement/)
- NVIDIA, [TensorRT Plugin 开发指南](https://docs.nvidia.com/deeplearning/tensorrt/latest/extend-tensorrt/custom-plugins.html)

