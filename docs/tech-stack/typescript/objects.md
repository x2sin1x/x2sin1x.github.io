---
title: 对象类型
weight: 50
---

# 对象类型

> 本节目标：设计可读的对象契约，并理解可选、只读、索引签名、接口扩展和交叉类型。

## 属性修饰符

对象类型描述需要哪些属性以及各自的类型。TypeScript 采用结构化类型：只要对象拥有目标需要的成员，通常就能赋值给该类型。

```ts
interface Task {
  readonly id: number;
  title: string;
  done?: boolean;
}

function taskLabel(task: Task): string {
  return `${task.done ? "✓" : "○"} ${task.title}`;
}
```

`?` 表示可选；`readonly` 限制通过该引用重新赋值。它们只控制静态检查，不冻结运行时对象，也不保证嵌套对象不可变。

## 额外属性检查与赋值兼容

把对象字面量直接传给函数时，检查器会额外检查拼写错误：

```ts
interface Options { color?: string }
function paint(options: Options) { /* ... */ }

paint({ color: "blue" });
// paint({ colour: "blue" }); // 额外属性检查会报告可能的拼写错误
```

先赋值给变量后，结构兼容规则可能接受带有额外成员的对象。这不代表任意对象字面量都能传入；额外属性检查是帮助发现错误的特殊检查，不是精确对象类型系统。

## 索引签名

当对象键集合事先未知时，可用索引签名描述键和值：

```ts
interface Scores {
  [student: string]: number;
}

const scores: Scores = { Lin: 95, Kai: 88 };
```

索引签名表示任意字符串键都对应数字。若键集合有限，优先使用明确属性或 `Record<Keys, Value>`，这样拼写检查更严格。

## `interface` 与 `type`

两者都能描述对象结构。`interface` 适合可扩展的对象契约；`type` 还可表达联合、交叉、条件等组合类型。选择应保持团队一致，没必要强行只用其中一种。

接口扩展：

```ts
interface Identified { id: number }
interface Article extends Identified { title: string }
```

交叉类型把条件组合在一起：

```ts
type Timestamped = { createdAt: Date };
type SavedArticle = Article & Timestamped;
```

接口扩展会创建明确的继承关系；交叉类型要求一个值同时满足多个类型。相同属性冲突时交叉结果可能变成难以使用的 `never`，应避免无意的冲突。

## 函数属性、数组与元组

对象可以有函数属性，也可以用方法语法描述调用能力。数组是带数字索引的对象；只读数组可接受普通数组，但不能通过该引用修改元素。

```ts
type ReadonlyPair = readonly [string, number];
const entry: ReadonlyPair = ["章节", 1];

function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}
```

元组按位置描述固定长度或已知位置的元素类型；数组适合数量不固定、元素类型相同的集合。开启 `noUncheckedIndexedAccess` 可让一般数组索引访问显式包含 `undefined`，更准确反映越界可能性。

## 小结与练习

- 对象类型按结构兼容；额外属性检查主要帮助发现新鲜对象字面量中的拼写错误。
- `interface` 和 `type` 都可表达对象契约，后者也支持联合等类型运算。
- 用只读数组表达“不通过此函数修改集合”的约束。

练习：为课程目录定义 `Course`、`VideoCourse` 与 `BookCourse`，共享部分字段，并分别约束视频时长和书籍页数。下一节：[从类型创建类型](type-manipulation.md)，学习根据已有类型派生新类型。
