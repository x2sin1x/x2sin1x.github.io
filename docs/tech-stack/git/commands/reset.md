---
title: "reset 命令"
date: 2021-12-02T23:56:19+08:00
weight: 280
---

# reset 命令：重置暂存区和版本库

`git reset` 用于将当前分支的 HEAD 移动到指定提交，并可按模式选择是否同时重置暂存区与工作区。

`--mixed` 参数为默认，用于重置暂存区与指定提交保持一致，工作区文件内容保持不变。以下的命令是等价的：

```bash
git reset
git reset --mixed
git reset HEAD
```

`--soft` 参数只移动 HEAD，暂存区与工作区都保持不变，适合合并提交或重新组织暂存内容：

```bash
git reset --soft HEAD^		# 回退到上一个版本，改动保留在暂存区
```

`--hard` 参数丢弃暂存区与工作区中的所有改动，完全回到指定版本，被重置的提交内容将丢失：

```bash
git reset --hard
git reset --hard HEAD^		# 彻底回退到上一个版本
```

&#8203;**注**&#8203;：`git reset` 带文件路径时不移动 HEAD，仅用于将指定文件在暂存区中的版本重置为指定提交中的版本，且不能使用 `--soft` 或 `--hard`：

```bash
git reset 0b3dac -- foo.py	# 将 foo.py 的暂存版本重置为 0b3dac 中的版本
```

&#8203;**注**&#8203;：`git reset` 会改写历史（丢弃之后的提交），在已推送到远程的公共分支上慎用，必要时可借助 `git reflog` 找回。
