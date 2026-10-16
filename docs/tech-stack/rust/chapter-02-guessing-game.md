---
title: 编写猜数字游戏
weight: 20
---
# 第 2 章：编写猜数字游戏

> 本章目标：通过一个交互程序练习变量、标准输入、外部 crate、循环、比较和 `match`。

## 创建项目并读取输入

```shell
cargo new guessing-game
cd guessing-game
```

在 `src/main.rs` 中读取一行文本：

```rust
use std::io;

fn main() {
    println!("猜数字！请输入 1 到 100 之间的数字：");

    let mut guess = String::new();
    io::stdin()
        .read_line(&mut guess)
        .expect("读取输入失败");

    println!("你输入了：{guess}");
}
```

`read_line` 把用户输入追加到可变字符串中，并返回 `Result`。这里用 `expect` 在读入失败时停止程序；第 9 章会介绍更细致的错误处理。

先运行这个版本，确认程序能读取一整行；`read_line` 的返回值是读取的字节数，字符串本身还会包含换行符，所以后续解析前要调用 `trim()`。Rust 使用 `use` 把标准库模块带入当前作用域；若不导入，也能写完整路径 `std::io::stdin()`。

## 加入随机数 crate

随机数不属于标准库，本例使用 `rand`。在 `Cargo.toml` 的 `[dependencies]` 下添加：

```toml
rand = "0.10.1"
```

随后 Cargo 会解析并下载依赖，生成或更新 `Cargo.lock`，锁文件记录本次解析出的具体依赖版本。

`rand` 是 crate（可复用 Rust 代码包），当前项目是 binary crate。Cargo 根据语义化版本范围解析兼容版本，并把本次精确解析结果保存到 `Cargo.lock`。后续构建会复用锁定版本；需要主动更新时再运行 `cargo update`。`cargo doc --open` 可以查看当前项目和依赖的 API 文档。

```rust
use rand::prelude::*;

let secret = rand::rng().random_range(1..=100);
```

范围 `1..=100` 同时包含上下界。随机结果每次运行可能不同，因此不要把它写成固定的预期输出。

## 比较猜测并循环

用户输入先是 `String`，需要解析为整数。错误输入可以提示后重新输入：

```rust
let guess: u32 = match guess.trim().parse() {
    Ok(number) => number,
    Err(_) => {
        println!("请输入有效的整数。");
        continue;
    }
};
```

完整程序：

```rust
use std::cmp::Ordering;
use std::io;
use rand::prelude::*;

fn main() {
    let secret = rand::rng().random_range(1..=100);

    loop {
        println!("请输入猜测：");
        let mut input = String::new();
        io::stdin().read_line(&mut input).expect("读取输入失败");

        let guess: u32 = match input.trim().parse() {
            Ok(number) => number,
            Err(_) => {
                println!("请输入有效的整数。");
                continue;
            }
        };

        match guess.cmp(&secret) {
            Ordering::Less => println!("太小了！"),
            Ordering::Greater => println!("太大了！"),
            Ordering::Equal => {
                println!("猜对了！");
                break;
            }
        }
    }
}
```

`trim` 去除输入行末的换行符；`parse` 的目标类型由 `u32` 标注决定。`Ordering` 是表示小于、等于和大于的枚举。猜中后 `break` 退出循环。

阅读这个循环时可以拆成四步：显示提示并读取一行；修剪空白后解析 `u32`；把解析失败视为用户输入问题并继续循环；比较猜测与秘密值，只有相等时退出。`continue` 跳到下一轮，`break` 离开循环。`cmp` 返回 `Ordering`，所以 `match` 能明确处理全部结果。

运行 `cargo run`，反复输入数字直到猜中。不要打印秘密数字作为最终功能的一部分；调试时可以临时打印，完成后移除。

## 小结与练习

- 外部 crate 通过清单声明，Cargo 管理其下载与版本解析。
- `match` 同时处理比较结果与解析结果，循环让程序持续接受猜测。
- 练习：统计猜测次数；猜中后显示总次数，并拒绝范围外输入。

进一步练习：输入 `quit` 时结束程序；把读取与解析封装成返回 `Result<u32, _>` 的函数；为范围和比较规则增加单元测试。

下一章：[常见编程概念](chapter-03-common-concepts.md)。

官方对应章节：[Programming a Guessing Game](https://doc.rust-lang.org/book/ch02-00-guessing-game-tutorial.html)。
