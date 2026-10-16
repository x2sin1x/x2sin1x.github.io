---
title: 从类型创建类型
weight: 60
---

# 从类型创建类型

> 本节目标：组合泛型和类型运算符，从现有类型推导新类型，减少重复声明。

## 泛型：参数化类型

泛型类型可把类型作为参数。它不等同于 `any`：类型关系被保留，并由调用点具体化。

```ts
interface ApiResponse<T> {
  data: T;
  receivedAt: Date;
}

type User = { id: number; name: string };
const response: ApiResponse<User> = {
  data: { id: 1, name: "小林" },
  receivedAt: new Date(),
};
```

泛型约束 `T extends { id: number }` 可限定可接受类型；默认参数 `T = unknown` 可用于可省略的类型参数。避免仅因重复就抽出复杂泛型，抽象应让调用者更容易理解。

## `keyof`、类型上下文中的 `typeof` 与索引访问

`keyof T` 产生类型 `T` 的键联合；类型位置的 `typeof value` 读取变量的静态类型；`T[K]` 读取属性类型。

```ts
const settings = { theme: "dark", pageSize: 20 };
type Settings = typeof settings;
type SettingKey = keyof Settings; // "theme" | "pageSize"
type PageSize = Settings["pageSize"]; // number
```

运行时 `typeof value` 和类型操作 `typeof value` 使用同一关键字，但发生在不同语法位置。索引访问也可以处理数组：`typeof values[number]` 表示数组元素类型。

## 条件类型

条件类型 `A extends B ? X : Y` 在类型层面选择分支。对裸类型参数使用时，联合类型会逐成员分配条件，称为 distributive conditional type。

```ts
type ElementOf<T> = T extends readonly (infer Item)[] ? Item : T;

type A = ElementOf<string[]>; // string
type B = ElementOf<number>; // number
```

`infer` 在匹配结构时捕获类型。条件类型递归和分布规则功能强，但可读性成本较高；公共类型尽量提供容易理解的名称并测试边界情况。

## 映射类型

映射类型遍历已有键并为每个属性生成新属性：

```ts
type Mutable<T> = {
  -readonly [K in keyof T]-?: T[K];
};

type DraftTask = Mutable<{
  readonly id: number;
  title?: string;
}>;
```

`?` 与 `readonly` 可用 `+` 添加或用 `-` 移除。常见标准工具类型 `Partial<T>`、`Required<T>`、`Readonly<T>` 和 `Pick<T, K>` 都建立在类似机制上，详见[官方 Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)。

## 模板字面量类型

模板字面量可将字符串字面量类型拼接，并形成受限命名空间：

```ts
type EventName = "open" | "close";
type HandlerName = `on${Capitalize<EventName>}`;
// "onOpen" | "onClose"
```

它可与映射类型结合，生成事件处理器、属性名或 API 路径类型。它只在编译时约束字符串，不会自动创建运行时处理器。

## 小结与练习

- `keyof`、`typeof` 和索引访问用于从现有类型提取信息。
- 条件与映射类型适合表达通用转换；避免为复杂而复杂的类型体操。
- 字符串字面量类型可以组合，但不能替代运行时校验。

练习：定义 `ApiResponse<T>`；再创建 `Editable<T>`，移除所有只读属性并将可选属性变为必需属性。下一节：[类](classes.md)，把类型系统与 JavaScript 类语法联系起来。
