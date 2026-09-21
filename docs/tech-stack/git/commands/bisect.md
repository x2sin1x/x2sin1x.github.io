---
title: "bisect 命令"
date: 2021-12-02T23:57:45+08:00
weight: 430
---

# bisect 命令：二分定位 bug

`git bisect` 通过二分查找在提交历史中快速定位引入 bug 的提交，适合提交数量很多的仓库。

开始二分查找，并标定“好”“坏”两个端点：

```bash
git bisect start
git bisect bad HEAD			# 当前提交有 bug
git bisect good v1.0		# v1.0 版本没有 bug
```

Git 会自动切换到中间的某个提交，测试后标记它：

```bash
git bisect good		# 该提交没有 bug，继续在较新的提交中查找
git bisect bad		# 该提交有 bug，继续在较早的提交中查找
```

重复上述过程，每次提交数量折半，最终 Git 会给出第一个引入 bug 的提交。

结束查找，回到开始之前的分支状态：

```bash
git bisect reset
```

如果有一段测试脚本可以自动判断好坏，可以用 `run` 一步完成查找：

```bash
git bisect start HEAD v1.0
git bisect run npm test
```
