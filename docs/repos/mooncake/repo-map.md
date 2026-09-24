---
title: 仓库地图与模块边界
weight: 20
---

# 仓库地图与模块边界

> 本章回答：这个 monorepo 里有什么、每个模块一句话职责是什么、依赖方向指向哪里。读它可以在进入源码细节前建立方位感。

## 顶层目录速览

对 commit `056f67a` 快照统计（排除 vendored/generated 文件后约 2200 个文件，C++ 约 40 万行、Python 约 9 万行——口径：仅统计目录内源码文件）：

| 目录 | 职责 | 备注 |
| --- | --- | --- |
| `mooncake-transfer-engine/` | 传输引擎本体：拓扑、元数据、20+ 种 transport | 核心库，见[第 3、4 章](/repos/mooncake/te-topology) |
| `mooncake-store/` | 分布式 KVCache：Master + 客户端 + 存储后端 | 核心库，见[第 5–7 章](/repos/mooncake/store-client) |
| `mooncake-ep/` | 弹性 MoE / 专家并行相关组件 | 本文不深入，标记为未覆盖 |
| `mooncake-pg/` | 进程组（process group）抽象 | 同上 |
| `mooncake-conductor/` | 编排组件（含 prefixindex、zmq） | 同上 |
| `mooncake-reshard/` | KVCache 重分片 | 同上 |
| `mooncake-p2p-store/` | P2P 存储（checkpoint-engine 的前身） | Go 实现为主 |
| `mooncake-integration/` | Python 绑定的 C++ 胶水（pybind11） | 见[第 8 章](/repos/mooncake/integration) |
| `python/mooncake/` | Python 包：CLI shim、async 封装、启动器 | 见[第 8、9 章](/repos/mooncake/deployment) |
| `mooncake-common/` | 公共组件：etcd 客户端、k8s-lease 等 | 被上层的 Master 依赖 |
| `mooncake-wheel/` | PyPI 打包 | — |
| `docs/` | Sphinx 文档源（含 design/ 子目录） | 官方设计文档，与源码同仓库演进 |
| `benchmarks/`、`monitoring/`、`docker/` | 基准、Prometheus/Grafana、镜像 | 见[第 9 章](/repos/mooncake/deployment) |

## 依赖方向

模块间的依赖大体指向"上层消费下层库"，`mooncake-integration` 是唯一的胶水层：

::: mermaid
flowchart TD
    PY["python/mooncake（Python 包）"] --> INTEG["mooncake-integration（pybind11 胶水）"]
    INTEG --> TE["mooncake-transfer-engine"]
    INTEG --> STORE["mooncake-store"]
    STORE --> TE
    STORE --> COMMON["mooncake-common（etcd / k8s-lease）"]
    EP["mooncake-ep / reshard / conductor"] --> TE
    EP --> STORE
:::

两点值得注意（均为源码可验证的事实）：

1. **Store 依赖 TE**：Store 客户端读写副本数据时直接使用 `TransferEngine` 类，因此 `mooncake-store` 的 CMake 链接了 transfer-engine 目标。
2. **TE 不依赖 Store**：TE 可以独立使用，这也是 vLLM、SGLang、TensorRT-LLM 等只集成 TE 做 PD 分离传输的原因（集成关系来自各上游仓库，见仓库 README「Updates」列表）。

## 构建、测试与发布清单

- 构建：根 `CMakeLists.txt` 聚合各子目录；`dependencies.sh` 拉取依赖。
- 测试：各模块自带 `tests/`（全仓约 567 个测试文件——口径：文件名含 test 的源码文件）；Store 另有 `tests/master_service/` 与 e2e 目录。
- 发布：`mooncake-wheel/` 打 PyPI wheel，按硬件后端拆分多个变体（README 顶部徽章列出 cuda13 / non-cuda / npu / musa / efa / rocm 等包名）。
- Python 入口：`python/mooncake/cli.py` 等 shim 经 `_launcher.py` 定位 wheel 内嵌的 C++ 二进制（`python/mooncake/_launcher.py:5` 模块 docstring 明确了这一机制）。

## 收束

一句话记住每个核心模块：**TE 搬数据、Store 管 KVCache、integration 做绑定、python 做交付**。`mooncake-ep/`、`mooncake-reshard/`、`mooncake-conductor/` 在本文中只定位不展开——它们不在这两条主线之上。下一章进入 Transfer Engine 的第一层抽象：段、拓扑与元数据。
