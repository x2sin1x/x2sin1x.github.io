---
inHomePost: false
title: "实践建议"
---

# 实践建议

> 本节目标：把 pandas 代码写得可读、可验证，并在数据量增长时保持合理性能。

## 明确数据契约

读取后立刻检查：

```python
import pandas as pd

df = pd.DataFrame({"order_id": [1], "amount": [10], "status": ["paid"]})
required = {"order_id", "amount", "status"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"missing columns: {sorted(missing)}")

df = df.astype({"status": "string"})
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
```

对关键列声明 dtype、单位、时区和允许缺失规则。让错误尽早出现，比在最后导出时才发现更容易排查。

## 选择和赋值

始终使用明确的 loc 或 iloc：

```python
valid = df.loc[df["amount"].ge(0)].copy()
valid.loc[:, "amount_with_tax"] = valid["amount"] * 1.06
```

pandas 3.0 默认启用 Copy-on-Write；不要依赖链式赋值或切片回写原表。需要独立分支时显式 copy。

## 性能基础

- 只读取需要的列，使用 usecols。
- 用向量化方法、groupby 和 merge，少写逐行 iterrows 循环。
- 低基数文本考虑 category，数值列避免不必要地转成 object。
- 大文件使用 chunksize 分块读取，再逐块聚合。
- 用 memory_usage(deep=True) 定位内存占用。

分块读取示例：

```python
totals = []
for chunk in pd.read_csv("src/large.csv", usecols=["region", "amount"], chunksize=100_000):
    totals.append(chunk.groupby("region")["amount"].sum())
total = pd.concat(totals).groupby(level=0).sum()
```

## 可测试的管道

把步骤拆成小函数，并用 pipe 或 assign 串联：

```python
def clean_orders(frame):
    return (
        frame.rename(columns=str.lower)
        .assign(amount=lambda x: pd.to_numeric(x["amount"], errors="coerce"))
        .dropna(subset=["order_id", "amount"])
    )

cleaned = clean_orders(df)
```

为行数、列名、唯一键和关键汇总写断言；固定小数据夹具可以让测试稳定。

## 版本和弃用

运行前记录 pd.__version__。升级 pandas 时阅读发布说明，特别关注 dtype、时间频率别名、Copy-on-Write 和第三方 IO 引擎变化。不要用屏蔽警告的方式“修复”行为变化。

## 常见错误

- **过早优化**：先用 profile、memory_usage 和基准测试定位瓶颈。
- **静默修改输入**：函数默认返回新对象，并在文档中说明是否原地修改。
- **连接没有验证**：merge 加 validate，聚合前后检查行数和键。

## 小结

- 先定义数据契约，再清洗、计算、连接和导出。
- 明确索引与副本，避免链式赋值；用向量化和分块处理提升性能。
- 版本升级以官方发布说明为准，并为关键不变量写测试。

## 练习

1. 为一个清洗函数添加列存在性和非负金额断言。
2. 将逐行计算改写为向量化表达式，并用简单计时比较差异。

返回 [Pandas 首页](/tech-stack/pandas/)，或继续阅读官方[用户指南](https://pandas.pydata.org/docs/user_guide/index.html)。
