---
title: 显式资源管理
weight: 85
---

# 显式资源管理

> 本节目标：理解需要显式释放的资源，并识别 `using` / `await using` 语法的运行时支持边界。

## 为什么需要资源管理

文件句柄、锁或临时资源在使用后需要释放。传统写法在 `finally` 中清理：

```js
let resource;
try {
  resource = acquireResource();
  useResource(resource);
} finally {
  resource?.close();
}
```

清理代码需要覆盖成功、异常和提前返回等路径。显式资源管理规范提供 `Symbol.dispose`、`Symbol.asyncDispose` 及 `using`、`await using`，让资源在词法作用域退出时自动释放。

## 支持与使用条件

```js
// 仅在运行时支持显式资源管理语法及所需对象时使用
{
  using resource = createDisposableResource();
  resource.run();
}
```

`using` 绑定只在当前作用域有效，离开作用域时调用资源的同步释放方法；`await using` 等待异步释放。MDN 当前将 `using` 标记为尚未获得主流浏览器普遍支持的特性。语法和内置对象支持因引擎版本而异，使用前检查 [MDN 兼容性表](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Statements/using)。不能假定所有浏览器或 Node.js 版本均可运行。

## 小结与练习

- 资源应在所有执行路径中释放。
- 新语法可减少清理样板，但必须确认运行时支持。
- 对兼容环境，`try...finally` 仍是通用模式。

练习：为一个拥有 `close()` 方法的资源编写安全的 `try...finally` 使用模板，并考虑获取资源本身失败的情况。
