---
inHomePost: false
title: "基本概念"
---

# 基本概念

本页先建立 MongoDB 的数据模型，再启动一个本地实例。后面的所有命令都在这个实例中使用 `taskdb` 数据库和任务管理示例。

## 文档、集合和数据库

MongoDB 使用文档（Document）保存一条记录。文档类似 JSON 对象，但实际以 BSON（Binary JSON）格式存储，因此可以保存日期、二进制数据和 `ObjectId` 等类型。

一个任务文档可以写成这样：

```javascript
{
  _id: "t001",
  title: "编写 API 文档",
  status: "todo",
  priority: 3,
  assigneeId: "u001",
  tags: ["docs", "mongodb"],
  estimateHours: 4,
  checklist: [
    { name: "整理命令", done: true },
    { name: "补充示例", done: false }
  ],
  createdAt: ISODate("2026-01-10T09:00:00Z")
}
```

几个名称的关系如下：

| MongoDB 概念 | 关系型数据库中的近似概念 | 本教程中的示例 |
| --- | --- | --- |
| 数据库（Database） | 数据库 | `taskdb` |
| 集合（Collection） | 表 | `users`、`tasks` |
| 文档（Document） | 行 | 一个用户或一个任务 |
| 字段（Field） | 列 | `status`、`priority`、`tags` |

集合不要求每个文档拥有完全相同的字段，但同一业务集合仍然应该保持稳定的数据约定。这样可以在保留灵活性的同时，让查询和应用代码更容易维护。

## 常用 BSON 类型

| 类型 | 说明 | 示例 |
| --- | --- | --- |
| `String` | UTF-8 字符串 | `"todo"` |
| `Int32`、`Int64` | 整数 | `3` |
| `Double` | 浮点数 | `3.14` |
| `Boolean` | 布尔值 | `true` |
| `Array` | 有序数组 | `["docs", "mongodb"]` |
| `Object` | 嵌套文档 | `{ name: "整理命令", done: true }` |
| `Date` | UTC 日期时间 | `ISODate("2026-01-10T09:00:00Z")` |
| `ObjectId` | 12 字节的唯一标识符 | `ObjectId("...")` |
| `Null` | 空值 | `null` |

如果插入文档时没有提供 `_id`，MongoDB 会自动生成一个 `ObjectId`。本教程为了让查询结果更容易阅读，使用 `t001`、`u001` 这样的字符串作为示例 ID；字符串 ID 和自动生成的 `ObjectId` 都是有效选择，但一个集合应统一约定 ID 的类型。

## 启动 MongoDB

在终端中运行以下命令，启动一个没有启用认证的本地 MongoDB 8.0 容器：

```bash
docker run --name mongodb \
  --publish 27017:27017 \
  --detach \
  mongo:8.0
```

检查容器是否正在运行：

```bash
docker ps --filter name=mongodb
```

输出中应能看到 `mongodb` 容器及 `0.0.0.0:27017->27017/tcp` 端口映射。如果容器已经创建但处于停止状态，可以使用 `docker start mongodb` 重新启动，而不必再次执行 `docker run`。

## 连接并切换数据库

打开一个新的终端，使用 `mongosh` 连接：

```bash
mongosh "mongodb://127.0.0.1:27017"
```

连接成功后，在交互式 Shell 中执行：

```javascript
use taskdb
db.getName()
show collections
```

第一次执行 `use taskdb` 时，数据库可能还不存在。MongoDB 会在第一次写入文档或显式创建集合时真正创建它。此时 `show collections` 没有输出是正常的，下一页会创建集合并插入示例数据。

退出 Shell：

```javascript
exit
```

## 清理本地实例

教程完成后，如果不再需要容器，可以停止并删除它：

```bash
docker stop mongodb
docker rm mongodb
```

这些命令只影响名为 `mongodb` 的教程容器。继续学习时可再次运行上面的 `docker run` 命令。

## 常见错误

- **现象**：`docker run` 报错，提示 `port is already allocated`。
  **原因**：本机 `27017` 端口已被其他容器或进程占用。
  **修复**：执行 `docker ps -a` 找到占用端口的容器并停止它；或改用 `--publish 27018:27017` 启动，同时把后续连接串中的端口改为 `27018`。

- **现象**：终端提示 `mongosh: command not found`。
  **原因**：本机没有安装 MongoDB Shell。
  **修复**：按照 [mongosh 安装文档](https://www.mongodb.com/docs/mongodb-shell/install/)安装；或临时使用容器内置的 Shell：`docker exec -it mongodb mongosh`。

## 小结

- MongoDB 以 BSON 文档存储数据：文档组成集合，集合归属数据库，概念上近似关系型数据库的行、表和数据库。
- 字段类型由 BSON 决定；未提供 `_id` 时自动生成 `ObjectId`，同一集合应统一 ID 类型约定。
- `docker run` 启动容器，`mongosh` 连接实例；`use taskdb` 只切换上下文，数据库在第一次写入时才真正创建。

## 练习

1. 连接后执行 `db.version()`，确认服务端版本号与本教程的 8.0 基线一致。
2. 执行 `show dbs`，观察列表中是否出现 `taskdb`，并用本页关于数据库何时真正创建的说明解释原因。

下一步：进入[集合操作](/tech-stack/mongo/collection)，创建数据容器并准备任务数据。
