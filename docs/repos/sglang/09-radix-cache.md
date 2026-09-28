---
title: "第 9 章 RadixCache 与 KV 内存池"
---

# 第 9 章 RadixCache 与 KV 内存池

> 本章回答：前缀缓存如何把「历史 KV」变成可复用资产？树的插入、命中、锁定、淘汰如何与内存池协作？HiCache（主机层缓存）如何扩展这套机制？

## 9.1 两层结构

KV 内存层由两个独立组件组成，Scheduler 同时持有：

1. **RadixCache**&#8203;（`srt/mem_cache/radix_cache.py:280`）：逻辑层，把 token 序列前缀组织成基数树，节点持有「这段前缀对应的 KV 槽位列表」；
2. **KV 内存池**&#8203;（`srt/mem_cache/memory_pool.py`）：物理层，`MHATokenToKVPool`（`:1971`）等实现把整块显存切成槽位，`token_to_kv_pool_allocator` 负责分配/释放；`ReqToToken` 是「请求行 → 槽位序列」的表格（`memory_pool.py:314` 起的类定义，`available_size` / `alloc` / `free` 在 `:314`、`:317`、`:360`）。

树节点里的 `value`（`device_indices`）就是物理池中的槽位编号。树管「谁能复用」，池管「槽位给谁」。

## 9.2 命中：match_prefix

`srt/mem_cache/radix_cache.py:354`：

```python
# srt/mem_cache/radix_cache.py:354（节选，docstring 摘要）
def match_prefix(self, params: MatchPrefixParams) -> MatchResult:
    """Find the longest cached prefix of ``key`` in the radix tree.

    The logical namespace for prefix matching is determined by both the
    token id sequence and the optional ``extra_key`` carried by ``RadixKey``.
    ...
    Returns:
        MatchResult: ``device_indices`` is a 1-D ``torch.int64`` tensor of
        the concatenated KV cache indices corresponding to the longest
        cached prefix (may be length 0).
    ...
    """
```

三个行为细节源码可见：`page_size > 1` 时匹配长度先对齐到页；命中若结束在节点&#8203;**中间**&#8203;，会分裂节点以精确对齐边界；`extra_key` 命名空间使 LoRA 等场景下「token 相同但不该共享」的请求保持隔离。

命中的 `device_indices` 被写进 `req.prefix_indices`（第 8 章 prefill 裁剪的依据），同时 `inc_lock_ref` 沿命中路径锁住节点：锁定后这些 token 不计入 `evictable_size`，pre prefill 期间不被淘汰（第 7 章预算中「可淘汰部分」的互补面）。

## 9.3 写回与锁定

请求结束或 chunk 完成时，Scheduler 调 `cache_unfinished_req`（`srt/mem_cache/radix_cache.py:502`；chunked 调用点在 `srt/managers/scheduler.py:3535`，批处理组件中的调用在 `srt/managers/scheduler_components/batch_result_processor.py:383`）：

```python
# srt/mem_cache/radix_cache.py:502（节选）
def cache_unfinished_req(self, req: Req, chunked=False):
    """Cache request when it is unfinished."""
    ...
    radix_key, kv_indices, _ = self._insert_cache(req, req.get_fill_ids(), chunked=chunked)
    # The prefix indices could be updated, reuse it
    match_result = self.match_prefix(MatchPrefixParams(key=radix_key))
    ...
    self.dec_lock_ref(req.last_node)
    self.inc_lock_ref(new_last_node)
```

写回 = `insert`（把新 KV 段作为树节点挂上）+ 立即重匹配（树可能因合并产生更优路径）+ **锁切换**&#8203;：先释放旧命中路径的锁（`dec_lock_ref`），再锁住新插入路径（`inc_lock_ref`，`radix_cache.py:576` 附近）。锁的意义：在请求活着期间，它命中的前缀必须物理存在——这是第 6 章 retract 与第 7 章预算计算的正确性前提。

