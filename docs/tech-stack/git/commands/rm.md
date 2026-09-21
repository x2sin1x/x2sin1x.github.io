---
title: "rm 命令"
date: 2021-12-02T23:55:36+08:00
weight: 240
---

# rm 命令：删除文件

`git rm` 用于从工作区和暂存区中删除被跟踪的文件，为下一次提交记录这次删除。

```bash
git rm foo.class
```

如果文件的改动已经暂存，则必须使用 `-f` 参数强制删除：

```bash
git rm -f foo.class
```

如果只是想把文件从暂存区移除（取消跟踪），但仍然保留在当前工作目录中，可以使用 `--cached` 参数：

```bash
git rm --cached foo.class
```

递归删除整个目录：

```bash
git rm -r build/
```
