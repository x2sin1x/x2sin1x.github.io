---
title: "checkout 命令"
date: 2021-12-02T23:56:53+08:00
weight: 320
---

# checkout 命令：切换分支或恢复文件

`git checkout` 是一个多用途命令：既可以切换分支，也可以恢复工作区文件。Git 2.23 之后，这两类职责分别由 `git switch`（切换分支）和 `git restore`（恢复文件）承担，`checkout` 被保留以兼容旧习惯。

切换分支：

```bash
git checkout dev.branch
```

创建一个新的分支并切换到该分支：

```bash
git checkout -b dev.branch
```

它与下面的命令等价：

```bash
git branch dev.branch
git checkout dev.branch
```

基于远程分支创建并跟踪本地分支：

```bash
git checkout -b dev origin/dev
```

将指定文件恢复为暂存区（或指定提交）中的版本，丢弃工作区的修改：

```bash
git checkout -- test.py
```

&#8203;**注**&#8203;：切换分支前最好先提交或贮藏未完成的修改，否则改动可能被带到目标分支或导致切换失败。
