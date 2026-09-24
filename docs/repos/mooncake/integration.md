---
title: Python 绑定与推理引擎集成
weight: 80
---

# Python 绑定与推理引擎集成

> 本章回答：vLLM、SGLang 这些推理引擎如何"挂上"Mooncake——pybind 绑定暴露了什么、PD 分离的数据如何流动。这是 Mooncake 生态价值的落地层。

## 绑定层的两条通道

`mooncake-integration/` 用 pybind11 把两个 C++ 世界暴露给 Python，各自对应一条消费通道：

| 模块 | 绑定入口 | 消费者 |
| --- | --- | --- |
| Transfer Engine | `transfer_engine_py.cpp` | PD 分离连接器（KVCache 跨节点直传） |
| Store | `store_py.cpp` | KVCache 池（跨实例共享缓存） |

TE 绑定暴露与 C++ 同构的 API（`mooncake-integration/transfer_engine/transfer_engine_py.cpp:1526` 起）：

```cpp
.def("initialize", &TransferEnginePy::initialize)
.def("register_memory", &TransferEnginePy::registerMemory, ...)
.def("batch_transfer_async_write", &TransferEnginePy::batchTransferAsyncWrite, ...)
.def("batch_transfer_async_read", &TransferEnginePy::batchTransferAsyncRead, ...)
.def("get_batch_transfer_status", &TransferEnginePy::getBatchTransferStatus)
```

Store 绑定则包装成 `MooncakeDistributedStore` 类（`mooncake-integration/store/store_py.cpp:2376`），除 `get`/`put` 基础方法外，还提供张量语义的高层 API（`store_py.cpp:2657–2677`）：

```cpp
.def("get_tensor", &MooncakeStorePyWrapper::get_tensor, py::arg("key"), ...)
.def("put_tensor", &MooncakeStorePyWrapper::put_tensor, py::arg("key"), ...)
.def("batch_put_tensor", ...)
```

Python 层在此基础上叠加异步封装（`python/mooncake/async_store.py:7` 的 `MooncakeDistributedStoreAsync`）。

## PD 分离：发布/订阅张量 API

PD 分离场景下，Prefill 实例产出 KVCache，Decode 实例消费。Store 绑定为此提供了 pub/sub 风格的张量接口（`store_py.cpp:2696` 起）：

```cpp
.def("pub_tensor", &MooncakeStorePyWrapper::pub_tensor, py::arg("key"), ...)
```

对应实现类中的 `upsert_pub_tensor` / `batch_pub_tensor`（`store_py.cpp:1882–1973`），并有 `pub_tensor_with_tp` 处理张量并行的分片聚合。数据流：

::: mermaid
sequenceDiagram
    participant P as Prefill 实例（vLLM）
    participant S as Mooncake Store
    participant D as Decode 实例（vLLM）
    P->>S: pub_tensor(key, kv_tensor)
    S->>S: PutStart → 副本写入 → PutEnd
    D->>S: 查询/订阅 key
    S-->>D: 副本描述符
    D->>P: TransferRead（TE 直读，不经 Master）
:::

## 上游集成在哪里

一个容易误解的点：**vLLM / SGLang 的连接器代码不在 Mooncake 仓库里**，而在各上游仓库（它们 import `mooncake` Python 包）。Mooncake 仓库提供三样东西：绑定层 API、官方设计文档（`docs/source/design/`）与集成指南（`docs/source/deployment/`）。README「Updates」记录了主要集成点：vLLM 官方的 `MooncakeStoreConnector` 与 TransferEngine KV Connector、SGLang 的分层缓存后端与 EPD 分离、TensorRT-LLM 与 NIXL 的 TE 后端插件等。

集成层的加速器适配（CUDA/ROCm/Ascend 等）体现在 `device/` 与 allocator 相关文件（如 `ascend_allocator.h`、`mooncake-integration/allocator.py`），使绑定可以在不同硬件上分配可注册的 buffer。

## 失败边界

- Python 侧的 `batch_transfer_async_*` 返回句柄，调用方必须自行 `get_batch_transfer_status` 轮询；TE 的完成语义（"RDMA 成功指已入通知队列而非远端送达"）在 C++ 头文件注释中有明示（`transfer_engine.h` 中 `sendNotifyByID` 的注释）。
- 张量 API 假设调用方遵守"写后发布"的顺序；无版本冲突检测的部分依赖使用约定。

## 收束

1. 集成 = 两条绑定通道（TE 用于 PD 直传，Store 用于缓存池），连接器在上游仓库。
2. `pub_tensor`/`get_tensor` 把 KVCache 传输包装成张量语义，TP 分片由 `with_tp` 变体处理。
3. 绑定层不做任何数据搬运决策——协议路由与设备选择仍属于[第 4 章](/repos/mooncake/te-transfer)的 TE 内核。
