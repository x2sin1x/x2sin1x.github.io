---
title: 智能指针
weight: 150
---
# 第 15 章：智能指针

> 本章目标：理解智能指针如何拥有堆数据、提供引用式访问、共享所有权，以及为何内部可变性和引用计数需要谨慎使用。

## `Box<T>`：在堆上存储数据

`Box<T>` 在堆上分配值，并在离开作用域时释放。它适合大型值、需要固定大小表示的递归类型，或需要把值放在堆上的场景。

```rust
enum List {
    Cons(i32, Box<List>),
    Nil,
}

use List::{Cons, Nil};
let list = Cons(1, Box::new(Cons(2, Box::new(Cons(3, Box::new(Nil))))));
```

递归枚举若直接嵌套自身会导致大小无法确定；`Box` 提供已知大小的指针间接层。普通引用只借用数据，`Box` 则拥有其指向的值。单一所有者默认优先使用普通值或 `Box`，只有确实需要共享时才引入引用计数。

## 智能指针如何像普通引用一样使用

实现 `Deref` 的类型可像引用一样解引用，Rust 也会在适用时进行解引用强制转换。`Box<T>` 因而能自然地访问内部值。不要把强制转换理解为所有权转移：它主要是引用类型之间的便利转换。

```rust
use std::ops::Deref;

struct MyBox<T>(T);

impl<T> MyBox<T> {
    fn new(value: T) -> Self { Self(value) }
}

impl<T> Deref for MyBox<T> {
    type Target = T;
    fn deref(&self) -> &Self::Target { &self.0 }
}

let value = MyBox::new(String::from("Rust"));
assert_eq!(value.len(), 4);
```

`Deref` 强制转换会在调用点自动插入所需的解引用次数，并可在某些场景把 `&String` 转为 `&str`。实现 `DerefMut` 后还可支持可变目标转换；只有语义确实像透明指针时才实现这些 Trait，否则自动强制转换会让代码行为难以追踪。

## 用 `Drop` Trait 在清理时运行代码

`Drop` Trait 允许类型在值离开作用域时执行清理逻辑。Rust 按作用域结束顺序清理局部变量，通常是后创建者先清理。`std::mem::drop(value)` 可提前结束值的生命周期；不能直接调用 `value.drop()`，因为析构由语言负责调度。

自定义 `Drop` 可用于管理值以外的资源，但文件、锁和网络连接等标准库类型通常已经实现了清理逻辑。需要自定义资源类型时，应确保析构不 panic，并避免依赖不明确的析构顺序。

## `Rc<T>`：引用计数智能指针

当多个部分需要共同拥有同一份不可变数据时，`Rc<T>` 使用引用计数管理生命周期。克隆 `Rc` 会增加计数而不是复制底层数据：

```rust
use std::rc::Rc;

let value = Rc::new(String::from("shared"));
let another = Rc::clone(&value);
assert_eq!(Rc::strong_count(&value), 2);
drop(another);
assert_eq!(Rc::strong_count(&value), 1);
```

最后一个强引用离开作用域时，数据才会被释放。`Rc` 不是线程安全的；跨线程共享应考虑 `Arc<T>`。`Rc<T>` 本身只提供共享所有权，不能直接修改内部值。链表或图等多个节点共同拥有同一节点的结构，是它比普通所有权更合适的场景。

## `RefCell<T>` 与内部可变性

`RefCell<T>` 在运行时检查借用规则，允许通过不可变外层绑定修改内部值。`borrow()` 返回 `Ref<T>`，`borrow_mut()` 返回 `RefMut<T>`；借用守卫离开作用域时，相应借用结束。若运行时违反“多个共享借用或一个可变借用”的规则，会 panic。它适合编译期无法表达、但程序逻辑能保证的单线程场景，不能替代多线程同步原语。

测试替身可以实现生产代码要求的 Trait，并把调用记录写入 `RefCell<Vec<_>>`。例如 `Messenger` Trait 的测试实现可在 `send` 时保存消息，再断言发送次数和内容；测试不必连接真实邮件或消息服务。这体现内部可变性的用途，也提醒我们冲突借用风险从编译期移到了运行时。

`Rc<RefCell<T>>` 组合共享所有权和内部可变性：多个所有者共享同一个 `RefCell`，并能在运行时修改其中的数据。这个组合灵活但更难推理，应缩小可变状态范围并避免长期保存借用守卫。

## 引用环会造成内存泄漏

若两个 `Rc` 值互相持有对方，强引用计数就永远不会归零，内存无法释放。Rust 保证内存安全，但不会自动检测或回收这种逻辑上的引用环。

`Rc::downgrade` 创建 `Weak<T>`，不增加强引用计数。使用前要调用 `upgrade`，它返回 `Option<Rc<T>>`，因为被引用值可能已经释放。树结构常让父节点通过 `Rc` 拥有子节点、子节点通过 `Weak` 指回父节点：拥有方向用强引用，观察方向用弱引用。

```rust
use std::{cell::RefCell, rc::{Rc, Weak}};

struct Node {
    parent: RefCell<Weak<Node>>,
    children: RefCell<Vec<Rc<Node>>>,
}

let leaf = Rc::new(Node {
    parent: RefCell::new(Weak::new()),
    children: RefCell::new(vec![]),
});
let branch = Rc::new(Node {
    parent: RefCell::new(Weak::new()),
    children: RefCell::new(vec![Rc::clone(&leaf)]),
});
*leaf.parent.borrow_mut() = Rc::downgrade(&branch);
assert!(leaf.parent.borrow().upgrade().is_some());
```

`Weak` 的 `upgrade` 返回 `None` 是正常状态，调用方必须处理。设计共享图结构时，先画清楚谁拥有谁，再决定强引用和弱引用方向。

## 小结与练习

- `Box<T>` 提供堆分配，`Rc<T>` 共享单线程所有权，`RefCell<T>` 将借用检查移到运行时。
- `Deref` 与 `Drop` 支持引用式访问和清理；`Weak<T>` 可打断强引用环。
- 练习：观察 `Rc` 强引用计数在克隆和离开作用域后的变化；使用父子节点实现 `Rc`/`Weak` 关系，并检查父节点释放后 `upgrade` 的结果。

再练习：实现一个带 `Drop` 输出的小类型以观察清理顺序；用 `MyBox<T>` 实现 `Deref`；实现一个使用 `RefCell` 记录 Trait 调用的测试替身。

下一章：[无畏并发](chapter-16-concurrency.md)。

官方对应章节：[Smart Pointers](https://doc.rust-lang.org/book/ch15-00-smart-pointers.html)。
