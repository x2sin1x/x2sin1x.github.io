---
title: "switch 命令"
date: 2021-12-02T23:56:53+08:00
weight: 330
---

# switch 命令：切换分支

`git switch`（Git 2.23 引入）是专门用于切换分支的命令，从 `git checkout` 中拆分出来，语义更清晰；恢复文件请使用 `git restore`。

切换到指定分支：

```bash
git switch dev.branch
```

创建一个新的分支并切换到该分支（相当于 `git checkout -b`）：

```bash
git switch -c dev.branch
```

基于远程分支创建并跟踪一个新的本地分支：

```bash
git switch -c dev origin/dev
# 或直接简写为：
git switch dev
```

切换回上一次所在的分支：

```bash
git switch -
```

切换时放弃本地未提交的修改（危险操作，改动会丢失）：

```bash
git switch -f dev.branch
```
