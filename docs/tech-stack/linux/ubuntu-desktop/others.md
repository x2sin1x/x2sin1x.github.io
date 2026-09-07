---
inHomePost: false
title: "其他注意事项"
---

# 其他注意事项

## 视频编解码器

部分系统的 Firefox 浏览器可能无法播放部分视频，是因为缺少了编解码器。执行下面的命令安装即可：

```bash
sudo apt install ffmpeg
```

## <span name="boot-repair">引导修复</span>

U 盘启动，选择试用 Ubuntu。进入系统后执行下面的命令：

```bash
sudo add-apt-repository ppa:yannubuntu/boot-repair && sudo apt update   # 添加软件源
sudo apt install boot-repair                                            # 安装 boot-repair
boot-repair                                                             # 运行 boot-repair
```

然后选择默认修复，即可解决大部分引导丢失问题。

## 解决双系统时间不统一的问题

不少人在安装 Windows 和 Ubuntu 双系统的电脑后都会发现一个奇妙的小问题：在 Ubuntu 系统中重启进入 Windows 系统，会发现时间整整慢了 8 小时；而在 Windows 系统中重启进入 Ubuntu 系统，会发现时间整整快了 8 小时。

原因在于 Windows 认为 BIOS 时间是本地时间，Ubuntu 认为 BIOS 时间是 UTC（Universal Time Coordinated）时间，是由国际无线电咨询委员会规定和推荐，并由国际时间局（BIH）负责保持的以秒为基础的时间标度。UTC 相当于本初子午线（即经度 0 度）上的平均太阳时，过去曾用格林威治平均时（GMT）来表示。北京时间比 UTC 时间早 8 小时，因此 Ubuntu 认为实际的时间应该是主板上硬件的时间加上当前所在时区（东 8 区）。

在 Ubuntu 16.04 之后，时间改成了由 `timedatectl` 来管理。因此需要执行依次执行如下命令：

```bash
sudo apt update
timedatectl set-local-rtc 1 --adjust-system-clock   # 禁用 Ubuntu 的 UTC
sudo apt install ntpdate
sudo ntpdate time.windows.com                       # 使用 Windows 的服务器
sudo hwclock --localtime --systohc                  # 将本地时间更新到硬件上
```
