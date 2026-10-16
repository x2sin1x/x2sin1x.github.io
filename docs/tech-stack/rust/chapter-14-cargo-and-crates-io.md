---
title: 更多 Cargo 与 crates.io
weight: 140
---
# 第 14 章：更多 Cargo 与 crates.io

> 本章目标：了解发布配置、文档、工作空间、依赖发布和安装可执行程序的 Cargo 工作流。

## 发布配置与文档

Cargo 支持 `dev` 与 `release` 构建配置。可在 `Cargo.toml` 的 `[profile.release]` 中设置优化等级等选项；应根据构建时间、二进制大小和运行性能需要作选择。

Cargo 的默认配置适合开发：编译快、调试信息充分。release profile 通常会提高优化等级，运行更快但构建更慢。配置可分别控制优化级别、调试信息、增量编译与链接时优化；只有基准测量显示收益时才调整，避免盲目增加开发构建时间。

为公开 API 编写文档注释：

```rust
/// 将摄氏温度转换为华氏温度。
///
/// # Examples
///
/// ```
/// assert_eq!(temperature::celsius_to_fahrenheit(0.0), 32.0);
/// ```
pub fn celsius_to_fahrenheit(celsius: f64) -> f64 {
    celsius * 9.0 / 5.0 + 32.0
}
```

运行 `cargo doc --open` 生成并查看文档。文档代码块可作为文档测试编译运行。

文档注释支持标题、列表、代码示例和链接。`cargo test` 会运行文档示例中的代码块；这让 API 示例也成为可执行检查。文档中可用 `//!` 为 crate 或模块编写整体说明，用 `///` 描述紧邻的项。

## 发布 crate

发布前整理 `Cargo.toml` 中的描述、许可证、仓库和关键词等元数据，确认 README、许可证文件和公开 API 完整。创建 crates.io 账户并配置令牌后，使用 `cargo login` 登录；`cargo publish` 会发布 crate。发布后，版本通常不可撤回，因此先运行测试并检查打包内容。

crate 版本遵循语义化版本约定：补丁版本修复兼容问题，小版本增加向后兼容功能，大版本表示不兼容变化。发布前使用 `cargo package --list` 检查将要发布的文件，`cargo package` 执行本地打包验证；`cargo publish --dry-run` 可提前检查发布流程。依赖其他 crate 时要遵循发布顺序，先发布被依赖的包。

## 工作空间

工作空间让多个相关包共享顶层目录与构建产物：

```toml
[workspace]
members = ["adder", "add-one"]
resolver = "3"
```

每个成员仍有自己的 `Cargo.toml`。可用 `cargo build --workspace` 构建全部成员，或用 `-p package-name` 指定包。工作空间适合需要一起开发和版本管理的多个 crate。

工作空间根清单可统一管理成员目录和共享配置。成员间通过路径依赖引用本地 crate：

```toml
[dependencies]
add-one = { path = "../add-one" }
```

各成员仍是独立包，有自己的依赖声明和发布版本；工作空间根目录共享 `Cargo.lock` 与构建输出。一个典型练习是建立库 crate 提供数值运算，再由二进制 crate 调用它。

## 使用 `cargo install` 安装二进制

`cargo install` 从 crates.io 安装包含可执行程序的包到本地 Cargo bin 目录。使用前确认来源和维护状况；库 crate 通常作为项目依赖加入 `Cargo.toml`，并不通过 `cargo install` 引入。

`cargo install` 只安装可执行程序，不会把库依赖加入当前项目。安装后的二进制位于 Cargo 的 bin 目录；若终端找不到命令，应检查该目录是否在 PATH 中。

安装本地开发版本可用 `cargo install --path .`。它适合验证命令行工具的安装体验；更新已安装版本时再次执行安装命令。安装二进制与在 `[dependencies]` 声明库依赖是两种不同工作流。

## 扩展 Cargo 自定义命令

Cargo 会查找名为 `cargo-<subcommand>` 的可执行文件，并把 `cargo <subcommand>` 后的参数传给它。自定义命令可以利用 Cargo 的项目发现和命令行习惯，但它本身仍是普通可执行程序，必须正确处理参数、错误和退出状态。开发时可通过 `cargo install --path .` 安装到本地 Cargo bin 目录，再从项目之外测试命令解析与 PATH 配置。

## 小结与练习

- Cargo 管理构建配置、文档、工作空间、依赖和二进制安装。
- 发布 crate 前检查元数据、许可证、测试与打包内容。
- 练习：把两个小 crate 放进工作空间，并为公开函数添加文档注释与可运行示例。

再练习：创建一个含 `add-one` 库与 `adder` 程序的工作空间；运行 `cargo test --workspace`；使用 `cargo package --list` 检查发布文件，并为库中的公开函数补充文档测试。

下一章：[智能指针](chapter-15-smart-pointers.md)。

官方对应章节：[More about Cargo and Crates.io](https://doc.rust-lang.org/book/ch14-00-more-about-cargo.html)。
