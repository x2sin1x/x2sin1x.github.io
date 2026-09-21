---
title: "merge 命令"
date: 2021-12-02T23:56:53+08:00
weight: 360
---

# merge 命令：合并分支

`git merge` 用于将指定分支的提交合并到当前分支。

将指定分支合并到当前分支：

```bash
git merge dev.branch
```

`--no-ff` 参数强制生成一个合并提交（即使可以快进合并），保留分支合并的痕迹：

```bash
git merge --no-ff dev.branch
```

如果存在冲突，手动解决冲突并暂存后提交；也可以使用 `--abort` 终止合并，恢复到合并前的状态：

```bash
git merge --abort
```

合并过程中查看冲突的文件列表：

```bash
git diff --name-only --diff-filter=U
```
