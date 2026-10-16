---
title: 迭代器与闭包
weight: 130
---
# 第 13 章：迭代器与闭包

> 本章目标：使用闭包捕获环境变量，用迭代器组合数据转换，并改进第 12 章的搜索项目。

## 闭包

闭包是可赋值、传递或立即调用的匿名函数。编译器通常能推断参数和返回类型；闭包也可以捕获定义环境中的值：

```rust
let threshold = 10;
let is_large = |value: &i32| *value > threshold;
assert!(is_large(&12));
```

闭包按需借用或取得捕获值。使用 `move` 可将捕获值移动进闭包，常用于把闭包交给线程或异步任务。捕获方式决定闭包实现的 `Fn`、`FnMut` 或 `FnOnce` 特性。

闭包会按其调用方式实现一个或多个调用 Trait：`Fn` 可重复调用且只共享借用捕获值；`FnMut` 可重复调用并修改捕获状态；`FnOnce` 至少可调用一次，可能消耗捕获值。编译器根据闭包主体实际做的事推断所需 Trait。

```rust
let color = String::from("green");
let print_color = || println!("{color}"); // 只读借用，可重复调用
print_color();
print_color();

let mut count = 0;
let mut increment = || count += 1; // 可变借用
increment();
```

闭包定义时编译器会为捕获环境生成匿名类型。标准库的 `unwrap_or_else`、排序和线程 API 都会接收闭包，因此理解捕获与调用 Trait 能帮助读懂这些接口。

## 迭代器与惰性适配器

迭代器逐项产生值。`map`、`filter` 等适配器通常是惰性的，直到消费操作（如 `collect`、`sum` 或 `for`）发生才执行：

```rust
let values = [1, 2, 3, 4, 5];
let squares: Vec<i32> = values
    .iter()
    .filter(|value| **value % 2 == 1)
    .map(|value| *value * *value)
    .collect();
assert_eq!(squares, vec![1, 9, 25]);
```

`iter()` 借用元素，`iter_mut()` 可变借用，`into_iter()` 通常消费集合并移出元素。选择哪种迭代器会影响所有权和后续能否继续使用集合。

`Iterator` Trait 的核心方法是 `next`，返回 `Option<Self::Item>`。迭代器适配器（如 `map`、`filter`、`take`、`zip`）返回新的迭代器；消费者（如 `collect`、`sum`、`fold`）遍历并产生最终结果。迭代器通常惰性求值，所以未被消费的适配器不会执行。

```rust
let sum: i32 = [1, 2, 3].iter().sum();
let doubled: Vec<_> = [1, 2, 3].iter().map(|n| n * 2).collect();
assert_eq!(sum, 6);
assert_eq!(doubled, vec![2, 4, 6]);
```

实现 `Iterator` 时要定义关联类型 `Item` 和 `next`。自定义迭代器可以复用标准适配器，而不必自己实现整条数据处理链。

## 改进搜索项目

第 12 章的 `search` 可以用迭代器表达：

```rust
pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    contents
        .lines()
        .filter(|line| line.contains(query))
        .collect()
}
```

迭代器版本避免手动创建和逐项填充临时向量。闭包表达过滤条件，使数据流更集中。对 `minigrep` 来说，优化后应保留已有测试，确保行为没有改变。

还可以把筛选函数改为接收谓词闭包，让调用者决定匹配规则：

```rust
fn search_with<'a>(
    contents: &'a str,
    predicate: impl Fn(&str) -> bool,
) -> Vec<&'a str> {
    contents.lines().filter(|line| predicate(line)).collect()
}
```

生产代码可将大小写策略放在配置层，再选择相应谓词。测试应保证重构后结果与原始搜索保持一致。

## 性能思路

迭代器适配器常通过单态化和优化编译为高效循环。手写 `for` 循环和迭代器链最终可能生成相近机器码；清晰表达意图的迭代器不必然更慢。性能不能只凭语法判断，应测量实际工作负载，并避免为微小数据量牺牲可读性。

## 小结与练习

- 闭包捕获环境，捕获方式会影响所有权和调用能力。
- 迭代器适配器描述处理步骤，消费操作触发计算。
- 练习：将第 12 章搜索结果改为返回迭代器，并更新调用端和测试。

再练习：实现产生斐波那契数的自定义迭代器；用 `take` 限制项数，并用 `map` 和 `sum` 计算结果；为大小写不敏感搜索提取闭包谓词。

下一章：[更多 Cargo 与 crates.io](chapter-14-cargo-and-crates-io.md)。

官方对应章节：[Functional Language Features: Iterators and Closures](https://doc.rust-lang.org/book/ch13-00-functional-features.html)。
