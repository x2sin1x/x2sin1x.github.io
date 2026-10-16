---
title: 数字与字符串
weight: 55
---

# 数字与字符串

> 本节目标：选择合适的数值类型，完成字符串转换、格式化和常见文本处理。

## Number 与精度

JavaScript 的 `number` 使用 IEEE 754 双精度浮点数表示整数和小数。部分十进制小数无法精确表示：

```js
console.log(0.1 + 0.2); // 0.30000000000000004
console.log(Number.isInteger(8)); // true
console.log(Number.isFinite(Infinity)); // false
```

金额计算可用最小单位整数（例如分），或使用经过审查的十进制计算库。`Number.isNaN(value)` 和 `Number.isFinite(value)` 可验证数值状态。

## BigInt

`bigint` 可表示任意精度整数，字面量以 `n` 结尾。它不能与 `number` 直接混算：

```js
const huge = 9007199254740993n;
console.log(huge + 2n);
```

需在 `BigInt` 和 `Number` 间转换时，先确认目标范围和是否会损失精度。

## 字符串

字符串不可变；方法会返回新字符串。模板字符串适合插值，多行字符串也可直接换行：

```js
const title = "  JavaScript 指南  ";
const normalized = title.trim();
console.log(normalized.toUpperCase());
console.log(`标题长度：${normalized.length}`);
```

常见方法包括 `includes`、`startsWith`、`slice`、`replace`、`split` 和 `trim`。索引按 UTF-16 码元计数，因此 `length` 不一定等于用户看到的字符数（例如 emoji）。

## 转换与格式化

```js
const count = Number("42");
const invalid = Number("很多");
console.log(count, Number.isNaN(invalid)); // 42 true
console.log((1234.5).toFixed(1)); // "1234.5"
```

`parseInt` 和 `parseFloat` 会从字符串开头解析可读部分；`Number()` 要求整体可转换。展示格式应优先使用 `Intl.NumberFormat`，见[国际化](internationalization.md)。

## 小结与练习

- `number` 是浮点数；不要假设所有小数都能精确表示。
- `bigint` 用于超出安全整数范围的大整数，不能与 `number` 混算。
- 字符串方法返回新值；用 `Intl` 做面向用户的地区格式化。

练习：解析一组数字字符串，筛掉无效项，计算有效值总和，并输出规范化的标题。
