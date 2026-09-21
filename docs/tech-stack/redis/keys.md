---
title: "键与过期"
date: 2026-09-15T09:15:00+08:00
weight: 30
---
# 键与过期

> 对应官方文档：[How Redis expires keys](https://redis.io/docs/latest/develop/use/keyspace/#how-redis-expires-keys) 与 [Scanning keys](https://redis.io/docs/latest/develop/use/keyspace/#scanning-keys)

键空间（keyspace）是所有键的总称。本页学习如何安全地遍历键、删除键，以及 Redis 最有特色的过期机制——它是缓存、会话等场景的核心。

## 前置条件

请先完成[数据类型](/tech-stack/redis/data-types)中的示例，确保 `task:t001`、`queue:tasks` 等键已存在。下面的命令都在 `redis-cli` 中执行。

## 检查与重命名

```text
EXISTS task:t001
TYPE task:t001
RENAME task:t001 task:t101
EXISTS task:t001
EXISTS task:t101
```

你应该看到：

```text
(integer) 1
hash
OK
(integer) 0
(integer) 1
```

`EXISTS` 返回 `1` 表示键存在、`0` 表示不存在；`RENAME` 是原子操作，重命名后旧键立即消失。

## 删除键：DEL 与 UNLINK

```text
DEL task:t101
```

你应该看到：

```text
(integer) 1
```

`DEL` 同步删除并阻塞其他命令，键越大耗时越长。`UNLINK` 先从键空间摘除键，实际内存释放在后台异步完成，是删除大键时的推荐选择：

```text
UNLINK task:t101
```

## 设置过期时间

用 `EXPIRE` 为键设置 TTL（Time To Live，剩余存活秒数）：

```text
SET session:u001 "active"
EXPIRE session:u001 60
TTL session:u001
```

你应该看到：

```text
OK
(integer) 1
(integer) 59
```

`TTL` 的返回值有三种含义：正数是剩余秒数；`-1` 表示键存在但没有过期时间；`-2` 表示键不存在。

过期时间也可以在写入时一步完成，验证码这类「限时一次性数据」通常这样写：

```text
SET captcha:u001 "824193" EX 300
TTL captcha:u001
```

你应该看到：

```text
OK
(integer) 300
```

还可以用 `PERSIST` 移除过期时间，让键变成永久键：

```text
PERSIST session:u001
TTL session:u001
```

你应该看到：

```text
(integer) 1
(integer) -1
```

> 💡 **新手提示**：对同一个键再次执行 `SET` 会清除它的 TTL。想「更新值但保留过期时间」时，应使用 `SET key value KEEPTTL` 或继续用 `EXPIRE` 补设。

Redis 通过惰性删除（访问时检查）加定期抽样删除来清理过期键，所以过期键可能在 TTL 归零后的一小段时间内仍占用内存，这是正常现象。

## 遍历键：SCAN 而不是 KEYS

`KEYS pattern` 会一次性扫描全库并阻塞 Redis，键多时可能造成线上卡顿，生产环境应避免使用。`SCAN` 用游标分批遍历，每次只处理少量键：

```text
SCAN 0 MATCH task:* COUNT 100
```

你应该看到类似输出（游标值取决于实际数据）：

```text
1) "0"
2) 1) "task:t001:tags"
   2) "task:t001"
```

返回的第一行是下一次迭代的游标，`0` 表示遍历结束。在 `redis-cli` 中可以直接用 `--scan` 参数自动循环：

```bash
docker exec -it redis-tutorial redis-cli --scan --pattern "task:*"
```

你应该看到：

```text
task:t001:tags
task:t001
```

## 键命名建议

- 用冒号分层，如 `task:t001:tags`，便于按前缀管理和扫描。
- 把对象类型放进键名，如 `session:u001`、`stats:views`，读命令时一目了然。
- 避免超长键名：键本身也占内存，长键名应在不损失可读性的前提下缩短。

## 小结

- `EXISTS`、`TYPE`、`RENAME` 用于检查和整理键；删除大键优先用 `UNLINK`。
- `EXPIRE`/`SET ... EX` 设置 TTL，`TTL` 返回剩余秒数或 `-1`/`-2` 状态码，`PERSIST` 取消过期。
- 重新 `SET` 会清除 TTL，需要保留时使用 `KEEPTTL`。
- 线上遍历键使用 `SCAN` 或 `redis-cli --scan`，不要用会阻塞的 `KEYS`。

## 练习

1. 写入 `cache:home` 并设置 120 秒过期，然后用 `TTL` 观察数值递减，等它过期后再 `GET` 并解释 `(nil)`。
2. 对 `cache:home` 重新 `SET` 一次值，检查 `TTL` 是否变成 `-1`，再用 `KEEPTTL` 验证保留过期时间的写法。
3. 使用 `--scan` 列出所有以 `queue:` 开头的键。

下一步：进入[管道与事务](/tech-stack/redis/pipeline)，学习批量执行命令与原子性保证。
