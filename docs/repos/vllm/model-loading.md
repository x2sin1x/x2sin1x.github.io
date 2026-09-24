---
title: 模型加载与量化
weight: 110
---

# 模型加载与量化

> 本章回答：一份 HF 格式的 checkpoint 如何变成多进程各持一份（或分片）的模型实例，量化方法又是如何嵌入层实现而不污染模型代码的。

## 加载器框架：按 load_format 分派

`get_model_loader()`（`vllm/model_executor/model_loader/__init__.py:123`）按 `LoadConfig.load_format` 查表返回加载器，全部继承 `BaseModelLoader`（`base_loader.py:25`）：

| 加载器 | 场景 |
|---|---|
| `DefaultModelLoader`（`default_loader.py:50`） | 常规 safetensors/GGUF 加载 |
| `RunaiModelStreamerLoader` | 流式加载对象存储上的权重 |
| `ShardedStateLoader` | 加载 vLLM 自己保存的分片状态 |
| `TensorizerLoader` | Tensorizer 序列化格式的快速加载 |
| `DummyModelLoader` | 只建结构不装权重（profiling、spec drafter 占位） |

离线类还提供 `register_model_loader`（`__init__.py` 的 `__all__` 中导出），允许外部注册自定义加载格式。

加载的关键分岔在并行配置：**TP > 1 时，每个 rank 只加载并持有自己那一片权重**。`DefaultModelLoader` 依循"先建空模型 → 逐个权重文件流式读取 → 按各层注册的权重加载器（`weight_loader` 回调）把分片写进对应 rank 的参数"的顺序，因此 70B 模型 8 卡 TP 的单卡内存占用不需要放下完整 checkpoint。

## 量化：层内插入的 QuantizationMethod

vLLM 的量化不是后处理工具，而是**层实现的一部分**。`model_executor/layers/quantization/`（快照中 23 个文件）为每种量化方案提供一个 config 类：`fp8.py`、`awq_triton.py`、`auto_awq.py`、`compressed_tensors/`、`mxfp4.py`、`quark/` 等。

接入协议是：模型里的 `Linear`、`MoE` 等层在构造时向量化配置询问"用哪种方法实例化我"，量化 config 返回一个实现了相同前向接口的替换层（如 W8A8 的 fp8 线性层、AWQ 反量化线性层）。由此带来三个性质：

1. **模型代码零感知**：`model_executor/models/` 下的模型只声明层类型，不写 `if quant_method == "fp8"`；
2. **KV Cache 也可量化**：`kv_cache.py` 处理 KV 缓存 dtype 的缩放逻辑，与 attention 后端的 `supports_kv_cache_dtype`（第 9 章）呼应；
3. **权重与激活规格绑定**：checkpoint 里检测到的量化格式决定 config 类，config 类决定层实现——格式不匹配会在加载期报错，而不是运行期产生错误数值。

::: mermaid
flowchart LR
    CK["checkpoint<br/>safetensors + config.json"] --> GL["get_model_loader<br/>model_loader/__init__.py:123"]
    GL --> L["DefaultModelLoader"]
    L -- "读 hf config" --> MCLS["get_model_architecture<br/>确定模型类"]
    MCLS -- "构造" --> MODEL["空模型<br/>各层询问量化方法"]
    L -- "流式读权重" --> W["weight_loader 回调<br/>按 TP rank 切分写入"]
    W --> MODEL
    MODEL --> RDY["可执行模型<br/>+ 已初始化的量化层"]
:::

## 模型实现的两个目录

快照中的模型实现分布在两处：老主力 `model_executor/models/`（数百个模型文件），以及新的 `vllm/models/`（`deepseek_v32/`、`kimi_k3/`、`qwen4_exp/` 等新一代模型的目录式组织）。两处实现共用 `model_executor/layers/` 的层原语（`linear.py`、`fused_moe/`、`mla.py` 等），从层复用的角度看它们是同一生态。

## 失败与边界

- 加载期常见的失败是**架构名不匹配**（config.json 的 architectures 找不到模型类）与 **TP 切分不兼容**（某些层不支持当前 TP 度的 world size）；
- `DummyModelLoader` 的存在说明"建模型"与"装权重"是可分离的：GPU 利用率 profile、CUDA Graph 捕获预热都用 dummy 权重跑；
- 多模态与编码器权重走相同的 weight_loader 协议，但允许在 worker 侧延迟到首请求才处理（多模态注册表按需初始化）。

## 本章收束

- 加载器按 load_format 分派，TP 场景天然分片加载，rank 不持有全量 checkpoint；
- 量化以"量化 config 返回替换层"的方式嵌入层实现，模型代码零感知；
- 权重格式的检测在加载期一次性完成，不匹配即失败，规避了运行期的静默错误。

下一章解释多卡协同的另一半：TP/PP/DP/EP 通信组如何建立，执行器后端如何把 Worker 进程组织起来。
