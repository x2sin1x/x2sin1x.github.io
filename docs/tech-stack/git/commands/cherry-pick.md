---
title: "cherry-pick 命令"
date: 2021-12-02T23:56:53+08:00
weight: 380
---

# cherry-pick 命令：摘取单个提交

`git cherry-pick` 用于将其他分支上的某一个（或某几个）提交单独“摘取”并应用到当前分支，生成新的提交。

将指定的提交应用到当前分支：

```bash
git cherry-pick 90fa3b
```

一次应用多个提交：

```bash
git cherry-pick 90fa3b 0b3dac
```

应用一段连续的提交（左开右闭区间）：

```bash
git cherry-pick A^..B
```

只把改动放进工作区和暂存区，不自动生成提交：

```bash
git cherry-pick -n 90fa3b
```

出现冲突时，解决冲突并暂存后继续，或放弃本次摘取：

```bash
git cherry-pick --continue
git cherry-pick --abort
```
