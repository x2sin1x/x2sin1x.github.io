---
title: "窗口计算"
---

# 窗口计算

> 本节目标：计算滚动、扩展和指数加权统计，观察趋势而不破坏原始数据。

窗口对象描述“当前行附近的一段观测”。rolling 使用固定窗口，expanding 从第一行逐步扩大，ewm 对近期数据赋予更高权重。

## rolling

```python
import pandas as pd

sales = pd.Series([10, 12, 9, 15], index=pd.date_range("2026-01-01", periods=4))
rolling = sales.rolling(window=2, min_periods=1)
result = pd.DataFrame(
    {"sales": sales, "mean_2": rolling.mean(), "sum_2": rolling.sum()}
)
print(result)
```

```text
            sales  mean_2  sum_2
2026-01-01     10    10.0   10.0
2026-01-02     12    11.0   22.0
2026-01-03      9    10.5   21.0
2026-01-04     15    12.0   24.0
```

window=2 表示两条观测；min_periods=1 让开头窗口也能产生结果。默认 min_periods 等于窗口大小时，前一行会是缺失。

## 时间窗口

DatetimeIndex 可使用时间跨度：

```python
sales.rolling("2D", min_periods=1).mean()
```

时间窗口按日期范围而非行数计算，数据不等频时尤其重要。

## expanding 和 ewm

```python
sales.expanding(min_periods=1).mean()
sales.ewm(span=3, adjust=False).mean()
```

扩展平均表示截至当前的累计统计；指数加权平均更强调近期值。span、halflife 和 alpha 选择一种参数表达即可。

## 按组窗口

```python
df = pd.DataFrame(
    {
        "region": ["east", "east", "west", "west"],
        "date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-01", "2026-01-02"]),
        "amount": [10, 12, 8, 11],
    }
).sort_values(["region", "date"])

df["mean_2"] = df.groupby("region")["amount"].transform(
    lambda values: values.rolling(2, min_periods=1).mean()
)
```

先按分组键和时间排序；transform 确保结果能按原索引对齐。

## 常见错误

- **窗口未排序**：时间窗口前必须按日期排序。
- **开头出现 NaN**：检查 min_periods 是否应设置为更小值。
- **把 ewm 当普通平均**：它会给近期值更高权重，参数应在业务上有解释。

## 小结

- rolling 看局部趋势，expanding 看累计趋势，ewm 强调近期观测。
- window 可以是行数或时间跨度；min_periods 控制最小样本数。
- 分组窗口先排序，再用 transform 对齐结果。

## 练习

1. 计算销售额的 3 条观测滚动最大值。
2. 对每个 region 计算 2 天滚动和，并检查结果是否按原行对齐。

下一节：[快速可视化](/tech-stack/pandas/visualization)，把窗口结果画出来。
