---
title: "附录 C：术语表"
---

# 附录 C：术语表

| 术语 | 本书译名 | 含义 |
| --- | --- | --- |
| Expert Parallelism (EP) | 专家并行 | 将不同 MoE experts 分布到多个 rank，并在 token 路由处交换数据的并行方式。 |
| Mixture of Experts (MoE) | 混合专家 | 由 router 为 token 选择部分专家参与计算的模型层或模型结构。 |
| dispatch | 分发 | 根据 top-k 路由把 token 与必要元数据送到目标 expert rank。 |
| combine | 回收 / 聚合 | 按 dispatch 保存的来源关系，把专家计算结果归并回 token 所属 rank。 |
| rank | 进程秩 | 分布式进程组中的参与者编号；在 GPU 训练场景通常对应一个 GPU worker。 |
| scale-up domain | 节点内扩展域 | 由本地高速互连（代码中通过 NCCL LSA / NVLink domain 识别）连接的 rank 集合。 |
| scale-out domain | 节点间扩展域 | 通过 RDMA/Gin 等网络通信扩展到其他节点的 rank 集合。 |
| NVLink IPC | NVLink 进程间共享 | V1 用 CUDA IPC 句柄打开同节点 peer GPU 内存的机制。 |
| NVSHMEM / IBGDA | NVSHMEM / IBGDA | V1 的设备侧跨节点通信栈与 GPU initiated communication 路径。 |
| NCCL Gin | NCCL Gin 设备通信接口 | V2 使用的 NCCL device-side network communication 能力。 |
| GDAKI | GDA Kernel Initiated | NCCL Gin 中由 GPU kernel 发起数据传输的一种能力类型；DeepEP Context 会检查其支持。 |
| QP | 队列对 | RDMA/Gin 通信操作使用的发送/接收队列资源，数量会受 context 初始化预算约束。 |
| symmetric memory | 对称内存 | 分布式各 rank 按兼容布局分配并注册、供远端/设备通信寻址的内存区域。 |
| workspace | 工作区 | 用于同步信号、计数器、元数据等控制状态的临时内存区域。 |
| expert alignment | 专家对齐 | 将每个 expert 接收 token 数对齐到指定粒度，以匹配后续 grouped GEMM 的输入布局。 |
| expanded layout | 展开布局 | 按 expert 组织接收 token，让每个 expert 的数据占据连续且可对齐的片段。 |
| epilogue | 收尾阶段 | 通信 kernel 之后对输出执行复制、重排、归约或融合操作的阶段。 |
| handle | 通信句柄 | dispatch 保存的路由、布局和 source metadata，供复用布局或 combine 回传。 |
| EventOverlap | 事件重叠封装 | DeepEP 包装 CUDA event 与延后工作，让调用方安排通信和计算 stream 的依赖。 |
| DeepJIT | DeepJIT 运行时编译 | DeepEP 用于按配置编译和 launch GPU kernel 的 JIT runtime。 |
