---
title: "pull 命令"
date: 2021-12-02T23:57:45+08:00
weight: 410
---

# pull 命令：获取远程更新并合并

`git pull` 相当于先执行 `git fetch` 再执行 `git merge`（或 `git rebase`），即获取远程仓库的更新并合并到当前分支。

拉取远程仓库到本地，并且进行合并：

```bash
git pull
```

默认情况下，合并的方式是按照分支名称对应合并的（前提是远程和本地都有该分支）：

```bash
git pull origin dev.branch
```

也可以指定合并不同的分支，其中 `:` 号前为远程分支，`:` 号后为本地分支。

```bash
git pull origin master:dev.branch
```

使用变基而不是合并的方式整合远程更新，保持提交历史线性：

```bash
git pull --rebase
```

&#8203;**注**&#8203;：若本地有未提交的修改，`git pull` 可能失败或产生冲突，建议先执行 `git stash` 或提交再拉取。
