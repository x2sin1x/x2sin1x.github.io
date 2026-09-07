---
inHomePost: false
title: "分类数据"
---

# 分类数据

> 本节目标：为有限取值的列使用 category dtype，并控制类别顺序和缺失行为。

分类数据由“实际值”和“类别集合”组成。例如订单状态只能是 paid、pending、refunded。用 category 表示后，pandas 可以复用类别编码，节省内存并保留顺序信息。

## 创建和转换

```python
import pandas as pd

status = pd.Series(
    ["pending", "paid", "paid", "refunded"],
    dtype="category",
)
status = status.cat.set_categories(["pending", "paid", "refunded"])
print(status.cat.categories.tolist())
```

从字符串转换：

```python
df = pd.DataFrame({"priority": ["high", "low", "medium", "low"]})
order = ["low", "medium", "high"]
df["priority"] = df["priority"].astype(
    pd.CategoricalDtype(categories=order, ordered=True)
)
```

## 类别操作

```python
df["priority"] = df["priority"].cat.rename_categories(
    {"high": "高", "medium": "中", "low": "低"}
)
df["priority"] = df["priority"].cat.reorder_categories(
    ["低", "中", "高"], ordered=True
)
df["priority"].cat.remove_unused_categories()
```

添加新类别前必须注册：

```python
df["priority"] = df["priority"].cat.add_categories(["未知"])
df["priority"] = df["priority"].fillna("未知")
```

## 排序和分组

ordered=True 后，sort_values 会按类别定义排序，而不是按字符串字典序：

```python
df.sort_values("priority")
df.groupby("priority", observed=True).size()
```

groupby 的 observed 参数控制是否包含未观测类别；报表通常使用 observed=True，避免产生空类别行。

## 何时使用

适合取值有限、重复很多的状态、地区、等级和标签列。高基数列或几乎每行不同的文本列转换为 category 通常收益有限。

## 常见错误

- **直接填充未注册的类别**：先 add_categories，或改回字符串 dtype。
- **类别顺序不符合业务**：创建时传 ordered=True 和明确 categories。
- **分组出现空类别**：检查 observed 参数和是否需要 remove_unused_categories。

## 小结

- category 同时保存类别集合和编码，适合低基数字段。
- .cat 访问器用于增删类别、改名和排序。
- 分组时明确 observed，排序时明确 ordered。

## 练习

1. 创建有序的优先级列 low、medium、high，并验证排序结果。
2. 统计包含未观测类别和仅观测类别时的 groupby 行数差异。

下一节：[窗口计算](/tech-stack/pandas/window)，在类别或分组内计算滚动统计。
