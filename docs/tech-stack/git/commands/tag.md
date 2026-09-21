---
title: "tag 命令"
date: 2021-12-02T23:56:53+08:00
weight: 350
---

# tag 命令：标签管理

`git tag` 用于给某个提交打上标签，常用于标记发布版本（如 `v1.0`）。

查看所有标签：

```bash
git tag
```

给当前提交打标签，其中 `-a` 参数表示创建一个带注解的标签（推荐，包含作者、日期与说明）：

```bash
git tag -a v1.0 -m "release 1.0"
```

给指定的提交追加标签：

```bash
git tag -a v1.1 90fa3b
```

创建轻量标签（只记录一个提交指针，无注解信息）：

```bash
git tag v1.0-light
```

删除本地标签：

```bash
git tag -d v1.0
```

推送标签到远程仓库：

```bash
git push origin v1.0		# 推送单个标签
git push origin --tags		# 推送所有标签
```
