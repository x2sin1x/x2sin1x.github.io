---
title: "fetch 命令"
date: 2021-12-02T23:57:45+08:00
weight: 400
---

# fetch 命令：获取远程更新

`git fetch` 用于从远程仓库下载新的提交与分支信息，但不会合并到本地的当前分支，因此可以在合并前先检查远程的改动，是比 `git pull` 更安全的同步方式。

拉取远程仓库到本地，但不进行合并：

```bash
git fetch origin master
```

&#8203;**注**&#8203;：拉取下来的远程分支顶端记录在 `origin/master` 等远程跟踪分支中，单次 `git fetch <remote> <branch>` 的结果临时记录在 `FETCH_HEAD`。

拉取远程仓库所有分支的更新：

```bash
git fetch origin
# 或
git fetch --all
```

拉取的同时删除远程已经不存在的分支的本地跟踪引用：

```bash
git fetch -p
```

拉取后查看远程分支相对本地的差异：

```bash
git fetch origin
git log master..origin/master --oneline
```
