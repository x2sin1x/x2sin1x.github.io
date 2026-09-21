---
title: "rebase 命令"
date: 2021-12-02T23:56:53+08:00
weight: 370
---

# rebase 命令：变基

`git rebase` 将当前分支上的一系列提交“摘下来”，重新逐个应用到指定分支的顶端，使提交历史呈现为一条直线。

将在各个分支的分散提交衍合到指定分支上：

```bash
git rebase master
```

交互式变基，可以编辑、合并（`squash`）、调整或删除一系列提交：

```bash
git rebase -i HEAD~3
```

变基过程中出现冲突时，解决冲突并暂存后继续，或放弃本次变基：

```bash
git rebase --continue
git rebase --abort
```

&#8203;**注**&#8203;：`git rebase` 会改写提交历史，变基后的提交哈希会变化。不要对已经推送到远程、他人可能基于其工作的提交执行变基。
