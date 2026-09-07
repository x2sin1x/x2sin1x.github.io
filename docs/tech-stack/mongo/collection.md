---
inHomePost: false
title: "集合操作"
---

# 集合操作

本页在 `taskdb` 数据库中创建两个集合：`users` 保存负责人，`tasks` 保存任务。完成后，后续页面可以直接复用这些数据。

## 前置条件

请先完成[基本概念](/tech-stack/mongo/concept)中的 Docker 启动和 `mongosh` 连接步骤。下面的命令都在 `mongosh` 中执行。

## 创建集合

切换到教程数据库：

```javascript
use taskdb
```

显式创建两个集合：

```javascript
db.createCollection("users")
db.createCollection("tasks")
show collections
```

你应该看到：

```text
tasks
users
```

MongoDB 也支持隐式创建集合。直接运行 `db.tasks.insertOne(...)` 时，如果 `tasks` 不存在，MongoDB 会在写入时创建它。显式创建适合需要在创建时配置集合选项的场景；初学阶段使用隐式创建也很常见。

## 插入示例数据

将两个负责人写入 `users` 集合：

```javascript
db.users.insertMany([
  {
    _id: "u001",
    name: "Alice",
    email: "alice@example.com",
    team: "平台组"
  },
  {
    _id: "u002",
    name: "Bob",
    email: "bob@example.com",
    team: "数据组"
  }
])
```

再写入三条任务：

```javascript
db.tasks.insertMany([
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
  },
  {
    _id: "t002",
    title: "实现任务查询",
    status: "doing",
    priority: 2,
    assigneeId: "u002",
    tags: ["backend", "api"],
    estimateHours: 6,
    checklist: [
      { name: "设计查询条件", done: true },
      { name: "补充分页", done: false }
    ],
    createdAt: ISODate("2026-01-11T09:00:00Z")
  },
  {
    _id: "t003",
    title: "修复登录超时",
    status: "done",
    priority: 1,
    assigneeId: "u001",
    tags: ["bug", "backend"],
    estimateHours: 2,
    checklist: [
      { name: "定位原因", done: true },
      { name: "补充回归测试", done: true }
    ],
    createdAt: ISODate("2026-01-12T09:00:00Z")
  }
])
```

每次 `insertMany` 都会返回 `insertedIds`。如果其中一个 `_id` 已经存在，整批写入可能因为重复键错误而中止。需要重新准备这组固定数据时，可以先在本地教程数据库中清空两个集合，再重新执行插入：

```javascript
db.users.deleteMany({})
db.tasks.deleteMany({})
```

不要在包含真实业务数据的数据库中直接执行这两条清理命令。

## 查看和检查集合

查看集合中的文档数量：

```javascript
db.users.countDocuments()
db.tasks.countDocuments()
```

预期结果分别为 `2` 和 `3`。查看集合统计信息：

```javascript
db.tasks.stats()
```

只查看任务标题和状态：

```javascript
db.tasks.find(
  {},
  { _id: 0, title: 1, status: 1 }
).sort({ _id: 1 })
```

这里的第二个参数是投影，`_id: 0` 表示隐藏 ID，`title: 1` 和 `status: 1` 表示只保留这两个字段。

## 重命名和删除集合

重命名操作会影响后续所有查询：

```javascript
db.tasks.renameCollection("work_items")
db.work_items.renameCollection("tasks")
```

删除集合会同时删除其中的全部文档：

```javascript
db.tasks.drop()
```

因此，删除前应确认当前数据库和集合名称。完成本页后不要执行 `drop()`，否则后续页面将没有可查询的数据。

## 常见错误

- **现象**：`insertMany` 报错 `E11000 duplicate key error`，但检查发现部分文档已经写入。
  **原因**：`insertMany` 默认按顺序写入（`ordered: true`），遇到重复键就停止，之前提交的文档会保留。
  **修复**：先用本页提供的 `deleteMany({})` 清空集合，再重新执行完整的插入命令。

- **现象**：准备重新插入数据时，忘了集合里还残留旧文档，导致统计结果比预期多。
  **原因**：集合不会因为程序结束而清空，数据会一直保留。
  **修复**：执行 `db.tasks.countDocuments()` 检查数量；需要固定的示例数据时，先清空再插入。

## 小结

- 集合可以在写入时隐式创建，也可以用 `createCollection` 显式创建并获得配置选项。
- `insertMany` 返回 `insertedIds`；重复 `_id` 触发 `E11000`，且默认顺序写入会保留先前已插入的文档。
- `renameCollection` 重命名集合，`drop()` 删除集合及其全部文档，两者都会影响后续查询。

## 练习

1. 执行 `db.tasks.stats()`，在输出中找到 `count` 和 `storageSize` 字段，理解它们的含义。
2. 再插入一条 `_id` 为 `"t001"` 的任务，观察报错信息，并用 `findOne` 确认原来的文档没有被覆盖，最后清空集合并重新执行本页的种子数据。

下一步：进入[增删改查](/tech-stack/mongo/document)，使用查询条件和更新操作管理任务文档。
