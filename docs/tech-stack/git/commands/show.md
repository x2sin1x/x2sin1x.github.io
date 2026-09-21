---
title: "show 命令"
date: 2021-12-02T23:53:58+08:00
weight: 180
---

# show 命令：查看对象详情

`git show` 用于查看某个 Git 对象（提交、标签、树、文件内容）的详细信息。默认显示当前 `HEAD` 提交的内容与差异。

查看最新一次提交的详细信息与改动：

```bash
git show
```

查看指定提交的详细信息与改动：

```bash
git show 0b3dac
```

只查看某次提交的提交说明（不显示差异）：

```bash
git show -s 0b3dac
```

查看某次提交中指定文件的变化：

```bash
git show 0b3dac:test.py		# 查看该提交中文件的完整内容
git show 0b3dac -- test.py	# 查看该提交中文件的改动差异
```

查看标签指向的提交信息：

```bash
git show v1.0
```
