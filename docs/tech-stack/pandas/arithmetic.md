---
title: "基本运算"
---

# 基本运算

> 本节目标：使用向量化表达式完成数值、比较和布尔运算。

```python
import pandas as pd

df = pd.DataFrame(
    {"price": [10.0, 20.0, 15.0], "quantity": [2, 1, 4]},
    index=["a", "b", "c"],
)
```

## 算术运算

列与标量运算会逐元素执行：

```python
df["total"] = df["price"] * df["quantity"]
df["discounted"] = df["total"].mul(0.9).round(2)
print(df)
```

```text
   price  quantity  total  discounted
a   10.0         2   20.0        18.0
b   20.0         1   20.0        18.0
c   15.0         4   60.0        54.0
```

`+`、`-`、`*`、`/`、`//`、`%` 和 `**` 都支持向量化；`add`、`sub`、`mul`、`div` 等方法提供 `fill_value` 和轴控制。

```python
df["net"] = df["total"].sub(5)
df["unit_price"] = df["total"].div(df["quantity"])
```

## 缺失值和安全比较

算术遇到缺失值通常返回缺失值。先明确业务规则，再选择填充或跳过：

```python
prices = pd.Series([10.0, None, 30.0])
prices.fillna(0).sum()       # 缺失按 0：40.0
prices.sum()                 # 默认跳过缺失：40.0
prices.mean()                # 默认跳过缺失：20.0
```

比较结果是布尔序列，可直接用于 `.loc`：

```python
df.loc[df["total"].ge(30), ["price", "total"]]
df["quantity"].eq(1)
```

对于浮点数，不要用 `==` 判断计算结果是否完全相等；使用 `np.isclose` 或设定容差。

## 描述统计

```python
df[["price", "quantity", "total"]].describe()
df["total"].sum()
df["total"].mean()
df["total"].quantile(0.5)
```

`sum`、`mean` 等默认忽略缺失值。若要在缺失时得到缺失结果，查看对应方法的 `skipna` 参数。

## 布尔运算

```python
is_large = (df["total"] >= 30) & (df["quantity"] >= 2)
is_small = df["total"] < 25
df.loc[is_large | is_small]
```

`&` 表示逐元素“且”，`|` 表示逐元素“或”，`~` 表示逐元素取反；每个比较表达式都应加括号。

## 函数应用

优先使用现成的向量化方法：

```python
df["rounded"] = df["unit_price"].round(1)
df["label"] = df["total"].map(lambda value: "high" if value >= 30 else "low")
```

`map` 适合一列值到一个值的映射；跨列逻辑用向量化表达式或 `DataFrame.assign`。`apply(axis=1)` 灵活但通常更慢，不应作为第一选择。

## 常见错误

- **用 Python 的 `and`/`or` 组合列条件**：改用 `&`/`|` 并加括号。
- **整数除法得到浮点数**：`/` 始终是真除法；需要整除时使用 `//`，并确认负数规则符合业务。
- **误把缺失当 0**：只有在业务定义明确时才 `fillna(0)`，否则会改变统计含义。

## 小结

- 标量和列运算是向量化的，优先使用列表达式。
- 缺失值传播和 `skipna` 会影响统计结果，要显式确认。
- 布尔筛选使用 `&`、`|`、`~`；复杂逐行函数最后才考虑 `apply`。

## 练习

1. 为 `df` 增加含税金额列（税率 6%），并筛选含税金额至少为 30 的订单。
2. 构造含缺失值的销量列，比较 `sum()`、`sum(skipna=False)` 和 `fillna(0).sum()` 的结果。

下一节：[数据对齐](/tech-stack/pandas/data-alignment)，理解不同索引之间为何会产生缺失值。
