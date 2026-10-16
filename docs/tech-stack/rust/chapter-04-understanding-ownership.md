---
title: 理解所有权
weight: 40
---
# 第 4 章：理解所有权

> 本章目标：理解 Rust 如何在编译期管理内存，并使用引用和切片而不复制数据。

## 所有权规则

所有权是 Rust 管理值与内存的核心机制。每个值都有一个所有者；同一时刻只有一个所有者；所有者离开作用域时，值会被清理。编译器在编译期检查这些规则，因此常见的悬垂引用和重复释放问题会被拒绝。

栈适合大小固定、生命周期随调用栈变化的数据。堆适合运行时大小可变的数据；`String` 会管理堆上的 UTF-8 缓冲区。

变量的作用域从声明处开始，到包含它的块结束。值离开作用域时 Rust 自动执行清理逻辑。`String` 可增长，因此通常把指针、长度和容量等元数据放在栈上，把文本缓冲区放在堆上；`String::from` 创建拥有缓冲区的字符串，字符串字面量则通常是程序二进制中的只读数据。

## 移动与复制

赋值 `String` 时通常移动所有权，而不是复制堆内存：

```rust
let first = String::from("hello");
let second = first;
// first 已失效，所有权现在属于 second
```

这避免两个值同时释放同一缓冲区。需要明确复制堆数据时调用 `clone`。实现 `Copy` 的简单类型（如整数）赋值时会复制值，而不移动。

移动转移资源的管理权，旧绑定不能继续使用；`Copy` 类型适合按位复制，类型若拥有需要释放的资源就不能实现 `Copy`。函数调用遵循同一规则：把值传给函数可能移动它；函数返回值则可以把所有权交还调用者。借用让函数访问数据而不取得所有权。

函数调用和返回也会转移所有权：值传入函数后由参数拥有；函数返回值可以把所有权交还给调用者。引用允许函数临时访问数据而不取得所有权。

## 借用

不可变引用 `&T` 允许读取；可变引用 `&mut T` 允许修改。一个作用域内可以有多个不可变引用，或者一个可变引用，但不能同时混用冲突的活跃借用。

```rust
fn word_count(text: &str) -> usize {
    text.split_whitespace().count()
}

fn append_world(text: &mut String) {
    text.push_str(", world");
}

fn main() {
    let mut message = String::from("hello");
    append_world(&mut message);
    println!("{} words", word_count(&message));
}
```

引用必须始终指向有效数据。编译器会根据引用的使用位置推断其有效范围，并拒绝引用比被引用值存活更久的代码。

借用检查可用三个判断帮助理解：任一时刻可以有多个只读引用，或者只有一个可变引用；引用必须在被引用值有效期间使用。可变引用独占访问可以避免数据竞争，也让编译器安全地推断修改顺序。把借用缩小到最后一次使用之后，往往能解决不必要的冲突。

## 切片

切片是对连续数据范围的借用，不拥有数据。字符串切片 `&str` 按 UTF-8 字节范围表示，边界必须落在有效字符边界上。

```rust
fn first_word(text: &str) -> &str {
    text.split_whitespace().next().unwrap_or("")
}

fn main() {
    let sentence = String::from("Rust 管理内存");
    println!("{}", first_word(&sentence));
}
```

处理 Unicode 文本时不要假设字符等于一个字节。可以使用 `chars()` 按 Unicode 标量值遍历。

对数组或向量也可以借用切片，例如 `&items[1..3]`。字符串切片的边界是字节偏移，若切在多字节 UTF-8 字符中间会 panic；需要按词处理时优先使用 `split_whitespace` 等 API。切片让函数既能接收 `String` 的借用，也能接收字符串字面量。

## 小结与练习

- 移动转移所有权，`clone` 显式复制，引用允许借用数据。
- 可变借用必须独占；切片是对连续数据的借用视图。
- 练习：写一个借用 `&str` 并返回最长单词切片的函数，思考返回值为何仍然有效。

再练习：实现 `calculate_length(&String) -> usize`，验证调用后原字符串仍可使用；再把参数改为 `&str`，分别用 `String` 和字面量调用。尝试写出会产生悬垂引用的函数，观察编译器如何定位问题。

下一章：[使用结构体组织相关数据](chapter-05-structs.md)。

官方对应章节：[Understanding Ownership](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html)。
