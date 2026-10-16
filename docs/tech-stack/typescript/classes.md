---
title: 类
weight: 70
---

# 类

> 本节目标：声明具有字段和方法的类，并理解 TypeScript 的访问控制与 JavaScript 运行时行为。

## 字段、构造器和方法

TypeScript 类基于 JavaScript 类语法。字段类型声明仅在编译期检查，构造器负责建立运行时对象状态：

```ts
class Counter {
  private value: number;

  constructor(initial = 0) {
    this.value = initial;
  }

  increment(): number {
    this.value += 1;
    return this.value;
  }
}

console.log(new Counter(2).increment()); // 3
```

`strictPropertyInitialization` 会要求字段在构造时初始化，或明确说明初始化时机。参数属性可在构造参数前写 `public`、`private`、`protected` 或 `readonly`，同时声明字段并赋值；可读性更重要时可分开写。

## 继承与 `override`

`extends` 继承基类行为，子类构造器需要先调用 `super()`：

```ts
class Animal {
  constructor(public name: string) {}
  move(distance: number): string { return `${this.name} 前进 ${distance} 米`; }
}

class Bird extends Animal {
  override move(distance: number): string {
    return `${this.name} 飞行 ${distance} 米`;
  }
}
```

启用 `noImplicitOverride` 可要求覆盖成员明确写 `override`，避免基类重命名后子类方法意外变成新成员。

## `public`、`private`、`protected` 和 `readonly`

TypeScript 的 `public`、`private`、`protected` 是静态访问限制。`private` 关键字保护编译器层面的访问；ECMAScript 的 `#field` 才是 JavaScript 运行时私有字段。`protected` 允许子类访问；`readonly` 限制初始化后的重新赋值。

```ts
class Account {
  #balance = 0;
  deposit(amount: number): void {
    if (amount <= 0) throw new Error("金额必须大于零");
    this.#balance += amount;
  }
}
```

静态成员属于类本身而不是实例。静态块可在类定义时执行初始化逻辑。抽象类可以包含实现和抽象成员，不能直接实例化；它适合需要共享状态或实现的层次。

## 类类型与 `implements`

类的实例类型由实例成员组成；静态成员与构造器不属于实例接口。`implements` 检查类实例是否满足某个结构契约，但不会改变类自身推断的类型，也不会自动把接口成员复制进类。

```ts
interface Printable { print(): string }

class Report implements Printable {
  print(): string { return "本周报告"; }
}
```

JavaScript 的很多对象协作可以直接用接口和函数完成。不要为了熟悉 Java 或 C# 的写法，把每个数据对象都强行包装为类。

## 小结与练习

- 类在运行时存在；接口与类型别名只参与静态检查。
- 静态访问修饰符与 ECMAScript `#private` 的运行时行为不同。
- `implements` 检查契约，不会令类自动继承接口实现。

练习：实现 `Shape` 抽象类和 `Rectangle` 子类，提供面积方法并用 `override` 覆盖。下一节：[模块](modules.md)，学习把类、类型和函数拆分到不同文件。
