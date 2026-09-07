---
inHomePost: false
title: "重塑和透视"
---

# 重塑和透视

> 本节目标：在宽表和长表之间转换，并生成交叉汇总报表。

长表每行表示一条观测，宽表把某个维度展开成多列。分析和绘图通常需要在两种形状之间切换。

## pivot：唯一键的宽化

```python
import pandas as pd

long = pd.DataFrame(
    {
        "date": ["Mon", "Mon", "Tue", "Tue"],
        "metric": ["sales", "cost", "sales", "cost"],
        "value": [10, 4, 12, 5],
    }
)
wide = long.pivot(index="date", columns="metric", values="value")
print(wide)
```

```text
metric  cost  sales
date
Mon        4     10
Tue        5     12
```

pivot 要求每个 index、columns 组合唯一；存在重复组合时会抛出错误。

## pivot_table：带聚合的宽化

有重复观测时使用 pivot_table：

```python
wide = long.pivot_table(
    index="date",
    columns="metric",
    values="value",
    aggfunc="sum",
    fill_value=0,
)
```

aggfunc 可以是 mean、sum、count 或自定义函数。fill_value 只影响结果中的缺失单元格。

## melt：宽表转长表

```python
wide = pd.DataFrame(
    {"date": ["Mon", "Tue"], "sales": [10, 12], "cost": [4, 5]}
)
long = wide.melt(
    id_vars="date",
    var_name="metric",
    value_name="value",
)
```

id_vars 是保持不变的标识列；其余列被转换为变量和值两列。

## stack 和 unstack

stack 把列标签压入行索引，unstack 把索引层展开为列：

```python
indexed = wide.set_index("date")
stacked = indexed.stack(future_stack=True)
restored = stacked.unstack()
```

多级索引时可传 level 指定层。pandas 3.0 中使用 future_stack=True 可采用新的栈实现，不能同时指定旧实现专用的 fill_value 或 dropna 参数。

## explode 和 crosstab

列表列展开为多行：

```python
tags = pd.DataFrame({"id": [1, 2], "tags": [["a", "b"], ["b"]]})
tags.explode("tags", ignore_index=True)
```

交叉频数表：

```python
pd.crosstab(long["date"], long["metric"])
```

## 常见错误

- **pivot 报重复索引**：改用 pivot_table 并明确 aggfunc。
- **多级列难以使用**：用 rename_axis、reset_index 或 columns.map 展平前先确认报表需求。
- **melt 误把标识列展开**：把业务键放进 id_vars。

## 小结

- pivot 只适用于唯一键；pivot_table 能聚合重复观测。
- melt 把宽表变成长表，stack/unstack 操作索引层。
- 重塑后检查列名、索引和数据类型，再进行连接或导出。

## 练习

1. 将包含 region、month、amount 的长表透视为地区为行、月份为列的宽表。
2. 对宽表执行 melt，再验证行数等于原行数乘以指标列数。

下一节：[输入输出](/tech-stack/pandas/io)，保存重塑后的明细和报表。
