---
title: PagedAttention 与 KV Cache 管理
weight: 70
---

# PagedAttention 与 KV Cache 管理

> 本章回答：KV Cache 如何被切成块、按内容寻址共享与淘汰；`allocate_slots` 的一次调用内部发生了什么。本章解释的是 EngineCore 里的"账本"——Worker 里的实际张量在第 8 章出现。

## 三层结构：Spec → Manager → BlockPool

EngineCore 侧的 KV 管理分三层，各管一件事：

| 层 | 符号 | 职责 |
|---|---|---|
| 缓存形状声明 | `KVCacheSpec`（`vllm/v1/kv_cache_interface.py:156`） | 每层的块形状：block size、token 数、页大小字节 |
| 缓存账本 | `KVCacheManager`（`vllm/v1/core/kv_cache_manager.py:131`） | 每请求的块分配/释放、前缀查找、事件发布 |
| 物理块池 | `BlockPool`（`vllm/v1/core/block_pool.py:134`） | 空闲块队列、hash → block 索引、引用计数与淘汰 |

初始化时 Worker 探测各注意力层的 KV 形状上报给 EngineCore（`EngineCore._initialize_kv_caches()`，`vllm/v1/engine/core.py:258`），形状相似的层被归入同一个 `KVCacheGroupSpec`（`kv_cache_interface.py:1410`），管理器按组统一分配。这个设计让"每层一种缓存格式"成为可能—— MLA、滑动窗口、Mamba 线性注意力可以各用各的 `KVCacheSpec` 共存于一个请求。

## 内容寻址：BlockHash 与前缀缓存

每个**装满**的 KV 块都会被赋予一个内容哈希：`hash_block_tokens()`（`vllm/v1/core/kv_cache_utils.py:649`）对"父块哈希 + 本块 token 序列 + 额外键（LoRA id、cache salt、多模态位置等，`generate_block_hash_extra_keys`，`:610`）"做哈希。父块哈希进哈希串意味着**前缀即路径**——两块 token 相同但前缀不同的块哈希不同，天然避免误共享。

请求到达时，调度器在第二轮扫描里触发前缀查找：`KVCacheManager.get_computed_blocks()`（`kv_cache_manager.py:264`）把请求的 prompt 按 block 切哈希，交给协调器 `find_longest_cache_hit()` 找最长命中：

```python
max_cache_hit_length = request.num_tokens - 1
computed_blocks, num_new_computed_tokens, num_uncached = (
    self.coordinator.find_longest_cache_hit(
        request.block_hashes, max_cache_hit_length
    )
)
```

注意 `num_tokens - 1`：即使 prompt 全部命中，也必须重算最后一个 token 才能拿到 logits（`:289` 附近的 NOTE）。

## 一次分配的账本流

`allocate_slots()`（`kv_cache_manager.py:371`）的 docstring 画出了一次分配的完整布局：

```text
| < comp > | < new_comp > | < ext_comp > | < new > | < lookahead > |
```

- `comp`：请求已计算的 token（前缀命中部分）；
- `new_comp`：本步刚发现的新前缀命中（免算，但也要把块"touch"进本请求）；
- `ext_comp`：来自 KV Connector（如 P/D 分离的远端 KV）的 token；
- `new`：本步要真正计算的新 token，从空闲池取块装填；
- `lookahead`：为投机解码（如 Eagle 的 KV 提前量）预留的槽位。

分配成功后，块池把这些块挂到请求名下；请求结束或被抢占时 `free()`（`:610`）归还。归还的块**不是立即销毁**，而是带着哈希进入空闲队列——这就是前缀缓存的实现方式：没有独立的"缓存区"，只有带内容的空闲块。

## 淘汰：引用计数 + LRU

`BlockPool` 用 `FreeKVCacheBlockQueue`（`vllm/v1/core/kv_cache_utils.py:246`）管理空闲块，每个块是 `KVCacheBlock`（`:176`），带 `ref_cnt`：

- `touch()`（`block_pool.py:746`）：请求复用某缓存块时把 `ref_cnt` 加一，同时把它从空闲队列中间摘除——正在使用的块不可被淘汰；
- 请求释放时 `ref_cnt` 减一；归零的块按"最后使用时间"回到空闲队列，供后续分配（近似 LRU）；
- `cache_full_blocks()`（`block_pool.py:224`）在块被填满时登记哈希索引，使后续请求能通过 `get_cached_block()`（`:196`）找到它。

显存压力下，`evict_blocks()`（`:801`）可以强制摘除无引用的缓存块。所以淘汰顺序事实上是：先抢无引用的缓存块，再不行才触发调度器抢占正在运行的请求（上一章的抢占循环）。

## 代价与边界

- **哈希开销**：每个满块都要算哈希，prompt 越长开销越大；关闭前缀缓存时 `prefix_cache_lookup_enabled`（`kv_cache_manager.py:249`）直接短路查找；
- **块对齐浪费**：命中必须对齐到块边界，`allocate_slots` 的注释明确说 `num_computed_tokens` 需要块对齐，可能整块重算最后一个 token（`kv_cache_manager.py:293` 附近）；
- **共享写坏问题不存在**：块一旦被缓存（ref_cnt > 0）就不可变，任何新写入都走新块——copy-on-语义由不可变性保证，而不是显式拷贝。

## 本章收束

- KV Cache 管理是三层结构：Spec 声明形状、Manager 记账、BlockPool 管物理块；
- 前缀缓存 = 带内容哈希的空闲块队列，"缓存"与"空闲"是同一批块的两个视角；
- 淘汰先于抢占：先回收无引用缓存块，再牺牲运行中的请求。

下一章进入 Worker 进程，看块表如何变成 GPU 上的实际读写。
