---
title: "diff 命令"
date: 2021-12-02T23:53:58+08:00
weight: 150
---

# diff 命令：查看变更内容

`git diff` 用于以补丁的形式比较两个版本之间的差异。

查看尚未暂存的改动（工作区 vs 暂存区）：

```bash
git diff
```

查看已经暂存的改动（暂存区 vs 上一次提交）：

```bash
git diff --cached
```

查看工作区相对上一次提交的所有改动（已暂存与未暂存）：

```bash
git diff HEAD
```

比较两个提交之间的差异：

```bash
git diff 0b3dac HEAD
```

只比较指定的文件或目录：

```bash
git diff -- test.py
```

显示更简短的摘要统计信息（增删行数）：

```bash
git diff --stat
```
