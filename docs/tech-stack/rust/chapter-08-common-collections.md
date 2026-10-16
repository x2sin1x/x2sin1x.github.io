---
title: 常见集合
weight: 80
---
# 第 8 章：常见集合

> 本章目标：使用 `Vec<T>`、`String` 和 `HashMap<K, V>` 管理运行时增长的数据。

## 向量 `Vec<T>`

向量在堆上保存同类型元素，可在运行时增长：

```rust
let mut scores = vec![88, 92, 75];
scores.push(95);

for score in &scores {
    println!("{score}");
}
```

可用索引读取，但越界会 panic。若位置可能不存在，使用 `get` 并处理 `Option`：

```rust
if let Some(second) = scores.get(1) {
    println!("第二项：{second}");
}
```

借用元素时不能同时改变向量导致其重新分配；所有权规则会阻止无效引用。

`Vec::new()` 创建空向量；若编译器无法从后续插入推断元素类型，可写 `Vec::<i32>::new()`。`push` 在末尾添加元素，`pop` 移除并返回最后一个元素。索引表达式适合已知边界的情况；面对用户提供的索引，应选择 `get`，并用 `Option` 处理不存在的元素。遍历时按值、按共享引用或按可变引用访问，会决定元素是否移动或可修改。

## UTF-8 字符串

`String` 是可增长、拥有所有权的 UTF-8 字符串；`&str` 是字符串切片。可以用 `push` 和 `push_str` 修改 `String`。字符串不支持整数索引，因为 UTF-8 字符可能占多个字节，按字节索引不一定落在字符边界。

```rust
let mut text = String::from("你好");
text.push('，');
text.push_str("Rust");
for character in text.chars() {
    print!("{character} ");
}
```

根据问题选择 `bytes()`、`chars()`、`char_indices()` 或 `split_whitespace()`。它们表达的遍历单位不同。

`+` 拼接会取得左侧 `String` 的所有权，并借用右侧字符串切片；格式化多个片段时 `format!` 更清晰。`String` 是字节序列而不是可随机访问的字符数组。`len()` 返回字节数；`chars().count()` 计算 Unicode 标量值数量；组合附加符和表情序列等用户感知字符还可能由多个标量值组成，需要 Unicode 分段库才能按字素簇处理。

```rust
let hello = String::from("你好");
assert_eq!(hello.len(), 6); // UTF-8 字节数
assert_eq!(hello.chars().count(), 2); // Unicode 标量值数量
```

## 哈希映射

`HashMap<K, V>` 通过键查找对应值。使用 `entry` 可以简洁地累计计数：

```rust
use std::collections::HashMap;

let mut counts = HashMap::new();
for word in ["rust", "safe", "rust"] {
    *counts.entry(word).or_insert(0) += 1;
}
assert_eq!(counts.get("rust"), Some(&2));
```

插入拥有所有权的键和值时，映射会取得它们；若传入引用，则需保证引用有效。哈希映射遍历顺序不固定，不应依赖特定顺序。

用 `insert` 添加或覆盖键值；`get` 借用值，`remove` 删除条目。键和值分别实现 `Hash` 与 `Eq`，才可用于标准 `HashMap`。`entry(key).or_insert(default)` 返回对应值的可变引用，可在键不存在时插入默认值；这也适合保存旧值并基于它更新。若需要稳定遍历顺序，可按需求使用 `BTreeMap`。

```rust
let mut scores = HashMap::new();
scores.insert(String::from("Blue"), 10);
let score = scores.entry(String::from("Blue")).or_insert(0);
*score += 5;
assert_eq!(scores.get("Blue"), Some(&15));
```

## 小结与练习

- `Vec<T>` 维护有序元素，`String` 保存 UTF-8 文本，`HashMap` 保存键值关系。
- 对可能越界的访问用 `get`；处理字符串时明确字节、字符和文本边界。
- 练习：统计一段文本中每个单词的出现次数，并按字母顺序输出结果。

再练习：分别用 `Vec`、`String` 和 `HashMap` 做一个简化的投票统计；测试不存在的索引、空字符串和重复键的行为。

下一章：[错误处理](chapter-09-error-handling.md)。

官方对应章节：[Common Collections](https://doc.rust-lang.org/book/ch08-00-common-collections.html)。
