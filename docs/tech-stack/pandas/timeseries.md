---
inHomePost: false
title: "时间序列"
---

# 时间序列

> 本节目标：解析日期、创建 DatetimeIndex，并按时间重采样和滚动计算。

## 解析日期

```python
import pandas as pd

df = pd.DataFrame(
    {
        "date": ["2026-01-01", "2026-01-02", "2026-01-04"],
        "amount": [10, 12, 9],
    }
)
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.set_index("date").sort_index()
```

errors="coerce" 会把无法解析的值变为 NaT；转换后检查 isna()，不要静默丢弃坏日期。

## 日期组件和偏移

```python
df.index.year
df.index.month
df.index.day_name()
df["amount"].resample("D").sum()
```

DatetimeIndex 的属性可提取日期组件。resample 需要 DatetimeIndex、TimedeltaIndex 或 PeriodIndex；D 表示日频率，MS 表示月初频率。

## 重采样

```python
daily = df["amount"].resample("D").asfreq()
weekly = df["amount"].resample("W").sum(min_count=1)
```

asfreq 保留频率并产生缺失日期，sum 等聚合会按窗口汇总。选择频率别名时查阅官方 offset alias 文档，避免使用已弃用拼写。

## 滚动和时间窗口

```python
df["rolling_2"] = df["amount"].rolling(2, min_periods=1).mean()
df["rolling_2d"] = df["amount"].rolling("2D", min_periods=1).mean()
```

整数窗口按观测数计算，时间窗口按时间跨度计算。min_periods 控制窗口内最少有效观测数。

## 时区

```python
utc = pd.to_datetime(["2026-01-01 08:00"], utc=True)
local = utc.tz_convert("Asia/Shanghai")
naive = local.tz_localize(None)
```

tz_localize 为无时区时间添加时区；tz_convert 在已有时区之间转换。跨地区系统优先存 UTC，展示时再转换。

## 常见错误

- **日期仍是字符串**：确认 dtype 为 datetime64；不要对字符串做日期比较。
- **重采样结果为空**：检查索引是否排序、是否真的为 DatetimeIndex。
- **混淆 localize 和 convert**：前者赋予时区，后者转换瞬时时刻。

## 小结

- 用 to_datetime 解析，DatetimeIndex 支持组件提取和重采样。
- 整数窗口按行数，时间窗口按时间跨度。
- 存储时统一时区，展示时再转换。

## 练习

1. 为缺失日期补出每日索引，并比较 asfreq 和 resample("D").sum()。
2. 计算 3 天滚动平均，并说明窗口起始几行为什么可能是缺失。

下一节：[窗口计算](/tech-stack/pandas/window)，深入滚动、扩展和指数加权统计。
