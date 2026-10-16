---
title: 异步 JavaScript 与 Promise
weight: 70
---

# 异步 JavaScript 与 Promise

> 本节目标：理解等待操作的异步结果，使用 Promise 与 `async` / `await` 组织代码，并处理失败情况。

## 为什么需要异步

网络请求、定时器和文件 I/O 可能需要等待。异步 API 让程序在等待结果时继续处理其他任务。异步不等于自动并行；JavaScript 回调仍由运行时安排执行。

## Promise

Promise 表示未来可能成功或失败的结果。它只能从 pending 转为 fulfilled 或 rejected：

```js
const result = new Promise((resolve) => {
  setTimeout(() => resolve("完成"), 10);
});

result.then((value) => console.log(value));
```

`then()` 返回新的 Promise，链式返回值会传给下一个处理器；抛出的错误会进入后续拒绝处理。`Promise.all()` 等全部成功，`Promise.allSettled()` 收集全部结果，`Promise.race()` 取第一个敲定结果，`Promise.any()` 取首个成功结果。

## `async` 与 `await`

`async` 函数总是返回 Promise。`await` 取得兑现值；若 Promise 拒绝，则在该位置抛出异常，可用 `try...catch` 处理：

```js
async function loadUser(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("读取用户失败：", error);
    throw error;
  }
}
```

`fetch()` 遇到 HTTP 404 等响应时通常仍会兑现 Promise，因此需检查 `response.ok`。相互独立的请求可用 `Promise.all()` 并发等待；有依赖的步骤才逐个 `await`。

## 回调、Worker 与取消

事件监听器和定时器使用回调表达稍后执行的逻辑。避免多层嵌套回调，可把流程拆成函数或 Promise。Web Worker 能在独立线程运行计算任务，通过消息传递通信；它不能直接操作页面 DOM。可取消的网络任务可配合 `AbortController`。

## 小结与练习

- Promise 表示将来完成的操作；`async` / `await` 是组织 Promise 的语法。
- `fetch` 的 HTTP 错误要检查响应状态，拒绝要明确处理。
- 并发调用可用 Promise 组合方法，长计算可考虑 Worker。

练习：使用 `Promise.all()` 并发加载两个 JSON 资源；如果任一响应非成功状态，抛出可读错误。
