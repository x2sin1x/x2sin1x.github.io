---
title: "Matplotlib 概述"
---

# Matplotlib 概述

![](overview/anatomy.png)


```python
%matplotlib inline
import matplotlib.pyplot as plt
```

## Matplotlib 绘图对象

### Figure 对象

即绘图面板，`matplotlib` 中的所有图像都是位于 `Figure` 对象中，一个图像只能有一个 `Figure` 对象。


```python
fig = plt.figure()
```

可以指定 `Figure` 的宽和高，单位为英寸：


```python
fig = plt.figure(figsize=(640, 480))
```

可以用 `dpi` 参数指定绘图对象的分辨率，即每英寸有多少像素。


```python
fig = plt.figure(dpi=300)
```

可以指定背景颜色 `facecolor` 和边框颜色 `edgecolor`:


```python
fig = plt.figure(facecolor='y', edgecolor='g')
```

也可以不显示边框：


```python
fig = plt.figure(frameon=False)
```

### Axes 对象

一个 `Figure` 对象可以有多个 `Axes` 对象，而一个 `Axes` 对象就代表一个独立的绘图区域，拥有一套独立的坐标系统。

我们可以向 `Figure` 对象中添加 `Axes` 对象：


```python
fig.add_axes([0.1, 0.1, 0.8, 0.8])
```

`list` 中的 4 个参数分别为横纵坐标、宽和高，范围是 $[0, 1]$。

### Axis 对象

一个 `Axes` 对象可以有多个 `Axis` 对象，而一个 `Axis` 对象就是一个坐标轴。对于 2D 图像，`Axis` 对象就是 x 轴和 y 轴；对于 3D 图像，`Axis` 对象就是 x 轴、y 轴和 z 轴。

不过，有时候许多数据会共用同一个坐标轴（一般是横轴），这个时候 `Axis` 对象上也存在 `Axes` 对象。

## Matplotlib 绘图元素

- title: 图像标题，`Figure` 对象和 `Axes` 对象都可以设置。
- data: 绘图数据，隶属于 `Axes` 对象。
- label: 坐标轴标题，隶属于 `Axis` 对象。
- tick: 刻度，隶属于 `Axis` 对象。
- ticklabel: 刻度说明，隶属于 `Axis` 对象。
- legend: 图例，`Figure` 对象和 `Axes` 对象都可以设置。
- lim: 取值范围，隶属于 `Axis` 对象。
