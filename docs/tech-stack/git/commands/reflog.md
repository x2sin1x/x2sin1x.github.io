---
title: "reflog 命令"
date: 2021-12-02T23:53:58+08:00
weight: 170
---

# reflog 命令：查看操作历史

`git reflog` 用于查看本地 HEAD 的全部变动记录。与 `git log` 相比，它除了可以查看提交历史外，还可以查看分支切换、合并、重置等所有本地操作记录，即使某些提交已经不在任何分支上（例如被 `git reset` 丢弃的提交）也能找到。

```bash
git reflog
```

每条记录都包含一个简短哈希值，可以配合 `git reset` 或 `git checkout` 进行“时光穿梭”，例如恢复到被误删的提交：

```bash
git reflog
git reset --hard HEAD@{2}
```

查看某次 HEAD 移动的详细时间等信息：

```bash
git reflog --date=iso
```

&#8203;**注**&#8203;：`reflog` 记录只保存在本地，默认保留 90 天，不会随 `git push` 上传到远程。
