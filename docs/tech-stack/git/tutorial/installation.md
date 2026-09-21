---
title: "安装与配置"
date: 2021-12-03T09:57:30+08:00
weight: 20
---

# 安装与配置 Git

## 安装 Git

### Linux

- Ubuntu

```sh
sudo apt-get install git
```

### Windows

直接从[官方网站](https://git-scm.com/downloads)下载安装。

## Git 基本配置

### 设置用户名和邮箱

```sh
git config --global user.name "Your Name"
git config --global user.email email@example.com #邮箱不需要引号
```

配置完成后，可以查看是否配置成功：

```sh
git config --global --list 
```

### 设置 ssh key

执行以下命令生成秘钥：

```sh
ssh-keygen -t rsa -C "email@example.com"
```

执行命令后需要进行3次或4次确认：
- 确认秘钥的保存路径（一般为 `~/.ssh/`，如果不需要改路径则直接回车）；
- 如果上一步置顶的保存路径下已经有秘钥文件，则需要确认是否覆盖（如果之前的秘钥不再需要则直接回车覆盖，如需要则手动拷贝到其他目录后再覆盖）；
- 创建密码（如果不需要密码则直接回车）；
- 确认密码；

在指定的保存路径下会生成2个名为 `id_rsa` 和 `id_rsa.pub` 的文件，前者为私钥，后者为公钥。私钥无论如何都不能泄露出去，公钥可以放心地告诉任何人。

```sh
cat ~/.ssh/id_rsa.pub
```

登录 [GitHub](https:github.com)，选择 `Settings -> SSH and GPG keys -> New SSH key`，将公钥 `id_rsa.pub` 中的内容拷贝进去，并取一个名称（名称应当好记并且能够唯一标识当前的电脑）保存。
