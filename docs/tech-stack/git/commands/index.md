---
title: "常用命令一览"
date: 2021-12-02T23:50:11+08:00
weight: 100
---

# Git 常用命令一览

本节将 Git 的常用命令按用途分类整理，每个命令单独一页，包含功能说明与常见用法示例。

## 创建版本库

| 命令 | 功能概述 | 详细用法 |
| ---- | -------- | -------- |
| `git init` | 初始化一个本地版本库 | [init 命令](/tech-stack/git/commands/init) |
| `git clone` | 克隆远程版本库到本地 | [clone 命令](/tech-stack/git/commands/clone) |

## 修改配置

| 命令 | 功能概述 | 详细用法 |
| ---- | -------- | -------- |
| `git config` | 查看、设置 Git 的各项配置（用户名、邮箱、别名等） | [config 命令](/tech-stack/git/commands/config) |

## 查询信息

| 命令 | 功能概述 | 详细用法 |
| ---- | -------- | -------- |
| `git status` | 查看工作区与暂存区的状态 | [status 命令](/tech-stack/git/commands/status) |
| `git diff` | 查看尚未暂存、已暂存或提交之间的变更内容 | [diff 命令](/tech-stack/git/commands/diff) |
| `git log` | 查看提交历史 | [log 命令](/tech-stack/git/commands/log) |
| `git reflog` | 查看本地所有 HEAD 变动记录，可用于“时光穿梭” | [reflog 命令](/tech-stack/git/commands/reflog) |
| `git show` | 查看某个提交、标签或对象的详细信息 | [show 命令](/tech-stack/git/commands/show) |
| `git blame` | 逐行显示文件的最后修改者与修改提交 | [blame 命令](/tech-stack/git/commands/blame) |
| `git shortlog` | 按作者归纳汇总提交历史 | [shortlog 命令](/tech-stack/git/commands/shortlog) |
| `git grep` | 在版本库内容中搜索指定的文本 | [grep 命令](/tech-stack/git/commands/grep) |

## 修改和提交

| 命令 | 功能概述 | 详细用法 |
| ---- | -------- | -------- |
| `git add` | 将文件内容加入暂存区（跟踪新文件） | [add 命令](/tech-stack/git/commands/add) |
| `git mv` | 移动或重命名文件、目录（Git 会自动跟踪） | [mv 命令](/tech-stack/git/commands/mv) |
| `git rm` | 从工作区和暂存区中删除文件 | [rm 命令](/tech-stack/git/commands/rm) |
| `git commit` | 将暂存区的内容提交到版本库 | [commit 命令](/tech-stack/git/commands/commit) |
| `git stash` | 临时保存（贮藏）当前未提交的修改 | [stash 命令](/tech-stack/git/commands/stash) |

## 撤销与回退

| 命令 | 功能概述 | 详细用法 |
| ---- | -------- | -------- |
| `git restore` | 撤销工作区或暂存区中的修改 | [restore 命令](/tech-stack/git/commands/restore) |
| `git reset` | 重置暂存区或版本库到指定提交 | [reset 命令](/tech-stack/git/commands/reset) |
| `git revert` | 用一次新提交来反做某次历史提交 | [revert 命令](/tech-stack/git/commands/revert) |
| `git clean` | 删除工作区中未被跟踪的文件 | [clean 命令](/tech-stack/git/commands/clean) |

## 分支与标签

| 命令 | 功能概述 | 详细用法 |
| ---- | -------- | -------- |
| `git branch` | 查看、创建、删除分支 | [branch 命令](/tech-stack/git/commands/branch) |
| `git checkout` | 切换分支或恢复工作区文件（旧版通用命令） | [checkout 命令](/tech-stack/git/commands/checkout) |
| `git switch` | 切换或创建并切换分支（checkout 的分支专用替代） | [switch 命令](/tech-stack/git/commands/switch) |
| `git worktree` | 管理多个工作树，让多个分支同时检出 | [worktree 命令](/tech-stack/git/commands/worktree) |
| `git tag` | 查看、创建、删除标签 | [tag 命令](/tech-stack/git/commands/tag) |
| `git merge` | 将指定分支合并到当前分支 | [merge 命令](/tech-stack/git/commands/merge) |
| `git rebase` | 将一系列提交重新应用到另一基底上（变基） | [rebase 命令](/tech-stack/git/commands/rebase) |
| `git cherry-pick` | 将其他分支上的单个提交应用到当前分支 | [cherry-pick 命令](/tech-stack/git/commands/cherry-pick) |

## 远程操作

| 命令 | 功能概述 | 详细用法 |
| ---- | -------- | -------- |
| `git remote` | 管理远程仓库（查看、添加、重命名、删除） | [remote 命令](/tech-stack/git/commands/remote) |
| `git fetch` | 获取远程仓库的更新，但不合并到本地分支 | [fetch 命令](/tech-stack/git/commands/fetch) |
| `git pull` | 获取远程仓库的更新并合并到当前分支 | [pull 命令](/tech-stack/git/commands/pull) |
| `git push` | 推送本地提交到远程仓库 | [push 命令](/tech-stack/git/commands/push) |

## 调试

| 命令 | 功能概述 | 详细用法 |
| ---- | -------- | -------- |
| `git bisect` | 通过二分查找定位引入 bug 的提交 | [bisect 命令](/tech-stack/git/commands/bisect) |
