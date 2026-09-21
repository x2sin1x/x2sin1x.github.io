---
title: "remote 命令"
date: 2021-12-02T23:57:45+08:00
weight: 390
---

# remote 命令：远程仓库管理

`git remote` 用于管理远程仓库的关联：查看、添加、重命名与删除。

查看远程仓库：

```bash
git remote
```

`-v` 参数同时显示远程仓库的读写 `url`：

```bash
git remote -v
```

添加远程仓库：

```bash
git remote add origin git@github.com:Username/repo.git
```

重命名远程仓库名称：

```bash
git remote rename origin github-origin
```

查看远程仓库 `url`：

```bash
git remote get-url github-origin
```

修改远程仓库 `url`：

```bash
git remote set-url github-origin git@github.com:Username/repository.git
```

删除远程仓库关联：

```bash
git remote remove github-origin
```
