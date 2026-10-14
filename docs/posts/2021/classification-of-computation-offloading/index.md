---
title: "Classification of Computation Offloading"
description: "根据李克勤教授的学术报告整理，从用户设备、任务数量等十个维度建立移动边缘计算任务卸载研究的分类框架。"
date: 2021-07-05
categories:
  - Academic
tags:
  - 边缘计算
  - 任务卸载
---

# Classification of Computation Offloading

2021年6月23日上午8:30，湖南大学信息科学与工程学院博士生导师[李克勤](http://csee.hnu.edu.cn/people/likeqin)教授在线上做题为《移动边缘计算中任务卸载的博弈论方法》的报告。

本文将李教授报告中关于边缘计算领域研究的十个维度进行整理。对这十个维度熟悉到一定程度后，任何关于边缘计算的工作我们都可以进行定位。

## Number of UEs

- Single
- Multiple (homogeneous, heterogeneous)

UEs，即 User Equipments，用户的设备。在论文的场景中，究竟是单用户 `signle` 还是多用户 `multiple`？如果是多用户，那么用户设备是同构的 `homogeneous` 还是异构的 `heterogeneous`？

## Number of tasks per UE

- Single/multiple, Finite/infinite
- Independent/precedence constrained

在论文的场景中，每个用户产生的任务数量是多少？最简单的情况是每个用户只产生一个任务 `single`，稍微复杂一些的就是多任务 `multiple`。而多任务又可以分为有限 `finite` 个任务和无限 `infinite` 个任务。而无限个任务就是一个任务流 `task flow`，我们就需要用到排队论的知识。

任务之间可能没有任何依赖关系，或者说是独立的 `independent`；但也有可能彼此之间是有先后次序的，或者说具有优先级约束 `precedence constrained`。

## Number of MECs

- Single
- Multiple (homogeneous, heterogeneous)

MECs，即 Mobile Edge Clouds，移动边缘云，简单来说就是边缘服务器。同理，它也可以分为单个边缘服务器 `single` 和多个边缘服务器 `multiple`。而多个边缘服务器同样也涉及到同构 `homogeneous` 和异构 `heterogeneous` 的问题。

## Type of UE and MEC

- Uni-server (M/M/1, M/G/1, G/G/1)
- Multi-server (M/M/m, M/G/m, G/G/m)

所谓的用户设备并不是一个被动设备，它其实是有处理能力的。因此，从某种意义上说，用户设备也是一个服务器。排队论已经告诉我们如何对服务器进行建模。针对单核服务器 `uni-server`，我们可以建模成 M/M/1、M/G/1 或者 G/G/1 问题；针对多核服务器（边缘服务器通常都是多核服务器），我们可以建模成 M/M/m、M/G/m 或者 G/G/m 问题。

## Modeling of UE and MEC

- Deterministic
- Probabilistic
- Stochastic (queuing model)

针对用户设备和边缘服务器的数学建模主要有三种：

1. 确定型。例如组合优化，要求每个任务的执行时间是一个已知的量。
2. 概率型。任务执行时间是一个随机变量
3. 统计型。例如排队论模型。

## Variables to control

- Offloading strategy (load distribution)
- Computation speed (CPU frequency)
- Communication speed (transmission power)

可控变量，即哪些变量是可以调节的。

首先就是任务卸载策略 `offloading strategy`。任务到底卸不卸载？如果卸载，卸载到哪里去？如果有多个服务器，还涉及到负载均衡 `load distribution` 的问题。

其次是设备本身的计算速度 `computation speed`，或者说 CPU 的主频 `frequency`。计算速度如果快，那么能耗就会大。因此，计算速度和能耗需要进行平衡。不过，边缘服务器的计算机速度是不可调的，每个用户只能调节他自己设备的计算速度。

最后是通讯速度 `communication speed`，这个也可以调节。通讯速度主要取决于发射功率。发射功率越大，能耗也越大，这也需要进行平衡。

## Metric

- Performance (execution delay, response time)
- Cost (power consumption, energy consumption)
- Other (number of tasks completed)

度量方法主要分为性能和开销两大类，也有其他的一些方法。

具体来说，从性能角度看，主要有任务执行时延 `execution delay` 和任务响应时延 `response time` 两个指标。

从开销角度看，主要有功耗 `power consumption` 和能耗 `energy consumption` 两个指标。

性能和开销是两大最重要的度量方法，当然还有一些其他的度量方式。例如，已完成的任务数 `number of tasks completed` 等。

## Performance-cost tradeoff

- Cost constrained performance optimization
- Performance constrained cost optimization
- Joint performance and cost (multi-objective) optimization
- Combined performance and cost (weighted sum, cost-performance ratio) optimization

李教授认为，性能和开销的平衡是所有的服务计算（网格计算、分布式计算、集群计算、云计算、雾计算、边缘计算等）里面的重要问题，而且是鱼和熊掌不可兼得的。

我们应该怎样去研究呢？例如，在一定开销的约束下优化性能 `cost constrained performance optimization`，或者倒过来，在一定性能的约束下优化开销 `performance constrained cost optimization`。

还有一种方法，就是综合考虑这两种指标，这就涉及到多目标 `multi-objective` 优化。也可以把这两种指标结合 `combined` 起来，转化成单目标优化。例如加权求和 `weighted sum`，或者求性价比 ` cost-performance ratio`。

## Optimization

- Globalized, collective, and centralized optimization for all UEs
- Localized, individualized, and distributed optimization for each UE (non-cooperative game)

优化方法主要分为两大类：一种是整体的、中心式的优化，它是针对所有用户的优化；还有一种是局部的、个性化的、分布式的优化，它是为每个用户量身定制的优化。李教授认为，这和非合作博弈 `non-cooperative game` 非常类似。

## Technique

- Discrete and combinatorial (NP-hard, heuristics)
- Continuous and probabilistic (Lyapunov optimization)
- Continuous and stochastic (multi-variable optimization)

优化的具体的技术和方法主要有以下几种：

1. 离散和组合型变量优化。这种方法一般适用于解决 NP 难问题，启发式 `heuristics` 算法非常适合解决这种 NP 难问题。
2. 连续和概率型变量优化。李亚普诺夫优化是近几年来比较热门的方法之一。
3. 连续和统计型变量优化。即通过排队论将问题建模成传统的多变量优化问题。
