---
title: 类型收窄
weight: 30
---

# 类型收窄

> 本节目标：通过 JavaScript 运行时检查缩小联合类型，并用判别联合保证分支完整。

## 控制流分析

类型收窄（narrowing）是检查器根据分支、赋值和返回路径，把一个较宽的类型推导为更具体类型的过程。它依赖代码中真实存在的判断，而不是注释。

```ts
function printLength(value: string | string[] | null): string {
  if (value === null) return "没有内容";
  if (typeof value === "string") return `${value.length} 个字符`;
  return `${value.length} 项`;
}
```

首个分支排除 `null`，第二个分支再区分字符串和数组。每个路径都经过检查后才访问对应成员。

## 常见类型守卫

- `typeof value === "string"`：适用于 JavaScript 原始类型。注意 `typeof null` 的历史结果是 `"object"`。
- `Array.isArray(value)`：识别数组。
- `value instanceof Date`：根据原型链识别实例。
- `"kind" in value`：检查对象是否有属性，适用于有结构差异的对象联合。
- `===` / `!==`：按具体值排除联合成员。

```ts
function describe(value: string | number | string[]): string {
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "number") return value.toFixed(2);
  return value.toUpperCase();
}
```

真值判断也会收窄，但空字符串、`0` 和 `false` 会走假分支。若它们是合法数据，使用显式的 `!== undefined` 或 `!== null` 判断。

## 用户自定义类型谓词

当判断逻辑复用或无法由内置守卫表达时，可写类型谓词。谓词签名中的 `value is T` 是对检查器的承诺，函数实现仍需正确：

```ts
type Learner = { name: string; completed: number };

function isLearner(value: unknown): value is Learner {
  return typeof value === "object"
    && value !== null
    && "name" in value
    && typeof value.name === "string"
    && "completed" in value
    && typeof value.completed === "number";
}
```

本例对对象的属性分别检查，适合说明概念；复杂外部数据通常使用 schema 校验库并处理校验错误，而不是维护大量手写谓词。

## 判别联合与穷尽检查

给每种对象变体加一个共同的字面量字段，可以让 `switch` 精确区分它们：

```ts
type Result =
  | { kind: "success"; value: string }
  | { kind: "failure"; message: string };

function render(result: Result): string {
  switch (result.kind) {
    case "success": return result.value;
    case "failure": return `错误：${result.message}`;
    default: return assertNever(result);
  }
}

function assertNever(value: never): never {
  throw new Error(`未处理的结果：${JSON.stringify(value)}`);
}
```

如果未来新增一种 `Result`，`assertNever(result)` 会产生类型错误，提醒开发者补上分支。这比静默返回默认文本更可靠。

## 常见错误与练习

- **只判断真值**：会把 `0` 和空字符串误当成缺失值；明确判断缺省条件。
- **不安全地声称类型谓词成立**：谓词实现错误会误导检查器，必要时做逐字段验证。
- **使用强制断言绕过分支**：优先写出能证明类型的判断。

练习：定义包含 `loading`、`success`、`error` 的请求状态联合，并用 `switch` 返回对应文本；新增第四种状态后确认穷尽检查能提示遗漏。下一节：[深入函数](functions.md)，把类型信息用于设计可靠调用边界。
