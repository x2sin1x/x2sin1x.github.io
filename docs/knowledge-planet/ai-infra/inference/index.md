---
title: "推理 / 服务"
date: 2026-09-22T18:00:00+08:00
weight: 1
---

# 推理 / 服务

> 训练一次，服务一生。&#8203;**推理系统的 KPI 是延迟、吞吐、成本三角，而所有优化都围着同一块稀缺资源转：显存带宽。**

本板块内容：

1. [KV Cache](/knowledge-planet/ai-infra/inference/kv-cache)——为什么它决定一切，以及 PagedAttention。
2. [Continuous Batching](/knowledge-planet/ai-infra/inference/continuous-batching)——iteration 级调度，吞吐的革命。
3. [请求调度](/knowledge-planet/ai-infra/inference/request-scheduling)——SLO 之下的排队与抢占。
4. [Chunked Prefill](/knowledge-planet/ai-infra/inference/chunked-prefill)——把长提示切块，填平预填充与解码的鸿沟。
5. [Prefix Caching](/knowledge-planet/ai-infra/inference/prefix-caching)——相同前缀只算一次。
6. [量化](/knowledge-planet/ai-infra/inference/quantization)——更低精度、更少显存、更快生成。
7. [投机采样](/knowledge-planet/ai-infra/inference/speculative-decoding)——小模型起草、大模型验卷。
8. [P/D 分离](/knowledge-planet/ai-infra/inference/pd-disaggregation)——预填充与解码分开部署。
9. [A/F 分离](/knowledge-planet/ai-infra/inference/af-disaggregation)——注意力与 FFN 分开部署。

阅读主线：先理解 KV Cache 这个"显存霸主"，再理解调度如何榨干带宽，最后是三类系统级架构（量化、投机、分离式）如何层层加码。
