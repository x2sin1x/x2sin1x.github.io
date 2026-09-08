---
title: "Python API"
weight: 50
---

# Python API

本页把前几页的 `mongosh` 命令改写成 Python 程序。程序使用 PyMongo 的同步 API，连接本地 MongoDB 8.0，写入任务数据，查询未完成任务，并运行一个聚合统计。

## 创建 Python 环境

在项目目录中创建并激活虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell 使用：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

安装 PyMongo：

```bash
python -m pip install "pymongo>=4.8,<5"
```

确认驱动版本：

```bash
python -c "import pymongo; print(pymongo.version)"
```

请先按照[基本概念](/tech-stack/mongo/concept)启动名为 `mongodb` 的容器。

## 连接并检查服务

创建 `mongo_tasks.py`，写入下面的代码：

```python
import os

from pymongo import MongoClient
from pymongo.errors import PyMongoError


MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")


def main() -> None:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5_000)

    try:
        client.admin.command("ping")
        print("MongoDB 连接成功")
    except PyMongoError as exc:
        print(f"MongoDB 连接失败: {exc}")
        raise SystemExit(1) from exc
    finally:
        client.close()


if __name__ == "__main__":
    main()
```

运行程序：

```bash
python mongo_tasks.py
```

看到 `MongoDB 连接成功` 后再继续。`serverSelectionTimeoutMS` 让连接失败在 5 秒后返回，而不是长时间等待。`client.close()` 应在程序结束时调用；在 Web 服务中通常将一个客户端实例复用于多个请求。

## 写入和查询任务

将 `mongo_tasks.py` 替换为下面的完整示例。程序每次运行都会重置本地 `taskdb` 数据库中的两个集合，因此输出保持可重复。不要在真实数据库中直接使用这种清理方式。

```python
import os
from datetime import datetime, timezone

from pymongo import DESCENDING, MongoClient
from pymongo.errors import PyMongoError


MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")


def build_seed_data() -> tuple[list[dict], list[dict]]:
    users = [
        {
            "_id": "u001",
            "name": "Alice",
            "email": "alice@example.com",
            "team": "平台组",
        },
        {
            "_id": "u002",
            "name": "Bob",
            "email": "bob@example.com",
            "team": "数据组",
        },
    ]
    tasks = [
        {
            "_id": "t001",
            "title": "编写 API 文档",
            "status": "todo",
            "priority": 3,
            "assigneeId": "u001",
            "tags": ["docs", "mongodb"],
            "estimateHours": 4,
            "createdAt": datetime(2026, 1, 10, tzinfo=timezone.utc),
        },
        {
            "_id": "t002",
            "title": "实现任务查询",
            "status": "doing",
            "priority": 2,
            "assigneeId": "u002",
            "tags": ["backend", "api"],
            "estimateHours": 6,
            "createdAt": datetime(2026, 1, 11, tzinfo=timezone.utc),
        },
        {
            "_id": "t003",
            "title": "修复登录超时",
            "status": "done",
            "priority": 1,
            "assigneeId": "u001",
            "tags": ["bug", "backend"],
            "estimateHours": 2,
            "createdAt": datetime(2026, 1, 12, tzinfo=timezone.utc),
        },
    ]
    return users, tasks


def main() -> None:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5_000)

    try:
        client.admin.command("ping")
        database = client["taskdb"]
        users_collection = database["users"]
        tasks_collection = database["tasks"]

        users, tasks = build_seed_data()
        users_collection.delete_many({})
        tasks_collection.delete_many({})
        users_collection.insert_many(users)
        tasks_collection.insert_many(tasks)

        unfinished = list(
            tasks_collection.find(
                {"status": {"$ne": "done"}},
                {"_id": 0, "title": 1, "status": 1},
            ).sort("createdAt", DESCENDING)
        )
        print("未完成任务:")
        for task in unfinished:
            print(f"- {task['title']} ({task['status']})")

        summary = list(
            tasks_collection.aggregate(
                [
                    {
                        "$group": {
                            "_id": "$status",
                            "count": {"$sum": 1},
                            "hours": {"$sum": "$estimateHours"},
                        }
                    },
                    {"$sort": {"_id": 1}},
                ]
            )
        )
        print("状态统计:")
        for item in summary:
            print(f"- {item['_id']}: {item['count']} 条, {item['hours']} 小时")
    except PyMongoError as exc:
        print(f"MongoDB 操作失败: {exc}")
        raise SystemExit(1) from exc
    finally:
        client.close()


if __name__ == "__main__":
    main()
```

