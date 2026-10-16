---
title: 模式与匹配
weight: 190
---
# 第 19 章：模式与匹配

> 本章目标：在 Rust 的控制流、绑定和函数参数中使用模式，理解穷尽匹配与可失败匹配。

## 模式出现的位置

模式用于解构数据并绑定其中的值。常见位置包括 `match` 分支、`if let`、`while let`、`for` 循环、`let` 绑定和函数参数：

```rust
let point = (3, 7);
let (x, y) = point;

for (index, value) in ["a", "b"].iter().enumerate() {
    println!("{index}: {value}");
}
```

`let` 的模式必须匹配，`if let` 和 `while let` 则允许模式不匹配。`match` 要求所有可能情况被覆盖。

在 `if let`、`while let`、`for` 和函数参数中，模式失败时各结构有不同处理规则：`if let` 跳过主体，`while let` 结束循环，`for` 为每项解构，函数参数则必须匹配调用传入的值。`let...else` 可在不匹配时通过 `return`、`break` 或 `panic!` 离开当前控制流。`matches!` 宏可把简单模式测试写成布尔表达式，例如 `matches!(value, Some(1..=5))`。

## 可失败与不可失败模式

Refutable（可失败）模式可能无法匹配某个值，例如 `Some(x)` 对任意 `Option` 值。Irrefutable（不可失败）模式总能匹配，例如普通变量绑定。`let` 要求不可失败模式；`if let`、`while let` 和 `match` 可使用可失败模式。

例如 `let Some(x) = value;` 对任意 `Option` 不保证成功，编译器会拒绝；可改成 `if let Some(x) = value { ... }`，或 `let Some(x) = value else { return; };`。模式的可失败性决定了程序能否保证后续代码中的变量已经绑定。

## 模式语法

模式可按字段名或位置解构复合值，也可用 `..` 忽略其余字段：

```rust
struct Point { x: i32, y: i32 }
let point = Point { x: 4, y: 9 };

match point {
    Point { x: 0, y } => println!("在 y 轴：{y}"),
    Point { x, y: 0 } => println!("在 x 轴：{x}"),
    Point { x, y } => println!("({x}, {y})"),
}
```

模式可以嵌套，也能通过 `&`、`ref` 或 `ref mut` 等绑定形式影响借用方式。编写模式时应同时检查是否移动了值。

模式还包括字面量、变量、通配符和范围。`1 | 2` 表示多个候选模式；`1..=5` 表示闭区间；`_` 忽略值；`..` 忽略结构体或元组中的其余字段。默认绑定会取得匹配值，必要时用引用模式借用。结构体字段名可简写为同名变量，元组结构体则按位置解构。

对不需要的值优先写 `_`，它不会创建变量；写 `_name` 会绑定变量但不触发未使用警告，仍可能移动值。用 `..` 忽略元组中间字段或结构体剩余字段时，必须确保至少有一个明确解构的字段。数组和切片模式也可匹配前缀、后缀与剩余部分，例如 `[first, middle @ .., last]`。

绑定默认按值匹配：若模式取出非 `Copy` 字段，所有权可能移入绑定。可以在引用上匹配或使用 `ref` / `ref mut` 借用绑定；在 Rust 2024 Edition 中，优先依据匹配位置的引用形态和默认绑定模式理解借用，避免机械地添加旧式 `ref`。

```rust
enum Message {
    Move { x: i32, y: i32 },
    Write(String),
}

let message = Message::Move { x: 4, y: 7 };
match message {
    Message::Move { x, y: 0 } => println!("x 轴上的 {x}"),
    Message::Move { x, y } => println!("坐标：({x}, {y})"),
    Message::Write(text) => println!("{text}"),
}
```

### 匹配守卫与 `@`

匹配守卫是在模式匹配成功后再检查的布尔条件：`Some(x) if x > 10 => ...`。`@` 可在匹配某个范围或结构的同时绑定整个值，例如 `id: id_value @ 3..=7`。

使用匹配守卫时留意它可能改变原本看起来穷尽的匹配；必要时保留兜底分支。

匹配守卫允许模式之后再检查额外条件，但守卫中绑定值的使用不参与编译器的穷尽性证明。`@` 模式会在匹配范围或结构的同时绑定整个值，例如 `id @ 3..=7`；当既要判断范围、又要保留原值时很有用。

守卫可与多个模式一起使用，例如 `Some(3) | Some(4) if enabled`；守卫条件作用于整组模式。范围模式仅支持允许范围匹配的数值和字符类型，字符区间按 Unicode 标量值排列。需要忽略某个分支但仍满足穷尽性时使用 `_`，需要把特定模式前置时注意 `match` 按从上到下顺序选择第一个匹配分支。

## 小结与练习

- 模式既用于解构，也用于控制流；可失败模式只能放在允许失败的位置。
- `match` 的穷尽性与解构能力帮助编译器检查状态处理。
- 练习：用匹配解构嵌套枚举，为特定变体添加守卫条件，并记录哪些分支还未覆盖。

再练习：为结构体、嵌套枚举和元组各写一个解构模式；用 `matches!` 过滤范围；比较 `let`、`if let` 与 `let...else` 在失败时的控制流。

下一章：[高级特性](chapter-20-advanced-features.md)。

官方对应章节：[Patterns and Matching](https://doc.rust-lang.org/book/ch19-00-patterns.html)。
