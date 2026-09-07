---
inHomePost: false
title: "Series 对象"
---

# Series 对象

> 本节目标：创建带标签的一维数据，并理解索引、类型和向量化运算。

`Series` 可以看作“带索引的列”。它包含一组值、一个索引和一个 dtype（数据类型）。索引不必是连续整数，也不要求唯一，但清晰的唯一索引更适合日常分析。

## 创建 Series

```python
import pandas as pd
import numpy as np

scores = pd.Series([88, 92, 76], index=["Alice", "Bob", "Cindy"], name="score")
print(scores)
```

```text
Alice    88
Bob      92
Cindy    76
Name: score, dtype: int64
```

常见输入方式：

```python
pd.Series({"Alice": 88, "Bob": 92})  # dict 的键成为索引
pd.Series(0, index=["a", "b", "c"])  # 标量会广播到每个索引
pd.Series(np.array([1.5, 2.5]))       # NumPy 数组
```

使用字典时，键的顺序会保留；使用标量时必须提供 `index`，否则无法确定长度。

## 访问值和索引

```python
scores.loc["Bob"]       # 按标签：92
scores.iloc[1]          # 按位置：92
scores.loc[["Alice", "Cindy"]]
scores.iloc[:2]
```

不要用 `scores[0]` 表示“第一个元素”。整数键在新版本中按标签解释，位置访问请使用 `.iloc`。

查看结构：

```python
print(scores.index.tolist())  # ['Alice', 'Bob', 'Cindy']
print(scores.to_numpy())      # [88 92 76]
print(scores.dtype)           # int64
print(scores.shape)           # (3,)
```

## 向量化运算和对齐

运算直接作用于整列，不需要手写 `for` 循环：

```python
passed = scores >= 80
bonus = scores + 5
print(passed.tolist())
print(bonus.tolist())
```

```text
[True, True, False]
[93, 97, 81]
```

两个 `Series` 会按索引标签对齐，而不是按数组位置相加：

```python
left = pd.Series({"a": 10, "b": 20})
right = pd.Series({"b": 1, "c": 2})
print(left + right)
```

```text
a     NaN
b    21.0
c     NaN
dtype: float64
```

如果业务规则是“缺少值按 0 计算”，显式使用 `fill_value`：

```python
print(left.add(right, fill_value=0))
```

## 类型与缺失值

需要可空整数或字符串时，使用 pandas 扩展 dtype：

```python
ids = pd.Series([1, None, 3], dtype="Int64")
names = pd.Series(["A", None, "C"], dtype="string")
print(ids.isna().tolist())          # [False, True, False]
print(names.str.lower().tolist())    # ['a', <NA>, 'c']
```

`pd.NA` 的布尔值是不确定的，不能直接写 `if value:`。筛选时使用 `.isna()`、`.notna()` 或先填充缺失值。

## 常见方法

```python
scores.min()
scores.max()
scores.mean()
scores.value_counts()
scores.sort_values(ascending=False)
scores.rename("points")
```

这些方法返回新对象或标量。除非明确传入 `inplace=True`（不建议依赖），原 `Series` 不会被改变。

## 常见错误

- **把位置当标签**：`s[0]` 可能访问标签 `0`，用 `s.iloc[0]` 表示第一个元素。
- **忽略索引对齐**：两个列相加出现 `NaN` 时，先检查 `left.index` 和 `right.index` 是否一致。
- **混用 `object` 和数值**：读取数据后用 `pd.to_numeric(..., errors="coerce")` 显式转换，并检查结果中的缺失值。

## 小结

- `Series` = 值 + 索引 + dtype。
- `.loc` 按标签，`.iloc` 按位置；向量化运算会按标签对齐。
- 用扩展 dtype 表示可空整数和字符串，缺失值判断使用专用方法。

## 练习

1. 创建一个以月份为索引的销售额 `Series`，找出销售额最高的月份。
2. 创建两个索引顺序不同的 `Series`，分别比较直接相加和 `.add(fill_value=0)` 的结果。

下一节：[DataFrame 对象](/tech-stack/pandas/dataframe)，把多列 `Series` 组合成二维表格。
