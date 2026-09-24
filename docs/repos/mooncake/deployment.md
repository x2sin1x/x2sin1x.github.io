---
title: 部署形态、可观测性与 HA
weight: 90
---

# 部署形态、可观测性与 HA

> 本章回答：Mooncake 实际怎么跑起来——进程形态、配置入口、指标出口，以及 Master 单点的可用性方案。

## 进程形态与分发

Mooncake 以两个 Python 发行物交付（`pyproject.toml` / `mooncake-wheel/`）：

- `mooncake-transfer-engine`（TE 绑定 + wheel 内嵌的演示/工具二进制）；
- Store / Master 相关二进制按硬件变体打包。

`python/mooncake/_launcher.py` 的机制值得一看：CLI 入口（`cli.py`、`cli_client.py`、`cli_bench.py`）只是 shim，真正 `exec` 的是 wheel 内嵌的 C++ 二进制，经 `importlib.resources.files` 定位、按需补执行位（`_launcher.py:5–18` 的 docstring 与 `locate()` 实现）。这样避免 PATH 上混入版本不匹配的系统构建。

容器化部署提供 `docker/`（master、mooncake 等镜像）与 `monitoring/docker-compose.yml`（Prometheus + Grafana 栈，Grafana 预置 dashboard）。

## 可观测性

- 指标：Master 与客户端各有一套 metric 管理器（`master_metric_manager.h`、`client_metric.h`），第 5 章见过的 `put_latency_us` / `get_latency_us` 直方图即来自 `metrics_->transfer_metric`（`client_service.cpp:2009`、`:1360`）。
- HA 指标独立成模块：`ha_metric_manager.h`、`master_heartbeat_metric.h`。
- 出口：Prometheus 抓取（`monitoring/prometheus/prometheus.yml` 配置抓取目标），Grafana 展示；延迟直方图埋点分别在 `client_service.cpp:2010`（Put）与 `:1359`（Get）。TENT 子系统另有独立 metrics 设计文档（`docs/source/design/tent/metrics.md`）。

## Master 的 HA：热备 + 快照 + 租约

Master 是元数据单点，Store 为它准备了完整的 HA 组件族（`mooncake-store/src/ha/`）：

| 组件 | 职责 |
| --- | --- |
| `leadership/` | 领导者协调（`leader_coordinator_factory.cpp`、`master_service_supervisor.cpp`），支持 etcd / k8s-lease 两种后端（`mooncake-common/` 下各有对应实现） |
| `snapshot/` | 周期快照与编解码（`MasterSnapshotCodec`、catalog 存储），配合 `src/master_snapshot_manager.cpp` |
| `oplog/` | 操作日志（`batch_oplog/`），快照间增量 |
| `standby_controller.cpp` + `standby_state_machine.h` | 备机状态机 |
| `hot_standby_service.cpp` | 热备服务入口 |

恢复链路：备机持续消费 oplog 保持热状态；主机故障时经领导权协调切换；新主机从「快照 + 回放」恢复全量元数据，存储后端的 `ScanMeta` 提供兜底重建（[第 7 章](/repos/mooncake/store-storage)）。README 更新记录显示 2026-09 仍在迭代"托管权重版本与 Master HA 集成"（本系列快照的最新提交即此主题），说明该体系仍在活跃演进。

::: mermaid
stateDiagram-v2
    [*] --> Leader: 经 leadership 协调当选
    Leader --> Leader: 服务 RPC + 周期快照 + 写 oplog
    Leader --> Standby: 故障 / 失去租约
    Standby --> Leader: 备机接管（快照 + oplog 回放）
    Standby --> Standby: 消费 oplog 保持热状态
:::

## 失败边界

- HA 组件族横跨 etcd、k8s-lease 两种领导权后端，部署时二选一；混用配置属未定义行为（配置校验程度未逐一核对）。
- 客户端对 Master 的短暂不可见有重试与缓存（`etcd_helper.h`、`master_client.h`），但 Master 长时间宕机期间的新对象元数据会丢失——这正是 oplog + 快照存在的原因。

## 收束

1. 交付形态是「Python shim + wheel 内嵌 C++ 二进制」，多硬件变体各出各的 wheel。
2. 可观测性走 Prometheus/Grafana，延迟直方图在客户端与 Master 两侧都有埋点。
3. Master HA = 领导权（etcd/k8s-lease）+ 热备状态机 + 快照/oplog 恢复，是 Store 敢于做元数据权威的底气。
