---
title: 国际化
weight: 88
---

# 国际化

> 本节目标：用 Intl 按用户语言和地区格式化日期、数字，并执行本地化排序。

## Intl API

国际化 API（ECMA-402）提供地区敏感的格式化和比较。避免自行拼接货币符号、日期顺序或千位分隔符：

```js
const price = new Intl.NumberFormat("zh-CN", {
  style: "currency",
  currency: "CNY",
}).format(1234.5);

console.log(price);
```

格式结果依赖运行环境所带的国际化数据，因此不同环境的空格或标点细节可能不同。

## 日期和数字

`Intl.DateTimeFormat` 按地区格式化日期；指定 `timeZone` 可避免受设备默认时区影响。`Intl.NumberFormat` 支持货币、百分比和有效位数等格式选项。

```js
const formatter = new Intl.DateTimeFormat("zh-CN", {
  dateStyle: "medium",
  timeZone: "Asia/Shanghai",
});
console.log(formatter.format(new Date("2026-10-16T00:00:00Z")));
```

## 排序与复数

```js
const names = ["张三", "阿明", "小林"];
names.sort(new Intl.Collator("zh-CN").compare);
console.log(names);
```

`Intl.Collator` 可按地区规则比较字符串。`Intl.PluralRules` 可判断特定地区对数量使用的复数类别。界面文案较多时，需使用完整的本地化消息资源，而不只是替换日期数字格式。

## 小结与练习

- Intl API 根据语言标签和选项格式化，而不是硬编码展示规则。
- 对日期明确时区；对字符串排序使用 Collator。
- 格式输出受平台国际化数据影响，不宜进行字节级固定断言。

练习：把一个价格分别显示为人民币和美元，并将一组日期格式化为指定时区。