请求&#8203;**完成**&#8203;时走对称的 `cache_finished_req` 路径（同一文件族，`unified_radix_cache.py:1134` 等实现可见同一模式），释放输出部分的锁、把整条序列留给后人复用，然后 `dec_lock_ref` 归零——此时节点回到 `evictable` 集合。

## 9.4 淘汰：evict

KV 池不足时（第 7 章预算、第 6 章 retract 的压力来源），`evict`（`srt/mem_cache/radix_cache.py:553`）回收缓存：

```python
# srt/mem_cache/radix_cache.py:553（节选）
def evict(self, params: EvictParams) -> EvictResult:
    ...
    leaves = list(self.evictable_leaves)
    eviction_heap = [
        (self.eviction_strategy.get_priority(node), node) for node in leaves
    ]
    heapq.heapify(eviction_heap)

    num_evicted = 0
    while num_evicted < num_tokens and len(eviction_heap):
        _priority, x = heapq.heappop(eviction_heap)
        ...
        self.token_to_kv_pool_allocator.free_segment(x.value, start_pos=0)
        num_evicted += len(x.value)
        self._delete_leaf(x)
        if len(x.parent.children) == 0 and x.parent.lock_ref == 0:
            ...
            heapq.heappush(eviction_heap, (new_priority, x.parent))
        self.kv_events.record_remove(x)
```

要点：&#8203;**只从叶子淘汰**&#8203;（中间节点的槽位被子孙引用）；按 `eviction_strategy.get_priority` 的优先级出堆；淘汰后父节点若也变成无锁叶子则入堆继续淘汰；每次淘汰发出 KV 事件（`kv_events.record_remove`），这是网关做缓存感知路由的数据源（第 15 章）。

## 9.5 全景：一次多轮对话

::: mermaid
sequenceDiagram
    participant Sch as Scheduler
    participant RC as RadixCache
    participant Al as KV 分配器
    Note over RC: 树中已有 [system prompt] 节点
    Sch->>RC: match_prefix(新请求 key)
    RC-->>Sch: 命中前缀 device_indices + last_node
    Sch->>RC: inc_lock_ref(last_node)
    Sch->>Al: alloc_for_extend（仅未命中部分）
    Note over Sch: 前向：attention 读命中槽位，写新槽位
    Sch->>RC: cache_unfinished_req / cache_finished_req
    RC->>RC: insert 新节点，dec/inc_lock_ref 切换
:::

## 9.6 HiCache 与变体

`mem_cache/` 下还有一整层扩展，按源码可归类：

- **主机层**&#8203;（HiCache，`memory_pool_host.py`、`hicache_*.py`）：KV 段在 CPU 侧多存一份，命中时可从主机回载（第 7 章 `add_one_req` 中 `init_load_back` 与 `host_hit_length` 的逻辑），显存外的「第二层缓存」；
- **统一/混合变体**&#8203;：`unified_radix_cache.py`、`hybrid_cache/`（滑动窗口层 + 全注意力层共存）、`pure_swa_radix_cache.py`，为 SWA 类模型提供不同的树语义；
- **Rust 树核**&#8203;：`rust_tree_core/` 与 `rust/sglang-radix-tree`——树操作下沉到 Rust 的实现选项；
- **存储后端**&#8203;：`storage/`（含 LMCache 等外部 KV 存储）、`l2_transfer.py`。

这些变体都实现 `BasePrefixCache`（`mem_cache/base_prefix_cache.py`）的接口，Scheduler 以 `self.tree_cache` 统一持有——多态替换点。

## 9.7 本章收束

- 树管复用、池管槽位，`device_indices` 是两者的协议；`req_to_token` 表是执行期的查询索引。
- 生命周期闭环：match（命中 + 锁）→ alloc（新部分）→ forward → cache（insert + 锁切换）→ finish（解锁入可淘汰集）→ evict（叶子优先、按策略出堆）。
- 所有变体（HiCache、SWA 混合、Rust 树、外部存储）都在 `BasePrefixCache` 接口后替换。
- 下一章进入 GPU 前向：ModelRunner 如何把 ForwardBatch 变成 logits。
