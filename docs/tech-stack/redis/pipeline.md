---
title: "管道与事务"
date: 2026-09-15T09:20:00+08:00
weight: 40
---
# 管道与事务

> 对应官方文档：[Redis pipelining](https://redis.io/docs/latest/develop/use/pipelining/) 与 [Transactions](https://redis.io/docs/latest/develop/use/transactions/)

每条 Redis 命令都是一次网络往返。需要连续执行多条命令时，往返延迟会成为瓶颈；多个命令必须「一起生效」时，则需要原子性保证。本页介绍解决这两个问题的机制：管道和事务。

## 前置条件

请先完成[键与过期](/tech-stack/redis/keys)中的步骤，并确保 `redis-cli` 已连接。本页命令相互独立，可以按顺序执行后用 `FLUSHDB` 以外的任何方式随意重试。

## 管道：批量发送命令

没有管道时，执行 3 条命令需要 3 次网络往返：

```text
客户端 -> SET a 1 -> 服务器
客户端 -> SET b 2 -> 服务器
客户端 -> SET c 3 -> 服务器
```

使用管道后，3 条命令一次发出，响应也一次性收回，往返次数降为 1。在 `redis-cli` 中可以用 `echo` 配合管道符演示：

```bash
docker exec -it redis-tutorial redis-cli --pipe <<'EOF'
SET a 1
SET b 2
SET c 3
EOF
```

你应该看到：

```text
All data transferred. Waiting for the last reply...
Last reply received from server.
errors: 0, replies: 3
```

管道只解决「攒一批一起发」的效率问题，不保证这些命令是原子执行的——服务器处理期间可能穿插其他客户端的命令。需要原子性时使用事务。

## 事务：MULTI 与 EXEC

`MULTI` 开启事务，之后的命令进入队列，`EXEC` 一次性按顺序执行整个队列，执行期间不会插入其他客户端的命令：

```text
MULTI
SET order:1001 "created"
DECR stock:sku001
LPUSH orders:pending "order:1001"
EXEC
```

你应该看到：

```text
OK
QUEUED
QUEUED
QUEUED
1) OK
2) (integer) 99
3) (integer) 1
```

每条入队命令返回 `QUEUED`，`EXEC` 按顺序返回每条命令的结果。中途想放弃时使用 `DISCARD`：

```text
MULTI
SET order:1002 "draft"
DISCARD
GET order:1002
```

你应该看到：

```text
OK
QUEUED
OK
(nil)
```

**注意**：Redis 事务保证「整批执行、不被打断」，但不支持回滚。入队阶段会拒绝语法错误的命令，但运行时错误（如对字符串执行 `LPUSH`）只会让那一条命令失败，队列中的其他命令照常执行。这与关系型数据库的事务语义不同，需要应用层自行处理部分失败。

## WATCH：乐观锁

当事务的写入依赖「读到的值没有被人改过」时，用 `WATCH` 监视键：`EXEC` 时如果被监视的键已被其他客户端修改，整个事务放弃执行。下面模拟「库存足够才扣减」：

```text
WATCH stock:sku001
GET stock:sku001
```

假设读到 `"99"`，只要不小于 1 就执行扣减：

```text
MULTI
DECR stock:sku001
EXEC
```

你应该看到：

```text
OK
QUEUED
1) (integer) 98
```

如果在 `WATCH` 和 `EXEC` 之间有其他客户端修改了 `stock:sku001`，`EXEC` 返回 `(nil)`，应用应重试整个「读取—判断—事务」流程。

## Lua 脚本：更强的原子性

当判断逻辑复杂到 `WATCH` 难以表达时，可以用 Lua 脚本把「读取、判断、写入」封装成单个原子命令：

```text
EVAL "local s = redis.call('GET', KEYS[1]) if tonumber(s) > 0 then return redis.call('DECR', KEYS[1]) else return -1 end" 1 stock:sku001
```

你应该看到：

```text
(integer) 97
```

`EVAL` 后的第一个参数 `1` 是键名个数，`KEYS[1]` 即 `stock:sku001`。脚本在服务器端原子执行，是限流、分布式锁等场景的常用手段。初学阶段了解即可，不必急着写复杂脚本。

## 小结

- 管道把多条命令攒成一次网络往返，大幅提升批量写入性能，但不保证原子性。
- `MULTI`/`EXEC` 把命令作为整批原子执行，`DISCARD` 中止，事务不支持回滚。
- `WATCH` 提供乐观锁：被监视键在事务前被改动时 `EXEC` 失败，应重试。
- Lua 脚本在服务器端原子运行，适合封装带判断逻辑的多步操作。

## 练习

1. 用 `--pipe` 一次性写入 10 个 `stats:pageN` 计数键，再用 `--scan` 确认它们都存在。
2. 开启事务写入两个键后执行 `DISCARD`，用 `EXISTS` 验证两个键都没有被创建。
3. 仿照 `WATCH` 示例，写出「余额足够才扣款」的监视流程，并在两个 `redis-cli` 窗口中模拟竞争。

下一步：进入[Python API](/tech-stack/redis/python)，用 redis-py 在程序中完成同样的操作。
