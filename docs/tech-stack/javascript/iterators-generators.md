---
title: 迭代器与生成器
weight: 80
---

# 迭代器与生成器

> 本节目标：理解 `for...of` 背后的迭代协议，并用生成器按需产出值。

## 可迭代协议

可迭代对象提供 `[Symbol.iterator]()` 方法，该方法返回迭代器。迭代器的 `next()` 返回 `{ value, done }`。数组、字符串、Map 和 Set 都是内置可迭代对象。

```js
const iterator = ["语法", "函数"][Symbol.iterator]();
console.log(iterator.next()); // { value: "语法", done: false }
console.log(iterator.next()); // { value: "函数", done: false }
```

`for...of`、展开语法和数组解构都会消费可迭代对象。不要把 `for...in` 当成相同协议：它枚举对象属性键。

## 生成器

生成器函数用 `function*` 声明，`yield` 暂停并产出一个值。调用生成器函数会得到迭代器：

```js
function* ids() {
  yield "a";
  yield "b";
}

console.log([...ids()]); // ["a", "b"]
```

生成器适合惰性序列和可暂停流程。无限生成器不能直接展开成数组，否则会一直运行。

## 异步迭代器

异步可迭代对象通过 `[Symbol.asyncIterator]()` 提供迭代器，`for await...of` 会逐项等待结果。它适合流式异步数据；普通 Promise 列表则通常用 `Promise.all()`。

## 小结与练习

- 迭代协议让不同集合通过一致的接口逐项提供值。
- 生成器用 `yield` 惰性地产生序列。
- 异步迭代使用 `for await...of`，注意结束和错误处理。

练习：写一个生成器，从起始数开始每次递增 2；读取前三个值并打印。
