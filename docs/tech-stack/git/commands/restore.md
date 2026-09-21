---
title: "restore 命令"
date: 2021-12-02T23:56:19+08:00
weight: 270
---

# restore 命令：撤销工作区或暂存区

`git restore`（Git 2.23 引入）用于撤销工作区或暂存区中的修改，是 `git checkout` 撤销文件职责的专用替代命令。

将所有本地文件未暂存的更改撤销，恢复到暂存区（或指定来源）的状态：

```bash
git restore .
```

将指定未暂存的文件的更改撤销：

```bash
git restore test.py
```

`--staged` 参数用于将暂存区的文件撤销暂存，但不改变工作区已有的更改：

```bash
git restore --staged
git restore --staged test.py
```

同时撤销暂存区与工作区的修改（危险操作，改动会丢失）：

```bash
git restore --staged --worktree test.py
```

从指定的提交恢复文件内容：

```bash
git restore --source HEAD~2 test.py
```
