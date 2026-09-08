---
title: "Python 包管理器"
weight: 150
---

# Python 包管理器

## pip

`pip` 是 **Python** 包管理工具，该工具提供了对 **Python** 包的查找、下载、安装、卸载的功能。

软件包也可以在 [PyPI](https://pypi.org/) 中找到。

目前最新的 **Python** 版本已经预装了 `pip`。可以通过如下命令查看 `pip` 是否已经安装：

```bash
pip --version
```

::: info
**当 Python2 与 Python3 共存**

对于 **Windows** 系统，Python2 和 Python3 可以共存。一般来说，在终端中输入 `python` 进入的是 Python2 环境，而输入 `python3` 才会进入 Python3 环境。

同理，输入 `pip` 命令实际上是对 Python2 环境的包进行管理，输入 `pip3` 命令才是对 Python3 环境的包进行管理。
:::

### 查看 Python 包

```bash
pip list
```

### 安装 Python 包

```bash
pip install numpy
pip install pandas matplotlib
```

### 删除 Python 包

```bash
pip uninstall numpy
```

### 分享环境

在很多使用 **Python** 编写的开源项目中我们能够看到 `requirements.txt` 这个文件，它能够方便其他开发者 `clone` 仓库后并且快速构建开发环境。

```bash
pip freeze > requirements.txt
```

上述命令生成了当前 **Python** 环境中所有的包。其他开发者想要快速构建当前项目的开发环境，只需要 `clone` 后运行如下命令：

```bash
pip install -r requirements.txt
```

## Conda

`Conda` 是一个开源的软件包管理系统和环境管理系统，用于安装多个版本的软件包及其依赖关系，并在它们之间轻松切换。`Conda` 是跨平台的，支持 Windows、MacOS 和 Linux。

### 安装 Conda

[Anaconda](https://www.anaconda.com/) 是一个开源的、跨平台的、包含了大量科学计算包的 `Conda` 虚拟环境。然而，它的安装包非常大，安装也非常慢。因此，不推荐初级用户安装。

[Miniconda](https://conda.io/en/latest/miniconda.html) 是 Anaconda 的轻量级版本，只包含一些最基本的 **Python** 包和包管理工具。我们非常推荐初级用户安装 Miniconda，安装速度快，不需要编译源码。安装完成后就会有一个 **Python** 环境，不需要额外安装 **Python** 环境。

`Conda` 环境最好只为当前用户安装。根据向导提示完成安装后，需要注意添加环境变量，这样操作系统就能够识别 `conda` 命令。

#### Windows 系统

```
C:\Users\<username>\miniconda3
C:\Users\<username>\miniconda3\Library\mingw-w64\bin
C:\Users\<username>\miniconda3\Library\usr\bin
C:\Users\<username>\miniconda3\Library\bin
C:\Users\<username>\miniconda3\Scripts
```

进入终端后，`Conda` 可能会提示是否运行 `conda init`。其意义在于进入终端以后默认进入 `Conda` 环境，如果是需要经常使用 `Conda` 环境建议运行。

```bash
conda init powershell   # 在 Windows 系统中，进入 powershell 终端默认进入 Conda 环境
conda init zsh          # 在 Linux 系统中，进入 zsh 终端默认进入 Conda 环境
```

### Conda 环境管理

#### 激活环境

```bash
conda activate pth  # 进入名为 pth 的环境
conda activate      # 默认进入 base 环境
conda deactivate    # 退出 conda 环境
```

#### 创建环境

```bash
conda create --name pth             # 创建一个名为 pth 的环境
conda create -n pth python=3.6      # 指定 python 的版本
conda create -n pth numpy           # 创建包含 numpy 包的环境
conda create -n pth --clone base    # pth 环境由 base 环境复制而来
```

#### 查看环境

```bash
conda env list
conda info --envs   # 等价命令
```

#### 删除环境

```bash
conda env remove -n pth
```

#### 分享环境

和 `pip` 类似，`Conda` 也提供了分享环境的方法。

```bash
conda env export > environment.yml
```

其他开发者只需要 `clone` 后运行如下命令：

```bash
conda env create -f environment.yml
```

### Conda 包管理

#### 查看 Conda 包

```bash
conda list
```

#### 安装 Conda 包

```bash
conda install -c conda-forge jupyterlab                                     # 安装 jupyterlab
conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch    # 安装 PyTorch
```

#### 删除 Conda 包

```bash
conda uninstall numpy
```
