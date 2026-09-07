---
inHomePost: false
title: "快速可视化"
---

# 快速可视化

> 本节目标：用 DataFrame.plot 快速检查分布和趋势，并知道何时转向 Matplotlib。

pandas 的 plot 方法是 Matplotlib 的便捷封装，适合探索性分析；正式图表应显式设置标题、坐标轴、图例和尺寸。

## 折线图和柱状图

先安装 matplotlib：

```shell
uv pip install matplotlib
```

```python
import pandas as pd
import matplotlib.pyplot as plt

monthly = pd.DataFrame(
    {"sales": [10, 12, 9], "cost": [4, 5, 6]},
    index=["Jan", "Feb", "Mar"],
)
ax = monthly.plot(kind="line", marker="o", figsize=(6, 3))
ax.set(title="Monthly amount", xlabel="Month", ylabel="Amount")
plt.tight_layout()
plt.show()
```

常用 kind 包括 line、bar、barh、area、hist、box 和 scatter。数值列会自动成为系列，索引成为横轴。

## 分组后绘图

```python
summary = pd.DataFrame(
    {"region": ["east", "west"], "amount": [270, 170]}
)
summary.plot.bar(x="region", y="amount", legend=False)
```

绘图前先完成聚合和排序；不要把数千行明细直接绘成不可读的图。

## 缺失值和保存

绘图会受缺失值影响，先确认是否需要插值或保留间断：

```python
ax = monthly.plot()
ax.figure.savefig("dist/monthly.png", dpi=150, bbox_inches="tight")
```

保存图像前确保输出目录存在。服务器或脚本环境可使用非交互后端，并关闭 figure 释放资源。

## 何时使用其他工具

需要复杂布局、统计图层、主题或交互时，使用 Matplotlib、Seaborn 或专门的可视化库。pandas plot 的目标是快速探索，不是替代完整绘图库。

## 常见错误

- **缺少 matplotlib**：安装可选依赖，或只使用表格输出。
- **中文显示方框**：配置系统中存在的中文字体，不要把字体文件提交到教程目录。
- **图例和标签重叠**：设置 figsize、tight_layout 和明确的轴标签。

## 小结

- plot 是 Matplotlib 的便捷入口，适合快速查看趋势。
- 绘图前先聚合、排序和处理缺失值。
- 复杂图表应转向 Matplotlib 或其他专用库。

## 练习

1. 将每日销售额画成折线图，并标记最高的一天。
2. 按地区汇总后画水平条形图，保存为 PNG。

下一节：[实践建议](/tech-stack/pandas/best-practices)，把清洗、计算和验证组合成可靠流程。
