---
title: "Git 标签管理"
---

# Git 标签管理

发布一个版本时，我们通常先在版本库中打一个标签 `tag`，这样，就唯一确定了打标签时刻的版本。将来无论什么时候，取某个标签的版本，就是把那个打标签的时刻的历史版本取出来。所以，标签也是版本库的一个快照。

实际上，标签就是一个特定的提交，本质上是指向某一个 `commit` 的指针常量。标签与某个版本绑定在一起，是一个让人容易记住的有意义的名字。

## 创建标签

```sh
git tag v1.0			#创建版本为v1.0的标签
git tag v0.9 f52c633	#指定特定的commit哈希值为v0.9的标签
```

可以直接使用 `git tag` 查看所有已创建的标签：

```sh
git tag
```

还可以创建带有说明的标签，用 `-a` 指定标签名，`-m` 指定说明文字：

```sh
git tag -a v0.1 -m "version 0.1 released" 1094adb
```

用命令 `git show <tagname>` 可以看到说明文字：

```sh
git show v0.1
```

## 操作标签

如果标签打错了，也可以删除：

```sh
git tag -d v0.1
```

如果要推送某个标签到远程，使用命令 `git push origin <tagname>`：

```sh
git push origin v1.0
git push origin --tags	#推送本地所有标签
```

如果标签已经推送到远程，要删除远程标签就麻烦一点，先从本地删除，再 `push`：

```sh
git tag -d v0.9
git push origin :refs/tags/v0.9
```
