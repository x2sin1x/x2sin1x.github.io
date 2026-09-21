---
title: "commit 命令"
date: 2021-12-02T23:55:36+08:00
weight: 250
---

# commit 命令：提交暂存文件

`git commit` 用于将暂存区中的全部内容作为一次提交记录到版本库。

提交暂存区的所有文件，并备注一些提交信息：

```bash
git commit -m "first commit"
```

自动暂存所有已跟踪文件的改动并提交（不包含未跟踪的新文件）：

```bash
git commit -a
```

只提交暂存区中的部分文件：

```bash
git commit file1 file2 -m "add file1 & file2"
```

追加到上一次提交（修改提交说明或补充文件，会生成新的提交替换原提交）：

```bash
git commit --amend
```

使用编辑器编写多行提交信息（不使用 `-m` 时为默认行为）：

```bash
git commit
```
