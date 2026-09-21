---
title: "数据类型"
date: 2026-09-15T09:10:00+08:00
weight: 20
---
# 数据类型

> 对应官方文档：[Data types](https://redis.io/docs/latest/develop/data-types/)

Redis 的值不是单一的「字符串」，而是一组开箱即用的数据结构。为数据选择合适的类型，后续的查询和统计会简单很多。本页继续使用任务管理示例，用五种核心数据类型分别表达任务详情、待办队列、负责人集合和优先级排行。

## 前置条件

请先完成[基本概念](/tech-stack/redis/concept)中的 Docker 启动和 `redis-cli` 连接步骤。下面的命令都在 `redis-cli` 中执行。

本页约定以下键名：

- `task:t001`：哈希，保存单个任务的字段。
- `queue:tasks`：列表，待处理任务队列。
- `task:t001:tags`：集合，任务标签。
- `board:priority`：有序集合，任务优先级排行。

## String：字符串

String 是最基础的类型，可以保存文本、数字甚至序列化后的 JSON。

**示例 1：写入与读取**

```text
SET task:t001:title "编写 API 文档"
GET task:t001:title
```

你应该看到：

```text
OK
"编写 API 文档"
```

**示例 2：原子计数**

```text
SET stats:views 0
INCR stats:views
INCRBY stats:views 9
GET stats:views
```

你应该看到：

```text
OK
(integer) 1
(integer) 10
"10"
```

`INCR` 是原子操作，多个客户端并发自增也不会丢失计数，这是用 Redis 做计数器的基础。

**常见错误**：对保存非数字内容的字符串执行 `INCR`：

```text
# ❌ 值不是整数，命令失败
SET greeting "hello"
INCR greeting
```

```text
(error) ERR value is not an integer or out of range
```

## Hash：哈希

Hash 类似一个小型字典，适合保存一个对象的多个字段。每个任务用一个哈希表示，键名统一为 `task:<id>`：

```text
HSET task:t001 title "编写 API 文档" status "todo" priority 3 assignee "u001"
HGET task:t001 title
HGETALL task:t001
```

你应该看到：

```text
(integer) 4
"编写 API 文档"
 1) "title"
 2) "编写 API 文档"
 3) "status"
 4) "todo"
 5) "priority"
 6) "3"
 7) "assignee"
 8) "u001"
```

修改单个字段并读取部分字段：

```text
HSET task:t001 status "doing"
HMGET task:t001 title status
```

你应该看到：

```text
(integer) 0
 1) "编写 API 文档"
 2) "doing"
```

> 💡 **新手提示**：`HSET` 返回新建字段的数量，修改已有字段返回 `0`，这不是错误。与 MongoDB 的文档相比，Hash 的字段值只能是字符串和数字，不能嵌套对象；需要嵌套时可以把子结构序列化成 JSON 字符串存进一个字段。

## List：列表

List 是按插入顺序排列的字符串集合，可以从两端插入和弹出，适合队列和最近动态。

把三个任务 ID 压入待处理队列：

```text
RPUSH queue:tasks "task:t001" "task:t002" "task:t003"
LRANGE queue:tasks 0 -1
```

你应该看到：

```text
(integer) 3
1) "task:t001"
2) "task:t002"
3) "task:t003"
```

从队头取出一个任务，模拟消费者处理：

```text
LPOP queue:tasks
LRANGE queue:tasks 0 -1
```

你应该看到：

```text
"task:t001"
1) "task:t002"
2) "task:t003"
```

`RPUSH` + `LPOP` 组成先进先出队列；`LPUSH` + `LPOP` 则是栈。列表还能配合 `BLPOP` 实现阻塞式等待，是轻量级任务队列的常见做法。

## Set：集合

Set 保存不重复的字符串，适合表达成员关系和做交并差运算。用一个集合保存任务标签：

```text
SADD task:t001:tags "docs" "redis" "api"
SADD task:t001:tags "docs"
SCARD task:t001:tags
SMEMBERS task:t001:tags
```

你应该看到：

```text
(integer) 3
(integer) 0
(integer) 3
1) "api"
2) "docs"
3) "redis"
```

第二次 `SADD` 返回 `0`，因为 `docs` 已存在，Set 自动去重。判断成员与做交集：

```text
SISMEMBER task:t001:tags "redis"
SADD task:t002:tags "redis" "python"
SINTER task:t001:tags task:t002:tags
```

你应该看到：

```text
(integer) 1
(integer) 2
1) "redis"
```

## Sorted Set：有序集合

Sorted Set（ZSet）的每个成员关联一个分数（score），集合按分数有序，是排行榜和优先级队列的直接实现。把任务的优先级写入排行：

```text
ZADD board:priority 3 "task:t001" 1 "task:t002" 2 "task:t003"
ZSCORE board:priority "task:t001"
```

你应该看到：

```text
(integer) 3
"3"
```

按优先级从高到低取出前两名：

```text
ZRANGE board:priority 0 1 REV WITHSCORES
```

你应该看到：

```text
1) "task:t001"
2) "3"
3) "task:t003"
4) "2"
```

查看排名与增减分数：

```text
ZREVRANK board:priority "task:t002"
ZINCRBY board:priority 1 "task:t002"
```

你应该看到：

```text
(integer) 2
"2"
```

> 💡 **新手提示**：`ZRANK` 按分数从低到高排名（从 `0` 开始），`ZREVRANK` 相反。榜单场景几乎总是用 `ZREVRANGE` + `ZREVRANK` 组合。

## TYPE 与类型选择

忘记某个键用了什么类型时，用 `TYPE` 查询：

```text
TYPE task:t001
TYPE queue:tasks
TYPE board:priority
```

你应该看到：

```text
hash
list
zset
```

选型经验：对象属性用 Hash，顺序队列用 List，去重成员用 Set，需要排序的场景用 Sorted Set，简单值和计数器用 String。

## 小结

- Redis 的值有类型：String、Hash、List、Set、Sorted Set 各有适用场景，类型决定可用命令。
- `INCR` 等计数命令是原子的，适合并发计数。
- List 两端进出可以组成队列或栈；Set 自动去重并支持交并差；Sorted Set 按分数有序，天然适合排行。
- `TYPE` 命令可以随时确认键的类型，避免 `WRONGTYPE` 错误。

## 练习

1. 为 `task:t002` 创建哈希，字段包括 `title`、`status` 和 `priority`，然后用 `HGETALL` 验证。
2. 用 `RPUSH` 向 `queue:tasks` 加入两个新 ID，再用 `LRANGE queue:tasks 0 -1` 观察顺序。
3. 建一个集合保存你自己的技能标签，尝试 `SADD` 一个重复值并解释返回值。

下一步：进入[键与过期](/tech-stack/redis/keys)，学习遍历、删除键并为缓存设置 TTL。
