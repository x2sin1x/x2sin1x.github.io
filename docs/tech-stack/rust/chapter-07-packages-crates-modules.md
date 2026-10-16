---
title: 使用包、crate 与模块管理项目
weight: 70
---
# 第 7 章：使用包、crate 与模块管理项目

> 本章目标：理解包、crate 和模块的区别，并通过路径、可见性和文件拆分组织项目。

## 包与 crate

crate 是 Rust 编译的最小单元，可以是二进制程序或库。包（package）由 Cargo 管理，通过 `Cargo.toml` 描述；一个包可包含一个库 crate、多个二进制 crate，以及集成测试和示例。

典型项目：

```text
my-project/
├── Cargo.toml
└── src/
    ├── main.rs
    └── lib.rs
```

`src/main.rs` 是默认二进制 crate 根；`src/lib.rs` 是库 crate 根。

crate 根由 Cargo 惯例确定：`src/main.rs`、`src/lib.rs`，以及 `src/bin/` 下的文件。一个包至少有一个 crate；包最多有一个库 crate，但可有多个二进制目标。crate 根是模块树的起点，`mod` 声明的子模块构成树状结构。

## 用模块控制作用域与可见性

模块按逻辑职责分组代码，并建立树状命名空间。路径可以从 crate 根开始（`crate::...`），也可以相对当前模块书写（`self::...`、`super::...`）。

```rust
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

fn main() {
    crate::front_of_house::hosting::add_to_waitlist();
}
```

模块和成员默认私有，`pub` 用于暴露接口。子模块可以访问其祖先模块的私有项，反向访问则需公开。结构体字段默认仍是私有的，即使结构体本身是 `pub`；枚举变体则随公开枚举一起公开。公开构造函数常用于维护结构体的不变量。

模块边界既是组织方式，也是封装边界：调用方只需要知道公开函数和类型，不需要了解内部实现。将实现保持为私有，可在不改变公开接口的前提下重构内部代码。

## 在模块树中使用路径

绝对路径从 crate 根开始，可写 `crate::front_of_house::hosting::add_to_waitlist()`；二进制 crate 引用同包库时通常以包名开始。相对路径从当前位置开始，`self::` 表示当前模块，`super::` 表示父模块。绝对路径在移动模块后往往更稳定；相对路径适合模块内部紧密关联的实现。

## 使用 `use` 将路径引入作用域

`use` 导入后可用短名称调用。导入函数通常引入其父模块，导入结构体、枚举等类型通常直接引入类型。重命名可避免冲突：`use std::fmt::Result as FmtResult;`。导入多个相邻项时可用嵌套路径减少重复前缀；通配导入适用于测试前导模块等明确场景，公共模块里应谨慎使用以免名称来源不清。`pub use` 会重新导出路径，让使用者通过更方便的公共路径访问内部模块，也能帮助库在调整内部文件结构时维持稳定 API。

## 将模块拆到文件

模块可放在根文件中，也可拆成独立文件。将上例拆分时，可在 `src/lib.rs` 中声明 `mod front_of_house;`，并将模块内容放入 `src/front_of_house.rs`；更深层模块可继续拆分为子目录中的文件。

先按职责建立清楚的模块边界，再决定文件布局。文件拆分是模块树的组织方式，不会改变路径和可见性规则。

文件模块声明 `mod garden;` 会让编译器查找 `src/garden.rs` 或 `src/garden/mod.rs`；子模块可放在 `src/garden/vegetables.rs` 等位置。模块树仍由 `mod` 声明决定，文件夹本身不会自动成为模块。

## 小结与练习

- Cargo 管理包，crate 是编译单元，模块组织 crate 内部名称和可见性。
- 路径定位项，`use` 简化引用，`pub` 控制公开接口。
- 练习：创建 `temperature` 模块，提供摄氏与华氏转换函数，并从二进制入口调用。

再练习：把转换库拆为 `temperature` 与 `units` 子模块；让实现函数保持私有，只公开稳定的转换接口；通过 `pub use` 提供更短的调用路径。

下一章：[常见集合](chapter-08-common-collections.md)。

官方对应章节：[Packages, Crates, and Modules](https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html)。
