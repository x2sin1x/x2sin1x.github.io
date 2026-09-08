---
title: "索引和选择"
weight: 30
---

# 索引和选择

> 本节目标：准确表达“选哪些行、哪些列”，并安全地修改筛选结果。

准备一张小表：

```python
import pandas as pd

df = pd.DataFrame(
    {
        "name": ["A", "B", "C", "D"],
        "score": [88, 72, 95, 64],
        "team": ["red", "blue", "red", "blue"],
    },
    index=["r1", "r2", "r3", "r4"],
)
```

## 选择列

```python
df["score"]                    # 一个 Series
df[["name", "score"]]          # 一个 DataFrame
df.loc[:, "score"]             # 等价的标签写法
df.filter(regex="^s")          # 按列名模式选择
```

属性访问 `df.score` 只适合简单、合法且不冲突的列名；需要动态列名或修改列时始终使用方括号。

## 按标签选择：loc

`.loc[行标签, 列标签]` 的切片端点都包含：

```python
df.loc["r1", "score"]
df.loc[["r1", "r3"], ["name", "score"]]
df.loc["r1":"r3", "name"]
```

缺少的标签通常会抛出 `KeyError`。不确定标签是否存在时，可先用 `df.index.intersection(labels)` 求交集。

## 按位置选择：iloc

`.iloc` 使用从 0 开始的位置，切片右端不包含：

```python
df.iloc[0, 1]
df.iloc[:2, :2]
df.iloc[[0, 2], [1, 2]]
```

`.loc` 和 `.iloc` 不要混用：前者表达业务标签，后者表达物理位置。

## 条件筛选

比较表达式会生成布尔 `Series`：

```python
high = df.loc[df["score"] >= 80]
red_high = df.loc[(df["team"] == "red") & (df["score"] >= 80)]
```

组合条件必须使用 `&`、`|`、`~`，并给每个条件加括号：

```python
df.loc[df["team"].isin(["red", "green"])]
df.loc[df["name"].str.startswith("A", na=False)]
df.loc[df["score"].between(70, 90, inclusive="both")]
```

不要写 `and`/`or`，它们只适用于单个布尔值。

## query

列名简单、条件较长时，`query` 可提高可读性：

```python
df.query("score >= 80 and team == 'red'")
threshold = 80
df.query("score >= @threshold")
```

外部 Python 变量要加 `@`。列名包含空格或关键字时使用反引号，例如 ``df.query('\`order amount\` > 100')``。

## 安全赋值

用 `.loc` 一次完成条件和目标列：

```python
df.loc[df["score"] < 70, "remark"] = "needs_review"
df.loc[df["score"] >= 70, "remark"] = "ok"
```

需要先复制筛选结果再独立修改时，显式调用 `.copy()`：

```python
subset = df.loc[df["team"] == "red"].copy()
subset["score"] = subset["score"] + 1
```

pandas 3.0 默认启用 Copy-on-Write；不要依赖切片对象回写原表的旧行为。

## 缺失标签和重复标签

```python
df.reindex(["r3", "r9"])            # r9 的整行是缺失值
df.index.is_unique                  # 检查索引是否唯一
df.loc[:, ~df.columns.duplicated()] # 去掉重复列名（确认业务允许后使用）
```

如果需要“按索引查找并保留缺失项”，优先使用 `reindex`，而不是循环调用 `loc`。

## 常见错误

- **条件优先级错误**：`df["score"] > 80 & df["team"] == "red"` 会产生解析错误，改成 `(df["score"] > 80) & (df["team"] == "red")`。
- **SettingWithCopy 警告**：使用 `.loc[...] = ...` 或先 `.copy()`。
- **整数索引误解**：`df.iloc[0]` 是第一行，`df.loc[0]` 是标签为 `0` 的行，两者不是一回事。

## 小结

- `[]` 适合简单选列，`.loc` 按标签，`.iloc` 按位置。
- 布尔条件用 `&`/`|`/`~` 并加括号；赋值优先使用 `.loc`。
- `reindex` 用于按目标标签重排并补出缺失标签。

## 练习

1. 选择 `score` 在 70 到 90 之间且属于 `blue` 队的行。
2. 给所有 `score >= 90` 的行增加 `grade = "A"`，确认原表被明确修改。

下一节：[基本运算](/tech-stack/pandas/arithmetic)，对选出的列进行向量化计算。
