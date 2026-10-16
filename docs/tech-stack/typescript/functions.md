---
title: 深入函数
weight: 40
---

# 深入函数

> 本节目标：描述函数调用形状，使用可选参数、泛型与重载表达常见 API。

## 函数类型与回调

函数类型由参数和返回值构成。参数名是描述信息，类型写在冒号后：

```ts
type Formatter = (value: number) => string;

const format: Formatter = (value) => value.toFixed(1);

function applyFormat(value: number, formatter: Formatter): string {
  return formatter(value);
}
```

上下文类型推断会根据 `Formatter` 自动推断箭头函数的 `value` 是 `number`。这就是为什么回调参数常不需要再写一遍类型。

## 可选参数、默认值和剩余参数

可选参数写作 `name?: T`，调用时可省略，函数体中类型会包含 `undefined`。默认参数在省略或传入 `undefined` 时生效；剩余参数收集零个或多个参数。

```ts
function label(name: string, prefix = "学员"): string {
  return `${prefix}：${name}`;
}

function total(...values: number[]): number {
  return values.reduce((sum, value) => sum + value, 0);
}
```

必需参数不能排在可选参数之后，除非可选参数采用默认值或通过对象参数建模。参数多且含义相近时，使用选项对象通常比多个布尔参数更易读。

## 泛型函数

泛型让函数保留输入与输出之间的类型关系。下面的函数返回与输入相同类型的数组：

```ts
function asArray<T>(value: T): T[] {
  return [value];
}

const names = asArray("Mina"); // string[]
const ids = asArray<number | string>(12);
```

通常让检查器推断类型参数即可。只有推断不够明确，或调用点需要表达特定关系时，才显式给出 `<T>`。

## 约束与 `keyof`

泛型函数只能使用它已知的操作。约束用 `extends` 声明调用者必须提供的结构：

```ts
function getProperty<T, K extends keyof T>(object: T, key: K): T[K] {
  return object[key];
}

const user = { name: "小林", age: 20 };
const age = getProperty(user, "age"); // number
```

`K extends keyof T` 保证键确实存在；返回 `T[K]` 保留属性对应的精确类型。不要为了“泛型化”而增加没有必要的类型参数。

## 函数重载与 `this`

重载用多个调用签名表达不同输入对应的返回类型，随后提供一个兼容实现：

```ts
function makeLabel(value: string): string;
function makeLabel(value: number): string;
function makeLabel(value: string | number): string {
  return typeof value === "string" ? value : `编号 ${value}`;
}
```

调用者只能使用公开重载签名；实现签名不直接可见。若联合参数就足够清楚，优先使用联合类型，避免重载组合爆炸。

JavaScript 的 `this` 由调用方式决定。需要约束调用上下文时，可在 TypeScript 函数的第一个“伪参数”位置写 `this: SomeType`；它不会出现在运行时参数列表中。箭头函数则从外层捕获 `this`。

## `void`、回调返回值与常见陷阱

当回调类型返回 `void`，含义是调用方会忽略返回值，不代表传入函数必须真的没有返回值。处理异步操作时注意 Promise 返回类型：`async function load(): Promise<Data>`。

避免把函数参数标为宽泛 `Function`；它丢失参数和返回值信息。写出明确调用签名，才能让编辑器提示参数并检查返回值。

## 小结与练习

- 使用函数签名表达 API，利用上下文推断减少重复注解。
- 泛型用于保留输入输出之间的关系，约束用于限定可用操作。
- 联合参数通常比不必要的重载简单；回调返回 `void` 表示返回值会被忽略。

练习：实现泛型 `first<T>(items: readonly T[]): T | undefined`。下一节：[对象类型](objects.md)，深入描述对象属性和结构关系。
