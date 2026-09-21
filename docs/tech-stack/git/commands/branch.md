---
title: "branch 命令"
date: 2021-12-02T23:56:53+08:00
weight: 310
---

# branch 命令：分支管理

`git branch` 用于查看、创建、删除和重命名分支，但不能用来切换分支（切换请使用 `git switch` 或 `git checkout`）。

查看当前所有分支，`*` 标记当前所在分支：

```bash
git branch
```

查看所有远程分支，或同时查看本地与远程分支：

```bash
git branch -r
git branch -a
```

创建分支：

```bash
git branch dev.branch
```

删除分支（要求已合并），或强制删除未合并的分支：

```bash
git branch -d dev.branch
git branch -D dev.branch
```

重命名分支：

```bash
git branch -m dev.branch dev
```

查看每个分支的最近一次提交：

```bash
git branch -v
```
