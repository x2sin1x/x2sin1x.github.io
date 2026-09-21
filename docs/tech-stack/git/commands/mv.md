---
title: "mv 命令"
date: 2021-12-02T23:55:36+08:00
weight: 230
---

# mv 命令：移动或重命名文件

`git mv` 用于移动或重命名文件、目录，等价于重命名文件后再执行 `git rm --cached` 与 `git add`，Git 会自动记录这一改名操作。

```bash
git mv test.py ./src/foo.py
```

如果目标文件已经存在，但仍要重命名覆盖，可以使用 `-f` 参数强制覆盖：

```bash
git mv -f test.py ./src/foo.py
```
