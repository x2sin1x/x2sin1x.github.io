---
title: DeepEP
weight: 10
---

# DeepEP 源码解读：从 NVSHMEM 双路径到 NCCL Gin

> 本书把 DeepEP V1 与 EPv2 放在一条演进线上解释：V1 如何用 NVLink IPC、NVSHMEM 和两种通信模式完成专家分发与回收；V2 如何围绕 NCCL Gin、DeepJIT 和统一的 `EPBuffer` 重组执行路径。分析范围覆盖 V1 `v1.2.1` 与当前仓库 `main` 的 V2.5 快照，两代实现始终分开追踪。

## 版本快照

| 字段 | V1 | V2.5 |
| --- | --- | --- |
| 仓库 | [deepseek-ai/DeepEP](https://github.com/deepseek-ai/DeepEP) | [deepseek-ai/DeepEP](https://github.com/deepseek-ai/DeepEP) |
| 版本锚点 | `v1.2.1` | `main` |
| commit | [`9af0e0d0e74f3577af1979c9b9e1ac2cad0104ee`](https://github.com/deepseek-ai/DeepEP/tree/9af0e0d0e74f3577af1979c9b9e1ac2cad0104ee) | [`93eb6eb238127e96c6d7a4a625a6dad158348509`](https://github.com/deepseek-ai/DeepEP/tree/93eb6eb238127e96c6d7a4a625a6dad158348509) |
| 提交时间 | 2025-09-15 | 2026-09-30 |
| 核对日期 | 2026-10-13 | 2026-10-13 |
| 分析范围 | Python `Buffer`、C++ runtime、CUDA kernels 与测试 | `EPBuffer`、NCCL/Gin context、DeepJIT kernels、相关测试与模块生命周期 |

> V2.5 的 README 声明 V1 已完整移除，包括旧 API 与 NVSHMEM 后端。因此本书不从 V2.5 源码倒推 V1 行为：凡涉及旧路径，均明确使用 `v1.2.1` 快照；凡涉及当前 API，均使用 V2.5 快照。

## 主要源码锚点

- V1：[`deep_ep/buffer.py`](https://github.com/deepseek-ai/DeepEP/blob/9af0e0d0e74f3577af1979c9b9e1ac2cad0104ee/deep_ep/buffer.py)、[`csrc/deep_ep.cpp`](https://github.com/deepseek-ai/DeepEP/blob/9af0e0d0e74f3577af1979c9b9e1ac2cad0104ee/csrc/deep_ep.cpp)、[`csrc/kernels/intranode.cu`](https://github.com/deepseek-ai/DeepEP/blob/9af0e0d0e74f3577af1979c9b9e1ac2cad0104ee/csrc/kernels/intranode.cu)。
- V2：[`deep_ep/buffers/ep.py`](https://github.com/deepseek-ai/DeepEP/blob/93eb6eb238127e96c6d7a4a625a6dad158348509/deep_ep/buffers/ep.py)、[`csrc/buffers/ep.hpp`](https://github.com/deepseek-ai/DeepEP/blob/93eb6eb238127e96c6d7a4a625a6dad158348509/csrc/buffers/ep.hpp)、[`csrc/kernels/comm/context.cpp`](https://github.com/deepseek-ai/DeepEP/blob/93eb6eb238127e96c6d7a4a625a6dad158348509/csrc/kernels/comm/context.cpp)、[`csrc/kernels/ep/dispatch.hpp`](https://github.com/deepseek-ai/DeepEP/blob/93eb6eb238127e96c6d7a4a625a6dad158348509/csrc/kernels/ep/dispatch.hpp)。
- V2 初次公开提交：[`b306af06afd412c88e51e71802951606e40b7358`](https://github.com/deepseek-ai/DeepEP/commit/b306af06afd412c88e51e71802951606e40b7358)；V2.5 发布提交：[`def865146e95aa9ea223e277c0a8a4c6b81e5ac7`](https://github.com/deepseek-ai/DeepEP/commit/def865146e95aa9ea223e277c0a8a4c6b81e5ac7)。

## 全书要回答的问题

- 一份 token 的 top-k 路由结果如何变成跨 rank 的发送计划、专家输入与反向 combine？
- V1 的 normal / low-latency 双 API 与 V2 的统一 EP API，分别把哪些工作交给调用者和运行时？
- NVLink、RDMA、同步计数、布局元数据和异步事件由哪些层共同管理？
- V2 通过 NCCL Gin 与 DeepJIT 重构后，哪些机制变简单，哪些部署条件与生命周期约束仍由调用方承担？

## 目录

### 第一部分：把两代实现放在同一张图上

- [01 定位与版本边界](/repos/deepep/01-overview)
- [02 仓库地图与模块职责](/repos/deepep/02-repo-map)
- [03 V1：Buffer 初始化与通信域建立](/repos/deepep/03-v1-buffer-lifecycle)
- [04 V1：布局、dispatch 与 combine](/repos/deepep/04-v1-dispatch-combine)

### 第二部分：V2 的执行模型

- [05 V2：Python API、C++ 扩展与 DeepJIT](/repos/deepep/05-v2-runtime)
- [06 V2：NCCL Gin 与对称内存](/repos/deepep/06-v2-transport)
- [07 V2：dispatch 如何构造专家输入](/repos/deepep/07-v2-dispatch)
- [08 V2：combine、句柄与异步重叠](/repos/deepep/08-v2-combine-events)
- [09 V2：容量、布局与通信资源](/repos/deepep/09-v2-memory-layout)
- [10 V2：EP 之外的 Buffer 与扩展能力](/repos/deepep/10-v2-other-buffers)
- [11 构建、测试与运行边界](/repos/deepep/11-build-tests)

### 附录

- [附录 A：按目标阅读](/repos/deepep/appendix-reading)
- [附录 B：核心符号速查](/repos/deepep/appendix-symbols)
- [附录 C：术语表](/repos/deepep/appendix-glossary)

## 阅读主线

::: mermaid
flowchart LR
    A[MoE 路由结果] --> B[V1 layout 与 rank 分组]
    B --> C[V1 dispatch / expert compute / combine]
    C --> D[版本边界：V1 被移除]
    D --> E[V2 EPBuffer 与 DeepJIT]
    E --> F[NCCL Gin 通信与对称窗口]
    F --> G[dispatch / 扩展布局 / expert compute]
    G --> H[combine / EventOverlap]
:::

V1 与 V2 的链路在章节中分别展开。图中的连接表达的是主题演进，不表示跨版本共享同一运行时或数据结构。

## References

- [DeepEP 仓库](https://github.com/deepseek-ai/DeepEP)
- [V1.2.1 固定快照](https://github.com/deepseek-ai/DeepEP/tree/9af0e0d0e74f3577af1979c9b9e1ac2cad0104ee)
- [EPv2 初次公开提交](https://github.com/deepseek-ai/DeepEP/commit/b306af06afd412c88e51e71802951606e40b7358)
- [V2.5 发布提交](https://github.com/deepseek-ai/DeepEP/commit/def865146e95aa9ea223e277c0a8a4c6b81e5ac7)
- [当前 V2.5 分析快照](https://github.com/deepseek-ai/DeepEP/tree/93eb6eb238127e96c6d7a4a625a6dad158348509)
