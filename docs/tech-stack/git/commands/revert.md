---
title: "revert 命令"
date: 2021-12-02T23:56:19+08:00
weight: 290
---

# revert 命令：反做历史提交

`git revert` 命令适用于想要撤销较早提交的某个版本，而不影响之后提交的其他版本。之所以该命令可以实现上述功能，是因为其实质是用一次新的提交来回滚之前较早的某个版本，而不同于 `git reset` 命令直接删除相应提交。因此它不会改写历史，适合用于已推送到远程的公共分支。

反做指定的提交：

```bash
git revert 34dafc
```

`-n` 或 `--no-commit` 参数表示只应用反做的改动到暂存区，不自动生成提交，便于将多次反做合并为一次提交：

```bash
git revert -n 34dafc
```

一次反做连续的多个提交（左开右闭区间）：

```bash
git revert old-commit^..new-commit
```

如果反做过程出现冲突，解决后继续，或放弃本次反做：

```bash
git revert --continue
git revert --abort
```
