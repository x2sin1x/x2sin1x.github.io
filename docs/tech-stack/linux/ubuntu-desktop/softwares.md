---
inHomePost: false
title: "必备软件"
---

# 必备软件

## Visual Studio Code

- [官方网站](https://code.visualstudio.com/)

### 通过 deb 包安装

下载 `deb` 安装文件，执行：

```bash
sudo dpkg -i <code-installer>.deb
```

### 通过 snap 安装

```bash
sudo snap install code --classic
```

## PyCharm & IntelliJ IDEA

PyCharm 和 IntelliJ IDEA 分别是 JetBrains 公司推出的 Python 和 Java 语言的强大 IDE。

- [PyCharm](https://www.jetbrains.com/pycharm/)
- [IntelliJ IDEA](https://www.jetbrains.com/idea/)

### 通过官方网站安装

下载的文件为 `tar.gz` 格式的压缩文件，使用如下命令解压。

```bash
tar -xzvf <pycharm-community>.tar.gz
tar -xzvf <idea-community>.tar.gz
```

解压后执行文件夹下的 `sh` 文件就可以运行软件，初次使用需要同意相关协议并进行配置。

```bash
sh <pycharm-community>/pycharm.sh
sh <ieda-community>/idea.sh
```

可以在设置中手动添加快捷方式图标到开始菜单。

### 通过 snap 安装

```bash
sudo snap install pycharm-community --classic
sudo sanp install idea-community --classic
```

## Typora

- [官方网站](https://www.typora.io/)

### 通过官网安装

```bash
# or run:
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys BA300B7755AFCFAE
wget -qO - https://typora.io/linux/public-key.asc | sudo apt-key add -

# add Typora's repository
sudo add-apt-repository 'deb https://typora.io/linux ./'
sudo apt update

# install typora
sudo apt install typora
```

国内访问非常慢，因此推荐 [Gitee](https://gitee.com/typora-mirror/Typora-Mirror/releases) 的镜像。

### 通过 snap 安装

```bash
sudo snap install typora
```

### Typora 主题推荐

- [OneDark](https://github.com/sweatran/typora-onedark-theme)
- [Github Night](https://github.com/kinoute/typora-github-night-theme)
- [Typora Notion Theme](https://github.com/adrian-fuertes/typora-notion-theme)

## 代理客户端

### Qv2ray

- [官方网站](https://qv2ray.net/)
- [仓库地址](https://github.com/Qv2ray/Qv2ray/releases)

在 Ubuntu 上使用代理服务器，Qv2ray 是一个很好的选择，它开源且提供友好的交互界面。搭建 Qv2ray 的工作环境总的来说分为两步：下载 Qv2ray 客户端；配置 v2ray 核心。

#### 下载 Qv2ray 客户端

官方网站提供了 Qv2ray 客户端的多种下载方式，前文也提供了 Qv2ray 客户端所在的 Github 下载地址。推荐下载 `AppImage` 格式的文件，它是免安装的独立可执行文件，基于 Qt 框架开发，具有很好的跨平台性。此外，Ubuntu 系统还可以通过 snap 应用商店搜索直接安装，或者和以下命令等价：

```bash
sudo snap install qv2ray
```

客户端的设置保持默认即可，完全适用于一般使用。

#### 配置 v2ray 核心

- [v2ray-core](https://github.com/v2fly/v2ray-core/releases)

v2ray 核心建议在 Github 上搜索，我们也提供了一个 Github 下载地址，要以实际开发和维护的仓库为准。克隆或下载后，将之放在用户文件夹下，然后打开 Qv2ray 客户端，在首选项中配置 v2ray 核心的路径以及可执行文件的地址，例如：

```bash
/home/username/vcore/v2ray      # 可执行文件路径
/home/username/vcore            # v2ray 路径
```

提供可执行权限：

```bash
sudo chmod +x /home/username/vcore/v2ray
sudo chmod +x /home/username/vcore/v2ctl
```

最后点击软件下方的验证按钮，一般没有问题都会验证通过。如果验证没有通过，可能的原因是 v2ray 核心文件的版本和客户端不匹配。

### v2rayA

- [官方网站](https://v2raya.org/)
- [仓库地址](https://github.com/v2rayA/v2rayA)

v2rayA 是一个易用而强大的，专注于 Linux 的 v2ray 客户端。其安装和配置相对而言更加方便快捷。

#### 安装 v2ray 内核

使用 [fhs-install-v2ray](https://github.com/v2fly/fhs-install-v2ray) 仓库的一件安装脚本：

```bash
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)
```

#### 安装 v2rayA

添加公钥

```bash
wget -qO - https://apt.v2raya.mzz.pub/key/public-key.asc | sudo tee /etc/apt/trusted.gpg.d/v2raya.asc
```

添加 v2rayA 软件源

```bash
echo "deb https://apt.v2raya.mzz.pub/ v2raya main" | sudo tee /etc/apt/sources.list.d/v2raya.list
sudo apt update
```

安装 v2rayA
```bash
sudo apt install v2raya
```

#### v2rayA 配置

启动 v2rayA

```bash
sudo systemctl start v2raya.service
```

设置开机自动启动

```bash
sudo systemctl enable v2raya.service
```

## QQ & 微信

目前在 Ubuntu/Debian 系统上使用 QQ 和微信最好的方法是使用 `wine` 容器。`wine` 容器相当于一个虚拟机，可以模拟 Windows 环境。

- [仓库地址](https://github.com/wszqkzqk/deepin-wine-ubuntu)
- [QQ](https://gitee.com/wszqkzqk/deepin-wine-containers-for-ubuntu/raw/master/deepin.com.qq.im_9.1.8deepin0_i386.deb)
- [微信](https://gitee.com/wszqkzqk/deepin-wine-containers-for-ubuntu/raw/master/deepin.com.wechat_2.6.8.65deepin0_i386.deb)

首先需要克隆该仓库，进入仓库文件夹后，执行安装脚本安装 `deepin-wine` 容器环境。

```bash
git clone https://github.com/wszqkzqk/deepin-wine-ubuntu.git
git clone https://gitee.com/wszqkzqk/deepin-wine-for-ubuntu.git   # gitee 仓库
sudo sh ./install.sh                                              # 需要授予可执行权限
```

安装好 `deepin-wine` 容器环境后，下载 QQ 和微信对应的 `deb` 安装包，执行如下安装命令安装即可：

```bash
sudo dpkg -i deepin.com.qq.im_9.1.8deepin0_i386.deb
sudo dpkg -i deepin.com.wechat_2.6.8.65deepin0_i386.deb
```

## LateX

**Ubuntu** 系统中最好用的 $\LaTeX$ 文档编辑器是 [Texmaker](https://www.xm1math.net/texmaker/index.html)。要特别注意的是，强烈推荐在官网下载，而不要使用 `apt install texmaker` 的方法安装。因为 `apt` 安装的 Texmaker 会附带 `texlive` 的很多东西，不仅安装时间长，而且和系统字体有冲突，还难以卸载。

## Nemo

Nemo 是 Ubuntu 更高级的文件资源管理器，具有很多更加方便的功能，非常推荐安装。

```bash
sudo apt install nemo
```

安装完成后，可以设置默认的文件资源管理器为 Nemo，与此同时，禁用 Nautilus。

```bash
xdg-mime default nemo.desktop inode/directory application/x-gnome-saved-search
gsettings set org.gnome.desktop.background show-desktop-icons false
gsettings set org.nemo.desktop show-desktop-icons true
```

## gnome 扩展

gnome 为 Ubuntu 提供了更友好的桌面环境，特别是 gnome-shell-extensions。

```bash
sudo apt install gnome-shell-extensions
```

安装完成后，我们可以看到它已经预装了一些扩展，可以定制我们的桌面。例如，使用 Desktop Icon 可以设置桌面是否显示应用和文件图标。

我们可以浏览[官方网站](https://extensions.gnome.org/)安装自己需要的插件。具体的安装方法是安装相应的浏览器插件，然后勾选需要的插件，就可以自动下载完成安装。

下面的一些插件值得推荐：

- [Clipboard Indicator](https://extensions.gnome.org/extension/779/clipboard-indicator/)：保持剪贴板历史，方便复制粘贴。
- [Screenshot Tool](https://extensions.gnome.org/extension/1112/screenshot-tool/)：屏幕截图。
- [Dash to Dock](https://extensions.gnome.org/extension/307/dash-to-dock/)：类似于 Windows 系统的任务栏，可以自由定制。
