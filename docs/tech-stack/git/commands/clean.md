---
title: "clean 命令"
date: 2021-12-02T23:56:19+08:00
weight: 300
---

# clean 命令：删除未跟踪文件

`git clean` 用于删除工作区中未被 Git 跟踪的文件，例如编译产物、临时文件等。

出于安全考虑，`git clean` 必须显式指定删除范围。先用 `-n` 或 `--dry-run` 预览将会删除哪些文件：

```bash
git clean -n
```

删除未跟踪的文件：

```bash
git clean -f
```

`-d` 参数同时删除未跟踪的目录，`-x` 参数连被 `.gitignore` 忽略的文件也一起删除：

```bash
git clean -fd		# 删除未跟踪的文件和目录
git clean -fdx		# 连同被忽略的文件一起删除
```

按模式只删除部分文件：

```bash
git clean -f "*.log"
```
