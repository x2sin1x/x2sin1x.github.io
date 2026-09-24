---
title: Attention 后端体系
weight: 90
---

# Attention 后端体系

> 本章回答：vLLM 如何在同一套调度与执行框架下支持 FlashAttention、FlashInfer、Triton、MLA 等数十种 attention 实现——注册、能力声明、按配置选择的三步协议。

## 一个抽象 + 一个注册表

attention 后端体系由三件东西撑起：

1. **抽象基类** `AttentionBackend`（`vllm/v1/attention/backend.py:58`）：定义后端必须回答的问题；
2. **注册表** `AttentionBackendEnum`（`vllm/v1/attention/backends/registry.py:34`）：枚举项即后端，枚举值是类的导入路径，支持运行时 `register_backend()` 覆盖（`:37`）——第三方后端走 `CUSTOM` 槽位（`:152`），必须先注册否则抛错；
3. **选择器** `get_attn_backend()`（`vllm/v1/attention/selector.py:105`）：按模型与配置挑出唯一后端。

`backends/` 目录下每个文件是一种实现：`flash_attn.py`、`flashinfer.py`、`triton_attn.py`、`flex_attention.py`、MLA 专用的 `mla/`，以及 ROCm 专属的 `rocm_aiter_fa.py` 等——快照中约 30 个后端文件。

## 能力声明：让选择器免于硬编码

`AttentionBackend` 的关键不是 `forward`（那在 `AttentionImpl` 里），而是一组**能力查询类方法**：

```python
class AttentionBackend(ABC):
    @classmethod
    def get_supported_kernel_block_sizes(cls) -> ...   # backend.py:72
    @classmethod
    def supports_head_size(cls, head_size: int) -> bool   # :101
    @classmethod
    def supports_kv_cache_dtype(cls, kv_cache_dtype) -> bool  # :110
    @classmethod
    def supports_block_size(cls, block_size) -> bool      # :118
    @classmethod
    def supports_sliding_window(cls) -> bool              # :186
    @classmethod
    def supports_kv_connector(cls) -> bool                # :209
```

选择器把模型与配置归集成 `AttentionSelectorConfig`（`selector.py:150` 附近构造）：head size、dtype、kv dtype、是否 MLA、是否滑动窗口、是否启用 KV Connector 等，然后逐一询问各后端的 capability 方法（`:105` 的 `get_attn_backend`）。这是一个"配置 → 能力匹配"的协议：模型说什么（如 DeepSeek 的 MLA），后端答什么，选择器只做匹配。

每个后端还声明三个构件（`backend.py:84-89`）：

| 构件 | 职责 |
|---|---|
| `get_impl_cls()` | 真正计算 attention 的 `AttentionImpl`（如 `FlashAttentionImpl`，`flash_attn.py:1105`） |
| `get_builder_cls()` | 把调度信息编译成 kernel 输入的 `AttentionMetadataBuilder`（如 `flash_attn.py:598`） |
| `get_supported_kernel_block_sizes()` | 声明支持的分页块大小，参与 `KVCacheSpec` 计算 |

## 选择的时机与后果

后端在引擎初始化时确定一次，其影响贯穿三层：

1. **KV 形状**：后端的 `customize_spec()`（`backend.py:137`）可以改写 `AttentionSpec`（例如声明自己偏好的块大小，`get_preferred_block_size`，`:151`），从而改变第 7 章的块池布局；
2. **每步执行**：`GPUModelRunner` 用 builder 产出 metadata，`AttentionImpl.forward`（如 `flash_attn.py:1230`）消费它——对调度器完全透明；
3. **投机解码与 Connector**：`supports_kv_connector` 等声明决定某些特性是否可用（如 P/D 分离要求后端配合 KV 传输）。

::: mermaid
flowchart TB
    M["模型 config<br/>head_size / MLA / sliding window"] --> SEL
    U["用户配置<br/>block_size / kv dtype / VLLM_ATTENTION_BACKEND"] --> SEL
    SEL["get_attn_backend<br/>v1/attention/selector.py:105"] -- "能力匹配" --> B["选中的 AttentionBackend"]
    B --> SPEC["customize_spec → KVCacheSpec<br/>（块大小、页形状）"]
    B -- "get_builder_cls" --> MB["每步构建 metadata"]
    B -- "get_impl_cls" --> IM["forward(q, k, v, metadata)"]
:::

## 覆盖与调参

用户可用环境变量 `VLLM_ATTENTION_BACKEND` 强制指定后端（跳过自动匹配），代价是自己承担能力不匹配的风险——选择器的自动匹配本质上就是这层保险。第三方硬件通过第 13 章的 Platform 机制 + `register_backend` 动态接入，不需要改动 vLLM 本体。

## 本章收束

- 后端 = `AttentionBackend`（静态能力声明）+ `MetadataBuilder`（每步输入编译）+ `AttentionImpl`（计算）三件套；
- 选择协议是"模型与配置提问、后端作答、选择器匹配"，避免在框架里散布 `if flashinfer` 式分支；
- 后端选择反过来决定 KV Cache 形状，是少数"执行层影响调度层"的通道。

下一章回到数据流的末端：采样出来的 token id 如何变成流式响应。
