---
title: 语法、数据类型与运算符
weight: 20
---

# 语法、数据类型与运算符

> 本节目标：声明变量，识别常见类型，使用运算符组合表达式，并理解 JavaScript 的基础语法规则。

## 基本语法与注释

语句通常以分号结束。JavaScript 有自动分号插入规则，但显式分号可减少换行造成的歧义。标识符区分大小写，通常使用 `camelCase` 命名变量和函数。

```js
// 单行注释
const subtotal = 18;
const tax = subtotal * 0.1;

/* 多行注释
   可用于解释较长的背景。 */
console.log(subtotal + tax);
```

## 声明与作用域

`const` 和 `let` 具有块级作用域。`const` 不能重新绑定，`let` 可以重新赋值。`var` 使用函数作用域并有提升等历史行为，新代码通常不使用它。

```js
const course = "JavaScript";
let completed = 0;
completed += 1;

if (completed > 0) {
  const status = "学习中";
  console.log(`${course}：${status}`);
}
```

`status` 只在 `if` 的花括号内部可访问。`let` 和 `const` 存在暂时性死区：声明执行前访问变量会抛出 `ReferenceError`，不要把这种行为与 `var` 的 `undefined` 混为一谈。

## 值类型与类型转换

原始类型有 `undefined`、`null`、`boolean`、`number`、`bigint`、`string` 和 `symbol`。对象、数组和函数属于对象值。变量绑定保存的是值；对象值可通过多个变量引用。

```js
console.log(typeof "hello"); // "string"
console.log(typeof 42); // "number"
console.log(typeof 10n); // "bigint"
console.log(typeof null); // "object"，这是历史遗留结果
```

`===` 不做隐式类型转换，通常应优先使用。`==` 会执行类型转换，理解遗留代码时会遇到。把用户输入转成数字时，显式使用 `Number()` 并检查结果是否有效。

## 字面量与解构

字面量直接写出值，如 `"文本"`、`42`、`true`、`[1, 2]` 和 `{ name: "小林" }`。解构从数组或对象中取出属性：

```js
const [first, second] = ["语法", "函数"];
const { name, level = "初学者" } = { name: "小林" };
console.log(first, second, name, level);
```

对象解构的变量名默认与属性名一致；数组解构按位置取值。默认值仅在取出的值为 `undefined` 时生效。

## 表达式与运算符

算术运算符 `+ - * / % **` 计算数值；比较运算符返回布尔值；`&&`、`||` 和 `??` 会短路求值。`??` 只在左侧为 `null` 或 `undefined` 时使用右侧默认值，适合保留 `0`、`false` 和空字符串。

```js
const input = 0;
const display = input ?? 10;
const isAdult = 20 >= 18;
console.log(display, isAdult); // 0 true
```

赋值表达式、三元表达式、可选链 `?.` 和展开语法 `...` 也是常用表达式。括号能明确运算顺序，复杂条件应加括号提高可读性。

```js
const user = { profile: { nickname: "小林" } };
console.log(user.profile?.nickname ?? "访客");
```

按位运算会把数值按 32 位整数处理，除非处理位掩码或二进制协议，一般不用于普通数值计算。

## 小结与练习

- 用 `const` 表示不重新绑定的值，用 `let` 表示需要重新赋值的变量。
- 区分原始值和对象引用；新代码通常选择严格相等 `===`。
- 用解构、可选链和空值合并简洁地处理数据，但别牺牲清晰度。

练习：给定一组商品对象，计算总价；对缺少商品名的记录显示“未命名”，并使用严格相等判断是否已售出。

下一节：[流程控制与错误处理](errors-debugging.md)。
