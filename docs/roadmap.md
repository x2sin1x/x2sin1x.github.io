---
title: 站点路线图
article: false
sidebar: false
---

# 站点路线图

本页是全站的「地图」：说明各板块的目录组织、每个目录收录的内容，以及新增页面时遵循的约定。无论你是想快速找到某类文章，还是想了解这个站点如何维护，都可以从这里开始。

## 站点总览

站点由「一个博客」与「两大笔记板块」构成，外加一组全站功能页：

| 板块 | 入口 | 内容定位 |
|------|------|----------|
| 首页 | [/](/) | 站点介绍与各板块导航卡片 |
| 博客 | [/posts/](/posts/) | 技术解读、论文精读与时事评论，按年份归档 |
| 技术栈 | [/tech-stack/](/tech-stack/) | 工具与技术的学习笔记、教程与速查手册 |
| 知识星球 | [/knowledge-planet/](/knowledge-planet/) | 各领域的系统性专栏笔记，按合集组织 |

## 顶层目录结构

```text
docs/
├── index.md            # 首页（hero + features 导航卡片）
├── roadmap.md          # 本页：站点结构与维护约定
├── posts/              # 博客文章（按年份分目录）
│   └── <year>/<slug>/  # 每篇文章一个目录，存放 index.md 与图片等资源
├── tech-stack/         # 技术栈笔记（按技术分目录）
├── knowledge-planet/   # 知识星球合集（按合集分目录）
├── @pages/             # 全站功能页源文件（归档、清单、分类、标签等）
├── public/             # 需要稳定根路径 URL 的静态资源（favicon 等）
└── .vitepress/         # 站点配置、主题扩展与构建产物（cache/、dist/ 不入库）
```

## 博客：`docs/posts/`

博客是站点的核心输出，文章按创建年份放在 `2021` 至 `2026` 的年份目录下，每篇文章使用独立的 `<slug>` 目录，文章的 `index.md` 与配图同目录存放。

内容范围不限于技术，涵盖论文精读、时事评论与个人感悟。所有文章自动进入归档页、清单页、分类与标签系统，无需手工登记。

## 技术栈：`docs/tech-stack/`

技术栈收录工具与技术的系统性学习笔记，每个技术一个子目录，子目录中的 `index.md` 是该技术的落地页（含学习目标、推荐阅读顺序与参考资料）。当前收录九个方向：

| 目录 | 内容 | 组织方式 |
|------|------|----------|
| [python](/tech-stack/python/) | Python 语言基础：列表、字典、函数、面向对象、多线程、正则等 | 按语法主题逐页讲解 |
| [git](/tech-stack/git/) | Git 版本控制：基础概念、常用命令与工作流 | 命令卡片式速查 |
| [linux](/tech-stack/linux/) | Linux 常用操作：文件、权限、Shell 等 | 按使用场景分页 |
| [mongo](/tech-stack/mongo/) | MongoDB 8.0 入门教程：`mongosh` 增删改查、聚合与 PyMongo | 任务管理示例贯穿全书 |
| [redis](/tech-stack/redis/) | Redis 8.10 入门教程：五大数据类型、键与过期、管道事务与 redis-py | 同一套任务管理示例，与 MongoDB 教程呼应 |
| [crawler](/tech-stack/crawler/) | Web 爬虫与逆向：从基础爬虫到 Web 逆向 | 基础与逆向两个部分 |
| [numpy](/tech-stack/numpy/) | NumPy 数组计算速查手册 | 用法速查为主 |
| [pandas](/tech-stack/pandas/) | Pandas 数据处理速查手册 | 用法速查为主 |
| [matplotlib](/tech-stack/matplotlib/) | Matplotlib 可视化笔记 | 图表类型组织 |

MongoDB 与 Redis 两个教程结构对齐：概念 → 基础操作 → 进阶特性 → Python API，每章末尾附小结和练习，正文标注内容基线版本与核对时间。

## 知识星球：`docs/knowledge-planet/`

知识星球按「合集」组织，每个合集是一个独立子目录，系统性地记录一个领域的完整学习过程。当前共 16 个合集，可按主题分为四组：

**计算机与数学**

- [算法分析与设计](/knowledge-planet/algorithm/)
- [凸优化](/knowledge-planet/convex-optimization/)
- [CS336：从零开始的语言模型](/knowledge-planet/cs336/)
- [深入理解 AI Infra](/knowledge-planet/ai-infra-book/)

**政治理论**

- [马克思主义](/knowledge-planet/marxism/)、[列宁主义](/knowledge-planet/leninism/)、[毛泽东思想](/knowledge-planet/maoism/)

**音乐理论**

- [乐理](/knowledge-planet/music-theory/)、[和声](/knowledge-planet/harmony/)、[曲式](/knowledge-planet/musical-form/)、[配器](/knowledge-planet/orchestration/)、[复调](/knowledge-planet/counterpoint/)

**其他**

- [金融学](/knowledge-planet/finance/)、[恋爱心理学](/knowledge-planet/love-psychology/)、[沈奕斐的社会学爱情思维课](/knowledge-planet/sociology-love/)

合集内部通常按章节顺序编号（如 `ch01`、`ch02`），配图与讲义随章节目录存放。

## 功能页：`docs/@pages/`

功能页是全站级的页面，源文件存放在 `docs/@pages/`，通过 frontmatter 中的 `permalink` 映射到根路径 URL：

| 页面 | URL | 说明 |
|------|-----|------|
| 归档 | [/archives](/archives) | 按时间线展示全部博客文章 |
| 清单 | [/articleOverview](/articleOverview) | 全部文章的结构化清单 |
| 分类 | [/posts/categories](/posts/categories) | 按分类浏览 |
| 标签 | [/posts/tags](/posts/tags) | 按标签浏览 |
| 登录 | [/login](/login) | 站点登录页 |
| 风险链接提示 | [/risk-link](/risk-link) | 外链跳转前的安全提示页 |

## 站点基础设施：`docs/.vitepress/`

- `config.mts`：站点配置，包括导航栏、本地搜索、侧边栏自动生成（基于 vitepress-plugin-sidebar-resolve，按 frontmatter `weight` 排序）与文章数据集的板块排除规则。
- `theme/`：主题扩展，如自定义导航下拉组件 `NavDropdownLink`、自定义面包屑等。
- `markdown/`：自定义 markdown 容器（`::: mermaid`、`::: abcjs` 乐谱渲染）。
- `cache/` 与 `dist/` 为构建产物，不入版本库。

## 新增内容的约定

新增页面时遵循以下约定，可以保证导航、侧边栏与文章数据集自动正确生成：

- **命名**：目录与英文文件名使用 kebab-case，合集与教程的落地页命名为 `index.md`。
- **frontmatter**：需要排序的页面写 `title`、`date` 与 `weight`；侧边栏顺序由 `weight` 决定，与文件名无关。
- **链接**：站内链接一律使用根相对路径（如 `/tech-stack/redis/`），图片与文章同目录存放。
- **板块隔离**：`tech-stack/` 与 `knowledge-planet/` 已从博客文章数据集中排除，新建板块若不希望出现在博客列表，需要同步更新 `fileContentLoaderIgnore` 配置。
- **校验**：改动配置、主题或新增板块后，运行 `pnpm typecheck` 与 `pnpm docs:build` 验证；涉及布局的改动还需在桌面与移动宽度下预览确认。
