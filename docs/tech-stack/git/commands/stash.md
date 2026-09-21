---
title: "stash 命令"
date: 2021-12-02T23:55:36+08:00
weight: 260
---

# stash 命令：贮藏修改

`git stash` 用于将工作区与暂存区中未提交的修改临时保存起来，使工作区恢复干净，之后可以再恢复这些修改。常用于开发到一半需要切换分支处理紧急任务的场景。

贮藏当前所有未提交的修改：

```bash
git stash
```

添加说明信息，便于之后辨认：

```bash
git stash push -m "wip: login feature"
```

查看贮藏列表：

```bash
git stash list
```

恢复最近一次贮藏的修改：

```bash
git stash pop			# 恢复并从贮藏列表中删除
git stash apply			# 恢复但保留在贮藏列表中
git stash apply stash@{1}	# 恢复指定的某次贮藏
```

删除贮藏：

```bash
git stash drop stash@{0}	# 删除指定贮藏
git stash clear				# 清空所有贮藏
```
