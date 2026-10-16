---
title: JavaScript 类型化数组
weight: 75
---

# JavaScript 类型化数组

> 本节目标：理解二进制缓冲区与数据视图，使用 TypedArray 处理固定格式的数值数据。

## ArrayBuffer 与视图

`ArrayBuffer` 表示一段固定长度的原始二进制内存，本身不负责解释每个字节的含义。TypedArray 或 `DataView` 在缓冲区上建立视图。

```js
const buffer = new ArrayBuffer(4);
const bytes = new Uint8Array(buffer);
bytes[0] = 255;
console.log(bytes[0], bytes.length); // 255 4
```

TypedArray 类型包括有符号和无符号整数、浮点数等。写入超出类型范围的值会按该类型规则处理，而不是像普通数组那样保存任意 JavaScript 值。

## TypedArray 与 DataView

TypedArray 适合连续、同类型元素，例如图像像素和音频样本。`DataView` 可在一个缓冲区中按字节偏移读取不同类型，并显式指定字节序，适合二进制协议：

```js
const buffer = new ArrayBuffer(4);
const view = new DataView(buffer);
view.setUint16(0, 0x1234, false); // big-endian
console.log(view.getUint16(0, false).toString(16)); // "1234"
```

## 共享内存

`SharedArrayBuffer` 与 `Atomics` 可用于多个 Worker 间共享数据并协调访问。它们涉及竞态和同步问题，部署还受浏览器安全隔离策略约束。只有在明确需要并理解并发语义时才使用。

## 小结与练习

- ArrayBuffer 存储原始字节，TypedArray 和 DataView 解释这些字节。
- TypedArray 适合固定类型数值数据，DataView 适合混合字段的二进制格式。
- SharedArrayBuffer 需要显式同步，并受安全策略影响。

练习：用 DataView 写入并读取一个 16 位无符号整数，分别按大端和小端解释，比较结果。
