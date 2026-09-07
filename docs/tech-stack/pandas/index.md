---
inHomePost: false
title: Pandas
---

# Pandas

![](pandas_white.svg)

Pandas 是 Python 中用于表格数据处理和分析的库。它提供带标签的一维 `Series`、二维 `DataFrame`，以及筛选、清洗、连接、聚合、时间序列和文件读写等工具。

本教程面向已经了解 Python 基础语法和 NumPy 数组的读者。内容以 pandas **3.0.5** 的官方用户指南为基线，最后核对日期为 **2026-09-03**。示例使用小型内存数据集，便于复制到脚本或 Jupyter Notebook 中运行。

## 环境准备

建议在项目目录创建虚拟环境：

```shell
uv venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
uv pip install "pandas==3.0.5" openpyxl pyarrow matplotlib
```

验证安装：

```shell
python -c "import pandas as pd; print(pd.__version__)"
```

如果只处理 CSV，可以暂时不安装 `openpyxl`、`pyarrow` 和 `matplotlib`。读取不同格式时，pandas 会调用相应的可选引擎。

## 推荐顺序

1. [Series 对象](/tech-stack/pandas/series)：理解带索引的一维数据。
2. [DataFrame 对象](/tech-stack/pandas/dataframe)：创建和检查二维表格。
3. [索引和选择](/tech-stack/pandas/indexing-selection)：用标签、位置和条件取数及赋值。
4. [基本运算](/tech-stack/pandas/arithmetic) 与 [数据对齐](/tech-stack/pandas/data-alignment)：掌握向量化计算和标签对齐。
5. [缺失数据](/tech-stack/pandas/missing-data) 与 [文本数据](/tech-stack/pandas/text)：清洗真实数据中的空值和字符串。
6. [合并与连接](/tech-stack/pandas/concat)、[分类汇总](/tech-stack/pandas/groupby) 与 [重塑和透视](/tech-stack/pandas/reshape)：组合多张表并生成报表。
7. [输入输出](/tech-stack/pandas/io)：在 CSV、Excel、JSON 和 Parquet 之间保存数据。
8. [时间序列](/tech-stack/pandas/timeseries)、[分类数据](/tech-stack/pandas/categorical) 与 [窗口计算](/tech-stack/pandas/window)：处理常见业务数据。
9. [快速可视化](/tech-stack/pandas/visualization) 和 [实践建议](/tech-stack/pandas/best-practices)：完成探索分析并减少隐蔽错误。

前四章是必学基础；只做简单表格清洗时，可以先跳过时间序列和窗口计算。

## 第一个示例

下面的程序读取内存中的销售记录，筛选有效订单并按地区汇总：

```python
from io import StringIO
import pandas as pd

csv = """date,region,amount,status
2026-01-01,华东,120,paid
2026-01-02,华南,80,refunded
2026-01-03,华东,150,paid
"""

orders = pd.read_csv(StringIO(csv), parse_dates=["date"])
paid = orders.loc[orders["status"].eq("paid")]
summary = paid.groupby("region", as_index=False)["amount"].sum()
print(summary)
```

预期结果：

```text
  region  amount
0     华东     270
```

这个流程贯穿后续章节：读取数据、检查类型、用 `.loc` 筛选、用 `groupby` 聚合，最后再写回文件或绘图。

## pandas 3.0 要点

- Copy-on-Write（写时复制）默认开启。通过切片得到的对象不会悄悄修改原表；赋值时使用明确的 `.loc` 或 `.iloc`。
- 字符串列逐步使用专用的 `str` dtype。需要稳定类型时可显式写 `dtype="string"`，不要依赖 `object`。
- 缺失值可能以 `NaN`、`NaT` 或 `pd.NA` 表示。比较、布尔运算和类型转换时要使用本教程介绍的方法。

## 参考资料

- [pandas 用户指南](https://pandas.pydata.org/docs/user_guide/index.html)：按主题查阅完整行为和参数。
- [pandas 安装说明](https://pandas.pydata.org/docs/getting_started/install.html)：查看 Python 支持范围和可选依赖。
- [pandas 3.0.5 发布文档](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)：了解 Copy-on-Write、字符串 dtype 等迁移信息。