运行：

```bash
python mongo_tasks.py
```

预期输出的顺序如下：

```text
未完成任务:
- 实现任务查询 (doing)
- 编写 API 文档 (todo)
状态统计:
- doing: 1 条, 6 小时
- done: 1 条, 2 小时
- todo: 1 条, 4 小时
```

“状态统计”按 `_id` 升序排列，字符串按二进制顺序比较，所以 `doing` 排在 `done` 前面，与[聚合操作](/tech-stack/mongo/aggregation)一页的结果一致。

两处值得注意的细节：

- `find()` 返回游标（Cursor），结果在迭代时才分批从服务端读取；示例用 `list(...)` 一次性取回，方便打印和统计条数。
- 示例统一使用带 `timezone.utc` 的 aware datetime。PyMongo 会把不含时区的 naive `datetime` 按 UTC 写入，读取时同样返回 UTC；展示前需要自行转换为本地时区。

## 使用环境变量连接

不要把带有真实凭据的连接字符串写进源代码。开发环境可以通过环境变量覆盖默认地址：

```bash
export MONGO_URI="mongodb://127.0.0.1:27017/taskdb"
python mongo_tasks.py
```

Windows PowerShell：

```powershell
$env:MONGO_URI = "mongodb://127.0.0.1:27017/taskdb"
python mongo_tasks.py
```

启用认证的 MongoDB 实例可以使用类似 `mongodb://user:password@host:27017/taskdb?authSource=admin` 的 URI，但用户名、密码和 `authSource` 必须根据服务端配置填写。

## 常见问题

| 现象 | 检查方式 |
| --- | --- |
| `ServerSelectionTimeoutError` | 执行 `docker ps`，确认 `mongodb` 容器正在运行且端口为 `27017`。 |
| `Connection refused` | 确认 URI 使用 `127.0.0.1:27017`，并检查端口是否被其他程序占用。 |
| 查询结果为空 | 在 `mongosh` 中执行 `use taskdb` 和 `db.tasks.countDocuments()`，确认数据库名称和种子数据正确。 |
| `ModuleNotFoundError: pymongo` | 激活 `.venv`，再运行 `python -m pip install pymongo`。 |
| 时间字段与预期相差若干小时 | 检查写入时是否使用了 naive datetime；PyMongo 按 UTC 存储，展示时需转换为本地时区。 |
| `InvalidDocument` 报错，提示无法编码对象 | 检查文档里是否混入了 PyMongo 无法编码的 Python 类型（如 `set` 或自定义类），先转换成 BSON 支持的类型。 |

## 小结

- PyMongo 的方法名与 `mongosh` 命令一一对应，只是改成 Python 的 snake_case 风格，查询和聚合文档完全通用。
- `MongoClient` 是线程安全的连接入口，进程内复用一个实例即可；脚本结束时调用 `close()`。
- 连接串通过环境变量注入，不要把凭据写进源代码；写入时间数据时显式带上时区。

## 练习

1. 修改程序：查询 `tags` 包含 `"backend"` 的任务，只返回 `title` 和 `status`，并打印结果。
2. 在状态统计管道的 `$group` 后追加 `{"$match": {"hours": {"$gt": 4}}}`，运行程序，核对输出是否只剩 `doing` 一行，并解释原因。

## 下一步

至此，你已经可以在 Python 中复用 MongoDB 的文档查询和聚合能力。可以回到[聚合操作](/tech-stack/mongo/aggregation)调整管道，再将它复制到 `tasks_collection.aggregate(...)` 中。

继续深入时，建议按这个顺序阅读 MongoDB 手册：[索引](https://www.mongodb.com/docs/manual/indexes/)提升查询性能，[事务](https://www.mongodb.com/docs/manual/core/transactions/)保证多文档一致性，[副本集与部署](https://www.mongodb.com/docs/manual/replication/)了解生产环境的高可用和数据安全。
