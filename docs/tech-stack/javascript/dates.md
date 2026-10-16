---
title: 表达日期与时间
weight: 60
---

# 表达日期与时间

> 本节目标：创建日期、理解时间戳和时区，并避免不稳定的日期解析。

## Date 表示什么

`Date` 表示一个时间点，内部以自 1970-01-01T00:00:00Z 起的毫秒数表示。它不保存原始时区；本地时间方法会按当前环境时区解释和展示。

```js
const now = new Date();
const epoch = new Date(0);
console.log(epoch.toISOString()); // 1970-01-01T00:00:00.000Z
```

## 创建与解析

优先使用 ISO 8601 格式，避免依赖各浏览器可能不同的非标准日期字符串解析：

```js
const appointment = new Date("2026-10-16T09:30:00+08:00");
console.log(appointment.toISOString());
```

日期对象提供 `getTime()`、`toISOString()`、`getUTCFullYear()` 等方法。日期运算前先明确是在计算“经过的毫秒数”还是“日历上的天数”；夏令时会让相邻本地日期不一定相差固定的 24 小时。

## 格式化

面向用户的日期格式应指定语言环境和时区：

```js
const date = new Date("2026-10-16T01:30:00Z");
const formatter = new Intl.DateTimeFormat("zh-CN", {
  dateStyle: "long",
  timeStyle: "short",
  timeZone: "Asia/Shanghai",
});
console.log(formatter.format(date));
```

展示不应手动拼接固定格式，也不应假定用户设备采用某一时区。新规范中的 `Temporal` 正在逐步进入运行环境，使用前检查兼容性；传统跨环境代码仍常用 `Date`。

## 小结与练习

- `Date` 存时间点，时区影响格式化和日历字段的解释。
- 用 ISO 字符串解析；跨地区显示时显式指定 `Intl.DateTimeFormat` 的时区。
- 日历运算不总等于固定毫秒数运算。

练习：把同一个 UTC 时间分别格式化为上海和纽约时间，并记录两者的日期差异。
