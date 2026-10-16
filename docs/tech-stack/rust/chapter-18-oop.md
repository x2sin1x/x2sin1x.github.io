---
title: 面向对象编程特性
weight: 180
---
# 第 18 章：面向对象编程特性

> 本章目标：用 Rust 的 Trait 对象和状态模式表达面向对象设计中的动态行为与封装状态。

## 面向对象与 Rust

面向对象语言常用对象封装数据与行为，并通过多态在运行时选择实现。Rust 的结构体和枚举可以封装数据，`impl` 提供方法，Trait 描述共享行为。Rust 没有传统类继承，但可以使用组合和 Trait 建模共享能力。

“面向对象”的定义因语言和流派而异。以对象封装状态与行为、通过消息调用对象方法等特征来看，Rust 能表达不少面向对象设计；若把类继承视为必需条件，Rust 就不采用那种对象模型。选择语言特性时，应先明确要解决的设计问题。

## Trait 对象与动态分发

当集合中的值来自不同类型，但都实现同一 Trait 时，可用 Trait 对象保存它们。`dyn Trait` 通过虚表在运行时选择实现：

```rust
trait Draw {
    fn draw(&self);
}

struct Button { label: String }
impl Draw for Button {
    fn draw(&self) { println!("按钮：{}", self.label); }
}

struct SelectBox { options: Vec<String> }
impl Draw for SelectBox {
    fn draw(&self) { println!("选项数：{}", self.options.len()); }
}

struct Screen {
    components: Vec<Box<dyn Draw>>,
}

impl Screen {
    fn run(&self) {
        for component in &self.components { component.draw(); }
    }
}
```

Trait 对象适合运行时异构集合或需要动态替换实现的场景。泛型通常使用静态分发，编译器知道具体类型；Trait 对象提供动态分发并带来间接调用成本。

Trait 对象可理解为数据指针和方法虚表信息的组合。具体类型在编译时未知，因此 `dyn Trait` 只能调用 Trait 定义的接口；并非所有 Trait 都能作为 Trait 对象使用。Trait 对象通常通过 `Box`、引用等指针类型使用。泛型集合中所有元素是同一种具体类型；Trait 对象集合则可容纳不同类型。

## 状态模式

状态模式把对象状态和每种状态允许的行为封装起来。可以用 Trait 对象实现传统状态模式，也可以考虑用枚举让状态变体显式可见。状态转换时注意所有权：某些设计会消耗旧状态并返回新状态。

设计时比较状态模式与枚举建模：若状态固定且行为简单，枚举常更直接；若希望通过 Trait 扩展状态行为，状态对象可能更合适。

Book 以博客文章状态为例：新文章从草稿（Draft）开始；提交审核后进入待审核（PendingReview）；再次审核后发布（Published）。`Post` 持有内容和当前状态对象，状态 Trait 决定哪些操作有效以及何时可读取内容。每次状态转换会返回新的状态对象，因此调用者无法绕过规定流程。

这种设计展示了封装和动态分发，也会带来额外状态类型与 Trait 对象间接层。若业务状态集合固定，枚举状态机通常更容易穷尽检查；Book 中的模式帮助理解如何把对象状态和行为分离。

## 小结与练习

- 结构体、方法、Trait 与 Trait 对象可以组合出封装和多态行为。
- 泛型采用静态分发；`dyn Trait` 适合运行时选择行为。
- 练习：为不同类型的 UI 组件实现 `Draw`，放入一个 `Screen` 并统一调用。

再练习：分别用 Trait 对象和枚举表示文章状态；明确草稿、审核中、已发布状态分别允许哪些操作，并比较两种实现的可扩展性与状态检查方式。

下一章：[模式与匹配](chapter-19-patterns.md)。

官方对应章节：[Object-Oriented Programming Features](https://doc.rust-lang.org/book/ch18-00-oop.html)。
