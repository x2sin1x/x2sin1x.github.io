---
title: 入门：安装、Hello World 与 Cargo
weight: 10
---
# 第 1 章：入门

> 本章目标：安装 Rust 工具链，编译并运行第一个程序，认识 Cargo 项目的基本结构。

## 安装 Rust

Rust 项目推荐使用 `rustup` 管理工具链。它负责安装编译器 `rustc`、包管理与构建工具 `cargo`，也可以切换 stable、beta 和 nightly 工具链。根据操作系统按照[官方安装指南](https://rust-lang.org/install/)操作。

安装后重启终端并检查：

```shell
rustc --version
cargo --version
rustup show active-toolchain
```

本教程采用 Rust 2024 Edition；官方 Book 当前以 Rust 1.97.0 或更新版本为基础。Edition 是项目选择的一组语言约定，不是编译器版本。不同 Edition 的 crate 可以互相依赖。

工具链检查也能帮助定位常见问题：`rustup show` 会列出已安装的工具链与目标；`rustup update stable` 更新 stable；`rustup doc` 打开本地文档。若终端提示找不到 `rustc`，先重开终端，再确认 Cargo 的 bin 目录已加入 PATH。Windows 上 MSVC 工具链还需要相应的 C++ 构建工具。

编辑器不影响 Rust 语言本身。可以使用支持 rust-analyzer 的编辑器获得补全、跳转和诊断；Rustup 安装的标准工具链还包含 rustfmt 与 Clippy，可分别用于格式化和静态建议。

## Hello, world!

创建 `main.rs`：

```rust
fn main() {
    println!("Hello, world!");
}
```

用 `rustc` 编译并运行：

```shell
rustc main.rs
./main
```

Windows 终端中可运行 `main.exe`。`fn main()` 是可执行程序入口；`println!` 后的 `!` 表示宏调用。Rust 源文件通常使用 `.rs` 扩展名。

## 使用 Cargo 创建项目

Cargo 帮助创建项目、解析依赖、编译代码和运行测试。创建项目：

```shell
cargo new hello-cargo
cd hello-cargo
```

目录中会生成 `Cargo.toml` 和 `src/main.rs`。清单文件描述包元信息、Edition 与依赖：

```toml
[package]
name = "hello-cargo"
version = "0.1.0"
edition = "2024"

[dependencies]
```

在项目根目录运行：

```shell
cargo check
cargo run
```

`cargo check` 快速检查代码但不生成最终可执行文件；`cargo run` 编译并运行。要只编译，可用 `cargo build`；加 `--release` 会使用优化配置。

这些命令都应在包含 `Cargo.toml` 的项目根目录运行。应用一般会把 `Cargo.lock` 纳入版本控制，以便团队使用相同的依赖解析结果。若只想创建单个源文件，`rustc main.rs` 也可以编译；实际项目通常使用 Cargo，因为依赖、测试、示例和发布流程都由 Cargo 统一管理。

## 小结与练习

- `rustup` 管理工具链，`rustc` 编译 Rust，Cargo 管理项目工作流。
- `Cargo.toml` 是项目清单，程序入口通常在 `src/main.rs`。
- 练习：修改问候文本，分别运行 `cargo check`、`cargo build` 和 `cargo run`，观察用途差异。

官方对应章节：[Getting Started](https://doc.rust-lang.org/book/ch01-00-getting-started.html)。

下一章：[编写猜数字游戏](chapter-02-guessing-game.md)。
