---
title: "输入输出"
weight: 70
---

# 输入输出

> 本节目标：读写常见文件格式，并在导入时控制类型、日期和缺失值。

pandas 的读取函数通常返回 DataFrame，写出函数通常通过 to_* 方法完成。读写前先确认路径、编码和可选引擎；本节示例都使用项目相对路径。

示例命令默认在 `docs/tech-stack/pandas` 目录执行；请按实际项目调整路径。

## CSV 和文本

读取 CSV：

```python
from io import StringIO
import pandas as pd

raw = "date,region,amount\n2026-01-01,华东,120\n2026-01-02,华南,80"
orders = pd.read_csv(
    StringIO(raw),
    parse_dates=["date"],
    dtype={"region": "string", "amount": "Float64"},
)
print(orders.dtypes)
```

常用参数：

- sep：分隔符，TSV 可写 sep="\t"。
- encoding：文件编码，中文文件常见 utf-8 或 gb18030。
- usecols：只读取需要的列，减少内存。
- na_values：指定额外的缺失标记。
- parse_dates：读取时解析日期列。

写出 CSV：

```python
orders.to_csv("dist/orders.csv", index=False, encoding="utf-8-sig")
```

index=False 避免把 DataFrame 行索引写成额外列。文件路径的父目录应提前创建。

## Excel

需要先安装 openpyxl：

```shell
uv pip install openpyxl
```

读写工作表。下面先生成一个最小输入文件，真实项目中可替换为已有路径：

```python
excel_source = pd.DataFrame({
    "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
    "region": ["华东", "华南"],
    "amount": [120, 80],
})
excel_source.to_excel("dist/source.xlsx", sheet_name="Orders", index=False)
orders = pd.read_excel("dist/source.xlsx", sheet_name="Orders")
orders.to_excel("dist/orders.xlsx", sheet_name="Orders", index=False)
```

多张表可使用 ExcelWriter：

```python
with pd.ExcelWriter("dist/report.xlsx", engine="openpyxl") as writer:
    orders.to_excel(writer, sheet_name="orders", index=False)
    orders.groupby("region", as_index=False)["amount"].sum().to_excel(
        writer, sheet_name="summary", index=False
    )
```

不要在循环中反复打开同一个 ExcelWriter；使用 with 统一写入并确保文件正确关闭。

## JSON

记录列表适合 orient="records"：

```python
payload = orders.to_json(orient="records", date_format="iso", force_ascii=False)
restored = pd.read_json(StringIO(payload), orient="records")
```

面对 API 返回的嵌套 JSON，先用 json.loads 检查结构，再按需要使用 json_normalize 展平；不要假设任意 JSON 都能直接变成规整表格。

## Parquet

Parquet 是列式格式，适合分析型数据。需要安装 pyarrow：

```shell
uv pip install pyarrow
```

```python
orders.to_parquet("dist/orders.parquet", index=False, engine="pyarrow")
loaded = pd.read_parquet("dist/orders.parquet", columns=["date", "amount"])
```

通过 columns 只读取所需列。Parquet 会保留比 CSV 更丰富的 dtype，跨语言交换时仍需确认 schema。

## SQL 和其他格式

从数据库读取时使用 read_sql_query 或 read_sql_table，并通过参数化查询传入用户输入；不要拼接未经处理的 SQL 字符串。HTML、XML、HDF5、Feather、STATA 等格式都有对应 read_* / to_* 函数，具体引擎和限制请查阅官方 IO 工具文档。

## 可靠读写

```python
from pathlib import Path

output = Path("dist/orders.csv")
output.parent.mkdir(parents=True, exist_ok=True)
orders.to_csv(output, index=False)

check = pd.read_csv(output)
assert len(check) == len(orders)
```

读回后检查行数、关键列、dtype 和缺失值。覆盖已有文件前确认目标路径，生产流程可先写临时文件再原子替换。

## 常见错误

- **找不到文件**：打印 Path.resolve()，确认运行目录和大小写。
- **中文乱码**：读取时指定 encoding；写给 Excel 用户可用 utf-8-sig。
- **日期变成字符串**：使用 parse_dates 或显式 pd.to_datetime，并处理无法解析的值。
- **Excel/Parquet 引擎缺失**：安装对应可选依赖，错误信息通常会指出包名。

## 小结

- CSV 适合通用交换，Excel 适合人工报表，Parquet 适合分析型存储。
- 导入时尽早指定列、类型、日期和缺失标记。
- 写出后读回做最小校验，避免静默损坏。

## 练习

1. 将 orders 写为 UTF-8 CSV，再读回并比较列名和行数。
2. 使用 ExcelWriter 生成明细和地区汇总两张工作表。

下一节：[缺失数据](/tech-stack/pandas/missing-data)，处理导入和连接过程中出现的空值。
