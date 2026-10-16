---
title: 相等比较和相同
weight: 120
---

# 相等比较和相同

> 本节目标：区分 `===`、`==` 和 `Object.is()` 的比较规则，避免隐式转换带来的意外。

## 严格相等

`===` 不做类型转换。原始值按类型和值比较；对象按引用身份比较：

```js
console.log(1 === "1"); // false
console.log({} === {}); // false，不是同一个对象
const value = {};
console.log(value === value); // true
```

日常业务判断通常使用 `===` 和 `!==`。

## 宽松相等

`==` 会按规范执行类型转换，例如 `0 == false` 为 `true`。这可能隐藏数据清洗问题。仅在明确理解转换规则时使用，代码审查时需特别检查 `null` / `undefined` 的宽松比较惯用法。

## Object.is

`Object.is()` 与严格相等类似，但对 `NaN` 和正负零有不同结果：

```js
console.log(NaN === NaN); // false
console.log(Object.is(NaN, NaN)); // true
console.log(Object.is(0, -0)); // false
```

## 小结与练习

- 默认使用严格相等，避免隐式类型转换。
- 对象相等判断比较是否为同一引用，不会自动深度比较属性。
- `Object.is()` 适合需要精确处理 `NaN` 和正负零的场景。

练习：预测 `0 == false`、`0 === false`、`NaN === NaN`、`Object.is(-0, 0)` 的结果并在控制台验证。
