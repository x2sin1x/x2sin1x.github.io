---
title: "Redis"
date: 2026-09-15T09:00:00+08:00
weight: 65
---
# Redis

本教程面向第一次接触 Redis 的开发者。你将使用 Redis 8.10、Docker、`redis-cli` 和 redis-py，围绕一个任务管理示例完成写入、查询、过期和统计等常见操作。

内容基线：Redis 8.10（Docker 镜像 `redis:8.10`）、redis-py 8.1.x，最后核对时间为 2026 年 9 月。

## 学习目标

完成本章节后，你将能够：

- 解释 Redis 的键值模型与五种核心数据类型。
- 使用 `redis-cli` 写入和读取字符串、哈希、列表、集合与有序集合。
- 为键设置过期时间，并安全地遍历大量键。
- 使用管道和事务减少网络往返并保证操作原子性。
- 在 Python 程序中通过 redis-py 访问同一组数据。

## 环境要求

- 已安装 Docker Desktop 或 Docker Engine。
- Docker 可以在本地映射 `6379` 端口。
- 已安装 Python 3.10 或更高版本（仅在学习 Python API 时需要）。
- 能够在终端中运行基本命令。

## 推荐顺序

1. [基本概念](/tech-stack/redis/concept)：启动 Redis，理解键值模型和命令行工具。&#8203;**必学**&#8203;，后续页面都依赖这里的容器和命名约定。
2. [数据类型](/tech-stack/redis/data-types)：用五种核心数据类型建模任务数据。&#8203;**必学**&#8203;，这是 Redis 与其他数据库差异最大的部分。
3. [键与过期](/tech-stack/redis/keys)：遍历、删除键并设置 TTL。&#8203;**必学**&#8203;，缓存等典型场景都建立在这组命令上。
4. [管道与事务](/tech-stack/redis/pipeline)：批量执行命令并理解原子性。只需要简单读写时可暂时跳过。
5. [Python API](/tech-stack/redis/python)：使用 redis-py 将命令写进 Python 程序。不使用 Python 的读者可以跳过。

每章末尾附有小结和练习。练习只需要已启动的 `redis-cli` 或本地 Python 环境，不需要额外工具。

## 参考资料

- [Redis 官方文档](https://redis.io/docs/latest/)：概念、数据类型和客户端的权威来源。
- [Redis 命令参考](https://redis.io/docs/latest/commands/)：每个命令的参数、返回值和时间复杂度。
- [Redis 官方教程](https://redis.io/tutorials/)：缓存、限流、排行榜等实战场景。
- [redis-py 官方文档](https://redis-py.readthedocs.io/en/latest/)：Python 驱动的入门教程与 API 说明。
- [Docker Hub 的 redis 镜像](https://hub.docker.com/_/redis)：镜像标签和数据持久化配置。
