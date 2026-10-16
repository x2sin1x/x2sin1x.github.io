---
title: "附录 B：核心符号速查"
weight: 130
---

# 附录 B：核心符号速查

| 符号 | 版本 | 职责 | 定义位置 | 章节 |
| --- | --- | --- | --- | --- |
| `Buffer` | V1 | Python 用户 API 与通信路径选择 | `deep_ep/buffer.py` | [03](/repos/deepep/03-v1-buffer-lifecycle)、[04](/repos/deepep/04-v1-dispatch-combine) |
| `deep_ep::Buffer` | V1 | 资源持有、IPC/NVSHMEM 生命周期与 kernel 接口 | `csrc/deep_ep.hpp`, `csrc/deep_ep.cpp` | [03](/repos/deepep/03-v1-buffer-lifecycle) |
| `get_dispatch_layout` | V1 | 从 top-k 生成 rank/expert 计数与 membership | `deep_ep/buffer.py`, `csrc/kernels/layout.cu` | [04](/repos/deepep/04-v1-dispatch-combine) |
| `EPBuffer` | V2 | EP 主 API、容量参数、handle 与 stream 控制 | `deep_ep/buffers/ep.py` | [05](/repos/deepep/05-v2-runtime) 至 [09](/repos/deepep/09-v2-memory-layout) |
| `EPHandle` | V2 | 保存 dispatch 布局与 combine 所需元数据 | `deep_ep/buffers/ep.py` | [07](/repos/deepep/07-v2-dispatch)、[08](/repos/deepep/08-v2-combine-events) |
| `BufferBase` | V2 | 各专用 buffer 的共同生命周期入口 | `deep_ep/buffers/base.py` | [10](/repos/deepep/10-v2-other-buffers) |
| `Context` | V2 | NCCL device communicator、domain 与 memory window | `csrc/kernels/comm/api.hpp`, `context.cpp` | [06](/repos/deepep/06-v2-transport) |
| `launch_dispatch` | V2 | dispatch specialization 与 kernel launch | `csrc/kernels/ep/dispatch.hpp` | [05](/repos/deepep/05-v2-runtime)、[07](/repos/deepep/07-v2-dispatch) |
| `launch_combine` | V2 | combine specialization 与 kernel launch | `csrc/kernels/ep/combine.hpp` | [05](/repos/deepep/05-v2-runtime)、[08](/repos/deepep/08-v2-combine-events) |
| `EventOverlap` | V2 | 封装 CUDA event、Tensor 生命周期和延后回调 | `deep_ep/utils/event.py` | [08](/repos/deepep/08-v2-combine-events) |
| `BufferAllocator` | V2.5 | 规划对称通信 storage 上的张量布局 | `deep_ep/buffers/allocator.py` | [09](/repos/deepep/09-v2-memory-layout)、[10](/repos/deepep/10-v2-other-buffers) |
