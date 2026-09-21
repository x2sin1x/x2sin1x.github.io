---
title: "status 命令"
date: 2021-12-02T23:53:58+08:00
weight: 140
---

# status 命令：查看状态

`git status` 用于显示工作区与暂存区的状态：哪些文件被修改、哪些已暂存、哪些尚未被 Git 跟踪。

```bash
git status
```

`-s` 或 `--short` 参数可以显示更简短的内容，每行开头的两个字符分别表示暂存区与工作区的状态（`M` 修改、`A` 新增、`D` 删除、`??` 未跟踪）：

```bash
git status -s
```

`-b` 参数在简短输出中同时显示当前分支及其跟踪关系：

```bash
git status -sb
```
