---
title: 构建命令行 I/O 项目
weight: 120
---
# 第 12 章：构建命令行 I/O 项目

> 本章目标：逐步构建 `minigrep` 风格的命令行搜索工具，并练习参数解析、文件读取、模块拆分、环境变量和测试。

## 项目目标与参数

工具接受查询字符串和文件路径，在文件中查找匹配行。创建项目：

```shell
cargo new minigrep
cd minigrep
```

程序通过 `std::env::args` 获取命令行参数。先检查参数数量，再读取文件并搜索：

```rust
use std::{env, fs, process};

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        eprintln!("用法：minigrep <查询词> <文件>");
        process::exit(2);
    }

    let query = &args[1];
    let path = &args[2];
    let contents = fs::read_to_string(path).unwrap_or_else(|error| {
        eprintln!("读取 {path} 失败：{error}");
        process::exit(1);
    });

    for line in search(query, &contents) {
        println!("{line}");
    }
}

fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    contents.lines().filter(|line| line.contains(query)).collect()
}
```

## 读取文件

`fs::read_to_string` 将 UTF-8 文本文件读入 `String`；文件不存在、权限不足或文本不是有效 UTF-8 时会返回错误。示例用 `unwrap_or_else` 报告路径和错误并退出。为便于阅读和测试，正式实现应将参数解析、配置构建和搜索逻辑拆分到库 crate。

`eprintln!` 写入标准错误，避免诊断信息混入程序正常输出。读取完整文件适合小型文本；处理大型文件时可以考虑缓冲读取，避免一次把全部内容载入内存。

命令行参数通过 `args()` 取得，第一项通常是程序路径，之后才是用户参数。若查询词或文件路径缺失，应打印用法并以非零状态退出。`std::env::args` 假设参数是有效 Unicode；若工具需要接受任意操作系统路径，应改用 `args_os`。

## 用配置类型与 `Result` 组织程序

在 `src/lib.rs` 中定义配置与业务函数，让二进制入口只负责连接输入输出：

```rust
use std::{error::Error, fs};

pub struct Config {
    pub query: String,
    pub file_path: String,
}

impl Config {
    pub fn build(mut args: impl Iterator<Item = String>) -> Result<Self, &'static str> {
        let _program = args.next();
        let query = args.next().ok_or("缺少查询词")?;
        let file_path = args.next().ok_or("缺少文件路径")?;
        Ok(Self { query, file_path })
    }
}

pub fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let contents = fs::read_to_string(config.file_path)?;
    for line in search(&config.query, &contents) {
        println!("{line}");
    }
    Ok(())
}

pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    contents.lines().filter(|line| line.contains(query)).collect()
}
```

`main` 调用 `Config::build` 和 `run`，在边界处打印错误并选择退出状态。这样 `search` 可独立测试，不需要真实文件或终端。

`Config::build` 只负责验证输入并构造配置；`run` 负责执行应用逻辑。错误在这两个函数中向上返回，`main` 负责把它们翻译成用户可读信息。错误类型可以先用 `String` 或 `&'static str` 表示参数问题；文件 I/O 则返回标准库错误。随着程序增大，可定义专用错误类型携带更明确上下文。

```rust
fn main() {
    let config = minigrep::Config::build(std::env::args()).unwrap_or_else(|error| {
        eprintln!("参数错误：{error}");
        std::process::exit(2);
    });

    if let Err(error) = minigrep::run(config) {
        eprintln!("应用错误：{error}");
        std::process::exit(1);
    }
}
```

## 环境变量与大小写

可以使用 `std::env::var` 读取配置，例如设置 `IGNORE_CASE` 后选择大小写不敏感搜索。检查环境变量时，处理变量不存在的情况；测试时要注意进程环境是共享状态，测试之间不要相互依赖。将选择逻辑放进配置构造阶段，让搜索函数仍保持纯函数：

```rust
use std::env;

let ignore_case = env::var("IGNORE_CASE").is_ok();
let config = Config { query, file_path, ignore_case };
```

在前一节的 `Config` 中加入 `ignore_case: bool` 字段，并在 `Config::build` 验证完参数后读取环境变量。环境变量存在且可读取时启用忽略大小写，否则按默认的区分大小写模式运行。

搜索函数可以拆成区分大小写和忽略大小写的实现。比较时统一将查询词和行转为小写会创建额外字符串；教学项目中可先采用简单实现，再分析更高效的方案。

```rust
pub fn search_case_insensitive<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    let query = query.to_lowercase();
    contents.lines()
        .filter(|line| line.to_lowercase().contains(&query))
        .collect()
}
```

先写测试描述期望，再补上实现；下面的测试要求查询词和文本中的大小写不同也能匹配：

```rust
#[test]
fn case_insensitive_search_finds_mixed_case() {
    let contents = "Rust: safe\nrust: fast\nGo: concurrent";
    assert_eq!(
        search_case_insensitive("rUsT", contents),
        vec!["Rust: safe", "rust: fast"]
    );
}
```

环境变量适合控制进程级选项；配置读取最好集中在构造阶段，不要让搜索函数在每一行都查询环境。`run` 根据 `config.ignore_case` 选择 `search` 或 `search_case_insensitive`，再打印匹配行。将查询词转成小写只做一次，逐行转换仍会分配字符串；对完整 Unicode 文本做大小写不敏感比较也可能需要更精细的 Unicode 规范化策略，这个版本保持教学代码的简单性。

## 用测试驱动开发添加功能

在库 crate 的 `#[cfg(test)]` 模块中测试匹配和不匹配行，以及大小写选项。测试输入直接作为字符串提供，能快速验证业务逻辑。

```rust
#[test]
fn finds_matching_lines() {
    let contents = "Rust is fast.\nOther language.\nRust is safe.";
    assert_eq!(search("Rust", contents), vec!["Rust is fast.", "Rust is safe."]);
}
```

运行 `cargo test`。手动验证时创建一个文本文件，再运行 `cargo run -- to poem.txt`；`--` 之后的参数会传给程序。

按照测试驱动开发（TDD）推进时，先为一个失败行为写测试，再写足以通过测试的实现，然后重构。搜索逻辑是纯函数，适合用字符串输入覆盖匹配、未匹配和边界情况。每轮只增加一个可观察行为，例如先测试匹配行，再测试大小写规则；这样失败反馈更容易定位。

## 将错误写入标准错误

运行时用 `cargo run -- <查询词> <文件>`；通过 shell 重定向标准输出时，错误仍会保留在终端，因为它写入 stderr。可用 `>` 保存匹配结果，用 `2>` 单独保存错误信息，例如 `cargo run -- to poem.txt > matches.txt 2> errors.txt`。`eprintln!` 与 `println!` 的区别就在于目标流不同。将诊断消息写入 stderr 可让其他程序继续通过管道读取 stdout 中的搜索结果。

## 小结与练习

- 将配置解析、搜索逻辑和终端 I/O 分开，能让代码更易测试。
- 用 `Result` 表达可恢复错误，并在程序边界选择输出和退出状态。
- 练习：为忽略大小写的搜索添加测试；为缺少参数和无法读取文件的情况提供清晰错误。

再练习：添加一个环境变量来控制大小写；把错误输出改为包含操作名称和路径；使用 shell 重定向验证 stdout 与 stderr 相互独立。

下一章：[迭代器与闭包](chapter-13-iterators-closures.md)。

官方对应章节：[An I/O Project: Building a Command Line Program](https://doc.rust-lang.org/book/ch12-00-an-io-project.html)。
