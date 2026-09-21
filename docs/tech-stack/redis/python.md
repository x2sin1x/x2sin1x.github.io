---
title: "Python API"
date: 2026-09-15T09:25:00+08:00
weight: 50
---
# Python API

> 对应官方文档：[redis-py client guide](https://redis.io/docs/latest/develop/clients/redis-py/)

本页把前几页的 `redis-cli` 命令改写成 Python 程序。程序使用 redis-py 连接本地 Redis 8.10，写入任务数据，处理队列，并演示管道和过期的用法。

## 创建 Python 环境

在项目目录中创建并激活虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

安装 redis-py：

```bash
pip install "redis>=8.1"
```

确认安装成功：

```bash
python -c "import redis; print(redis.__version__)"
```

你应该看到：

```text
8.1.0
```

## 连接 Redis

创建文件 `redis_tasks.py`，先建立连接并测试：

```python
import redis

# decode_responses=True 让返回值是 str 而不是 bytes，对新手更友好
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

print(r.ping())  # True 表示连接成功
```

运行程序：

```bash
python redis_tasks.py
```

你应该看到：

```text
True
```

连接失败的常见原因是 Docker 容器没有启动，或端口映射不是 `6379`。

## 写入任务数据

把[数据类型](/tech-stack/redis/data-types)中的哈希、集合和有序集合命令翻译成 redis-py 调用。方法名与命令同名、参数即为命令参数，这是 redis-py 最友好的地方：

```python
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Hash：任务详情，对应 HSET task:t001 field value ...
r.hset("task:t001", mapping={
    "title": "编写 API 文档",
    "status": "todo",
    "priority": 3,
    "assignee": "u001",
})
print(r.hgetall("task:t001"))

# Set：任务标签，对应 SADD / SISMEMBER / SINTER
r.sadd("task:t001:tags", "docs", "redis", "api")
print(r.scard("task:t001:tags"))            # 3
print(r.sismember("task:t001:tags", "redis"))  # True

# Sorted Set：优先级排行，对应 ZADD
r.zadd("board:priority", {"task:t001": 3, "task:t002": 1, "task:t003": 2})
print(r.zrange("board:priority", 0, 1, desc=True, withscores=True))
```

运行程序，你应该看到：

```python
{'title': '编写 API 文档', 'status': 'todo', 'priority': '3', 'assignee': 'u001'}
3
True
[('task:t001', 3.0), ('task:t003', 2.0)]
```

注意两点：哈希取出的所有值都是字符串，`priority` 需要时用 `int()` 转换；`zrange` 的 `desc=True` 等价于命令中的 `REV`。

## 消费任务队列

用列表模拟队列的「生产—消费」流程：

```python
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# 生产：三个任务入队
for task_id in ["task:t001", "task:t002", "task:t003"]:
    r.rpush("queue:tasks", task_id)

# 消费：逐个出队，队列为空时返回 None
while True:
    task_id = r.lpop("queue:tasks")
    if task_id is None:
        break
    status = r.hget(task_id, "status")
    print(f"处理 {task_id}（当前状态：{status}）")
```

运行程序，你应该看到：

```text
处理 task:t001（当前状态：todo）
处理 task:t002（当前状态：None）
处理 task:t003（当前状态：None）
```

`task:t002` 和 `task:t003` 的哈希还不存在，所以状态是 `None`。真实项目中通常在这里补充「检查队列剩余长度」「处理失败回退」等逻辑。

## 管道与过期

redis-py 的 `pipeline()` 对应前一章的管道和事务。默认开启 `MULTI`/`EXEC`（事务模式），`transaction=False` 则退化为纯管道：

```python
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# 纯管道：一次往返写入多个键并设置 TTL
pipe = r.pipeline(transaction=False)
pipe.set("cache:home", "rendered-html", ex=120)   # SET ... EX 120
pipe.set("stats:views", 0)
pipe.incr("stats:views", 9)
results = pipe.execute()
print(results)  # [True, True, 10]

# 事务管道：WATCH + MULTI/EXEC 实现乐观锁
with r.pipeline() as pipe:
    while True:
        try:
            pipe.watch("stats:views")
            current = int(pipe.get("stats:views"))
            pipe.multi()
            pipe.set("stats:views", current + 1)
            pipe.execute()
            break
        except redis.WatchError:
            continue  # 被其他客户端修改，重试

print(r.get("stats:views"))
print(r.ttl("cache:home"))  # 剩余秒数，最大 120
```

运行程序，你应该看到：

```text
[True, True, 10]
11
120
```

> 💡 **新手提示**：redis-py 的 `Redis` 对象自带连接池，应用内创建一个全局实例复用即可，不要为每次请求新建连接。

## 小结

- redis-py 的方法名与 Redis 命令一一对应，`hset`、`zadd`、`lpop` 可以直接从命令参考翻译过来。
- `decode_responses=True` 让程序直接处理 `str`；哈希中的数字同样以字符串返回，需要自行转型。
- `pipeline()` 默认是事务，`transaction=False` 得到纯管道；`WatchError` 对应命令行的 `EXEC` 失败，需要重试。
- `set(..., ex=120)`、`expire()`、`ttl()` 在 Python 中与命令行行为一致。

## 练习

1. 在 Python 中为 `task:t002` 创建哈希，并把它的优先级写入 `board:priority`，用 `zrange` 验证排行变化。
2. 把「消费任务队列」的程序改造成：出队后将该任务哈希的 `status` 字段更新为 `done`。
3. 用 `scan_iter(match="stats:*")` 遍历本页创建的统计键，打印键名和值。

本教程到此结束。可以回到[索引页](/tech-stack/redis/)查看其他章节，或前往 [Redis 官方教程](https://redis.io/tutorials/)继续学习缓存、限流等实战模式。
