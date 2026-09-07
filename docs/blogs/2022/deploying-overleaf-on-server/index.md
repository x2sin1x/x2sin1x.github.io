---
title: "在服务器上部署 Overleaf"
description: "记录在 Ubuntu 服务器上基于 Docker 与 Docker Compose 部署开源 Overleaf 在线协作 LaTeX 环境的全过程。"
---

# 在服务器上部署 Overleaf

[Overleaf](https://cn.overleaf.com/) 是开源的在线实时协作 $\LaTeX$ 编辑器。官方还提供了[开源镜像](https://github.com/overleaf/overleaf)，可以在服务器上部署。由于课题组需要多人在线协作撰写论文，特写此文记录 Overleaf 环境部署的说明。

## 准备工作

官方镜像是基于 Docker 的，最好部署在 Ubuntu 系统上。因此，如果服务器上没有部署 Docker，需要先安装 Docker。

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 安装 Docker Compose

不过，仅仅通过官方安装脚本安装的 Docker 还不够。还需要安装 Docker Compose：

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.2.2/docker-compose-\((uname -s)-\)(uname -m)" -o /usr/local/bin/docker-compose
```

如果要安装其他版本的 Docker Compose，替换路径中的 `v2.2.2`。（`v2.2.2` 是目前的稳定版本）

下面，将可执行权限应用于二进制文件 `docker-compose`：

```bash
sudo chmod +x /usr/local/bin/docker-compose
```

创建软链接：

```bash
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

测试是否安装成功：

```bash
docker-compose --version
```

## 拉取 Overleaf 镜像

```bash
docker pull sharelatex/sharelatex
```

我们可以新建一个空文件夹，在该文件夹下工作。

```bash
mkdir overleaf
cd overleaf
```

官方镜像是通过 Docker Compose 启动的，因此需要一个 [`docker-compose.yml`](docker-compose.yml) 配置文件。（单击文件名可以下载官方提供的 `yml` 文件）

接下来，使用下面的命令运行 Docker 容器：

```bash
docker compose up -d
```

由于完整安装 $\LaTeX$ 环境需要安装很多包，全部打包到 Docker 镜像中的话太大，不利于网络传输。因此，Overleaf 官方仅仅在 Docker 镜像中部署了很少一部分 $\LaTeX$ 的功能。完整的 $\LaTeX$ 功能需要我们手动安装。

## 安装完整的 LaTeX 环境

在运行的容器内部，我们手动安装如下包：

```bash
docker exec sharelatex tlmgr install scheme-full
```

安装的过程很漫长，需要耐心等待。

::: warning
我在安装过程中出现了报错如下：

```
tlmgr: Local TeX Live (2021) is older than remote repository (2022).
Cross release updates are only supported with
  update-tlmgr-latest(.sh/.exe) --update
See https://tug.org/texlive/upgrade.html for details.
```

根据报错的信息，我判断是 `tlmgr` 的版本过低需要更新。按照相应网站的提示，将一些必要命令转化为 Docker 容器可以运行的命令如下：

```bash
docker exec sharelatex wget https://mirror.ctan.org/systems/texlive/tlnet/update-tlmgr-latest.sh
docker exec sharelatex sh update-tlmgr-latest.sh -- --upgrade
docker exec sharelatex tlmgr update --self --all
```

然后再运行上面的安装命令，就可以成功。
:::

::: info
**注意**

`docker exec` 命令对 Docker 容器的更改是暂时的。如果用 Docker Compose 重新创建容器，之前所做的更改（安装完整的 $\LaTeX$）将会丢失。因此，可以使用 `docker commit` 命令：

```bash
docker commit sharelatex sharelatex/sharelatex:with-texlive-full
```

然后编辑 `docker-compose.yml` 文件：

```bash
vim docker-compose.yml
```

找到镜像设置，并且更改为：

```yml
# ...
services:
    sharelatex:
        image: sharelatex/sharelatex:with-texlive-full
# ...
```
:::

## Overleaf 配置

只要 Overleaf 容器运行起来，我们就可以访问 `/launchpad` 页面来初始化管理员用户。我们可以使用下面的命令创建第一个管理员：

```bash
docker exec sharelatex /bin/bash -c "cd /var/www/sharelatex; grunt user:create-admin --email=joe@example.com"
```

我们将得到一个带有 `token` 的网址，访问该网址就可以为管理员用户设置密码。

进入 Overleaf 前端界面后，可以进行创建工程、添加用户等操作，基本具有和 Overleaf 官方相同的功能。
