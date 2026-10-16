---
title: 索引集合与带键集合
weight: 40
---

# 索引集合与带键集合

> 本节目标：根据访问方式选择 Array、TypedArray、Map 或 Set，并用迭代处理集合。

## 数组与索引集合

数组（Array）按顺序保存值，索引从 `0` 开始。`map` 转换每项，`filter` 筛选，`find` 查找首个匹配项，`reduce` 汇总：

```js
const scores = [72, 91, 84];
const scaled = scores.map((score) => score + 5);
const passed = scores.filter((score) => score >= 80);
console.log(scaled, passed); // [77, 96, 89] [91, 84]
```

`for...of` 遍历元素，`forEach` 调用回调。`for...in` 遍历可枚举属性名，不适合遍历数组元素。`sort()` 会修改原数组；数字排序应提供比较函数：`values.sort((a, b) => a - b)`。

## 循环与可迭代对象

数组、字符串、Map 和 Set 都可迭代，因此可用于 `for...of`、展开语法和数组解构：

```js
for (const topic of ["语法", "函数"]) {
  console.log(topic);
}
```

迭代协议和自定义生成器见[迭代器与生成器](iterators-generators.md)。

## 带键集合

普通对象适合记录属性固定的实体；`Map` 适合动态键值表，键可以是任意类型，并保留插入顺序。`Set` 用于唯一值集合：

```js
const visits = new Map();
visits.set("/guide", 3);
console.log(visits.get("/guide")); // 3

const tags = new Set(["js", "web", "js"]);
console.log([...tags]); // ["js", "web"]
```

`WeakMap` 和 `WeakSet` 的键/成员必须是对象，并以弱引用方式关联，适用于与对象生命周期绑定的元数据；它们不可枚举。

## TypedArray

TypedArray 是固定元素类型的二进制数据视图，例如 `Uint8Array` 表示 0–255 的无符号 8 位数值。其底层缓冲区、`DataView` 等见[类型化数组](typed-arrays.md)。

## 小结与练习

- 顺序数据用 Array；唯一值用 Set；任意键映射用 Map。
- `for...of` 读取元素，`for...in` 读取可枚举键。
- 区分会修改原数组的方法和返回新数组的方法。

练习：从一组重复标签中得到唯一标签，并统计每个标签出现次数。
