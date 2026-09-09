---
title: "CUDA"
date: 2021-12-03T10:42:58+08:00
weight: 150
---
# CUDA

CUDA 是一种由显卡厂商 NVIDIA 推出的通用并行计算架构，该架构使 GPU 能够解决复杂的计算问题，在深度学习等领域具有广泛的应用。一些主流的深度学习框架诸如 `PyTorch`、`TensorFlow` 等都实现了一些调用 GPU 训练神经网络的 API，而 Ubuntu 系统本身并没有安装或者默认启用 NVIDIA 官方显卡驱动，因此需要用户手动进行配置。

## 准备工作

- [官方文档](https://docs.nvidia.com/cuda/index.html)：务必认真阅读！CUDA 对于 Ubuntu 系统的版本、`gcc` 的版本、深度学习框架的版本等有严格要求，否则会出现不可预知的错误！

查看 GPU 信息：

```bash
lspci | grep -i nvidia
```

查看系统信息：

```bash
uname -m && cat /etc/*release
```

查看 `gcc` 版本：

```bash
gcc --version
```

如果没有安装 `gcc`，请安装 `gcc`。要注意，`gcc` 的版本需要按照官方文档提供的标准，一般来说默认安装即可。

```bash
sudo apt install gcc
```

确认当前正在使用的内核版本，并安装当前运行的内核的内核头文件和开发包：

```bash
uname -r
sudo apt install linux-headers-$(uname -r)
```

::: warning
**特别注意！**

确定内核版本后，不要随意更换内核或更新内核，否则可能会导致无法进入桌面系统。
:::

## 禁用 Nouveau

Ubuntu 系统默认使用 X.org X Server 的 Nouveau 作为显示驱动程序，这与 NVIDIA 的驱动有冲突，需要将其禁用。

首先输入以下命令，确认 Ubuntu 系统是否使用 Nouveau：

```bash
lsmod | grep nouveau
```

若有输出，则必须执行下面的步骤：

```bash
sudo gedit /etc/modprobe.d/blacklist-nouveau.conf
```

在新建的文件中写入：

```
blacklist nouveau
options nouveau modeset=0
```

然后重新生成内核：

```bash
sudo /sbin/mkinitrd
```

若在此时重启电脑，有些机器可能无法显示桌面，有些机器可能会以较低的分辨率显示桌面。

目前，Ubuntu 官方提供了第三方的 NVIDIA 显卡驱动下载，我们可以在开始菜单中选择“软件与更新”，找到“附加驱动”选项卡，选择来自 NVIDIA 官方的驱动。应用之后Ubuntu会自动下载，重启后系统会有很多明显的动画效果，说明安装成功。也可以通过下面的命令验证：

```bash
nvidia-smi
```

当然，也可以在 NVIDIA 官方网站下载适用于特定型号显卡的驱动，例如 GTX 系列。但是必须确保 Nouveau 成功禁用，否则安装失败率很高。

## 安装 CUDA

- [下载地址](https://developer.nvidia.com/zh-cn/cuda-downloads)

强烈推荐下载 `runfile` 类型的安装包，安装成功率高。`deb` 包可能在某些情况下会安装失败，不推荐作为首选安装方式。

如果当前系统之前安装过 CUDA，特别是安装过其他版本的 CUDA，一定要将残留卸载干净，确保不存在 CUDA。可以尝试下面的命令：

```bash
sudo apt- autoremove --purge cuda       # 清理 apt 包
sudo dpkg -l | grep cuda                # 清理 deb 包
```

接下来执行下载好的 `runfile` 文件：

```bash
sudo sh cuda_<version>_linux.run
```

如果因禁用 Nouveau 而没有显卡驱动，需要重启进入文本模式。

安装程序可能需要等待一段时间，然后接受许可协议（输入 `accept` 回车），接下来需要选择安装的内容：

- 如果没有安装显卡驱动，可以通过此安装包安装 NVIDIA 显卡驱动，但一般不推荐。
- CUDA Toolkit 必选，一般默认即可。
- 其余可选，Samples 可用于验证CUDA是否安装成功。

安装完成后，注意终端的提示信息。主要包括以下两个方面：

1. CUDA 默认安装在 `/usr/local/cuda` 下，它本质上是个软链接，实际安装位置为 `/usr/local/cuda-<version>`。例如 CUDA 10.0 的安装位置为 `/usr/local/cuda-10.0`。
2. 需要在 shell 的配置文件中添加两个环境变量，例如使用 zsh，安装 CUDA 11.0，则需要在 `~/.zshrc` 中加入：

```bash
export PATH=$PATH:/usr/local/cuda-11.0/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-11.0/lib64
```

输入下面的命令可以验证是否安装成功：

```bash
nvcc -V
```

## 安装 cuDNN

- [官方文档](https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html)
- [下载地址](https://developer.nvidia.com/rdp/cudnn-download)

cuDNN 的全称是 The NVIDIA CUDA Deep Neural Network Library，是专门用于深度神经网络的 GPU 加速库。在安装之前首先要验证 CUDA 是否安装成功，并且需要确认版本是否对应，官方网站和文档有详细的说明。

安装 cuDNN 的方式有多种，一种常用的方法为 `tar` 格式压缩包解压即可：

```bash
tar -xzvf cudnn-x.x-linux-x64-v8.x.x.x.tgz
sudo cp cuda/include/cudnn*.h /usr/local/cuda/include
sudo cp cuda/lib64/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
```

官方还为 Debian 系的系统提供了 `deb` 包的安装方式，注意这里分为 `Runtime` 版和 `Developer` 版，即运行库和开发库。如果只需要能够运行深度学习应用（例如模型训练和推断）只需要运行库即可，如果需要开发深度学习底层框架（例如使用 C 或 C++ 编写 GPU 并行加速程序）则需要开发库。

```bash
sudo dpkg -i libcudnn8_x.x.x-1+cudax.x_amd64.deb
```
