---
title: 编写自动化测试
weight: 110
---
# 第 11 章：编写自动化测试

> 本章目标：使用 Cargo 测试验证程序行为，理解单元测试和集成测试的区别。

## 测试函数

测试函数通常断言代码是否满足预期。用 `#[test]` 标记，运行 `cargo test`：

```rust
pub fn add(left: u32, right: u32) -> u32 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds_two_numbers() {
        assert_eq!(add(2, 3), 5);
    }
}
```

`assert!` 检查布尔条件；`assert_eq!` 和 `assert_ne!` 比较值并在失败时显示差异。失败信息可追加自定义格式参数。

测试函数是普通 Rust 函数，通常没有参数并返回 `()`。Cargo 会编译测试目标并运行测试 harness；测试名称默认按字母排序，输出显示通过、失败或忽略数量。失败时查看断言差异和源码行号，先缩小失败条件，再修复实现或测试数据。

## 控制测试运行方式

测试运行默认并行，以缩短时间。依赖共享状态或外部资源的测试可能需要隔离；可通过 `cargo test -- --test-threads=1` 串行运行。向测试 harness 传递参数要放在 `--` 之后。`#[ignore]` 可暂时跳过耗时测试，运行时使用 `cargo test -- --ignored` 显式执行；忽略测试应保留原因说明。

测试名可以作为过滤器：`cargo test add` 只运行名称中包含 `add` 的测试；`cargo test -- --show-output` 可显示成功测试的标准输出。`cargo test` 默认会捕获通过测试的输出，失败时则显示相关输出。`#[should_panic(expected = "索引越界")]` 不仅检查发生 panic，还可确认错误信息包含预期文本。

## 预期 panic 与返回错误

若测试目标是确认某操作 panic，可使用 `#[should_panic]`，也可用 `expected` 限定 panic 消息。对复杂错误行为，返回 `Result<(), E>` 的测试可以用 `?` 传播测试准备阶段的错误，最终返回 `Ok(())`。

```rust
#[test]
#[should_panic(expected = "index out of bounds")]
fn out_of_range_index_panics() {
    let values = [1, 2, 3];
    let _ = values[10];
}

#[test]
fn parses_fixture() -> Result<(), std::num::ParseIntError> {
    let value = "42".parse::<i32>()?;
    assert_eq!(value, 42);
    Ok(())
}
```

## 单元测试与集成测试

单元测试放在源码的 `#[cfg(test)]` 模块中，能够访问当前模块的私有实现。集成测试位于项目根目录 `tests/` 下，每个文件作为独立 crate 编译，只能通过公开 API 使用被测库。

```text
my-library/
├── src/lib.rs
└── tests/integration_test.rs
```

可用测试名称过滤器只运行匹配项；`cargo test -- --test-threads=1` 可串行运行测试，测试后面的参数通过 `--` 传给测试执行器。

库 crate 的单元测试可以访问私有函数，因此适合覆盖模块内部边界情况。集成测试通过 crate 的公开接口验证消费者能否正确使用库。`tests/common/` 可放置帮助模块，但测试运行器不会把它当作独立测试目标；需要在测试文件中通过 `mod common;` 引入。

二进制 crate 的集成测试不能直接访问 `main.rs` 中的私有实现。若业务逻辑需要广泛测试，可将它移入 `src/lib.rs`，让 `main.rs` 只保留参数解析和程序入口。

## 小结与练习

- 测试用断言表达预期；失败会让 Cargo 将该测试标记为失败。
- 单元测试检查内部模块，集成测试通过公开接口验证整体行为。
- 练习：为字符串统计函数添加正常输入、空输入、标点和大小写的测试。

再练习：分别添加成功断言、预期 panic 测试、返回 `Result` 的测试和一项忽略测试；创建 `tests/` 集成测试，验证公开函数的输入输出。

下一章：[构建命令行 I/O 项目](chapter-12-io-project.md)。

官方对应章节：[Writing Automated Tests](https://doc.rust-lang.org/book/ch11-00-testing.html)。
