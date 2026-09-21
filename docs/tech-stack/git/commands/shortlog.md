---
title: "shortlog 命令"
date: 2021-12-02T23:53:58+08:00
weight: 200
---

# shortlog 命令：按作者归纳提交

`git shortlog` 用于按作者分组归纳提交历史，通常用于快速浏览每位作者的提交情况或生成变更摘要。

按作者归纳当前分支的提交：

```bash
git shortlog
```

不进入分页交互，直接输出统计（常用于管道或脚本）：

```bash
git shortlog -s
```

`-n` 参数按提交数量排序，`-e` 参数同时显示作者邮箱：

```bash
git shortlog -sne
```

统计某段时间内的提交：

```bash
git shortlog --since="1 month ago"
```
