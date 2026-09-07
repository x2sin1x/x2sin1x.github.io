---
inHomePost: false
title: "文本数据"
---

# 文本数据

> 本节目标：使用 str 访问器批量清洗、提取和拆分字符串列。

字符串操作应尽量向量化。先把列转换为 string dtype，再通过 .str 调用方法；缺失值会保留为 `<NA>`。

## 基本清洗

```python
import pandas as pd

names = pd.Series([" Alice ", "BOB", None], dtype="string")
clean = names.str.strip().str.lower()
print(clean.tolist())
```

```text
['alice', 'bob', <NA>]
```

常用方法包括 strip、lower、upper、replace、len、startswith 和 contains。

## 筛选和替换

```python
mask = names.str.contains("a", case=False, na=False)
names.loc[mask]
names.str.replace(r"[^A-Za-z]", "", regex=True)
```

contains 的 na 参数决定缺失值如何进入布尔筛选，通常在筛选时设为 False。

## 分割和提取

```python
emails = pd.Series(["a@example.com", "b@example.org"], dtype="string")
parts = emails.str.split("@", expand=True)
parts.columns = ["user", "domain"]
domains = emails.str.extract(r"@(?P<domain>[^@]+)$")
```

expand=True 把分割结果展开为多列；extract 使用正则捕获组并返回 DataFrame 或 Series。

## 连接字符串

```python
first = pd.Series(["A", "B"], dtype="string")
last = pd.Series(["One", "Two"], dtype="string")
full = first.str.cat(last, sep=" ")
```

使用 na_rep 时可为缺失值指定输出文本，但不要把展示文本写回原始列。

## 分类和性能

重复且取值有限的字符串列可转换为 category，见[分类数据](/tech-stack/pandas/categorical)。大规模文本处理时优先使用矢量化 str 方法，避免逐行 Python 循环。

## 常见错误

- **object 列上直接调用字符串方法**：先 astype("string")。
- **contains 结果含缺失**：传 na=False，或先 fillna。
- **正则转义错误**：使用原始字符串 r"..."，并为捕获组编写小测试。

## 小结

- .str 方法按列处理字符串，能保留索引和缺失值。
- 清洗、筛选、分割和提取都可以组合成链式表达式。
- 先确认 dtype，再决定是否使用 category。

## 练习

1. 清洗一列带空格和大小写混杂的邮箱地址，并提取域名。
2. 用 contains 筛选包含关键词的文本，比较 na=True 和 na=False 的结果。

下一节：[分类数据](/tech-stack/pandas/categorical)，为有限取值的文本列选择更合适的类型。
