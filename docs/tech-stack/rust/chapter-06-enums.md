---
title: 枚举与模式匹配
weight: 60
---
# 第 6 章：枚举与模式匹配

> 本章目标：用枚举表达有限状态，利用模式匹配处理每种可能情况。

## 定义枚举

枚举表示一个值只能属于若干变体之一。不同变体可以携带不同类型和数量的数据：

```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(u8, u8, u8),
}
```

比起用整数或字符串约定状态，枚举让合法状态显式可见。可以在 `impl` 中为枚举定义方法。

枚举变体可像结构体一样使用命名字段，也可使用元组字段或不携带数据。它们共享一个类型，因此函数参数可以接收整个枚举，并依据变体执行不同逻辑。枚举也可以嵌套其他枚举或结构体。

## `Option<T>` 表达缺失值

Rust 没有空指针作为任意类型的默认值。`Option<T>` 把“有值”和“没有值”写进类型：

```rust
let present: Option<i32> = Some(5);
let absent: Option<i32> = None;
```

使用 `Option` 时必须处理 `Some(value)` 与 `None`，从类型层面提醒调用者考虑缺失情况。`Option<T>` 与 `T` 不是同一类型，需要显式匹配或转换后才能使用内部值。

常用方法包括 `is_some`、`is_none`、`map`、`and_then` 和 `unwrap_or`。它们适合把简单转换或默认值逻辑留在 `Option` 链中；必须做多个不同动作时，`match` 更容易阅读。避免对外部数据直接 `unwrap`，除非程序逻辑已证明它一定存在。

## `match` 穷尽处理

`match` 根据值的形态选择分支。编译器要求覆盖所有可能变体：

```rust
enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter,
}

fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter => 25,
    }
}
```

分支可以绑定变体中的数据。`_` 可匹配其余情况；`other` 这类变量模式会绑定尚未匹配的值。穷尽匹配能让增加新变体后遗漏处理的代码及时暴露。

分支可以用逗号组合多个模式，也可用 `if` 添加匹配守卫。匹配表达式本身会产生值，所以可直接赋给变量。匹配引用时，模式可以解构其内部数据；注意是否移动了非 `Copy` 字段，必要时借用字段。

## `if let` 简化单分支匹配

只关心一个模式时，`if let` 可以减少样板代码：

```rust
let config_max = Some(3u8);
if let Some(max) = config_max {
    println!("上限为 {max}");
}
```

如果还要处理其余情况，可以配合 `else`。需要覆盖所有情况或逻辑分支较多时，使用 `match` 更清楚。

`let...else` 可在模式不匹配时提前退出当前作用域，适合“成功提取后继续、失败就返回”的校验流程：

```rust
fn port_from_config(value: Option<u16>) -> u16 {
    let Some(port) = value else {
        return 8080;
    };
    port
}
```

## 小结与练习

- 枚举将有限状态及其数据建模为一个类型；`Option<T>` 显式表达可能缺失。
- `match` 必须穷尽，`if let` 适合只关心少数模式的场景。
- 练习：定义包含 `Quit`、`Move` 和 `Text` 的消息枚举，并写函数按变体生成说明文字。

再练习：为枚举增加一个携带结构体字段的变体；用 `match` 计算变体对应结果，再用 `if let` 只处理一个状态；使用 `let...else` 从可选配置中取出必填字段。

下一章：[使用包、crate 与模块管理项目](chapter-07-packages-crates-modules.md)。

官方对应章节：[Enums and Pattern Matching](https://doc.rust-lang.org/book/ch06-00-enums.html)。
