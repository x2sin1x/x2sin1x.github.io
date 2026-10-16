---
title: 流程控制与错误处理
weight: 35
---

# 流程控制与错误处理

> 本节目标：根据条件选择执行路径，抛出和捕获异常，并用错误信息定位问题。

## 条件与分支

`if...else` 适合条件分支，`switch` 适合多个离散选项。条件表达式会转换为布尔上下文；空字符串、`0`、`NaN`、`null`、`undefined` 和 `false` 为假值。

```js
const score = 86;
if (score >= 90) {
  console.log("优秀");
} else if (score >= 60) {
  console.log("通过");
} else {
  console.log("继续练习");
}
```

分支条件应表达清楚的业务判断。避免复杂嵌套三元表达式；必要时把判断拆成具名布尔变量。

## 抛出与捕获异常

异常用于报告无法按正常路径继续的错误。抛出 `Error` 或其子类实例，调用者可用 `try...catch` 恢复或补充上下文：

```js
function parsePositiveInteger(text) {
  const value = Number(text);
  if (!Number.isInteger(value) || value <= 0) {
    throw new RangeError("请输入正整数");
  }
  return value;
}

try {
  console.log(parsePositiveInteger("0"));
} catch (error) {
  console.error(error.message);
}
```

`finally` 用于无论成功失败都要执行的收尾逻辑。捕获异常后应处理、转换或重新抛出；不要空 catch 掩盖故障。

## 错误类型与调试

常见错误包括 `SyntaxError`（语法无法解析）、`ReferenceError`（访问不存在或尚不可用的标识符）、`TypeError`（对不适当类型执行操作）和 `RangeError`（值超出有效范围）。

排查时阅读错误堆栈，确认首个属于自己代码的调用位置；检查变量类型和值；使用断点逐步执行。`console.log()` 适合快速观察，浏览器开发者工具和 Node.js 检查器适合交互调试。

## 循环和流程转移

`break` 结束循环或 `switch`，`continue` 跳过当前一轮。条件不变的 `while` 循环会无限执行；为循环设置明确的终止条件。具体循环和迭代器见[集合章节](collections.md)。

## 小结与练习

- 条件语句决定执行路径；将复杂条件命名有助于理解。
- 异常适用于异常情况，捕获后必须有明确处理。
- 错误类型、消息、堆栈和断点共同帮助定位故障。

练习：编写一个解析分数的函数，拒绝非数字或小于 0、大于 100 的输入，并在调用端显示错误消息。
