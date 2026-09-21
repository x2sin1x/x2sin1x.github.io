---
title: "基本概念"
date: 2026-09-15T09:05:00+08:00
weight: 10
---
# 基本概念

> 对应官方文档：[Get started with Redis](https://redis.io/docs/latest/develop/get-started/data-store/)

本页先建立 Redis 的数据模型，再启动一个本地实例。后面的所有命令都在这个实例中执行，并沿用同一套任务管理示例的键命名约定。

## 这是什么？

Redis（Remote Dictionary Server）是一个基于内存的键值数据库。可以把整个数据库想象成一个巨大的字典：每个条目有一个唯一的键（key），对应的值（value）可以是字符串、哈希、列表等结构。由于数据主要保存在内存中，读写延迟通常在亚毫秒级别。

**通俗解释**：如果 MongoDB 像一堆可以按字段查询的 JSON 文件，Redis 就更像一面贴满便签的白板——每张便签有固定位置（键），取用极快，但便签本身适合写短小的内容，而不是整篇文档。

### 适用场景

- **缓存**：把关系型数据库的查询结果暂存到 Redis，设置过期时间，减轻后端压力。
- **会话存储**：Web 应用的登录态天然有 TTL 需求，与 Redis 的过期机制非常契合。
- **计数与排行榜**：`INCR` 原子自增、有序集合按分数排序，几行命令就能实现。
- **队列与消息**：列表和 Pub/Sub 可以承担轻量级的任务队列和广播。

> 💡 **新手提示**：Redis 不是用来替代 MongoDB 或 MySQL 的，而是与它们配合。适合放进来的是「读得多、体积小、允许丢失或可重建」的数据。

## 键值模型

Redis 最核心的约定有三条：

- **键是二进制安全的字符串**：`task:t001`、`user:u001:follower` 这样的冒号分层命名是社区惯例，但 Redis 本身不解析键的含义。
- **值有类型**：值的类型决定可用的命令，不能对列表执行 `HGET`。
- **一个键只有一个值**：想保存多个字段时，要么换用哈希等复合类型，要么用多个键组合表达。

查看某个键的类型使用 `TYPE` 命令，稍后的章节会反复用到。

## 启动本地实例

使用 Docker 启动 Redis 8.10：

```bash
docker run --name redis-tutorial --publish 6379:6379 --detach redis:8.10
```

确认容器在运行：

```bash
docker ps --filter name=redis-tutorial
```

你应该看到类似输出：

```text
CONTAINER ID   IMAGE         ...   NAMES
3f9c2a1b0d8e   redis:8.10    ...   redis-tutorial
```

## 连接与第一条命令

Redis 自带命令行客户端 `redis-cli`。容器内直接执行：

```bash
docker exec -it redis-tutorial redis-cli
```

进入交互界面后，先测试连通性：

```text
PING
```

你应该看到：

```text
PONG
```

写入并读取一个字符串键：

```text
SET greeting "hello redis"
GET greeting
```

你应该看到：

```text
OK
"hello redis"
```

删除键并确认它已经不存在：

```text
DEL greeting
GET greeting
```

你应该看到：

```text
(integer) 1
(nil)
```

> 💡 **新手提示**：返回值中的 `(nil)` 表示键不存在，`(integer) 1` 表示命令影响了 1 个元素。读懂这两类返回值是排查问题的第一步。

## 逻辑数据库

一个 Redis 实例默认提供 16 个逻辑数据库，编号 `0` 到 `15`，用 `SELECT` 切换：

```text
SELECT 0
```

你应该看到：

```text
OK
```

不同逻辑数据库之间完全隔离，但同一连接同一时刻只能使用一个。实践中绝大多数应用只用默认的 `0` 号库；多业务隔离更推荐部署多个实例而不是共用编号。

## 常见错误

- **现象**：`docker run` 报错，提示 `port is already allocated`。
  **原因**：本机 `6379` 端口已被其他容器或本地 Redis 占用。
  **修复**：执行 `docker ps -a` 找到占用端口的容器并停止它；或改用 `--publish 6380:6379` 启动，同时把后续连接中的端口改为 `6380`。

- **现象**：终端提示 `WRONGTYPE Operation against a key holding the wrong kind of value`。
  **原因**：对某个键执行了与其值类型不匹配的命令，例如对字符串键执行 `HGET`。
  **修复**：先用 `TYPE 键名` 确认类型，再选择对应类型的命令。

- **现象**：本机执行 `redis-cli` 提示 `command not found`。
  **原因**：本机没有安装 Redis 命令行工具。
  **修复**：直接使用容器内置客户端 `docker exec -it redis-tutorial redis-cli`，无需本机安装。

## 小结

- Redis 是内存键值数据库：键是二进制安全字符串，值的类型决定可用命令。
- `PING`、`SET`、`GET`、`DEL`、`TYPE` 是验证环境和学习模型的最小命令集。
- 一个实例包含 16 个逻辑数据库，日常使用默认的 `0` 号库即可。
- Redis 适合缓存、会话、计数等小而热的场景，而不是替代主数据库。

## 练习

1. 执行 `SET counter 1`，然后连续执行 3 次 `INCR counter`，用 `GET counter` 确认结果为 `4`。
2. 对 `counter` 执行 `TYPE counter`，观察返回的 `string`；再尝试执行 `HGET counter x`，阅读 `WRONGTYPE` 报错并解释原因。

下一步：进入[数据类型](/tech-stack/redis/data-types)，用五种核心数据类型为任务数据建模。
