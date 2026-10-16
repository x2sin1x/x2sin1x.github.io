---
title: 无畏并发
weight: 160
---
# 第 16 章：无畏并发

> 本章目标：使用线程、消息传递和共享状态组织并发，并理解 `Send` 与 `Sync` 如何参与安全检查。

## 使用线程

`std::thread::spawn` 创建新线程，返回的 `JoinHandle` 可用于等待线程结束：

```rust
use std::thread;

let handle = thread::spawn(|| {
    for i in 1..5 {
        println!("工作线程：{i}");
    }
});
handle.join().expect("线程 panic");
```

若不调用 `join`，主线程可能先结束。`move` 闭包可把捕获值的所有权移入线程，避免线程访问已失效的借用。

```rust
use std::thread;

let values = vec![1, 2, 3];
let handle = thread::spawn(move || {
    println!("线程取得 values 的所有权：{values:?}");
});
handle.join().expect("线程 panic");
```

线程调度由操作系统决定，多个线程的打印顺序不应假设固定。`JoinHandle::join` 会阻塞当前线程直到目标线程结束，并返回线程是否 panic 的结果。创建大量线程会消耗系统资源，因此高并发应用通常使用有界线程池。

## 消息传递

channel 让线程通过发送消息共享信息，而不直接共享可变状态。标准库的多生产者单消费者 channel 使用发送端 `Sender` 和接收端 `Receiver`：

```rust
use std::{sync::mpsc, thread};

let (tx, rx) = mpsc::channel();
thread::spawn(move || {
    tx.send(String::from("来自工作线程")).expect("接收端已关闭");
});
let message = rx.recv().expect("发送端已关闭");
println!("{message}");
```

发送消息会转移其所有权。可克隆发送端创建多个生产者；接收端可用 `recv` 阻塞等待，或遍历接收消息。

```rust
let (tx, rx) = mpsc::channel();
let tx2 = tx.clone();
thread::spawn(move || tx.send(String::from("第一条")).unwrap());
thread::spawn(move || tx2.send(String::from("第二条")).unwrap());
for message in rx {
    println!("收到：{message}");
}
```

当所有发送端都被丢弃后，接收迭代器结束。channel 可排队多个值；通过值传递消息能让所有权转移关系更清楚。

## 共享状态

共享状态适合需要多线程访问同一数据的场景。`Mutex<T>` 一次只允许一个线程持有锁；`Arc<T>` 提供线程安全的引用计数所有权。

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let counter = Arc::new(Mutex::new(0));
let mut handles = Vec::new();
for _ in 0..10 {
    let counter = Arc::clone(&counter);
    handles.push(thread::spawn(move || {
        *counter.lock().expect("mutex poisoned") += 1;
    }));
}
for handle in handles { handle.join().expect("线程 panic"); }
assert_eq!(*counter.lock().expect("mutex poisoned"), 10);
```

缩短锁的持有时间，避免不同线程以不同顺序获取多把锁。消息传递和共享状态都是工具，按数据流和同步需求选择。

`Mutex::lock` 返回守卫；离开守卫作用域时锁自动释放。若线程在持锁期间 panic，锁会被标记为 poisoned，后续加锁返回错误。死锁通常来自多个线程以相反顺序等待锁，或在持锁期间执行可能阻塞的操作。`Arc<Mutex<T>>` 的两层类型各司其职：Arc 管共享所有权，Mutex 管互斥访问。

## `Send` 与 `Sync`

`Send` 表示类型的所有权可安全地在线程间转移；`Sync` 表示对类型的共享引用可安全地在线程间共享。编译器会为满足条件的类型自动实现这些标记 Trait。`Rc<T>` 不是 `Send`，而 `Arc<T>` 可在内部类型满足约束时跨线程共享。

标准库的线程、channel 和同步类型会通过 Trait bound 限制可传递的数据。若编译器拒绝把某类型送入线程，通常说明它内部包含非线程安全数据；不要轻率地手写 `unsafe impl Send` 或 `Sync`，因为这会把线程安全责任交给实现者。

## 小结与练习

- `join` 等待线程，channel 传递消息，`Mutex` 与 `Arc` 组合共享状态。
- `Send` 和 `Sync` 将线程安全属性纳入类型检查。
- 练习：让多个线程分别发送计算结果到主线程，并在主线程汇总。

再练习：启动多个线程计算不同区间的总和，并用 channel 汇总；再用 `Arc<Mutex<_>>` 实现共享计数器；观察线程数增加后任务时间和资源使用如何变化。

下一章：[异步编程基础](chapter-17-async-await.md)。

官方对应章节：[Fearless Concurrency](https://doc.rust-lang.org/book/ch16-00-concurrency.html)。
