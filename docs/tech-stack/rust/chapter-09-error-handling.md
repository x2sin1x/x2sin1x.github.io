---
title: 错误处理
weight: 90
---
# 第 9 章：错误处理

> 本章目标：区分不可恢复错误与可恢复错误，并在调用链中传递失败信息。

## 不可恢复错误与 panic

程序遇到无法继续的状态时可以 panic。`panic!` 会展开调用栈（或按配置终止进程），清理当前线程资源并报告错误。数组越界等标准库操作也可能 panic。

```rust
fn main() {
    let values = [1, 2, 3];
    println!("{}", values[5]); // 越界会 panic
}
```

库代码通常应让调用者决定如何恢复；应用入口则可以在遇到不可恢复状态时终止。不要把用户输入错误当成程序 bug 使用 `panic!`。

调试时可设置 `RUST_BACKTRACE=1` 查看 panic 调用栈。回溯能帮助定位 panic 发生的位置；优先关注第一个指向本项目代码的栈帧。程序也可以通过 `panic = "abort"` 配置改为直接终止，但这会改变清理过程和诊断信息。

## 可恢复错误与 `Result`

`Result<T, E>` 用 `Ok(T)` 表示成功，用 `Err(E)` 表示失败。调用者可以根据错误采取重试、提示或回退措施：

```rust
use std::{fs::File, io};

fn open_config(path: &str) -> Result<File, io::Error> {
    File::open(path)
}
```

处理文件创建等需要区分错误原因时，可用 `match` 检查 `ErrorKind`。`unwrap` 在 `Err` 时 panic；`expect` 还能提供上下文消息。它们适用于已确认不会失败的场景或教学示例，不适合未验证的外部输入路径。

```rust
use std::{fs::File, io::ErrorKind};

fn create_or_open(path: &str) -> std::io::Result<File> {
    match File::open(path) {
        Ok(file) => Ok(file),
        Err(error) if error.kind() == ErrorKind::NotFound => File::create(path),
        Err(error) => Err(error),
    }
}
```

真实程序应先确认“文件不存在就创建”符合业务语义；示例展示的是按错误种类分支。

## 传播错误

`?` 在结果为 `Err` 时提前从当前函数返回，在 `Ok` 时取出内部值。返回错误类型需要能够接收被传播的错误：

```rust
use std::{fs, io};

fn read_username(path: &str) -> Result<String, io::Error> {
    let text = fs::read_to_string(path)?;
    Ok(text.trim().to_owned())
}
```

`?` 也可用于 `Option` 返回路径。应用可在 `main` 返回 `Result`，由运行时报告错误；大型程序常在边界处添加更具体的上下文。

```rust
use std::{error::Error, fs};

fn read_config(path: &str) -> Result<String, Box<dyn Error>> {
    let text = fs::read_to_string(path)?;
    Ok(text)
}

fn main() -> Result<(), Box<dyn Error>> {
    let config = read_config("config.txt")?;
    println!("配置长度：{}", config.len());
    Ok(())
}
```

当 `main` 返回 `Result` 时，成功返回 `Ok(())`，错误会作为程序失败报告。不要仅为了缩短代码而吞掉错误；如果提供默认值，应明确说明该默认策略。

## 决定何时 panic

若调用者能合理恢复，返回 `Result`；若发生错误意味着程序状态已违反不变量，panic 可能更合适。解析用户输入、打开外部文件通常是可恢复错误；访问程序内部不可能越界的数据时，断言可帮助暴露逻辑 bug。测试中可用 `assert!` 检查不变量。

## 小结与练习

- `panic!` 用于无法恢复的程序状态；`Result` 将可恢复错误交给调用者。
- `?` 简化错误传播，不会替调用者决定如何处理失败。
- 练习：读取文件中的整数并解析，分别处理文件读取失败和格式错误。

再练习：分别设计“配置文件缺失时使用默认配置”和“必需文件缺失时返回错误”两种接口，比较错误信息如何帮助调用者做决定。

下一章：[泛型、Trait 与生命周期](chapter-10-generics-traits-lifetimes.md)。

官方对应章节：[Error Handling](https://doc.rust-lang.org/book/ch09-00-error-handling.html)。
