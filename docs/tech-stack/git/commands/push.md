---
title: "push 命令"
date: 2021-12-02T23:57:45+08:00
weight: 420
---

# push 命令：推送到远程仓库

`git push` 用于将本地分支的提交上传到远程仓库。

初次推送，需要添加 `-u` 参数，因为本地分支还没有和远程对应分支关联（关联后即可直接使用 `git push`）：

```bash
git push -u origin master
```

可以指定不同的分支进行推送：

```bash
git push origin master:dev.branch
```

`--force` 或 `-f` 参数表示强制推送（会覆盖远程历史，慎用）：

```bash
git push -f
```

更安全的强制推送，若远程有他人新推送的提交则会拒绝：

```bash
git push --force-with-lease
```

`--delete` 或 `-d` 参数表示删除远程分支：

```bash
git push origin -d master
```

推送标签（标签不会随分支自动推送）：

```bash
git push origin v1.0
git push origin --tags
```
