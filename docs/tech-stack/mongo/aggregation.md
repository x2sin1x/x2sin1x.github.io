---
inHomePost: false
title: "聚合操作"
---

# 聚合操作

查询适合取出已有文档，聚合（Aggregation）则适合把多条文档转换为新的结果集。本页使用 `taskdb.tasks` 演示聚合管道：每个阶段接收上一个阶段的结果，并将处理后的文档传给下一个阶段。

## 前置条件

请先完成[增删改查](/tech-stack/mongo/document)中的准备步骤，并确保 `tasks` 集合至少包含[集合操作](/tech-stack/mongo/collection)中的三条示例任务。为了让统计结果稳定，本页的查询只依赖这三条任务；如果你修改过数据，可以重新执行种子数据。

## 按状态统计任务数量

先筛选任务，再按 `status` 分组计数：

```javascript
db.tasks.aggregate([
  { $match: {} },
  {
    $group: {
      _id: "$status",
      count: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } }
])
```

预期结果类似：

```text
{ _id: 'doing', count: 1 }
{ _id: 'done', count: 1 }
{ _id: 'todo', count: 1 }
```

`$group` 的 `_id` 是分组键，`$sum: 1` 为每个文档贡献一个计数。`$sort: { _id: 1 }` 按分组值升序排列，字符串默认按二进制顺序比较，因此 `doing` 排在 `done` 前面。将 `$match` 换成 `{ $match: { priority: { $lte: 2 } } }`，就可以只统计高优先级任务。

## 计算总工时

下面的管道计算所有任务的预估工时，并把结果字段改成更容易阅读的名称：

```javascript
db.tasks.aggregate([
  {
    $group: {
      _id: null,
      taskCount: { $sum: 1 },
      totalHours: { $sum: "$estimateHours" },
      averageHours: { $avg: "$estimateHours" }
    }
  },
  {
    $project: {
      _id: 0,
      taskCount: 1,
      totalHours: 1,
      averageHours: { $round: ["$averageHours", 1] }
    }
  }
])
```

`$project` 可以保留、删除或计算字段。这里用 `$round` 将平均工时保留一位小数；它只改变输出，不会修改集合中的原始文档。

## 按负责人统计

任务文档只保存 `assigneeId`。先分组得到统计结果，再用 `$lookup` 关联 `users` 集合，显示负责人的姓名：

```javascript
db.tasks.aggregate([
  {
    $group: {
      _id: "$assigneeId",
      taskCount: { $sum: 1 },
      totalHours: { $sum: "$estimateHours" }
    }
  },
  {
    $lookup: {
      from: "users",
      localField: "_id",
      foreignField: "_id",
      as: "assignee"
    }
  },
  { $unwind: "$assignee" },
  {
    $project: {
      _id: 0,
      assigneeId: "$_id",
      name: "$assignee.name",
      taskCount: 1,
      totalHours: 1
    }
  },
  { $sort: { totalHours: -1 } }
])
```

`$lookup` 要求 `localField` 与 `foreignField` 的值能够精确等值匹配，类型不一致时不会自动转换，相关排查方法见本章末尾的“常见错误”。

## 按标签统计

一个任务可以包含多个标签。使用 `$unwind` 将数组拆成多条中间文档，再分组计数：

```javascript
db.tasks.aggregate([
  { $unwind: "$tags" },
  {
    $group: {
      _id: "$tags",
      taskCount: { $sum: 1 },
      totalHours: { $sum: "$estimateHours" }
    }
  },
  {
    $project: {
      _id: 0,
      tag: "$_id",
      taskCount: 1,
      totalHours: 1
    }
  },
  { $sort: { taskCount: -1, tag: 1 } }
])
```

如果某条任务没有 `tags` 字段，默认情况下它不会产生任何输出行。需要保留空数组或缺失字段时，可以将 `$unwind` 改成：

```javascript
{
  $unwind: {
    path: "$tags",
    preserveNullAndEmptyArrays: true
  }
}
```

## 调试聚合管道

不要一开始就写很长的管道。先运行前两个阶段，检查中间文档的字段形状：

```javascript
db.tasks.aggregate([
  { $match: { status: { $ne: "done" } } },
  { $project: { _id: 0, title: 1, status: 1, tags: 1 } }
])
```

确认字段名称和类型正确后，再追加 `$unwind`、`$group` 或 `$lookup`。阶段顺序会影响结果：例如在 `$unwind` 前后执行 `$group`，得到的计数含义不同。

## 验证查询计划

聚合管道的首个 `$match` 可以利用匹配字段上的索引。先创建一个本地示例索引：

```javascript
db.tasks.createIndex({ status: 1, assigneeId: 1 })
```

查看查询计划：

```javascript
db.tasks.explain("executionStats").aggregate([
  { $match: { status: "doing", assigneeId: "u002" } },
  { $project: { _id: 0, title: 1 } }
])
```

这里的重点是学会使用 `explain` 观察计划，而不是为每个字段盲目创建索引。索引设计应结合真实查询、数据规模和写入成本。

## 常见错误

- **现象**：`$lookup` 之后 `assignee` 数组为空，`$unwind` 使整行结果消失。
  **原因**：关联字段类型不一致，例如 `tasks.assigneeId` 是字符串而 `users._id` 是 `ObjectId`，等值匹配失败。
  **修复**：让两个集合的关联字段使用相同类型；插入数据前先确认 ID 约定。

- **现象**：`$group` 之后，原本文档里的字段“消失”了。
  **原因**：`$group` 输出的文档只包含 `_id` 和阶段内显式定义的字段。
  **修复**：需要携带其他字段时，在 `$group` 中补充累加器，例如 `$first` 取第一个值、`$push` 收集明细。

- **现象**：某条任务没有 `tags` 字段或为空数组，标签统计的结果条数对不上。
  **原因**：`$unwind` 默认会丢弃没有数组元素可拆分的文档。
  **修复**：按“按标签统计”一节的写法加上 `preserveNullAndEmptyArrays: true`，并在业务上决定这类文档的分组键。

- **现象**：聚合随数据量增长明显变慢。
  **原因**：大量文档进入后面的阶段，前面的 `$match` 没有索引可用。
  **修复**：把过滤和缩减文档数的阶段放在管道最前面，并用 `explain` 检查是否使用了索引。

## 小结

- 聚合管道由阶段组成，`$match`、`$group`、`$sort`、`$project`、`$unwind` 和 `$lookup` 覆盖大多数统计场景。
- `$group` 的 `_id` 决定分组键，`_id: null` 表示对全部文档做整体聚合。
- 阶段顺序会改变结果含义；先运行短管道检查中间文档，再逐步追加阶段。
- 管道开头的 `$match` 尽量写在有索引的字段上，并用 `explain("executionStats")` 验证。

## 练习

1. 修改“按负责人统计”的管道，只统计未完成（`status` 不为 `done`）的任务，并保持按总工时降序排列。
2. 在状态统计管道的 `$sort` 后追加一个 `$limit: 1` 阶段，让结果只显示任务数量最多的状态，然后换一组数据验证是否仍然正确。

下一步：进入 [Python API](/tech-stack/mongo/pymongo)，将相同的 CRUD 和聚合操作放进 Python 程序。
