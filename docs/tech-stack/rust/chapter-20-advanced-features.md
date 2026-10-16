---
title: 高级特性
weight: 200
---
# 第 20 章：高级特性

> 本章目标：认识 unsafe Rust、高级 Trait、类型系统边界、高阶函数与宏。

## Unsafe Rust

`unsafe` 允许使用编译器无法完全验证的少数操作：解引用裸指针、调用 `unsafe` 函数或方法、访问可变静态变量、实现 `unsafe` Trait，以及访问联合体字段。

```rust
let mut value = 5;
let pointer = &raw mut value;
unsafe {
    *pointer += 1;
}
assert_eq!(value, 6);
```

`unsafe` 不会关闭借用检查器，也不代表这段代码自动安全。每个 unsafe 操作都需要程序员维护安全不变量；应把 unsafe 封装在小而清楚的安全抽象中，并在代码旁说明依据。

裸指针可以为空、悬垂或未对齐；创建裸指针本身通常不要求 unsafe，但解引用必须进入 unsafe 块。调用 `unsafe fn` 表示调用者需要满足其安全契约；在函数体中执行不安全操作时，应由实现者证明不变量。`unsafe trait` 与其实现同样要求维护额外契约。

可变静态变量会引入全局共享状态，在并发访问时尤其危险；常量与不可变静态变量的约束不同。联合体允许多个字段复用相同内存，读取字段时需要确认当前有效成员。安全抽象应尽量限制这些操作的范围。

## 高级 Trait

Trait 可包含关联类型、默认泛型类型参数、运算符重载和超 Trait 等设计。完全限定语法可在多个 Trait 定义同名方法时明确指定调用对象。Newtype 模式用包装类型为外部类型实现本地 Trait，或增加局部领域语义。

关联类型将 Trait 实现与某个输出类型关联，例如迭代器的 `Item`；它与把类型参数放在 Trait 名上的设计不同。默认泛型参数可为 Trait 提供默认类型，也支持运算符 Trait 的左右操作数类型。完全限定语法形式为 `<Type as Trait>::method(...)`，可消除同名关联函数的歧义。超 Trait 要求实现当前 Trait 的类型也实现另一个 Trait。Newtype 还可绕过孤儿规则：本地包装类型可为外部类型实现本地 Trait。

这些功能适合库设计和抽象边界；普通应用代码应先使用更直接的类型和函数，确有需求时再引入复杂 Trait 约束。

```rust
use std::ops::Add;

trait Contains {
    type Item;
    fn contains(&self, item: &Self::Item) -> bool;
}

struct Millimeters(u32);
struct Meters(u32);

impl Add<Meters> for Millimeters {
    type Output = Millimeters;

    fn add(self, rhs: Meters) -> Self::Output {
        Millimeters(self.0 + rhs.0 * 1_000)
    }
}
```

`Contains::Item` 是关联类型：每个实现为 Trait 选择一个项目类型。`Add<Rhs = Self>` 使用默认泛型参数，因此可以像上面这样覆盖右操作数和输出类型。若多个 Trait 都定义同名关联函数，可用 `<Type as Trait>::function(...)` 完全限定调用。超 Trait（例如要求 `OutlinePrint: Display`）能让 Trait 默认方法依赖另一种行为。Newtype 可在本地包装类型上实现外部 Trait，满足孤儿规则，同时提供清楚的语义边界。

## 高级类型

类型别名为复杂类型提供短名称；永不返回类型 `!` 可用于必然发散的函数；动态大小类型（DST）通过指针形式使用，例如 `str` 和 `[T]`。函数指针与闭包都能作为参数，但捕获环境的闭包不能直接转换成普通函数指针。

`type Kilometers = i32;` 只是同一类型的别名，不会建立新的类型检查边界；若要区分领域单位，应使用 newtype 结构体。`!` 可用于 `panic!`、无限循环或总是返回错误的函数。`str` 的大小在编译期未知，因此必须通过 `&str`、`Box<str>` 等指针类型使用；Trait 对象也是动态大小类型。

类型别名不会阻止把不同领域的整数混用；newtype 则创建独立类型，可为单位、标识符或外部类型提供有意义的边界。`!` 是 never type，因为它不产生值，可用于 `match` 中必定发散的分支。动态大小类型（DST）不能直接作为普通局部变量存放，需通过指针携带其运行时元数据；`str`、`[T]` 和 `dyn Trait` 是常见例子。

## 高级函数与闭包

函数指针类型（如 `fn(i32) -> i32`）可保存函数地址，且能作为参数或返回值。无捕获闭包通常可转换为函数指针；捕获环境的闭包是拥有匿名具体类型的值。返回闭包时可使用 `impl Fn(...) -> ...`，或在需要异构返回类型时使用装箱 Trait 对象。

```rust
fn add_one(value: i32) -> i32 { value + 1 }

fn apply_twice(f: fn(i32) -> i32, value: i32) -> i32 {
    f(f(value))
}

fn make_adder(amount: i32) -> impl Fn(i32) -> i32 {
    move |value| value + amount
}

assert_eq!(apply_twice(add_one, 5), 7);
assert_eq!(make_adder(3)(4), 7);
```

函数指针实现 `Fn`、`FnMut` 和 `FnOnce`，所以需要接受闭包的通用 API 通常写成泛型 Trait bound；只有与外部 ABI 对接或明确要求函数指针时才限定 `fn`。返回的 `impl Fn` 仍代表单一隐藏的具体闭包类型；若不同分支返回不同闭包，可使用 `Box<dyn Fn(...) -> ...>`。

## 宏

声明式宏用模式匹配 token 并生成代码；适合表达普通函数无法表达的可变参数或语法结构。过程宏在编译期处理 TokenStream，可用于 derive、属性或函数式宏。宏增加了调试和错误诊断难度，优先考虑函数、Trait 或泛型。

`macro_rules!` 声明式宏按 token 模式匹配并展开成 Rust 代码，适合减少重复语法。过程宏必须定义在专门的 proc-macro crate 中，常见形式包括派生宏、属性宏和函数式宏；它们读取 TokenStream 并输出 TokenStream。过程宏可生成 Trait 实现或领域语法，但需要处理输入语法、诊断与展开结果，维护成本高于普通函数。

```rust
macro_rules! make_pair {
    ($left:expr, $right:expr) => {
        ($left, $right)
    };
}

let pair = make_pair!("Rust", 2024);
assert_eq!(pair, ("Rust", 2024));
```

宏与函数的主要差异是：宏在编译期间展开，可以接收可变数量的 token，并能生成实现等语法项；函数则按已声明的参数类型和数量在运行时调用。自定义 derive 用属性为结构体或枚举生成 Trait 实现；属性宏接收并改写带属性的项；函数式过程宏看起来像宏调用并处理括号内 token。编写过程宏通常要使用 `proc_macro` crate，宏定义需放在 `proc-macro = true` 的专用 crate 中。

## 小结与练习

- `unsafe` 将额外安全义务交给程序员；它不会自动证明操作安全。
- 高级 Trait、类型与函数工具用于表达特定抽象需求；宏用于生成结构化代码。
- 练习：为包装类型实现一个 Trait，写出其不变量；再比较手写实现和 derive 宏的适用场景。

再练习：为单位 newtype 实现加法 Trait；写一个接受函数指针的高阶函数，并比较无捕获与有捕获闭包；为 unsafe 函数写出调用前置条件和实现不变量。

下一章：[项目：构建多线程 Web 服务器](chapter-21-web-server.md)。

官方对应章节：[Advanced Features](https://doc.rust-lang.org/book/ch20-00-advanced-features.html)。
