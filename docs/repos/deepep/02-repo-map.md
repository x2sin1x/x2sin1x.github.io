---
title: "第 2 章 仓库地图与模块职责"
weight: 20
---

# 第 2 章 仓库地图与模块职责

> 本章回答应该从哪里读 DeepEP。源码树在两代之间已经大幅重组，按文件名一一对应会误导；本章改按职责建立地图。

## 2.1 V1：Python 编排，C++ 持有状态，CUDA 执行通信

V1 仓库规模较小，入口落在 `deep_ep/buffer.py`。Python 根据进程组、设备号和唯一 ID 完成 peer 协商，然后转给 `deep_ep_cpp.Buffer`。C++ 对象管理缓冲区、通信 stream、同步计数和生命周期；`csrc/kernels/` 提供布局、intranode NVLink、internode RDMA 和低延迟 kernel。测试分别覆盖 `tests/test_intranode.py`、`test_internode.py` 与 `test_low_latency.py`。

| 路径 | 职责 | 阅读时关注 |
| --- | --- | --- |
| `deep_ep/buffer.py` | Python API、通信路径分派、handle 打包 | `get_dispatch_layout`、`dispatch`、`combine` |
| `csrc/deep_ep.hpp` | C++ runtime 接口与状态字段 | IPC、RDMA、workspace、计数器 |
| `csrc/deep_ep.cpp` | 对象生命周期、验证、内存分配、pybind | `sync`、`destroy`、kernel 调用前检查 |
| `csrc/kernels/layout.cu` | top-k 到 rank/token 布局元数据 | rank count、expert count、membership |
| `csrc/kernels/intranode.cu` | NVLink intranode dispatch/combine | channel、head、counter 与超时 |
| `csrc/kernels/internode*.cu` | 高吞吐和低延迟跨节点路径 | NVSHMEM/IBGDA、分段与 hook |

## 2.2 V2：API 对应 buffer，runtime 与 kernel 编译分层

V2.5 把代码按 buffer 类型拆分。`deep_ep/buffers/ep.py` 实现 EP API 和 `EPHandle`；`base.py` 定义共享生命周期入口；`comm/` 提供 NCCL communicator、barrier 与 stream 能力；`csrc/buffers/ep.hpp` 管理 EP 专用 C++ 状态；`csrc/kernels/ep/` 负责 kernel specialization 与 launch；更底层的 `deep_ep/include/deep_ep/impls/ep/` 才是 JIT 编译的设备端实现。

::: mermaid
flowchart TB
    U[MoE 框架 / 调用方] --> P[deep_ep.buffers.ep.EPBuffer]
    P --> B[C++ EPBuffer 与 Context]
    P --> J[deep_ep.runtime.jit]
    B --> C[NCCL communicator / Gin / memory window]
    J --> K[csrc/kernels/ep launch wrappers]
    K --> I[include/deep_ep/impls/ep device kernels]
    B --> W[对称 buffer 与 workspace]
    K --> W
:::

依赖方向说明：Python 暴露易用 API 和 PyTorch 对象生命周期；C++ 对接 NCCL、CUDA 和 buffer；JIT wrapper 将运行时形状/并行参数转成编译模板参数；device header 实现数据移动。这个分层是源码结构可见的事实；把它概括成“把通信资源初始化与 kernel specialization 解耦”属于机制解释。

## 2.3 入口、构建和测试

Python 导入 `deep_ep` 时，`__init__.py` 先验证 NCCL 动态库，再调用 `_C.init_jit(...)`，之后导出 `EPBuffer`、`EPHandle`、各类 Buffer 与事件类型（`deep_ep/__init__.py:1-64`）。因此 import 不只是名称导出，也会触发扩展加载和 JIT runtime 初始化。

包初始化代码的执行顺序如下：

```python
# Run initialization
check_nccl_so()
init_jit()

# Import APIs after initialization
from . import comm
from .comm import destroy_all_managed_nccl_comm, get_physical_domain_size, get_logical_domain_size
from .buffers.allocator import BufferAllocator
from .buffers.base import BufferBase
from .buffers.ep import EPBuffer, EPHandle
from .buffers.engram import EngramBuffer
from .buffers.bucket import BucketBuffer, BucketSession
from .buffers.pp import PPBuffer
from .utils.event import EventOverlap, EventHandle
```

构建入口由 `setup.py` / CMake 和 `install.sh` 等构成。当前 README 说明安装会构建 host C++ 扩展，而 GPU kernel 运行时由 DeepJIT 编译；这是区分“安装时构建”和“调用时构建”的关键。本文不执行 DeepEP 安装或 GPU 测试，因为当前环境的任务只是源码分析，且测试需要特定 CUDA/NCCL/GPU 集群。

## 本章收束

- V1 的代码入口和主要状态集中在 `Buffer` 与 C++ runtime，kernel 按通信情形拆文件。
- V2 按 buffer 类型和层次拆分，公共 API、NCCL context、JIT launch 与 device kernel 可分别追踪。
- 第 3 章先解释 V1 初始化，因为它明确展示了资源如何跨 Python、C++ 和节点初始化。
