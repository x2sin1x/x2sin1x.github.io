---
title: 元编程
weight: 130
---

# 元编程

> 本节目标：理解用于观察和拦截对象操作的反射机制，并知道 Proxy 的不变量限制。

## 属性描述符

属性描述符可查询或设置属性的可写、可枚举、可配置状态；访问器属性用 getter 和 setter 代替直接值。`Object.defineProperty()` 提供底层控制，普通业务对象优先使用直接属性。

## Proxy

Proxy 为目标对象创建代理，可拦截读取、赋值、枚举等操作：

```js
const target = { count: 1 };
const proxy = new Proxy(target, {
  get(object, key, receiver) {
    console.log(`读取 ${String(key)}`);
    return Reflect.get(object, key, receiver);
  },
});

console.log(proxy.count);
```

拦截器称为 trap。Proxy 必须遵守目标对象属性的不可配置等不变量，否则运行时会抛错。代理不会自动深层代理内部对象。

## Reflect

Reflect 提供与对象内部操作对应的方法，如 `Reflect.get()`、`Reflect.set()` 和 `Reflect.ownKeys()`。在 Proxy trap 中使用 Reflect 可委托默认行为，避免手写不完整逻辑。

## 使用边界

Proxy 适合验证、响应式系统和 API 适配等基础设施场景。它会改变对象行为，可能影响调试、性能和第三方库兼容性。普通数据转换通常用显式函数更直观。

## 小结与练习

- 描述符控制对象属性的特性；Reflect 提供对应的反射操作。
- Proxy 可拦截操作，但需要遵循语言规定的不变量。
- 元编程适合构建基础工具，不宜无必要地隐藏普通对象行为。

练习：用 Proxy 拒绝把负数写入 `count` 属性，并让其他属性赋值正常委托给 Reflect。
