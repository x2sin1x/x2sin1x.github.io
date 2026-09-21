---
title: "log 命令"
date: 2021-12-02T23:53:58+08:00
weight: 160
---

# log 命令：查看提交历史

`git log` 用于按时间倒序查看当前分支的提交历史。

```bash
git log
```

`-p` 或 `--patch` 参数可以同时显示每次提交引入的差异：

```bash
git log -p
```

只显示最近 2 次提交：

```bash
git log -2
```

`--oneline` 参数将每条提交压缩为一行（短哈希 + 提交说明）：

```bash
git log --oneline
```

以图形方式显示分支与合并历史：

```bash
git log --graph --oneline --all
```

其他常用参数：

```bash
git log --author="Username"		# 只看某位作者的提交
git log --grep="fix"			# 按提交说明关键字搜索
git log --since="2 weeks ago"	# 只看某段时间内的提交
git log --stat					# 显示每次提交的文件变更统计
```
