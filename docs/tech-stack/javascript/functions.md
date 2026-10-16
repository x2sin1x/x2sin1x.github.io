---
title: 函数与闭包
weight: 30
---

# 函数与闭包

> 本节目标：定义函数、传入参数、返回结果，并理解词法作用域与闭包。

## 声明、调用与返回值

函数把一组操作命名起来，便于重复调用。参数是输入，`return` 结束本次调用并给出结果：

```js
function formatTitle(title) {
  return `阅读：${title.trim()}`;
}

console.log(formatTitle("  JavaScript 入门  "));
```

函数声明可在所在作用域中提前调用（函数提升）。函数表达式和箭头函数则受变量声明规则约束。箭头函数适合简短回调，但没有自己的 `this`、`arguments`，不应机械替换方法或构造函数。

## 参数

```js
function greet(name = "访客", ...topics) {
  return `${name} 正在学习：${topics.join("、")}`;
}

console.log(greet("小林", "函数", "对象"));
```

默认参数在对应实参缺省或为 `undefined` 时生效。剩余参数 `...topics` 收集额外参数为数组。现代代码优先用剩余参数代替 `arguments`，以获得明确的数组语义。

## 作用域与闭包

函数在定义时形成词法环境，内部函数可访问外层作用域。即使外层函数已经返回，只要内部函数仍引用其变量，这些绑定仍会保留，这种函数与其词法环境的组合称为闭包。

```js
function makeCounter() {
  let count = 0;
  return () => {
    count += 1;
    return count;
  };
}

const next = makeCounter();
console.log(next(), next()); // 1 2
```

闭包可封装状态、创建回调，也可能因长期引用大型对象而延长其生命周期。只保留确实需要的数据。

## `this` 与函数形式

普通函数中的 `this` 通常由调用方式决定；对象方法以 `object.method()` 调用时，`this` 指向调用对象。箭头函数从外层词法环境捕获 `this`。若需要绑定特定接收者，可使用 `bind()`，但优先让调用方式清楚。

## 小结与练习

- 参数传入信息，`return` 交回结果；不写 `return` 的函数返回 `undefined`。
- 闭包让函数访问定义时的外层变量，可用于封装私有状态。
- 箭头函数和普通函数的 `this` 规则不同。

练习：编写 `makeAccumulator(start)`，返回一个函数；每次传入增量后更新并返回累计值。
