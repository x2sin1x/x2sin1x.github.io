---
title: "合并与连接"
---

# 合并与连接

> 本节目标：选择 concat、merge 或 join，把多张表组合成可核对的结果。

准备两张表：

```python
import pandas as pd

jan = pd.DataFrame({"order_id": [1, 2], "amount": [100, 80]})
feb = pd.DataFrame({"order_id": [3, 4], "amount": [120, 60]})
customers = pd.DataFrame(
    {"order_id": [1, 2, 3], "customer": ["A", "B", "C"]},
)
```

## concat：堆叠对象

按行追加同结构表：

```python
all_orders = pd.concat([jan, feb], ignore_index=True)
```

按列并排组合：

```python
left = pd.DataFrame({"a": [1, 2]}, index=["x", "y"])
right = pd.DataFrame({"b": [3, 4]}, index=["x", "y"])
pd.concat([left, right], axis="columns")
```

默认按轴标签取并集，不存在的位置为缺失值。需要只保留共同列时使用 join="inner"。ignore_index=True 仅重建结果轴，不会修复业务键。

## merge：按键连接

把订单和客户信息按 order_id 连接：

```python
enriched = all_orders.merge(customers, on="order_id", how="left")
print(enriched)
```

```text
   order_id  amount customer
0         1     100        A
1         2      80        B
2         3     120        C
3         4      60      NaN
```

常用 how：

| how | 保留的键 |
| --- | --- |
| inner | 两边共同键 |
| left | 左表全部键 |
| right | 右表全部键 |
| outer | 两边全部键 |
| cross | 笛卡尔积，不需要连接键 |

列名不一致时用 left_on 和 right_on：

```python
keyed_orders = pd.DataFrame({"customer_id": [1, 2], "amount": [10, 20]})
profiles = pd.DataFrame({"id": [1, 2], "name": ["A", "B"]})
keyed_orders.merge(profiles, left_on="customer_id", right_on="id")
```

同名非键列会自动添加 _x、_y 后缀，可通过 suffixes=("_order", "_profile") 改名。

## 验证连接关系

连接前应明确键的基数。validate 能在重复键时尽早报错：

```python
all_orders.merge(
    customers,
    on="order_id",
    how="left",
    validate="many_to_one",
    indicator=True,
)
```

many_to_one 表示左表可以重复，右表键必须唯一；其他选项包括 one_to_one、one_to_many 和 many_to_many。indicator=True 会增加 _merge 列，帮助检查未匹配记录。

## join：按索引连接

join 适合把另一个对象按索引并入：

```python
all_orders.set_index("order_id").join(
    customers.set_index("order_id"),
    how="left",
    lsuffix="_order",
    rsuffix="_customer",
)
```

如果键在普通列中，merge 通常更直观。

## 连接后的检查

```python
before = len(all_orders)
result = all_orders.merge(customers, on="order_id", how="left")
assert len(result) == before
assert result["order_id"].notna().all()
```

行数意外增加通常表示连接键在两边都有重复值；先用 duplicated("order_id") 定位，而不是直接 drop_duplicates 掩盖关系错误。

## 常见错误

- **把 concat 当作 SQL JOIN**：concat 按轴堆叠，merge 才按键匹配。
- **连接后行数膨胀**：检查键是否唯一，并使用 validate。
- **忘记保留未匹配行**：需要以左表为准时使用 how="left"，不要默认 inner。
- **重复列名难以解释**：提前选择列或指定 suffixes。

## 小结

- 同结构表上下拼接用 concat；按键匹配用 merge；按索引并入用 join。
- how 决定保留哪些键，validate 和 indicator 用于质量检查。
- 连接前后都检查键唯一性、行数和缺失值。

## 练习

1. 将两个月的销售表用 concat 合并，并重建连续索引。
2. 为一个含重复客户键的连接添加 validate="many_to_one"，观察错误并修复右表键。

下一节：[分类汇总](/tech-stack/pandas/groupby)，对合并后的明细生成统计结果。
