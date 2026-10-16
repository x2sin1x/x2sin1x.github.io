---
title: 对象、原型与类
weight: 50
---

# 对象、原型与类

> 本节目标：读写对象属性，理解属性查找和原型继承，并用 class 描述共享行为。

## 创建对象与访问属性

对象由属性组成。属性名通常是字符串或 Symbol，值可以是任意类型：

```js
const book = {
  title: "语言入门",
  pages: 240,
  describe() {
    return `${this.title}（${this.pages} 页）`;
  },
};

console.log(book.title, book["pages"]);
console.log(book.describe());
```

点号用于已知标识符属性名；方括号适合动态属性名。对象解构、展开和简写属性可降低样板代码，但展开是浅拷贝，嵌套对象仍共享引用。

## 属性枚举与所有权

`Object.hasOwn(object, key)` 检查自有属性；`in` 也会检查原型链。`Object.keys()` 返回自有、可枚举的字符串键。`Object.getOwnPropertyDescriptor()` 可检查可写、可枚举、可配置属性及 getter/setter。

枚举和复制数据前应考虑继承属性、Symbol 键及访问器副作用；处理外部输入时，不要把任意对象直接当作可信字典。

## 原型链

每个普通对象都可关联一个原型。读取自有属性失败后，运行时沿原型链继续查找；写属性通常创建或修改对象自身的属性。原型机制是 JavaScript 对象委托的基础。

```js
const defaults = { category: "未分类" };
const article = Object.create(defaults);
article.title = "对象模型";
console.log(article.category); // 从原型读取
console.log(Object.hasOwn(article, "category")); // false
```

日常开发通常不需要修改对象原型。优先使用对象字面量和类语法，避免原型污染。

## 类

`class` 提供创建实例和共享方法的语法，方法放在原型上。类语法建立在原型机制之上：

```js
class Book {
  #pages;
  constructor(title, pages) {
    this.title = title;
    this.#pages = pages;
  }
  describe() {
    return `${this.title}：${this.#pages} 页`;
  }
}

console.log(new Book("JavaScript", 300).describe());
```

`extends` 表示继承，`super()` 调用父类构造函数，`static` 定义类自身成员。私有字段以 `#` 声明，不能从类外直接访问。继承层次应保持简单；组合对象在很多场景下更灵活。

## 小结与练习

- 对象属性可通过点号或方括号访问；展开复制是浅拷贝。
- 自有属性和原型属性有不同的枚举与访问行为。
- `class` 是基于原型的语法形式，不是与原型无关的新对象模型。

练习：实现 `Book` 和 `AudioBook` 两个类，使用私有字段保存时长，并让子类扩展描述文本。
