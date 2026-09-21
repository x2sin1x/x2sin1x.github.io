---
title: "grep 命令"
date: 2021-12-02T23:53:58+08:00
weight: 210
---

# grep 命令：在版本库中搜索文本

`git grep` 用于在工作区或指定提交的内容中搜索匹配的文本，比操作系统级的搜索更快，且只搜索被 Git 跟踪的文件。

在工作区中搜索包含 `TODO` 的行：

```bash
git grep TODO
```

在指定提交的内容中搜索：

```bash
git grep TODO v1.0
```

显示匹配行的行号：

```bash
git grep -n TODO
```

统计每个文件中匹配的行数：

```bash
git grep -c TODO
```

忽略大小写，或使用扩展正则：

```bash
git grep -i todo
git grep -E "foo(bar|baz)"
```
