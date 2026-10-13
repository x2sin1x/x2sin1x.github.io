---
title: "附录 A：按目标阅读"
---

# 附录 A：按目标阅读

## 想先掌握整体

按 [第 1 章](/repos/deepep/01-overview) → [第 2 章](/repos/deepep/02-repo-map) → [第 7 章](/repos/deepep/07-v2-dispatch) → [第 8 章](/repos/deepep/08-v2-combine-events) 阅读。前两章建立版本与模块坐标，后两章沿当前 EP 黄金路径走完 dispatch 和 combine。

## 想理解 V1 如何工作

阅读 [第 3 章](/repos/deepep/03-v1-buffer-lifecycle) → [第 4 章](/repos/deepep/04-v1-dispatch-combine)，并打开 `v1.2.1` 固定提交下的 `deep_ep/buffer.py` 和 `csrc/deep_ep.cpp`。重点看 rank 分组、IPC / NVSHMEM 初始化以及 normal / low-latency API 的契约。

## 想把 V1 与 V2 做机制比较

阅读 [第 4 章](/repos/deepep/04-v1-dispatch-combine) → [第 5 章](/repos/deepep/05-v2-runtime) → [第 6 章](/repos/deepep/06-v2-transport)。比较入口和状态迁移，不要拿两代同名函数假定内部语义一致。

## 想接入 V2 或排查资源问题

阅读 [第 5 章](/repos/deepep/05-v2-runtime)、[第 6 章](/repos/deepep/06-v2-transport)、[第 9 章](/repos/deepep/09-v2-memory-layout) 与 [第 11 章](/repos/deepep/11-build-tests)。再结合 README 的版本要求、buffer size hint、Gin capability 检查和当前部署拓扑检查。

## 想接入冗余专家或旁支通信原语

先阅读 [第 10 章](/repos/deepep/10-v2-other-buffers)，再沿对应 `tests/ep/`、`tests/engram/`、`tests/pp/` 或 `tests/bucket/` 追踪调用点和结果契约。
