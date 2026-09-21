---
title: "worktree 命令"
date: 2021-12-02T23:56:53+08:00
weight: 340
---

# worktree 命令：多工作树管理

`git worktree` 允许同一个版本库同时检出多个分支到不同目录，无需 `git clone` 多份仓库或频繁切换分支。例如一边在 `main` 上修 bug，一边在另一个目录继续开发新功能。

添加一个工作树，将分支检出到指定目录：

```bash
git worktree add ../hotfix-dir hotfix
```

基于远程分支创建工作树并跟踪：

```bash
git worktree add -b dev ../dev-dir origin/dev
```

查看当前所有工作树：

```bash
git worktree list
```

删除不再使用的工作树：

```bash
git worktree remove ../hotfix-dir
```

清理已删除目录但未注销的工作树记录：

```bash
git worktree prune
```
