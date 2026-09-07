---
inHomePost: false
title: "数据对齐"
---

# 数据对齐

> 本节目标：理解 pandas 如何按标签匹配数据，并在需要时明确指定填充值和对齐方式。

pandas 的核心区别之一是“标签优先”。Series 或 DataFrame 运算会先对齐索引和列名，再执行逐元素计算。这样可以避免位置错位，但也会在标签不匹配时产生缺失值。

## Series 按索引对齐

```python
import pandas as pd

sales = pd.Series({"Mon": 10, "Tue": 20})
cost = pd.Series({"Tue": 5, "Wed": 7})

print(sales - cost)
```

```text
Mon     NaN
Tue    15.0
Wed     NaN
dtype: float64
```

结果索引是两个索引的并集。只有共同标签 Tue 能直接计算。

## 使用 fill_value

如果缺少的数值在业务上应视为 0，可使用二元方法：

```python
sales.sub(cost, fill_value=0)
```

这会得到 Mon=10、Tue=15、Wed=-7。fill_value 只填补一侧缺失；两侧都缺失的位置仍然是缺失。

## DataFrame 对齐

```python
left = pd.DataFrame({"a": [1, 2], "b": [3, 4]}, index=["x", "y"])
right = pd.DataFrame({"b": [10, 20], "c": [30, 40]}, index=["y", "z"])

result = left + right
print(result)
```

```text
     a     b   c
x  NaN   NaN NaN
y  NaN  14.0 NaN
z  NaN   NaN NaN
```

行索引和列名都会取并集。b/y 是唯一同时存在的单元格。

## 显式对齐

需要同时拿到两个对象的相同轴时，使用 align：

```python
left_aligned, right_aligned = left.align(right, join="outer", fill_value=0)
left_inner, right_inner = left.align(right, join="inner")
```

常见 join：

| 值 | 含义 |
| --- | --- |
| outer | 并集，默认，保留所有标签 |
| inner | 交集，只保留共同标签 |
| left | 保留左对象的轴 |
| right | 保留右对象的轴 |

align 返回两个新对象，不会修改原表。

## reindex 和广播

用 reindex 按指定顺序重排或补出标签：

```python
target = sales.reindex(["Wed", "Tue", "Thu"], fill_value=0)
```

把 Series 加到 DataFrame 时，默认按列名匹配。按行索引广播时指定 axis="index"：

```python
adjustment = pd.Series({"x": 100, "y": 200})
left.add(adjustment, axis="index")
```

## 常见错误

- **以为按位置运算**：先检查 index 和 columns；需要位置运算时使用 to_numpy()，并确认形状一致。
- **无意中制造 NaN**：连接或重命名后重新检查 isna().sum()，不要立即用 fillna(0) 掩盖问题。
- **广播方向错误**：DataFrame.add(series) 默认匹配列；按行计算要明确传 axis="index"。

## 小结

- pandas 运算先按标签对齐，再计算。
- 对齐产生的缺失值可以用 fill_value、reindex 或显式 fillna 处理。
- align(join=...) 用于控制两个对象共同的轴。

## 练习

1. 构造两个索引不同的库存 Series，分别用直接相加和 add(fill_value=0)，解释结果。
2. 对两个行列标签不同的 DataFrame 使用 align(join="inner")，确认只剩共同轴。

下一节：[缺失数据](/tech-stack/pandas/missing-data)，系统处理对齐和读取产生的缺失值。
