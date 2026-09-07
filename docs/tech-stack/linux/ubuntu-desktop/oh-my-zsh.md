---
title: "终端美化"
---

# 终端美化

## zsh

`zsh`，被誉为终极 Shell。

```bash
sudo apt install zsh
```

## oh-my-zsh

- [官方网站](https://ohmyz.sh/)
- [官方仓库](https://github.com/ohmyzsh/ohmyzsh)

```bash
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"			    # 通过 curl 命令安装
sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"	# 通过 wget 命令安装
```

速度慢可以在国内 [GitClone](https://www.gitclone.com/) 平台搜索相应仓库克隆，然后执行安装脚本：

```bash
git clone https://gitclone.com/github.com/ohmyzsh/ohmyzsh
sh oh-my-zsh/tools/install.sh
```

## 主题

编辑 `zsh` 配置脚本：

```bash
gedit ~/.zshrc
```

在文件中找到：

```
ZSH_THEME="robbyrussell"
```

改为自己想要的主题：

```
ZSH_THEME="ys"
```

在 Github 上浏览所有的[主题](https://github.com/ohmyzsh/ohmyzsh/wiki/Themes)。

## 插件

安装插件的一般方法：在 Github 上搜索插件名称，克隆或者打包下载下来之后将之移动到 `~/.oh-my-zsh/plugins/` 下，编辑 `zsh` 配置脚本：

```
mv <plugin> ~/.oh-my-zsh/plugins/
gedit ~/.zshrc
```

在文件中找到：

```
plugins=(
  git
  bundler
  dotenv
  osx
  rake
  rbenv
  ruby
)
```

在其中添加相应插件即可。

### zsh-syntax-highlighting

- [仓库链接](https://github.com/zsh-users/zsh-syntax-highlighting)

```
git clone https://github.com/zsh-users/zsh-syntax-highlighting
git clone https://gitclone.com/github.com/zsh-users/zsh-syntax-highlighting
```

一个智能高亮插件，当命令 Shell 无法解析时，显示红色，否则显示绿色。

### zsh-autosuggestions

- [仓库链接](https://github.com/zsh-users/zsh-autosuggestions)

```
git clone https://github.com/zsh-users/zsh-autosuggestions
git clone https://gitclone.com/github.com/zsh-users/zsh-autosuggestions
```

一个命令提示插件，会根据当前输入的内容猜测可能要执行的命令（基于历史记录），然后按方向右键即可立刻补全。

### autojump

- [仓库链接](https://github.com/wting/autojump)

autojump 通过数据库记录本地文件目录结构，并且使用及其简单的命令就可以快速切换文件夹。

```bash
git clone https://github.com/wting/autojump
cd autojump
./install.py
```

具体使用方法详见仓库说明。

## 设置默认终端

我们可以设置 `zsh` 为默认终端。

```bash
sudo chsh -s $(which zsh)
```

设置完成后，需要注销当前用户。登录后，使用下面的命令验证是否成功修改：

```bash
echo $SHELL
```

如果需要将默认终端切换回 `bash`，执行下面的命令：

```bash
sudo chsh -s $(which bash)
```
