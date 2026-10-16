---
title: 泛型、Trait 与生命周期
weight: 100
---
# 第 10 章：泛型、Trait 与生命周期

> 本章目标：用泛型消除重复逻辑，用 Trait 表达共享行为，并理解引用有效期的约束。

## 泛型函数与类型

泛型适合消除“逻辑相同、只有类型不同”的重复代码。先抽取重复逻辑为普通函数，再把具体类型改成参数，最后添加该实现真正需要的 Trait bound。这样可以避免过早泛型化。

```rust
fn largest_i32(items: &[i32]) -> &i32 {
    let mut largest = &items[0];
    for item in items {
        if item > largest { largest = item; }
    }
    largest
}
```

泛型参数让函数或数据类型适用于多种具体类型，同时由编译器检查每种用法：

```rust
fn largest<T: Ord>(items: &[T]) -> Option<&T> {
    items.iter().max()
}
```

约束说明泛型类型必须支持哪些行为。结构体、枚举和方法也能使用泛型。编译器通常会在编译期生成具体实现，不需要运行时类型查找。

可以将 `T` 用于结构体字段、枚举变体和 `impl` 方法。定义泛型类型时每次使用都要提供或推断具体类型；方法可以只对满足额外 Trait 的 `T` 开放。泛型代码经单态化后，编译器会为实际使用的类型生成具体版本，这通常让泛型没有动态分发成本，但也可能增加编译时间和二进制体积。

## Trait 与 Trait bound

Trait 定义一组共享行为；类型通过 `impl Trait for Type` 实现它。泛型函数可用 Trait bound 限制参数能力：

```rust
trait Summary {
    fn summary(&self) -> String;
}

struct Article { title: String }

impl Summary for Article {
    fn summary(&self) -> String {
        format!("文章：{}", self.title)
    }
}

fn print_summary(item: &impl Summary) {
    println!("{}", item.summary());
}
```

`&impl Summary` 是 Trait bound 的简写。需要多个约束、复用类型参数或返回实现某 Trait 的类型时，使用显式泛型与 `where` 子句更合适。`impl Trait` 返回类型仍代表一个确定的具体类型。

Trait 可以给出默认方法实现，实现类型可直接使用或覆写。Trait bound 可以写成 `T: Summary + Display`，也可用 `where T: Summary + Display` 放到签名后方以改善可读性。Trait 还支持返回 `impl Trait`，但同一个返回位置只能返回一种确定的具体类型。若需要在运行时持有不同实现，可查看[第 18 章 Trait 对象](chapter-18-oop.md)。

## 生命周期

生命周期标注描述引用之间的有效期关系，帮助编译器排除悬垂引用；它不会延长数据的实际存活时间。大多数局部引用无需手动标注。

```rust
fn longer<'a>(left: &'a str, right: &'a str) -> &'a str {
    if left.len() >= right.len() { left } else { right }
}
```

这里的 `'a` 表示返回引用只在两个输入引用共同有效的范围内有效。结构体持有引用时也可能需要生命周期参数。静态字符串 `&'static str` 可在整个程序运行期间有效，但不应把它误用为通用解决办法。

生命周期省略规则让很多常见函数签名无需写标注：每个引用参数会获得自己的生命周期；若只有一个输入引用，返回引用会关联到该输入；若方法有 `&self` 或 `&mut self`，返回引用默认与 `self` 关联。超出这些规则时，显式标注才能说明输入和输出引用的约束。

```rust
struct Excerpt<'a> {
    text: &'a str,
}

impl<'a> Excerpt<'a> {
    fn part(&self) -> &str {
        self.text
    }
}
```

`Excerpt` 的实例不能比其引用的文本活得更久。`'static` 表示引用在整个程序期间有效，常见于字符串字面量；它不表示“把普通数据永久保存在内存”。

## 小结与练习

- 泛型复用类型与函数，Trait 抽象行为，Trait bound 描述所需能力。
- 生命周期标注约束引用关系，而不是改变内存生命周期。
- 练习：为 `Book` 和 `Podcast` 实现同一摘要 Trait，再写一个接收任意摘要类型的函数。

再练习：为泛型 `Point<T>` 实现构造函数，为数值点只实现 `distance_from_origin`；为 Trait 添加默认摘要方法；编写返回最长输入切片的函数，并用不同作用域验证其引用边界。

下一章：[编写自动化测试](chapter-11-writing-tests.md)。

官方对应章节：[Generic Types, Traits, and Lifetimes](https://doc.rust-lang.org/book/ch10-00-generics.html)。
