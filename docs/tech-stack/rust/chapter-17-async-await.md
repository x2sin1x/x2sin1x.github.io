---
title: 异步编程基础
weight: 170
---
# 第 17 章：异步编程基础

> 本章目标：理解 `async`、`await`、Future、任务与流的关系，并区分并发等待和并行计算。

## Future 与 `async` / `await`

Future 表示未来可能完成的计算。调用 `async fn` 会构造 Future；Future 本身不会立刻运行，必须由执行器轮询。`.await` 在当前异步计算中等待 Future 完成，并允许执行器运行其他任务。

Rust 标准库定义 Future trait，但不提供通用异步 I/O 运行时。官方 Book 使用教学支持库 `trpl` 展示异步概念。新建项目并添加依赖：

```shell
cargo new hello-async
cd hello-async
cargo add trpl
```

Book 例子会用 `trpl::block_on` 执行异步块：

```rust
use std::time::Duration;

fn main() {
    trpl::block_on(async {
        let task = async {
            trpl::sleep(Duration::from_millis(100)).await;
            "任务完成"
        };
        println!("{}", task.await);
    });
}
```

`trpl` 用于跟随 Book 学习，不是生产应用的通用运行时。实际项目应根据生态选择 Tokio、async-std 等运行时，并使用其 I/O 类型和执行器。

`async { ... }` 会生成一个匿名 Future；`async fn` 是返回 Future 的函数。`.await` 只能出现在异步上下文中，并会暂停当前 Future，直到被等待的值准备好。它不会阻塞整个线程；执行器可在等待期间推进其他任务。Future 是惰性的，必须交给 `block_on`、任务调度器等执行机制运行。

Book 的异步示例通过 `trpl::get` 发送 HTTP 请求，再从响应提取网页标题。网络 I/O 会等待数据返回，因此适合用异步表达。真实网络请求会受连接、站点响应和网络状态影响，不应把示例输出写成固定值。

## 并发等待与组合 Future

顺序 `await` 会先等待一个 Future 再等待另一个。需要同时推进多个异步工作时，可用组合器将 Future 放在一起等待。并发适合程序大部分时间等待 I/O 的场景；它不会自动让 CPU 密集计算并行。

异步函数在每个 `.await` 处暂停并保存后续执行需要的状态。跨 `.await` 持有锁或资源时，应留意任务暂停期间资源是否仍被占用。

Book 用 `trpl::spawn_task` 和 `trpl::sleep` 展示任务交替推进。任务句柄本身可等待；如果不等待句柄，外层 future 可能先结束，任务也不会按预想完成。两个 Future 可以用 `trpl::join` 一起等待：

```rust
use std::time::Duration;

fn main() {
    trpl::block_on(async {
        let first = async {
            trpl::sleep(Duration::from_millis(100)).await;
            "第一项完成"
        };
        let second = async {
            trpl::sleep(Duration::from_millis(50)).await;
            "第二项完成"
        };
        let (a, b) = trpl::join(first, second).await;
        println!("{a}；{b}");
    });
}
```

两个异步块都开始被轮询，等待时间重叠；总耗时接近较慢任务的时长。若改为先 `first.await` 再 `second.await`，就是顺序等待。异步并发与线程并行是不同概念：异步可以在单线程上交替推进任务，运行时也可能把任务调度到多个线程。

异步 channel 与线程 channel 的形状相似，但接收端等待时不会阻塞线程。`recv().await` 会暂停接收 Future，直到有消息或发送端关闭；发送端移入 `async move` 块后，块结束时会释放发送端并让接收循环终止。一个 async 块中的语句仍按顺序执行，只有把工作拆成多个 Future 并交给 `join` 等组合器，才会并发推进。

## Streams

Stream 是异步产生一系列值的抽象，可视作异步版本的迭代器。消费者等待下一个元素时，执行器可安排其他任务。Stream 的组合和轮询规则通常由运行时或生态库提供。

Rust 标准库目前没有稳定的 Stream trait。Book 的 `trpl` 提供 `stream_from_iter` 和 `StreamExt` 作为教学接口；`next().await` 逐项等待值：

```rust
use trpl::StreamExt;

trpl::block_on(async {
    let values = [1, 2, 3, 4];
    let iter = values.iter().map(|value| value * 2);
    let mut stream = trpl::stream_from_iter(iter);

    while let Some(value) = stream.next().await {
        println!("{value}");
    }
});
```

流适合连续到达的数据，例如网络事件、消息或分批读取结果。组合 Stream 的方法与普通迭代器相似，但每一步都可能异步等待。低层 `poll_next` 同时表达“还没准备好”和“这一串已经结束”：返回 `Poll::Pending` 表示之后还可能有项目，`Poll::Ready(Some(item))` 给出一项，`Poll::Ready(None)` 表示结束。`StreamExt` 为 Stream 提供 `next` 等较方便的组合方法；它不是标准库 Trait，具体 API 以运行时或生态 crate 为准。

## 等待多个 Future

