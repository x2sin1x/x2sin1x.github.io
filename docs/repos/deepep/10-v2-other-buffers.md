---
title: "第 10 章 V2：EP 之外的 Buffer 与扩展能力"
---

# 第 10 章 V2：EP 之外的 Buffer 与扩展能力

> 本章回答 V2.5 中还有哪些机制共享底层运行时，以及这些能力为何不应与 EP dispatch/combine 主路径混成一个 API。

## 10.1 BufferBase 统一的是生命周期

`BufferBase` 只统一 runtime 引用、memory usage 输出和显式 destroy 入口（`deep_ep/buffers/base.py:1-27`）。V2.5 README 描述 `EPBuffer`、`EngramBuffer`、`PPBuffer`、`BucketBuffer` 共用该生命周期，但各类 Buffer 的操作和数据契约保持专用。它们不是一个有多种 operation flag 的万能 buffer。

基类保留 runtime，并把显式销毁检查和 runtime 清理集中在 `destroy()`：

```python
class BufferBase(ABC):
    """Common lifecycle for communication buffers."""

    def __init__(self, explicitly_destroy: bool = False):
        self.explicitly_destroy = explicitly_destroy
        self.runtime = None

    @property
    def main_context(self):
        """The first communication context, or ``None`` after destruction."""
        return self.runtime.main_context if self.runtime is not None else None

    def print_memory_usage(self) -> None:
        assert self.runtime is not None
        self.runtime.print_memory_usage()

    @abstractmethod
    def destroy(self) -> None:
        assert self.explicitly_destroy
        if self.runtime is not None:
            self.runtime.destroy()
            self.runtime = None
```

## 10.2 与 EP 的关联能力

EPBuffer 还提供冗余专家负载均衡相关操作：`lb_prefetch_weights` 在 expert compute 前搬运副本权重，`lb_reduce_grads` 在 backward 聚合冗余副本的梯度（`deep_ep/buffers/ep.py:846-920`；C++ kernel wrappers 在 `csrc/kernels/ep/prefetch_weights.hpp` 和 `reduce_grads.hpp`）。它们复用 EP buffer 的额外 load-balance 区域，构造时需要传入容量或 `BufferAllocator` 计划。

Python wrapper 会把单个 Tensor 统一包装成序列，并将异步 runtime event 包装为 `EventOverlap`；梯度接口则将 reduction 参数直接传到底层：

```python
def lb_prefetch_weights(self, redundant_expert_weights, expert_weights,
                        redundancy_mapping: torch.Tensor, num_sms: int = 0,
                        previous_event: Optional[EventHandle] = None) -> EventOverlap:
    redundant_expert_weights = ([redundant_expert_weights] if isinstance(redundant_expert_weights, torch.Tensor)
                                else list(redundant_expert_weights))
    expert_weights = [expert_weights] if isinstance(expert_weights, torch.Tensor) else list(expert_weights)

    num_sms = self.lb_get_theoretical_num_sms() if num_sms == 0 else align(num_sms, 2)
    return EventOverlap(self.runtime.lb_prefetch_weights(
        redundant_expert_weights, expert_weights, redundancy_mapping, num_sms, previous_event))

def lb_reduce_grads(self, redundant_expert_grads: torch.Tensor,
                    expert_grads: torch.Tensor, redundancy_mapping: torch.Tensor,
                    num_sms: int = 0,
                    previous_event: Optional[EventHandle] = None) -> EventOverlap:
    num_sms = self.lb_get_theoretical_num_sms() if num_sms == 0 else align(num_sms, 2)
    return EventOverlap(self.runtime.lb_reduce_grads(
        redundant_expert_grads, expert_grads, redundancy_mapping, num_sms, previous_event))
```

该功能存在调用顺序契约：先按 redundancy mapping 配置并预取权重，再用副本执行 expert 计算；反向阶段再将副本梯度规约到原专家。源码可确认这些 API 和 C++ kernel 的存在；具体如何与 MoonEP、UltraEP 等上层调度结合，由相应框架集成代码定义。

## 10.3 实验性通信原语

README 把 Engram、PP 和 bucket collectives 标注为实验能力。`EngramBuffer` 面向远程记忆存储 fetch/wait；`PPBuffer` 提供 PP send/recv；`BucketBuffer` 支持分桶的 all-gather、reduce-scatter、all-reduce 与普通 PyTorch tensor session。它们分别对应不同数据生命周期和消费者，放在单独章节脉络比较比塞入 EP 黄金路径更准确。

::: mermaid
flowchart TB
    B[BufferBase 生命周期] --> E[EPBuffer: MoE dispatch / combine]
    B --> G[EngramBuffer: 远程存储 fetch / wait]
    B --> P[PPBuffer: pipeline send / recv]
    B --> K[BucketBuffer: 分桶 collective]
    E --> L[load-balance 预取权重 / 梯度规约]
:::

## 10.4 边界与风险

- V1 的 normal/low-latency 旧 API 不应被当成当前 EPBuffer 的 alias；V2.5 README 明确它们已移除。
- Engram/PP/Bucket 在当前 README 中标为实验特性；使用时需按对应测试与硬件条件判断成熟度。
- 新增 buffer 类型共享生命周期基类，不代表能够共享同一 workspace size、消息协议或失败语义。

## 本章收束

- V2.5 扩大了 DeepEP 的系统范围，但 EPBuffer 仍是本书核心主线。
- BufferBase 统一生命周期和诊断入口，各 buffer 保留专属数据面。
- load-balance 原语扩展 EP 的资源用途；Engram、PP、Bucket 是独立通信场景。
