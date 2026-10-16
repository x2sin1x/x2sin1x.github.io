---
title: 日常类型
weight: 20
---

# 日常类型

> 本节目标：用基础类型描述变量、函数和对象，并知道何时使用联合类型、断言与 `unknown`。

## 原始类型与数组

TypeScript 使用小写的 `string`、`number`、`boolean` 表示 JavaScript 原始类型；大写包装对象类型 `String`、`Number` 通常不应用作注解。

```ts
let title: string = "类型入门";
let page: number = 1;
let published: boolean = false;
const tags: string[] = ["基础", "类型"];
const scores: Array<number> = [90, 88];
```

数组可写成 `T[]` 或 `Array<T>`。前一种更常见；泛型形式在复合类型中有时更容易阅读。

## 函数与对象

参数类型表达函数接受什么，返回类型表达调用结果。返回类型经常可以推断，但公共函数显式标注有助于稳定接口。

```ts
function formatLesson(name: string, minutes: number): string {
  return `${name}：${minutes} 分钟`;
}

type Learner = {
  name: string;
  completed?: number;
  readonly id: number;
};

const learner: Learner = { id: 1, name: "小林" };
console.log(formatLesson(learner.name, learner.completed ?? 0));
```

`?` 表示属性可以缺省；访问时要考虑 `undefined`。`readonly` 限制通过该类型的引用重新赋值属性，但不表示对象深层冻结。

## 联合类型与类型别名

联合类型表示一个值可能属于几种类型之一。使用它前，程序通常先检查当前是哪一种。

```ts
type Identifier = number | string;

function showId(id: Identifier): string {
  return typeof id === "string" ? id.toUpperCase() : `#${id}`;
}
```

`type` 可以命名联合、对象或函数类型，帮助接口获得有意义的名称。它创建类型别名，不会在运行时生成新类或新值。

## 字面量类型与 `as const`

字面量类型把值限制到特定选项，适合状态和配置：

```ts
type Status = "todo" | "doing" | "done";
let status: Status = "todo";
status = "done";
// status = "finished"; // 不属于允许值

const routes = ["/home", "/settings"] as const;
// 推断为只读元组，而不是 string[]
```

`as const` 保留更窄的字面量类型并添加只读属性。它是类型层面的限制，不会在运行时冻结对象。

## `any`、`unknown` 与类型断言

`any` 会关闭该值后续操作的检查；从旧 JavaScript 迁移时可能暂用，但应尽量限制范围。`unknown` 表示尚未确认的值，使用前必须先缩窄。

```ts
function parseCount(input: unknown): number {
  if (typeof input === "number" && Number.isFinite(input)) {
    return input;
  }
  throw new Error("数量必须是有限数字");
}
```

类型断言 `value as SomeType` 告诉编译器“我已确认其类型”，但不会转换或验证数据。只有在编译器缺少上下文、而你确实掌握额外信息时才使用。

## `null`、`undefined`、枚举和特殊类型

严格空值检查启用时，普通 `string` 不包含 `null` 或 `undefined`。可用联合明确表达缺省：`string | undefined`。可选链 `?.` 和空值合并 `??` 是处理可选值的常用操作。

枚举 `enum` 会生成与传统 JavaScript 类型别名不同的运行时构造。很多场景可用字符串字面量联合表达允许值；需要运行时枚举对象时再选择 `enum`。`object` 表示非原始值；`never` 表示不可能到达的值；`void` 常用于没有有用返回值的函数。

## 小结与练习

- 用 `unknown` 接收未经验证的数据，用守卫确认后再使用。
- 用联合类型表达封闭选项；可选属性意味着访问结果可能是 `undefined`。
- 断言不会做运行时校验，`readonly` 也不是深冻结。

练习：定义 `PaymentStatus` 联合类型，并写函数将 `"paid"` 显示为“已支付”，其他状态显示为待处理。下一节：[类型收窄](narrowing.md)，系统学习检查器怎样从运行时条件推导更具体的类型。
