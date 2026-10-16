---
title: 使用结构体组织相关数据
weight: 50
---
# 第 5 章：使用结构体组织相关数据

> 本章目标：用结构体建模领域数据，并用方法和关联函数定义类型行为。

## 定义与创建结构体

结构体把多个相关字段组合成一个有意义的类型。字段可具有不同类型：

```rust
struct User {
    name: String,
    email: String,
    active: bool,
    sign_in_count: u64,
}

fn main() {
    let mut user = User {
        name: String::from("Lin"),
        email: String::from("lin@example.com"),
        active: true,
        sign_in_count: 1,
    };
    user.sign_in_count += 1;
    println!("{}: {}", user.name, user.sign_in_count);
}
```

字段可变性属于整个实例，因此修改字段时实例绑定要声明为 `mut`。结构体更新语法可从旧实例复制未显式指定的字段；若字段拥有非 `Copy` 值，旧实例相应字段可能被移动。

元组结构体适用于需要独立类型但字段含义简单的场景。单元结构体没有字段，可用于实现 Trait 等用途。

结构体更新语法 `..old_user` 可复用旧实例中未显式赋值的字段。它会按字段类型移动或复制值；如果非 `Copy` 字段被移动，旧实例不能再整体使用。构造时也可以用字段简写 `User { name, email, .. }`，前提是局部变量与字段同名。

## 使用结构体编写示例程序

用元组表示矩形时，调用端要记住哪个位置代表宽和高；结构体给字段命名后，程序更容易读，也便于把相关操作放在一起：

```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

fn area(rectangle: &Rectangle) -> u32 {
    rectangle.width * rectangle.height
}

fn main() {
    let rectangle = Rectangle { width: 30, height: 50 };
    println!("{rectangle:#?} 的面积是 {}", area(&rectangle));
}
```

函数借用矩形而不是取得所有权，所以调用后仍可使用实例。`Debug` 派生让示例能够打印结构体；实际领域类型还应考虑字段是否需要对外公开，以及哪些构造方式应由函数约束。

## 方法

在 `impl` 块中定义与类型相关的函数。第一个参数为 `&self` 的函数是方法；它借用实例。方法也可使用 `&mut self` 修改实例，或用 `self` 消耗实例。

```rust
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width >= other.width && self.height >= other.height
    }

    fn square(size: u32) -> Self {
        Self { width: size, height: size }
    }
}
```

`area` 和 `can_hold` 是方法，通过实例调用；`square` 不接收 `self`，属于关联函数，常用于构造值。`Self` 指当前 `impl` 对应的类型。

```rust
let larger = Rectangle { width: 30, height: 50 };
let smaller = Rectangle { width: 10, height: 40 };
assert!(larger.can_hold(&smaller));
assert_eq!(smaller.area(), 400);
```

方法调用会自动借用接收者，因此 `smaller.area()` 等价于以 `&smaller` 调用。方法签名中的 `&self`、`&mut self` 和 `self` 分别表达共享借用、可变借用和取得所有权。

## 派生调试输出

开发时常用 `Debug` 格式查看结构体：

```rust
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    println!("{:#?}", Point { x: 3, y: 5 });
}
```

`{:?}` 和 `{:#?}` 要求类型实现 `Debug`。`derive` 可以自动实现常见 Trait；更复杂的显示格式可以自行实现 `Display`。

用 `PartialEq` 和 `Eq` 可以比较结构体，`Clone` 可以显式复制字段。派生 Trait 前要确认字段类型也实现该 Trait；包含浮点数的类型通常不能实现 `Eq`，因为 NaN 与自身比较也不相等。调试打印适合开发期检查值，面向用户的稳定格式则应实现 `Display`。

## 小结与练习

- 结构体将相关状态组织成一个类型；字段拥有各自类型和所有权语义。
- 方法定义类型行为；关联函数不依赖某个实例，常用于构造。
- 练习：为 `Rectangle` 增加 `perimeter` 方法和 `square` 关联函数，再比较两块矩形的面积。

完整练习：从两个 `u32` 参数创建矩形，编写 `area`、`can_hold` 和 `square`，为矩形派生调试格式，并用断言验证面积与包含关系。

下一章：[枚举与模式匹配](chapter-06-enums.md)。

官方对应章节：[Using Structs to Structure Related Data](https://doc.rust-lang.org/book/ch05-00-structs.html)。
