---
title: 常见编程概念
weight: 30
---
# 第 3 章：常见编程概念

> 本章目标：掌握变量、基本类型、函数、注释和控制流，为理解所有权做好语法准备。

## 变量与可变性

Rust 默认让绑定不可变。使用 `mut` 明确允许修改；`const` 必须声明类型，且值必须是编译期常量。

```rust
fn main() {
    let name = "Rust";
    let mut attempts = 1;
    attempts += 1;
    const MAX_ATTEMPTS: u8 = 5;
    println!("{name}: {attempts}/{MAX_ATTEMPTS}");
}
```

`let` 也可重新绑定同名变量，这叫遮蔽（shadowing）。它可以改变类型或转换含义，同时保留不可变绑定：

```rust
let input = "42";
let input: u32 = input.trim().parse().expect("需要整数");
```

遮蔽与 `mut` 不同：`mut` 允许继续给同一绑定赋值，遮蔽则创建新的绑定。它常用于把原始输入转换成验证后的值。常量在编译时求值，不能用运行时结果初始化；常量名通常使用大写蛇形命名。

## 数据类型

常见标量类型包括有符号和无符号整数、浮点数、`bool` 和 `char`。复合类型包括元组与数组：

```rust
let point: (i32, i32) = (3, 8);
let x = point.0;
let colors: [&str; 3] = ["红", "绿", "蓝"];
let first = colors[0];
```

元组可组合不同类型的固定数量值；数组长度固定且元素类型相同。编译器通常会推断类型，但在数字默认类型不合适或接口需要明确时应写出类型。

Rust 的整数类型按有无符号和位宽区分，例如 `i32`、`u64`；浮点类型为 `f32` 和 `f64`。整数溢出在调试构建中会触发检查，发布构建可采用回绕行为，因此需要显式控制时使用 `checked_add`、`saturating_add` 或 `wrapping_add`。`char` 是 Unicode 标量值，不等同于 UTF-8 字节，也不一定对应一个用户感知字符。元组可用 `()` 表示单元类型；不返回有意义值的函数实际返回 `()`。

## 函数与语句、表达式

函数参数必须标注类型。函数返回类型写在 `->` 后；函数体末尾不带分号的表达式会成为返回值。

```rust
fn square(value: i32) -> i32 {
    value * value
}

fn main() {
    let result = square(6);
    println!("{result}");
}
```

带分号的语句不返回值。块本身也可以是表达式：

```rust
let result = {
    let base = 4;
    base * 2
};
```

函数由 `fn` 声明，参数和返回类型都写在签名中。Rust 不会自动把块最后一条语句当作返回值；只有不带分号的尾表达式才返回。这个约定使“执行语句”和“产生值”的区别清晰可见。

## 注释

普通行注释以 `//` 开始，编译器会忽略它们。文档注释使用 `///` 描述紧随其后的公开项，`//!` 描述当前 crate 或模块；`cargo doc` 会把这些注释生成可浏览的 API 文档。文档代码块还可以作为文档测试运行，因此示例应能独立编译。

```rust
/// 返回摄氏温度对应的华氏温度。
///
/// # Examples
///
/// ```
/// let celsius = 0.0;
/// let fahrenheit = celsius * 9.0 / 5.0 + 32.0;
/// assert_eq!(fahrenheit, 32.0);
/// ```
pub fn to_fahrenheit(celsius: f64) -> f64 {
    celsius * 9.0 / 5.0 + 32.0
}
```

## 控制流

行注释以 `//` 开始。`if` 是表达式，分支必须产生相同类型的值；`loop`、`while` 和 `for` 提供循环控制。

```rust
fn category(score: u8) -> &'static str {
    if score >= 60 { "及格" } else { "未及格" }
}

fn main() {
    for number in 1..=3 {
        println!("第 {number} 次：{}", category(number * 30));
    }
}
```

`if` 条件不需要括号，条件必须是 `bool`，Rust 不会把整数隐式转换为真假值。由于 `if` 是表达式，所有分支的返回类型必须一致。`match` 可按枚举或其他模式分支；第 6 章会详细讨论它。

范围 `1..=3` 包含终点；`1..3` 不包含终点。需要根据条件循环时用 `while`，需要无限循环并通过 `break` 退出时用 `loop`。

循环标签可用于从嵌套循环中跳出指定层；`loop` 也可以通过 `break value` 返回值。遍历固定次数或集合时，`for` 通常比手动维护索引更安全。文档注释以 `///` 开头，可由 rustdoc 提取并展示公开 API 的说明和示例。

## 小结与练习

- Rust 绑定默认不可变；`mut`、类型标注和遮蔽分别表达不同意图。
- 语句执行动作，表达式产生值；分号会结束表达式并丢弃其值。
- 练习：编写摄氏度转华氏度的函数，再用 `if` 或 `match` 给温度分级。

再练习：实现 FizzBuzz，使用 `for` 和 `if` 表达分支；为温度转换函数补充边界测试。

下一章：[理解所有权](chapter-04-understanding-ownership.md)。

官方对应章节：[Common Programming Concepts](https://doc.rust-lang.org/book/ch03-00-common-programming-concepts.html)。
