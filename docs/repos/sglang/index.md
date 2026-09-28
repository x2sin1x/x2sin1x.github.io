---
title: "SGLang"
---

# SGLang 源码解读：从一个请求到一次生成

![](cover.webp)

> 本系列把 SGLang（`sgl-project/sglang`）当作一个真实的推理服务系统来解剖：沿「HTTP 请求 → 分词 → 调度 → KV 内存 → 模型执行 → 采样 → 反分词 → 流式响应」这条主执行链，用源码证据解释它为什么这样工作。

## 版本快照

| 字段 | 内容 |
| --- | --- |
| 仓库 | https://github.com/sgl-project/sglang |
| 分支 | `main` |
| 快照 commit | `65824258549671404188450748b90ab7cacab2ae` |
| 核对日期 | 2026-09-28 |
| 分析范围 | 以 `python/sglang`（SRT 运行时）为主线，兼及 Rust 网关 `sgl-model-gateway` |

正文所有代码引用均锚定在该 commit 上，写作格式为 `srt/xxx.py:行号`（即 `python/sglang/srt/xxx.py`）。行号以固定快照为准；上游 main 持续演进，阅读最新代码时请以符号名为锚点重新定位。

## 这一卷回答什么

- SGLang 服务端一次生成请求，&#8203;**从 socket 到 socket** 经过了哪些进程、哪些状态容器、哪些关键分支？
- 调度器如何决定「下一个 batch 是 prefill 还是 decode」，chunked prefill 与 retract 各自解决什么问题？
- RadixCache 前缀缓存如何与 KV 内存池、锁引用、淘汰策略协同？
- 重叠调度（overlap scheduling）用怎样的代价换取 CPU 调度与 GPU 计算的重叠？
- 多进程、多机、PD 分离、Rust 路由网关这些「跑得起来之后」的工程问题如何组织？

## 目录

### 第一部分 宏观

- [第 1 章 定位与心智模型](/repos/sglang/01-overview)
- [第 2 章 仓库地图](/repos/sglang/02-repo-map)

### 第二部分 进程与入口

- [第 3 章 启动与进程拓扑](/repos/sglang/03-launch)
- [第 4 章 HTTP 入口与 OpenAI 兼容层](/repos/sglang/04-entrypoints)
- [第 5 章 TokenizerManager：请求的第一站](/repos/sglang/05-tokenizer-manager)

### 第三部分 调度与执行

- [第 6 章 Scheduler 主循环与重叠调度](/repos/sglang/06-scheduler-loop)
- [第 7 章 PrefillAdder 与 chunked prefill](/repos/sglang/07-prefill-policy)
- [第 8 章 从 Req 到 ForwardBatch：批数据流水线](/repos/sglang/08-batch-pipeline)
- [第 9 章 RadixCache 与 KV 内存池](/repos/sglang/09-radix-cache)
- [第 10 章 ModelRunner 与模型执行](/repos/sglang/10-model-executor)
- [第 11 章 采样](/repos/sglang/11-sampler)
- [第 12 章 结果处理与 Detokenizer](/repos/sglang/12-output-path)

### 第四部分 集群与生态

- [第 13 章 并行体系：DP / TP / PP / EP](/repos/sglang/13-parallel)
- [第 14 章 PD 分离（Prefill/Decode disaggregation）](/repos/sglang/14-disagg)
- [第 15 章 Rust 路由网关](/repos/sglang/15-gateway)

### 附录

- [附录 A 推荐阅读路径](/repos/sglang/appendix-reading-path)
- [附录 B 核心符号速查](/repos/sglang/appendix-symbols)
- [附录 C 术语表](/repos/sglang/appendix-glossary)
