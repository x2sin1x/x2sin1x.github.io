---
title: "重装 Windows 系统和软件指南"
description: "从制作启动盘、系统配置到常用软件与开发环境安装，提供一份完整的 Windows 重装指南。"
date: 2025-10-27
categories:
  - Technique
tags:
  - 技术分享
# 精选文章：主题首页 topArticle 卡片读取 frontmatter 的 top 字段
top: true
---

# 重装 Windows 系统和软件指南

本文档旨在提供一个全面的指南，方便用户重装 Windows 系统并配置常用软件和开发环境。

## 制作启动盘

推荐使用 [Rufus](https://rufus.ie/) 制作启动盘。Github [下载地址](https://github.com/pbatard/rufus/releases)。

Microsoft 官方 Windows 系统镜像[下载地址](https://www.microsoft.com/zh-cn/software-download/windows11)。当前最新的系统版本为 25H2。

::: danger
需要注意，在 Rufus 中选择绕过至少 4GB RAM、安全启动和 TPM 2.0 检测，以确保系统能够顺利安装。
:::

## Windows 系统配置

### 激活

推荐使用[沧水的 KMS 服务](https://kms.cangshui.net/)激活 Windows 系统。激活脚本[下载地址](https://kms.cangshui.net/kms/KMS-Cangshui.net.bat)。

### 设置

- 启用开发者模式
- 用户账户控制等级设置为“从不通知”
- 关闭传递优化

### 永久禁用更新

注册表定位至

```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings
```

新建 `DWORD` 值 `FlightSettingsMaxPauseDays` 为 65535（0xFFFF），即最多可暂停更新 65535 天。然后在设置中即可发现选择暂停更新的时间更长。

### 右键菜单

使用经典 Win10 右键菜单：

```powershell
reg.exe add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /f /ve
```

使用 Win11 右键菜单：

```powershell
reg.exe delete "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /va /f
```

均须重启文件资源管理器生效。

### 系统字体

微软雅黑字体是一个**功勋卓著但廉颇老矣**的设计。它在模糊的屏幕时代解决了“看清”的问题，却在高清时代输给了“好看”。

使用 [DesktopOK](https://www.softwareok.com/?seite=Microsoft/DesktopOK) 可以定制系统字体。字体推荐更纱黑体（Sarasa Gothic），可以通过[微软应用商店](https://apps.microsoft.com/detail/9mw0m424ncz7?gl=CN&hl=zh-cn)下载。

> [更纱黑体这么多版本，要怎么选？ - 知乎](https://zhuanlan.zhihu.com/p/627059922)

系统字体可以使用 Sarasa UI SC，编程和终端字体通常使用等宽字体，包括 Sarasa Mono SC、Sarasa Term SC、Sarasa Fixed SC。

## 装机必备

|名称|描述|
| :---------------: | :---------------------------------------------------------------: |
|[VS Code](https://code.visualstudio.com/)|强大轻量级 IDE + Agent Coder|
|~~[Trae](https://www.trae.cn/)~~|字节跳动 Agent Coder|
|[WorkBuddy](https://copilot.tencent.com/work/)|腾讯出品小龙虾|
|[Microsoft Office](https://www.microsoft.com/zh-cn/microsoft-365/)|办公软件全家桶|
|[Office Tool Plus](https://otp.landian.vip/zh-cn/)|快速自定义安装 Office 软件|
|[Clash Verge Rev](https://www.clashverge.dev/)|基于 Clash Meta (Mihomo) 内核的 Clash 客户端|
|[FlClash](https://flclash.dev/)|基于 Clash Meta (Mihomo) 内核，采用 Flutter 构建的 Clash 客户端|
|[Notepad3](https://rizonesoft.com/downloads/notepad3/)|国产 Notepad++ 平替<br />|
|[SumatraPDF](https://www.sumatrapdfreader.org/free-pdf-reader)|轻量化 PDF 阅读器|
|~~[LocalSend](https://localsend.org/)~~|局域网文件传输|
|~~[Snipaste](https://www.snipaste.com/)~~|截图|
|~~[Pot](https://pot-app.com/)~~|全局翻译（已不再维护）|
|[Manggo](https://manggo.pylogmon.cn/)|Pot 的 Qt 重构版本|
|[思源笔记](https://b3log.org/siyuan/)|隐私优先的本地知识库|
|[Obsidian](https://obsidian.md/)|插件系统最为丰富的知识库|
|~~[7-Zip](https://www.7-zip.org/)~~|压缩|
|[NanaZip](https://nanazip.org/)|基于 7-Zip 且适配 Windows 11 的压缩软件|
|[Draw.io](https://app.diagrams.net/)|开源绘图|
|~~[Drawnix](https://drawnix.com/)~~|开源白板工具|
|[PotPlayer](https://potplayer.daum.net/)|全能视频播放器|
|[PowerToys](https://learn.microsoft.com/zh-cn/windows/powertoys/)|Windows 系统官方外挂|
|~~[uTools](https://www.u-tools.cn/)~~|功能丰富的插件应用生态|
|~~[OpenFiles](https://openfiles.pansysoft.app/)~~|~~开源万能格式文件查看器~~|
|~~[Allen Explorer](https://www.allenxiang.com/)~~|类 Chrome 的强大文件资源管理器|
|[Inkscape](https://inkscape.org/)|免费矢量图编辑器|

## 思源笔记

在[官网](https://b3log.org/siyuan/)下载安装包。推荐下载 `x86_64` 安装包，而不是微软商店版。这样比较方便在终端配置和使用 Siyuan CLI。

新建文档默认位置为 `Daily Notes` 笔记本，按年份和月份分类存放，文档名称为日期。

```go
/{{now | date "2006" }}/{{now | date "01"}}/{{now | date "2006-01-02"}}
```

## WSL

根据最新的 [Microsoft 官方 WSL 安装指南](https://learn.microsoft.com/zh-cn/windows/wsl/install)，首先在“控制面板 –> 程序 –> 启用或关闭 Windows 功能”中启用 Hyper-V。

重启后，在 PowerShell（管理员权限）中执行以下命令安装 WSL 和 Ubuntu 发行版：

```powershell
wsl --install -d Ubuntu
```

安装完成后，打开 Ubuntu 终端，设置用户名和密码。

更新软件包：

```bash
sudo apt update && sudo apt upgrade
```

### 终端美化

推荐使用 [Oh My Zsh](https://ohmyz.sh/) 美化终端。首先需要安装 Zsh：

```bash
sudo apt install zsh
```

设置 Zsh 为默认 shell：

```bash
chsh -s $(which zsh)
```

然后安装 Oh My Zsh：

1. 使用 curl 安装：

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

2. 使用 wget 安装：

```bash
sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"
```

安装 `zsh-syntax-highlighting` 插件以实现语法高亮：

```bash
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
${ZSH:-~/.oh-my-zsh}/plugins/zsh-syntax-highlighting
```

安装 `zsh-autosuggestions` 插件以实现命令自动补全：

```bash
git clone https://github.com/zsh-users/zsh-autosuggestions.git \
${ZSH:-~/.oh-my-zsh}/plugins/zsh-autosuggestions
```

编辑 `~/.zshrc` 文件，将它们都添加到插件列表中：

```bash
plugins=(git zsh-syntax-highlighting zsh-autosuggestions)
```

最后，重新加载 Zsh 配置：

```bash
source ~/.zshrc
```

### 网络

为了使 WSL 可以和 Windows 系统共享网络，需要将 WSL 的网络模式设置为桥接模式。在用户目录下创建或编辑 `.wslconfig` 文件，添加以下内容：

```ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
firewall=true
autoProxy=true
```

或者直接运行 WSL 设置的 GUI 程序，将网络模式修改为镜像即可。

### 访问 Windows 宿主文件系统

Windows C 盘挂载在 `/mnt/c`。因此，可以通过符号链接将 Windows 文件系统中的常用文件夹作为链接目标，例如：

```bash
ln -s /mnt/c/Users/<USER>/Downloads ~/downloads
```

## PowerShell

Windows 系统自带的 PowerShell 版本老旧，推荐安装最新的 [PowerShell 7](https://learn.microsoft.com/zh-cn/powershell/scripting/install/installing-powershell-on-windows)。

```powershell
winget install --id Microsoft.PowerShell --source winget
```

### 终端美化

安装完成后，再安装 [Oh My Posh](https://ohmyposh.dev/docs/installation/windows) 以美化 PowerShell 终端。

```powershell
winget install JanDeDobbeleer.OhMyPosh --source winget --scope user --force
```

创建配置文件：

```powershell
notepad $PROFILE
```

并在文件中添加以下内容：

```powershell
oh-my-posh init pwsh | Invoke-Expression
```

然后让配置生效：

```powershell
. $PROFILE
```

如果想要更改主题，使用 `--config` 参数指定主题配置文件即可。可以从 [Oh My Posh 主题库](https://ohmyposh.dev/docs/themes) 搜寻喜欢的主题。

```powershell
oh-my-posh init pwsh --config <THEME_NAME> | Invoke-Expression
```

### 系统代理

打开配置文件

```powershell
notepad $PROFILE
```

配置系统代理

```powershell
$env:HTTP_PROXY  = "http://127.0.0.1:7890"
$env:HTTPS_PROXY = "http://127.0.0.1:7890"
```

## Git

Windows 需要单独安装 [Git for Windows](https://git-scm.com/install/windows)，推荐使用 `winget` 进行安装：

```powershell
winget install --id Git.Git --source winget
```

Linux 发行版默认安装 Git。首先全局配置用户名和邮箱：

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

推荐使用 SSH 密钥进行身份验证。生成 SSH 密钥对：

```bash
ssh-keygen -t rsa -C "comment"
```

将公钥添加到 GitHub 账户中。`-C` 表示为 SSH 密钥添加备注。

```bash
cat ./.ssh/id_rsa.pub
```

### SSH 代理

由于通过 SSH 协议连接 Github 仓库不会走系统的 HTTP 代理，需要手动配置。编辑 `~/.ssh/config` 文件（若没有则新建）：

#### WSL

```bash
vim ~/.ssh/config
```

写入内容

```powershell
Host github.com
    HostName ssh.github.com
    Port 443
    User git
    # 如果你的 7890 是 SOCKS5 代理（Clash 等通常 7890 是混合端口或 HTTP，7891 是 SOCKS5，请按需修改）
    ProxyCommand nc -X 5 -x 127.0.0.1:7890 %h %p
    
    # 如果你的 7890 纯粹是 HTTP 代理，改用这行：
    ProxyCommand nc -X connect -x 127.0.0.1:7890 %h %p
```

#### Windows

```powershell
notepad ~/.ssh/config
```

写入内容

```
Host github.com
    HostName ssh.github.com
    Port 443
    User git
    ProxyCommand connect -S 127.0.0.1:7890 %h %p
```

最后，测试 SSH 连接是否正常

```bash
ssh -T git@github.com
```

::: danger
在 Windows 系统中，需要通过 Git Bash 来运行上述命令。这是因为它需要调用 `C:\Program Files\Git\mingw64\bin\connect.exe`。
:::

如果出现以下输出则说明配置成功，连接正常。

```
Hi USERNAME! You've successfully authenticated, but GitHub does not provide shell access.
```

## Agent

### Codex

OpenAI 官方推荐使用 `npm` 安装 [Codex CLI](https://developers.openai.com/codex/quickstart?setup=cli)。

```bash
npm i -g @openai/codex
```

如要通过 API Key 接入非 OpenAI 模型，配置 `~/.codex/auth.json`

```json
{
  "OPENAI_API_KEY": "<YOUR_API_KEY>"
}
```

配置 `~/.codex/config.toml`

```toml
model_provider = "<PROVIDER_NAME>"
model = "gpt-5.5"
model_reasoning_effort = "high"
disable_response_storage = true

[model_providers.<PROVIDER_NAME>]
name = "<PROVIDER_NAME>"
wire_api = "responses"
requires_openai_auth = false
base_url = "<PROVIDER_API_URL>"
```

此外，可以直接从微软应用商店安装 ChatGPT & Codex 桌面版，也可以从[官网](https://openai.com/zh-Hans-CN/index/codex-for-almost-everything/)下载安装程序。

### CC Switch

在使用 Codex 时，通常使用 [CC Switch](https://www.ccswitch.io/zh/) 统一管理 API 提供商比较方便。

但是在 Linux 或者 WSL 中，GUI 程序并不方便。目前 GitHub 已有 [CC-Switch CLI](https://github.com/SaladDay/cc-switch-cli) 实现了对终端更友好的 CLI 版本。

```bash
curl -fsSL https://github.com/SaladDay/cc-switch-cli/releases/latest/download/install.sh | bash
```

### OpenCode

[OpenCode](https://opencode.ai/) 官方推荐在 WSL 中安装 CLI，而不推荐在 Windows 中安装。

```bash
curl -fsSL https://opencode.ai/install | bash
```

### Pi

[Pi](https://pi.dev) 是践行了“**一切皆插件**”的极简 Coding Agent，理念是“让 Pi 适配你的工作流，而不是反过来”——默认只给模型 `read`、`write`、`edit`、`bash` 四个工具。

Linux & WSL

```bash
curl -fsSL https://pi.dev/install.sh | sh
```

Windows PowerShell

```powershell
powershell -c "irm https://pi.dev/install.ps1 | iex"
```

### Skills

可通过 `npx skills add` 命令从个人自用技能仓库安装技能。建议在项目级安装以确保 Skill 不会冗余占用上下文。

```bash
npx skills add git@gitee.com:bowenEI/myskills.git -a AGENT
```

## Python

### Conda

推荐使用 [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main) 作为 Python 包管理器。

#### WSL

```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

使用以下命令激活 Conda 的 `base` 环境：

```bash
source ~/miniconda3/bin/activate
```

使用以下命令激活使用 Conda 但不进入 `base` 环境：

```bash
source ~/miniconda3/etc/profile.d/conda.sh
```

如果希望每次打开终端时自动激活 Conda，可以在安装成功后的问询中选择 `yes`，或者手动执行以下命令：

```bash
conda init          # 对当前 shell 生效
conda init --all    # 对所有 shell 生效
```

#### Windows

```powershell
Invoke-WebRequest -Uri "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe" -OutFile ".\Miniconda3-latest-Windows-x86_64.exe"
```

### uv

[uv](https://docs.astral.sh/uv/) 是一个快速的 Python 包管理器，推荐使用它来安装 Python 包。

#### WSL

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows

一键安装脚本

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Windows 系统不会自带 Python 环境，因此可以通过 uv 安装一个用户级别的 Python 环境。

```powershell
uv python install 3.14 --default
```

## Node.js

[Node.js](https://nodejs.org/en/download) 是开源跨平台的 JS 运行时环境，可以用来创建 Web 应用、命令行工具和脚本。

### WSL

推荐使用 `nvm` 来安装和管理不同版本的 Node.js。

```bash
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.6/install.sh | bash

# in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"

# Download and install Node.js:
nvm install 24

# Verify the Node.js version:
node -v # Should print "v24.18.1".

# Verify npm version:
npm -v # Should print "11.16.0".
```

通常，安装后即为默认 `node` 版本。可以通过 `use` 命令在不同版本的 `node` 之间切换：

```bash
nvm use 24
```

WSL 可能在终端对话退出之后没有正确配置 `node` 和 `npm`。若出现了这个情况，使用如下命令修正默认别名：

```bash
nvm alias default v24.18.1
```

如果你想固定使用最新的 LTS，可以用这个命令：

```bash
nvm alias default lts/*
```

### Windows

直接在[官网](https://nodejs.org/en/download)下载长期稳定版 Node.js 的 `msi` 安装包安装。

::: warning
注意勾选 "Automatically install necessary tools"。
:::

也可以通过 Chocolatey 管理不同版本的 Node.js。

```powershell
powershell -c "irm https://community.chocolatey.org/install.ps1|iex"
```

安装最新版的 Node.js LTS：

```powershell
choco install nodejs --version="24.18.0"
```

## Go

Go 是 Google 支持的开源编程语言，非常适合用来写高性能后端。

访问 [Go 官方网站](https://golang.google.cn/dl/)下载安装包进行安装。Windows 系统直接下载 `.msi` 安装文件安装。

WSL 中的安装步骤如下：

1. 清理旧版本，并且将下载好的压缩包解压

```bash
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.26.5.linux-amd64.tar.gz
```

2. 配置 Go 环境变量，配置到 `$HOME/.zshrc`

```bash
export PATH=$PATH:/usr/local/go/bin
```

3. 配置通过 Go 安装的工具的环境变量，配置到 `$HOME/.zshrc`

```bash
export PATH="$PATH:$(go env GOPATH)/bin"
```

4. 重启终端或者通过 `source` 命令使环境变量生效。通过如下命令验证安装：

```bash
go version
```

---

还可以使用 [gvm](https://github.com/moovweb/gvm) 来安装和管理不同版本的 Go。

```bash
sudo apt-get install bison
zsh < <(curl -s -S -L https://raw.githubusercontent.com/moovweb/gvm/master/binscripts/gvm-installer)
```

然后通过 `gvm` 安装 Go 版本：

```bash
gvm install go1.4
gvm use go1.4 [--default]
```

### Hugo

[Hugo](https://gohugo.io/) 是一个流行的静态网站生成器，推荐使用它来搭建个人博客。Hugo 的安装需要先安装 Go 环境，当然使用 Debian 的包管理器可以自动安装 Go 的环境。

一般来说，需要安装 `extended` 版本。Linux / WSL 系统通过 APT 安装的 Hugo 已经包含了 `extended` 版本。

```bash
sudo apt install hugo
```

当然，也可以直接前往 [GitHub](https://github.com/gohugoio/hugo/releases) 发行版页面下载安装包。有些主题对于 Hugo 的版本有要求，建议安装最新版本。

Windows 系统可以通过 WinGet 安装。

```powershell
winget install Hugo.Hugo.Extended
```

## Tex

可以使用 [TeX Live](https://www.tug.org/texlive/) 作为 LaTeX 发行版。对于 Windows 系统来说，直接下载 [Windows 安装包](https://mirror.ctan.org/systems/texlive/tlnet/install-tl-windows.exe)即可。

但对于 Linux 系统来说，安装较为麻烦。通过 `apt` 安装较为方便，但版本可能较旧。

```bash
sudo apt install texlive-full
```

如果通过官方安装脚本安装，需要如下几个步骤：

1. 下载安装脚本

```bash
wget https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
# Or
curl -L -o install-tl-unx.tar.gz https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
```

2. 解压

```bash
zcat < install-tl-unx.tar.gz | tar xf -
```

3. 安装

```bash
cd install-tl-2*
sudo perl ./install-tl --no-interaction
```

4. 配置环境变量

根据偏好，可以在 `$HOME/.profile` 或 `$HOME/.bashrc` `$HOME/.zshrc` 中添加：

```bash
export PATH=/usr/local/texlive/2026/bin/x86_64-linux:$PATH
```

::: warning
注意确认安装路径。
:::

## Docker

推荐使用 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) 来管理 Docker 容器。安装完成后，可以通过 WSL 终端直接使用 Docker 命令。

::: danger
不推荐使用 Ubuntu Server 的安装方式在 WSL 中安装 Docker，因为这种方式需要额外配置 Docker 的守护进程，且不如 Docker Desktop 方便。
:::

## 编曲

- Cubase 专业 DAW（数字音频工作站）

  - Prism 音频转 MIDI 插件
  - Song Master Pro 音频分析
- Sibelius 专业打谱软件

  - NotePerformer 5 高质量替换音源

### 插件

- [VoiceMeeter Banana](https://vb-audio.com/Voicemeeter/banana.htm) 专业虚拟音频混音软件
- [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) 提供虚拟 MIDI 输入输出

### 音源

- [Pianoteq](https://www.modartt.com/pianoteq_overview) 物理建模钢琴音源
- [BBC Symphony Orchestra](https://www.spitfireaudio.com/en-us/collections/bbc-symphony-orchestra) 专业管弦音源
- ~~Keyscape 四巨头之钢琴音源~~
- Ample 系列民族乐器音源
