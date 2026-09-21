---
title: "add 命令"
date: 2021-12-02T23:55:36+08:00
weight: 220
---

# add 命令：暂存（跟踪）文件

`git add` 用于将工作区中文件的内容加入暂存区，为下一次提交做准备；对尚未跟踪的新文件执行 `git add` 也意味着开始跟踪它。

暂存所有已更改的文件：

```bash
git add .
git add -A
```

暂存指定的文件（可以添加多个）：

```bash
git add test.py
git add file1 file2
```

暂存交互式选择，逐个确认每一处改动（块）：

```bash
git add -p
```

&#8203;**注**&#8203;：`git add` 记录的是执行时刻的文件内容，暂存后又修改的文件需要重新执行 `git add`。
