---
title: "Matplotlib 条形图"
date: 2021-04-26T16:31:43+08:00
weight: 40
---
# Matplotlib 条形图

```python
import matplotlib.pyplot as plt
import numpy as np
```

## 入门

我们首先生成随机的数据：


```python
x = np.arange(1, 7)
y = np.abs(np.random.randn(6))
```

直接调用 `plt` 的绘图方法：


```python
plt.bar(x, y)
```


    <BarContainer object of 6 artists>


​    
![](bar/output_6_1.png)
​    


当然，一个好的习惯是使用 `Axes` 对象：


```python
fig = plt.figure()
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
ax.bar(x, y)
```


    <BarContainer object of 6 artists>


​    
![](bar/output_8_1.png)
​    

```python
ax.clear()
```

## 图像美化

### 设置颜色

我们可以使用 `color` 参数来改变条形图的颜色：


```python
ax.bar(x, y, color='g')
fig
```


​    
![](bar/output_13_0.png)
​    


```python
ax.clear()
```

甚至可以指定每个柱子都是不同颜色：


```python
ax.bar(x, y, color=['r', 'g', 'b', 'y', 'c', 'm'])
fig
```


​    
![](bar/output_16_0.png)
​    


```python
ax.clear()
```

### 设置轮廓

我们可以使用 `edgecolor` 参数来改变条形图的轮廓颜色：


```python
ax.bar(x, y, edgecolor='k')
fig
```


​    
![](bar/output_20_0.png)
​    


```python
ax.clear()
```

而 `linewidth` 参数可以调节边缘的粗细：


```python
ax.bar(x, y, edgecolor='k', linewidth=3)
fig
```


​    
![](bar/output_23_0.png)
​    


```python
ax.clear()
```

`linestyle` 参数与二维绘图 `plot` 同理，此处不再赘述。

### 设置填充

我们可以使用 `hatch` 参数来指定条形图的填充形状：


```python
ax.bar(x, y, hatch='\\', edgecolor='k', color='w')
fig
```


​    
![](bar/output_28_0.png)
​    


```python
ax.clear()
```

### 设置宽度

我们可以使用 `width` 参数来设置条形图的宽度：


```python
ax.bar(x, y, width=0.5)
fig
```


​    
![](bar/output_32_0.png)
​    

`width` 参数的取值范围一般为 $(0, 1]$ 之间的浮点数。如果 `width=1`，那么每个柱子之间就没有空隙。这个浮点数的几何意义相当于缩放比例。


```python
ax.clear()
```

## 系列条形图

现在，我们需要统计 CSGO 七张服役地图 T 和 CT 的胜率，数据如下：


```python
maps = ['Dust2', 'Inferno', 'Mirage', 'Nuke', 'Overpass', 'Train', 'Vertigo']
CT_win_rate = [53.7, 49.8, 48.1, 50.7, 57.9, 53.4, 58.6]
T_win_rate = [46.3, 50.2, 51.9, 49.3, 42.1, 46.6, 41.4]
```

我们需要设置好条形图的宽度。由于实例一共有两个系列（CT 和 T），我们可以将每个柱子的宽度设为 0.35，这样加起来一共 0.7，每一组柱子之间也有缝隙。


```python
width = 0.35
```

下面设置条形图的绘制位置，它由 `width` 和标签的索引位置 `x` 决定：


```python
x = np.arange(len(maps))
x_CT = x - width/2
x_T = x + width/2
```

绘制系列条形图：


```python
y_CT = ax.bar(x_CT, CT_win_rate, color='blue', width=width, label='CT')
y_T = ax.bar(x_T, T_win_rate, color='orange', width=width, label='T')
fig
```


​    
![](bar/output_43_0.png)
​    

添加标签、标题和图例：


```python
ax.set_xticks(x)
ax.set_ylim(40, 60)
ax.set_xticklabels(maps)
ax.set_ylabel('Win Rate (%)')
ax.legend(loc='upper right')
fig
```


​    
![](bar/output_45_0.png)
​    

为其添加水平网格线：


```python
ax.grid(linestyle='-.', axis='y')
fig
```


​    
![](bar/output_47_0.png)
​    

网格线显示在了条形图上方，使用 `zorder` 参数改变各个元素的层数。


```python
ax.clear()

y_CT = ax.bar(x_CT, CT_win_rate, color='blue', width=width, label='CT', zorder=2)
y_T = ax.bar(x_T, T_win_rate, color='orange', width=width, label='T', zorder=2)
ax.set_ylim(40, 60)
ax.set_xticks(x)
ax.set_xticklabels(maps)
ax.set_ylabel('Win Rate (%)')
ax.legend(loc='upper right')
ax.grid(linestyle='-.', axis='y', zorder=1)

fig
```


​    
![](bar/output_49_0.png)
​    


```python
ax.clear()
```

## 水平条形图


```python
x = np.arange(1, 7)
y = np.abs(np.random.randn(6))
```

**Matplotlib** 中使用 `barh` 来绘制水平条形图。


```python
ax.barh(x, y)
fig
```


​    
![](bar/output_54_0.png)
​    

其余设置与普通的条形图几乎没有任何区别。


```python
ax.clear()
```

## 堆叠条形图

我们现在给定一个 $3 \times 6$ 的矩阵，这三行数值都属于不同的系列，并且我们希望对其求和。


```python
x = np.arange(1, 7)
y = np.abs(np.random.randn(3, 6))
y1 = y[0, :]
y2 = y[1, :]
y3 = y[2, :]
```

下面我们绘制堆叠条形图，我们通过 `bottom` 参数来设置条形图的底部坐标。


```python
ax.bar(x, y1)
ax.bar(x, y2, bottom=y1)
ax.bar(x, y3, bottom=(y1 + y2))
fig
```


​    
![](bar/output_61_0.png)
​    


```python
ax.clear()
```

## 条形图与折线图的综合应用

我们经常会碰到如下情况：需要对比两个不在同一数量级的量。这个时候我们经常用一张图、两个纵坐标轴的方法来绘图。数据如下：


```python
x = np.arange(1, 7)
y1 = np.abs(np.random.rand(6))
y2 = np.abs(100 * np.random.rand(6))
```

使用 `Axes` 对象的 `twinx` 方法可以让返回的新 `Axes` 对象和原来的 `Axes` 对象共用同一个 $x$ 轴。


```python
ax_t = ax.twinx()
```

两个的 `Axes` 对象分别绘制条形图和折线图。我们希望折线图显示在条形图的上方，故使用 `zorder` 参数。


```python
ax.bar(x, y1, zorder=1)
ax_t.plot(x, y2, zorder=1, linewidth=2, marker='^', color='r')
fig
```


​    
![](bar/output_69_0.png)
​
