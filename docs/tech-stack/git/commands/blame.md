---
title: "blame 命令"
date: 2021-12-02T23:53:58+08:00
weight: 190
---

# blame 命令：追溯文件修改者

`git blame` 用于逐行标注文件中每一行内容最后是由谁、在哪次提交中修改的，常用于定位问题代码的来源。

查看整个文件的逐行修改记录：

```bash
git blame test.py
```

只查看指定行范围的记录（例如第 10 到 20 行）：

```bash
git blame -L 10,20 test.py
```

忽略空白符变化，让输出更干净：

```bash
git blame -w test.py
```

显示行的原始移动/复制来源（跨文件追踪）：

```bash
git blame -C test.py
```
