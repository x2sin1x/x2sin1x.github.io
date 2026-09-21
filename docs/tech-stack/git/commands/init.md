---
title: "init 命令"
date: 2021-12-02T23:53:04+08:00
weight: 110
---

# init 命令：初始化本地版本库

`git init` 用于创建一个空的 Git 版本库（会生成一个 `.git` 隐藏目录），或重新初始化一个已存在的版本库。

在当前目录新建一个 Git 仓库：

```bash
git init
```

在当前目录下新建一个目录，并将其初始化为 Git 仓库：

```bash
git init Project
```

初始化时指定初始分支名称（默认为 `master`，也可由 `init.defaultBranch` 配置决定）：

```bash
git init -b main
```

&#8203;**注**&#8203;：`git init` 不会覆盖已有的 `.git` 目录，对已有仓库重复执行是安全的。