固定数量的 Future 可用 `trpl::join!` 同时等待，即使它们的输出类型不同；集合中的 Future 则需要统一类型，才能存入同一个 `Vec`。`trpl::join_all` 接受同类型 Future 的集合，并等待所有项完成后按集合顺序返回结果。当只关心最先完成者时，可用 `trpl::select` 竞争两个 Future；它返回 `Either::Left` 或 `Either::Right`，分别标记先完成的一侧。

每个 `async` 块都有独一无二的匿名类型，所以即使两个 async 块都返回 `()`，也不能直接放进同一个 `Vec`。可以调用同一个 `async fn` 生成相同 Future 类型；若任务来自不同 async 块，则可用 `Pin<Box<dyn Future<Output = T>>>` 擦除具体类型并存入集合。`Pin` 使可能自引用的 Future 在被轮询期间保持地址稳定；`Box` 提供动态大小 Trait 对象的存储空间。

自定义 `timeout` 可把目标 Future 与计时器 Future 交给 `select`：目标 Future 先完成就返回其输出，计时器先完成就返回超时。这个模式说明高层异步功能可以由较小 Future 组合构造；超时是否会取消底层工作取决于 Future 和运行时的取消语义，不能假设所有外部操作都自动撤销。

在动态数量任务的场景中，需要同时考虑如何收集结果、如何处理某个任务提前失败，以及是否要等待所有任务结束。等待第一个 Future 完成与等待所有 Future 完成是不同策略；被 `select` 选中的结果以外的 Future 是否继续执行，取决于组合器返回了什么以及调用方如何保留它。选择组合器时应明确取消和剩余任务的生命周期。

异步执行只会在 `.await` 等让出点把控制权交还执行器。若在两个 `.await` 之间执行长时间同步计算，单线程执行器上的其他 Future 无法推进，这称为任务饥饿。可用 `trpl::yield_now().await` 合作式让出执行权，但它不把阻塞计算变成并行工作；CPU 密集或长时间阻塞任务应交给专门的阻塞线程池处理。`std::thread::sleep` 会阻塞当前线程，不应误用来模拟异步等待。

## 深入异步 Trait 与 Future

Future trait 的 `poll` 方法由执行器调用；返回 `Pending` 时，Future 需确保在能继续时唤醒任务，返回 `Ready` 时提供最终输出。多数应用开发者使用 async 语法和运行时，不直接手工实现轮询协议。

异步状态机可能包含自引用数据，因此 Pin 和 Unpin 关系会影响 Future 在内存中的移动。通常只在实现底层异步抽象或遇到相关 API 时深入学习。

`Future::Output` 是完成时产生的结果。执行器传入 `Context`，Future 在未就绪时通过 waker 请求后续再次轮询；实现者不应忙循环等待。`Pin<P>` 保证被指向的值不会被移动（除非其类型允许移动），这使包含自引用状态的 Future 可以安全地跨 `.await` 保存。大多数 async/await 用户不需要手写 `Pin`，但阅读底层接口时会遇到它。

`poll` 的核心形态是 `fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>`：`Ready(value)` 表示完成，`Pending` 表示尚未完成。执行器提供 `Context` 中的 waker，Future 在外部事件可继续时唤醒执行器，而不是自己不断轮询。通常不应在 `poll` 已返回 `Ready` 后再次轮询同一个 Future，除非该 Future 文档明确允许。

`Unpin` 表示类型不需要保持固定地址；大多数普通类型自动实现它，可能含自引用状态的 Future 则可能是 `!Unpin`，需要通过 `Pin` 安全地轮询。`Pin` 固定的是指针指向的数据地址，不是让指针本身不能移动。`Stream` 的底层接口类似地使用 `poll_next`，其返回类型是 `Poll<Option<Item>>`：外层 `Poll` 表示是否就绪，内层 `Option` 表示是否还有下一项。

## Future、任务与线程

线程由操作系统调度，适合并行执行计算任务；任务由异步运行时调度，适合大量 I/O 等待任务。Future 是更小的异步计算单元，任务负责推进一组 Future。两种模型可以组合，例如在线程中做 CPU 密集处理，再通过异步 channel 通知网络服务。

线程有独立的栈和操作系统调度成本；异步任务通常由运行时复用较少的线程来推进，适合大量等待网络、磁盘或计时器的工作。异步并不让阻塞调用自动变成非阻塞，也不保证 CPU 密集任务更快。选择线程、异步任务或二者组合时，应根据工作负载和运行时的阻塞 API 来决定。

## 小结与练习

- `async` 构造 Future，`.await` 等待结果，执行器负责推进 Future。
- Future 和 Stream 是异步程序的核心抽象；运行时负责调度与 I/O 支持。
- 练习：使用 Book 的 `trpl` 示例同时等待两个计时任务，比较顺序等待和并发等待的总时长。

再练习：用 `trpl::select` 对两个网页标题请求做竞速；将多个同类型 Future 放入 `Vec` 并用 `join_all` 等待；把一个迭代器转换为 Stream 并逐项 await；编写一个计时器与 Future 组合的超时函数。

下一章：[面向对象编程特性](chapter-18-oop.md)。

官方对应章节：[Fundamentals of Asynchronous Programming](https://doc.rust-lang.org/book/ch17-00-async-await.html)。
