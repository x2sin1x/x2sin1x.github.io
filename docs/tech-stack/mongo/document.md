---
inHomePost: false
title: "增删改查"
---

# 增删改查

MongoDB 的 CRUD 分别代表 Create、Read、Update 和 Delete。本页继续使用[集合操作](/tech-stack/mongo/collection)准备的 `taskdb.tasks` 集合，每条命令都可以在 `mongosh` 中直接执行。

## 准备数据库

如果刚启动了新的容器，请先连接并切换数据库：

```bash
mongosh "mongodb://127.0.0.1:27017/taskdb"
```

如果集合中没有三条示例任务，请先回到[集合操作](/tech-stack/mongo/collection)执行种子数据代码。

## 插入文档

插入一条任务：

```javascript
db.tasks.insertOne({
  _id: "t004",
  title: "增加任务提醒",
  status: "todo",
  priority: 2,
  assigneeId: "u002",
  tags: ["notification"],
  estimateHours: 3,
  createdAt: ISODate("2026-01-13T09:00:00Z")
})
```

插入多条文档时使用 `insertMany`：

```javascript
db.tasks.insertMany([
  {
    _id: "t005",
    title: "整理错误码",
    status: "todo",
    priority: 3,
    assigneeId: "u001",
    tags: ["api"],
    estimateHours: 2,
    createdAt: ISODate("2026-01-14T09:00:00Z")
  },
  {
    _id: "t006",
    title: "补充部署脚本",
    status: "doing",
    priority: 2,
    assigneeId: "u002",
    tags: ["devops", "backend"],
    estimateHours: 5,
    createdAt: ISODate("2026-01-15T09:00:00Z")
  }
])
```

如果再次运行包含相同 `_id` 的插入命令，会收到 `E11000 duplicate key error`。这是 MongoDB 保证 `_id` 唯一的结果，不是连接故障。

## 查询文档

查询集合中的全部任务：

```javascript
db.tasks.find()
```

查询条件写在第一个参数中。例如，查询所有进行中的任务：

```javascript
db.tasks.find({ status: "doing" })
```

MongoDB 使用点号访问嵌套字段。查询包含未完成清单项的任务：

```javascript
db.tasks.find({ "checklist.done": false })
```

数组字段可以用值匹配。查询带有 `backend` 标签的任务：

```javascript
db.tasks.find({ tags: "backend" })
```

常用比较和逻辑运算符如下：

```javascript
// 优先级小于等于 2 的任务
db.tasks.find({ priority: { $lte: 2 } })

// 估时在 2 到 5 小时之间的任务
db.tasks.find({ estimateHours: { $gte: 2, $lte: 5 } })

// 待办或进行中的任务
db.tasks.find({ status: { $in: ["todo", "doing"] } })

// 负责人是 u001 且优先级不为 1
db.tasks.find({
  $and: [
    { assigneeId: "u001" },
    { priority: { $ne: 1 } }
  ]
})
```

### 投影、排序和分页

使用投影减少返回字段。`_id` 默认会返回，因此要显式设置为 `0` 才能隐藏：

```javascript
db.tasks.find(
  { status: { $ne: "done" } },
  { _id: 0, title: 1, status: 1, priority: 1 }
)
```

按优先级升序、创建时间降序排列，并取前两条：

```javascript
db.tasks.find({})
  .sort({ priority: 1, createdAt: -1 })
  .skip(0)
  .limit(2)
```

`skip` 和 `limit` 适合入门示例。数据量很大时，应结合稳定的排序字段和范围查询设计分页方式。

## 更新文档

使用 `$set` 修改字段，不会影响同一文档中的其他字段：

```javascript
db.tasks.updateOne(
  { _id: "t001" },
  { $set: { status: "doing", priority: 2 } }
)
```

使用 `$inc` 增加数值：

```javascript
db.tasks.updateOne(
  { _id: "t001" },
  { $inc: { estimateHours: 1 } }
)
```

使用 `$push` 向数组追加元素：

```javascript
db.tasks.updateOne(
  { _id: "t001" },
  { $push: { tags: "tutorial" } }
)
```

批量更新所有待办任务：

```javascript
db.tasks.updateMany(
  { status: "todo" },
  { $set: { reviewRequired: true } }
)
```

更新后立即验证：

```javascript
db.tasks.find(
  { _id: "t001" },
  { _id: 0, title: 1, status: 1, priority: 1, estimateHours: 1, tags: 1 }
)
```

### 更新或插入（upsert）

`upsert: true` 表示找不到匹配文档时插入一条新文档：

```javascript
db.tasks.updateOne(
  { _id: "t007" },
  {
    $set: {
      title: "配置备份任务",
      status: "todo",
      priority: 3,
      assigneeId: "u001",
      tags: ["ops"],
      estimateHours: 2
    },
    $setOnInsert: {
      createdAt: ISODate("2026-01-16T09:00:00Z")
    }
  },
  { upsert: true }
)
```

## 删除文档

删除指定任务：

```javascript
db.tasks.deleteOne({ _id: "t007" })
```

删除所有已完成任务前，先用同样的条件查询确认范围：

```javascript
db.tasks.find({ status: "done" })
db.tasks.deleteMany({ status: "done" })
```

`deleteMany({})` 会删除当前集合中的全部文档。清空本地教程数据时可以使用它，但不要把空条件删除命令带到生产数据库。

## 完成检查

运行下面的查询，确认还剩哪些未完成任务：

```javascript
db.tasks.find(
  { status: { $ne: "done" } },
  { _id: 1, title: 1, status: 1 }
).sort({ _id: 1 })
```

## 常见错误

- **现象**：`updateOne` 的第二个参数写成 `{ status: "done" }` 这类不含操作符的文档，命令直接报错。
  **原因**：`updateOne` 和 `updateMany` 只接受以 `$` 开头的更新操作符；整篇替换文档需要使用 `replaceOne`。
  **修复**：把字段改动包进 `$set`；确实要整体替换时改用 `replaceOne`，并注意它会丢弃未列出的字段。

- **现象**：执行 `updateMany` 或 `deleteMany` 后，受影响的文档数远超预期。
  **原因**：第一个过滤条件为 `{}` 时会匹配集合中的全部文档。
  **修复**：先用相同条件执行 `db.tasks.countDocuments({...})` 确认范围，再执行更新或删除。

- **现象**：`$inc` 一个字符串字段时报错。
  **原因**：`$inc` 只能作用于数值类型字段。
  **修复**：确认字段类型；需要修改类型时先检查文档结构，再决定是新增字段还是迁移数据。

## 小结

- 插入使用 `insertOne` 和 `insertMany`；重复 `_id` 会触发 `E11000`，这是唯一性约束在起作用。
- 查询条件支持点号访问嵌套字段、数组值匹配，以及 `$gte`、`$in`、`$ne` 等运算符。
- 更新必须通过 `$set`、`$inc`、`$push` 等操作符完成；`upsert: true` 可以在找不到匹配文档时插入。
- 删除前先用相同条件查询确认范围；`deleteMany({})` 只应出现在本地教程数据库中。

## 练习

1. 把 `t004` 的状态更新为 `done`，同时向它的 `tags` 数组追加 `"persistence"`，再用一次 `find` 验证两个字段都发生了变化。
2. 用 `updateMany` 把所有 `priority` 小于等于 2 且未完成的任务标记 `reviewRequired: true`，查看返回结果中的 `matchedCount` 和 `modifiedCount` 是否一致，并解释原因。

下一步：进入[聚合操作](/tech-stack/mongo/aggregation)，把多条任务转换成统计结果。
