---
title: "更换软件源"
weight: 120
---

# 更换软件源

安装完成进入系统的第一件事就是换软件源，可以有效减少不必要的麻烦。

## 备份官方源

```bash
sudo mv /etc/apt/sources.list /etc/apt/sources.list.bak   # 备份官方源
sudo gedit /etc/apt/sources.list                          # 没有可视化文本编辑器的终端可以使用 vim
```

::: info
**Tip: Codename**

Ubuntu 中，每个版本都有一个更为特色的名字，这个名字由一个形容词和一个动物名称组成，并且，形容词和名词的首字母都是一致的。从 D 版本开始又增加了一个规则，首字母要顺延上个版本，如果当前版本是 D，下个版本就要以 E 来起头。

例如，Ubuntu 18.04 LTS 的代号为 Bionic Beaver，简称 `bionic`；Ubuntu 20.04 LTS 的代号为 Focal Fossa，简称 `focal`。

查询当前系统的版本代号可以使用下面的命令：

```bash
lsb_release -a
```
:::

## 添加软件源

**注意**：将软件源文本中关于代号的部分全部替换成相应的代号。本文列出的是 Ubuntu 18.04 LTS 对应的软件源。

### 阿里源

```
deb http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
```

### 清华源

```
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-proposed main restricted universe multiverse
deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse
deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-proposed main restricted universe multiverse
```

### 中科大源

```
deb https://mirrors.ustc.edu.cn/ubuntu/ bionic main restricted universe multiverse
deb https://mirrors.ustc.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
deb https://mirrors.ustc.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
deb https://mirrors.ustc.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
deb https://mirrors.ustc.edu.cn/ubuntu/ bionic-proposed main restricted universe multiverse
deb-src https://mirrors.ustc.edu.cn/ubuntu/ bionic main restricted universe multiverse
deb-src https://mirrors.ustc.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
deb-src https://mirrors.ustc.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
deb-src https://mirrors.ustc.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
deb-src https://mirrors.ustc.edu.cn/ubuntu/ bionic-proposed main restricted universe multiverse
```

## 更新软件源

```bash
sudo apt-get update     # 更新软件源
sudo apt-get upgrade    # 因为软件源更新了，所以要通过新的软件源再更新本地软件
```

**Tip: new apt command**

在 Ubuntu 16.05 之前，开发是通过 `apt-get`、`apt-cache`、`apt-config` 命令来和 `apt` 包管理系统交互的。这些工具提供了很多功能，但是一般来说开发者并没有使用他们提供的所有功能。

因此，Linux 想要创建一个更简单的工具——只具备基本功能即可。这一工具便是 `apt`，伴随 Ubuntu 16.05 和 Debian 8 发布。其主要目标是去合并最多使用的 `apt-get` 和 `apt-cache` 命令的功能到一个命令下：`apt`。

故更新软件源也可以用以下命令：

```bash
sudo apt update
sudo apt upgrade
```

今后使用 `apt` 包管理相关命令时，统一采用 `apt` 命令，而不使用 `apt-get` 命令。
