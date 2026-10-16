---
title: JavaScript 第一步与运行环境
weight: 10
---

# JavaScript 第一步与运行环境

> 本节目标：说清 JavaScript 语言和运行环境的关系，并在浏览器与 Node.js 中运行第一段代码。

## JavaScript 与运行环境

JavaScript 是一门语言，ECMAScript（通常写作 ES）是它的核心标准。标准定义值、表达式、函数、对象、模块等语言行为；宿主环境提供语言之外的能力。浏览器提供页面、事件和网络 API，Node.js 提供进程、文件和网络 API。

这意味着同一段纯 JavaScript 逻辑可在不同宿主运行，但 `document.querySelector()` 只能在提供 DOM 的环境中调用，`process.cwd()` 则属于 Node.js。

JavaScript 和 Java 是不同的语言。名称相似不代表语法、运行模型或用途相同。

## 运行第一段代码

在浏览器中打开开发者工具的 Console，输入：

```js
const greeting = "你好，JavaScript";
console.log(greeting);
```

预期输出：

```text
你好，JavaScript
```

也可保存为 `hello.js`，使用已安装的 Node.js 执行：

```sh
node hello.js
```

`console.log()` 是调试输出接口。它由宿主提供，在浏览器和 Node.js 中都可用，但其输出界面不同。

## 值、变量与表达式

程序处理值。变量名是对值的绑定，表达式则计算出一个值：

```js
const price = 12;
const quantity = 3;
const total = price * quantity;
console.log(total); // 36
```

`const` 表示变量绑定不能重新赋值；需要重新赋值时使用 `let`。优先使用 `const` 能减少意外改写。`const` 不会冻结对象内部的属性。

## 字符串、数字与数组

```js
const learner = "小林";
const lessons = 4;
const topics = ["变量", "函数", "对象"];

console.log(`${learner} 已完成 ${lessons} 课`);
console.log(topics[0]); // 变量，数组索引从 0 开始
```

模板字符串用反引号包围，可用 `${表达式}` 插入计算结果。数组按顺序存放多个值，长度通过 `topics.length` 获取。

## 错误与调试

出错时先读控制台中的错误类型、消息和文件行号。语法错误通常无法解析；运行时错误发生在代码执行过程中；逻辑错误则是程序能运行但结果不符合预期。可以逐步输出关键变量，缩小问题范围。

## 小结与练习

- ECMAScript 定义语言，浏览器和 Node.js 提供宿主 API。
- `const`、字符串、数字和数组构成入门代码的常用积木。
- 在控制台运行一行代码，是快速验证想法的起点。

练习：创建 `profile.js`，声明姓名、学习主题数组和完成课数，并打印一句包含这些信息的句子。

下一节：[语法与数据类型](syntax.md)。
