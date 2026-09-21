---
title: "使用教程"
date: 2021-12-03T09:57:48+08:00
weight: 10
---

# Git 使用教程

## Git 工作流一览

::: mermaid
sequenceDiagram
    participant C as 干净工作区<br/>Clean Workspace
    participant M as 已更改工作区<br/>Modified Workspace
    participant I as 暂存区<br/>Index
    participant R as 本地仓库<br/>Repository
    participant RR as 远程仓库<br/>Remote

    RR->>R: git clone
    Note over RR,R: 克隆远程仓库<br/>创建本地仓库

    C->>M: 编辑 / 修改文件
    Note over C,M: 工作区产生修改

    M->>I: git add
    Note over M,I: 将修改加入暂存区

    I->>R: git commit
    Note over I,R: 创建新的提交

    R->>RR: git push
    Note over R,RR: 推送本地提交

    RR->>R: git fetch
    Note over RR,R: 获取远程更新

    R->>R: git merge
    Note over R: 将其他分支合并到当前分支

    R->>R: git rebase
    Note over R: 将当前分支提交变基到目标分支

    RR->>R: git pull
    Note over RR,R: fetch + merge / rebase

    I->>M: git restore --staged
    Note over I,M: 取消暂存<br/>修改保留在工作区

    M->>C: git restore
    Note over M,C: 丢弃工作区修改

    R->>I: git reset --soft HEAD~1
    Note over R,I: HEAD 回退<br/>暂存区保留

    R->>M: git reset HEAD~1
    Note over R,M: HEAD 回退<br/>取消暂存，修改保留

    R->>C: git reset --hard HEAD~1
    Note over R,C: HEAD、暂存区、工作区<br/>全部回退
:::

## Contents

- [安装 Git](/tech-stack/git/tutorial/installation)
- [Git 本地仓库](/tech-stack/git/tutorial/repository)
- [Git 远程仓库](/tech-stack/git/tutorial/remote)
- [Git 分支管理](/tech-stack/git/tutorial/branch)
- [Git 标签管理](/tech-stack/git/tutorial/tag)
