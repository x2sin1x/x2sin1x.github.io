---
title: "clone 命令"
date: 2021-12-02T23:53:04+08:00
weight: 120
---

# clone 命令：克隆远程版本库

`git clone` 用于将远程版本库完整复制到本地，包括全部历史记录和分支。

在当前目录下克隆远程仓库，文件夹名称为仓库名称 `repo`：

```bash
git clone https://github.com/username/repo
```

克隆时指定本地的文件夹名称（必须是空文件夹）：

```bash
git clone https://github.com/username/repo ~/Projects
```

只克隆远程仓库的某个分支：

```bash
git clone -b dev https://github.com/username/repo
```

浅克隆：只获取最近一次提交的历史，适合仓库很大但只关心最新代码的场景：

```bash
git clone --depth 1 https://github.com/username/repo
```

&#8203;**注**&#8203;：克隆完成后，Git 会自动将远程仓库命名为 `origin` 并建立跟踪关系。
