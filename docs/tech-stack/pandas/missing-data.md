---
title: "缺失数据"
---

# 缺失数据

> 本节目标：识别缺失值，选择删除、填充或插值策略，并避免把未知数据误当成 0。

缺失值可能表示“没有记录”“不适用”或“尚未采集”，三者含义不同。pandas 常见标记包括 NaN、NaT 和 pd.NA；统一使用 isna、notna、fillna 等方法处理。

## 识别缺失值

```python
import pandas as pd

df = pd.DataFrame(
    {
        "name": ["A", "B", "C"],
        "score": [90, None, 75],
        "joined": pd.to_datetime(["2026-01-01", None, "2026-01-03"]),
    }
)

df.isna()
df.isna().sum()
df.notna().all(axis=1)
```

isna().sum() 能快速得到每列缺失数量；先统计再决定处理方式。

## 删除缺失值

```python
df.dropna(subset=["score"])       # 只删除 score 缺失的行
df.dropna(axis="columns", how="all")
df.dropna(thresh=2)               # 至少保留两个非缺失值
```

dropna 默认返回新对象。删除前确认缺失行是否确实无业务价值。

## 填充缺失值

```python
df["score"] = df["score"].fillna(df["score"].median())
df["name"] = df["name"].fillna("unknown")
```

按组填充：

```python
df["score"] = df.groupby("name")["score"].transform(
    lambda values: values.fillna(values.median())
)
```

使用前先确认每组都有可用统计量，否则中位数本身也可能是缺失。

## 前向、后向填充和插值

时间序列或有序观测常用：

```python
series = pd.Series([1.0, None, None, 4.0])
series.ffill(limit=1)   # 最多向前填一个
series.bfill()
series.interpolate()
```

填充方向必须符合数据生成过程；不能用未来值填补实时预测中的历史缺失。

## 可空 dtype 和判断

```python
ids = pd.Series([1, pd.NA, 3], dtype="Int64")
flags = pd.Series([True, pd.NA, False], dtype="boolean")
ids.isna()
flags.fillna(False)
```

pd.NA 不适合直接参与 if 判断；先用 isna 或 fillna 转成确定的布尔值。

## 常见错误

- **把所有缺失填成 0**：会改变平均值、比例和业务含义。
- **先填充再统计却忘记记录规则**：在代码中保留填充原因和来源。
- **字符串 "NA" 没被识别**：读取文件时通过 na_values 指定额外标记。

## 小结

- 先统计缺失模式，再选择 dropna、fillna 或插值。
- 填充值要符合列和业务语义，分组填充要检查空组。
- 使用 pandas 的可空 dtype 和专用缺失判断。

## 练习

1. 删除 score 缺失的记录，并比较删除前后的行数。
2. 对一列时间序列分别使用 ffill 和 interpolate，解释两者差异。

下一节：[文本数据](/tech-stack/pandas/text)，清洗字符串列和缺失字符串。
