---
title: "DataFrame 对象"
date: 2022-02-18T16:41:59+08:00
weight: 20
---
# DataFrame 对象

> 本节目标：创建二维表格，检查其结构，并完成列的新增、删除和类型转换。

`DataFrame` 是带行索引和列名的二维数据结构。每一列可以有不同 dtype；把它理解成“多个索引对齐的 `Series`”比把它当作无标签的二维数组更准确。

## 创建表格

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "order_id": [101, 102, 103],
        "region": ["华东", "华南", "华东"],
        "amount": [120.0, 80.0, 150.0],
    }
)
print(orders)
```

```text
   order_id region  amount
0       101     华东   120.0
1       102     华南    80.0
2       103     华东   150.0
```

也可以从记录列表、二维数组或字典中的 `Series` 创建：

```python
pd.DataFrame([{"name": "A", "score": 90}, {"name": "B", "score": 85}])
pd.DataFrame({"x": [1, 2], "y": [3, 4]}, index=["a", "b"])
```

字典中的列长度必须一致；`Series` 作为值时会按索引自动对齐，不匹配的位置填充缺失值。

## 查看结构

```python
orders.head(2)             # 前两行
orders.tail(1)             # 最后一行
orders.shape               # (3, 3)
orders.columns.tolist()    # 列名
orders.index.tolist()      # 行标签
orders.dtypes              # 每列 dtype
orders.info()              # 非空数量和内存摘要
orders.describe()          # 数值列统计
```

`head`、`tail` 和大多数转换方法返回新对象。探索数据时先用 `shape`、`dtypes` 和 `isna().sum()` 检查结构，再开始计算。

## 新增、修改和删除列

```python
orders["tax"] = orders["amount"] * 0.06
orders["amount_with_tax"] = orders["amount"] + orders["tax"]
orders = orders.drop(columns="tax")
orders = orders.rename(columns={"amount": "subtotal"})
```

按条件创建列时使用 `np.where` 或 `Series.where`：

```python
import numpy as np

orders["level"] = np.where(orders["subtotal"] >= 100, "large", "small")
```

删除行或列前确认轴：`drop(columns=...)` 删除列，`drop(index=...)` 删除行。默认返回副本，推荐重新赋值保存结果。

## 索引和排序

```python
orders = orders.set_index("order_id")
orders = orders.sort_index()
print(orders.loc[101, "region"])
orders = orders.reset_index()
```

`set_index` 适合把业务键设为行标签；如果仍需要普通列，使用 `reset_index` 恢复。

排序：

```python
orders.sort_values("subtotal", ascending=False)
orders.sort_values(["region", "subtotal"], ascending=[True, False])
```

## 类型转换

```python
orders["order_id"] = orders["order_id"].astype("int64")
orders["subtotal"] = pd.to_numeric(orders["subtotal"], errors="coerce")
orders["region"] = orders["region"].astype("string")
```

`errors="coerce"` 会把无法解析的值变为缺失值；转换后要再次检查 `isna()`，不要静默吞掉数据问题。

## 从表格选择列

```python
orders["region"]                  # Series
orders[["order_id", "subtotal"]]  # DataFrame
orders.loc[:, ["region", "subtotal"]]
```

注意第二种写法的列名列表只能有一层括号，正确代码是：

```python
orders[["order_id", "subtotal"]]
```

复杂筛选请阅读[索引和选择](/tech-stack/pandas/indexing-selection)，不要把 Python 列表索引和 pandas 标签索引混为一谈。

## 常见错误

- **列长度不一致**：创建表格时各列表长度必须相同；不同长度的数据先转成 `Series` 并明确索引。
- **链式赋值**：`orders[orders["subtotal"] > 100]["level"] = "large"` 不明确。用 `orders.loc[orders["subtotal"] > 100, "level"] = "large"`。
- **把 `info()` 当作返回值**：`info()` 主要打印摘要，通常不需要写 `print(orders.info())`。

## 小结

- `DataFrame` 同时有行索引、列名和每列 dtype。
- 先检查结构，再进行选择、转换和计算；默认把操作结果重新赋值。
- 用 `.loc` 做条件赋值，用 `set_index`/`reset_index` 管理业务键。

## 练习

1. 给 `orders` 增加 `is_large` 布尔列，并统计大订单数量。
2. 将 `region` 设为索引后按金额降序排序，再恢复默认索引。

下一节：[索引和选择](/tech-stack/pandas/indexing-selection)，系统学习标签、位置和条件筛选。
