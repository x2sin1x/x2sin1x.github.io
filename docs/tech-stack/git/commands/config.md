---
title: "config 命令"
date: 2021-12-02T23:54:48+08:00
weight: 130
---

# config 命令：修改配置

`git config` 用于查看和设置 Git 的各项配置。配置有三个作用域：`--system`（系统级）、`--global`（当前用户全局）与 `--local`（当前仓库，默认）。

设置用户名：

```bash
git config --global user.name "Username"
```

设置邮箱：

```bash
git config --global user.email username@server.com
```

&#8203;**注**&#8203;：如果去掉 `--global` 参数，则配置只对当前仓库有效。

设置默认编辑器与命令别名：

```bash
git config --global core.editor vim
git config --global alias.st status
```

查看配置：

```bash
git config --list			# 列出所有配置
git config user.name		# 查看某项配置的值
```

编辑或删除配置：

```bash
git config --global --edit		# 用编辑器打开全局配置文件
git config --global --unset user.name	# 删除某项配置
```
