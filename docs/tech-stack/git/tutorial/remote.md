---
title: "Git 远程仓库"
date: 2021-12-03T10:05:35+08:00
weight: 40
---
# Git 远程仓库

## 添加远程仓库

```sh
git remote add origin git@server-name:path/repo-name.git
```

此时可以查看远程仓库信息：

```sh
git remote
git remote -v		#显示更详细的信息
```

*注*

1. `origin` 是远程仓库的名字，不是参数。当然，也可以换成别的名字，但是 `origin` 让人一看就是远程仓库的意思。如果一个本地仓库需要关联至少两个远程仓库，应当起两个不同的名字以示区别。
2. 后面的地址是使用ssh协议的地址，我们非常建议使用ssh地址，因为它是非对称加密，稳定安全。

## 推送本地仓库

```sh
git push origin master
```

注意，这里 `master` 的含义是（主）分支，这将在后文详述。通常情况下，默认只有一个主分支。如果需要推送到其他分支，应当指定其名称。

如果是刚刚关联的远程仓库，一般需要使用下面的命令：

```sh
git push -u origin master
```

`-u` 参数的意思是，将本地的 `master` 分支和远程的 `master` 分支关联起来。使用 `-u` 参数后，可以简化推送命令 `git push`。即，本地是在哪个分支上，就推送到远程的哪个分支上去。

## 从远程仓库克隆

```sh
git clone git@server-name:path/repo-name.git
```

会在当前文件夹下创建一个名为 `repo-name` 的本地仓库。
