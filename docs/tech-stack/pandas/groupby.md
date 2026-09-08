---
title: "分类汇总"
weight: 60
---

# 分类汇总

> 本节目标：按一个或多个键分组，并区分聚合、转换和过滤三类操作。

GroupBy 遵循 split-apply-combine：先按键拆分数据，对每组应用计算，再把结果组合回 Series 或 DataFrame。

## 创建分组

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "region": ["华东", "华东", "华南", "华南"],
        "category": ["book", "food", "book", "food"],
        "amount": [100, 80, 120, 50],
        "status": ["paid", "paid", "refunded", "paid"],
    }
)

by_region = orders.groupby("region")
```

GroupBy 对象是延迟计算的描述，不会立即生成结果。选择列后再聚合：

```python
orders.groupby("region")["amount"].sum()
orders.groupby(["region", "category"], as_index=False)["amount"].mean()
```

## 聚合 aggregate

聚合把每组压缩为一行：

```python
summary = orders.groupby("region", as_index=False).agg(
    total_amount=("amount", "sum"),
    average_amount=("amount", "mean"),
    order_count=("amount", "size"),
)
print(summary)
```

```text
  region  total_amount  average_amount  order_count
0     华东           180            90.0            2
1     华南           170            85.0            2
```

多个统计量可以传列表：

```python
orders.groupby("region")["amount"].agg(["sum", "mean", "max"])
```

使用命名聚合可直接得到稳定列名，适合导出报表。

## 转换 transform

转换保留原行数，把每组结果广播回成员：

```python
orders["region_total"] = orders.groupby("region")["amount"].transform("sum")
orders["share"] = orders["amount"] / orders["region_total"]
```

典型用途是组内标准化、组均值填充和计算占比。若函数返回的形状与输入不同，优先检查是否应该使用聚合或 apply。

## 过滤 filter

过滤保留满足条件的整组：

```python
large_regions = orders.groupby("region").filter(
    lambda group: group["amount"].sum() >= 180
)
```

这会保留总额至少为 180 的地区及其所有原始行。

## apply 和排序

apply 适合每组需要自定义、且无法用现成聚合表达的逻辑：

```python
top_order = orders.groupby("region", group_keys=False).apply(
    lambda group: group.nlargest(1, "amount"),
    include_groups=False,
)
```

能用 agg、transform 或 filter 时优先使用它们，通常更快且返回结构更明确。

分组结果排序：

```python
summary.sort_values("total_amount", ascending=False)
orders.groupby("region", sort=False)["amount"].sum()
```

sort=False 保留首次出现的分组顺序；需要稳定报表时应显式排序。

## 缺失分组键

默认情况下，分组键为缺失值的行不会形成一个组。需要把缺失也作为一组时：

```python
orders.groupby("region", dropna=False)["amount"].sum()
```

分类 dtype 还会受到 observed 参数影响，见[分类数据](/tech-stack/pandas/categorical)。

## 常见错误

- **把聚合和转换混用**：需要每行结果时用 transform，不要把 agg 结果直接赋回原表。
- **重复键导致行数膨胀**：这是连接操作的问题，连接前后都检查 shape 和键的唯一性。
- **忽略缺失分组键**：先决定缺失值是丢弃、填充，还是通过 dropna=False 单独统计。

## 小结

- agg 压缩每组，transform 保持行数，filter 删除整组。
- 命名聚合能生成清晰列名；优先使用内置向量化函数。
- 用 dropna、observed 和 sort 明确分组边界和顺序。

## 练习

1. 按 region 和 status 统计订单数与金额总和。
2. 为每一行添加其地区内金额占比，并验证每个地区的占比和为 1。

下一节：[合并与连接](/tech-stack/pandas/concat)，把分组结果与其他表组合起来。
