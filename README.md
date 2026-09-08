# Bowen's Home

基于 [VitePress](https://vitepress.dev) 与 [vitepress-theme-teek](https://vp.teek.top) 构建的个人博客与知识库站点。

内容板块：

- **博客**（`/posts/`）：按年份组织的个人文章
- **技术栈**（`/tech-stack/`）：Python、Git、Linux、MongoDB、NumPy、Pandas、Matplotlib 等技术笔记
- **知识星球**（`/knowledge-planet/`）：算法、凸优化、金融学、马克思主义、列宁主义、毛泽东思想、乐理、恋爱心理学、社会学爱情思维课等学习资料

技术栈：VitePress · Vue 3 · TypeScript · pnpm · Teek 主题

## 网站结构

```text
.
├── docs/
│   ├── posts/                  # 博客文章，按 <year>/<slug>/index.md 组织
│   ├── tech-stack/             # 技术栈笔记（Python、Git、Linux、MongoDB、NumPy、Pandas、Matplotlib）
│   ├── knowledge-planet/       # 知识星球板块（算法、凸优化、金融学、马列毛、乐理、恋爱心理学等）
│   ├── @pages/                 # 分类 / 标签 / 归档 / 清单等功能页（frontmatter permalink 客户端重定向）
│   ├── public/                 # favicon、logo、静态 js（abcjs）等根路径资源
│   ├── assets/                 # 文章配图
│   ├── index.md                # 站点首页
│   └── .vitepress/
│       ├── config.mts          # 站点配置（导航、侧边栏、Markdown 渲染等）
│       └── theme/              # 自定义主题样式与组件
│           └── components/
│               ├── NavDropdownLink.vue   # 可点击 + hover 展开的导航下拉组件
│               └── AbcScore.vue          # ```abcjs 代码块渲染为乐谱的组件
├── package.json
├── pnpm-lock.yaml
└── tsconfig.json
```

## 功能实现

### 侧边栏定制（`docs/.vitepress/config.mts`）

基于 `vitepress-plugin-sidebar-resolve` 的 `sidebarResolved` 钩子做后处理：

- **weight 排序**：读取页面 frontmatter 中的 `weight` 字段（沿用旧 Hugo 站点约定），各层侧边栏条目按 `weight` 升序稳定排序，无 `weight` 的条目排在有 `weight` 的条目之后
- **博客板块两级结构**：将插件生成的 `<year>/<slug>/index.md` 三层结构压平为 `<year>` 分组 + 文章链接，年份倒序（最新在前）
- **板块拆分侧边栏**：`/tech-stack/`、`/knowledge-planet/` 下的一级子目录拆分为独立侧边栏，点开子目录页面时左侧只显示当前子目录结构
- **空分组裁剪**：递归剔除没有链接且没有子项的分组（如仅存放图片 / drawio 源文件的目录）
- **index 合并**：将目录下 `index.md` 条目的标题与链接合并到分组上，避免标题重复显示

### 自定义组件（`docs/.vitepress/theme/components/`）

- **NavDropdownLink**：导航栏下拉组件，单击标题进入总览页，hover 展开子菜单；功能页 permalink 仅在客户端重定向，因此 `activeMatch` 同时匹配 `@pages/` 源文件路径以保证高亮正确
- **AbcScore**：通过自定义 fence 渲染器将 ` ```abcjs ` 代码块渲染为可播放的乐谱（静态 abcjs 脚本位于 `docs/public/js/`）

### Markdown 能力

- **数学公式**：启用 MathJax3（`markdown-it-mathjax3`），支持行内 `$...$` 与块级 `$$...$$`
- **乐谱**：` ```abcjs ` 代码块

### 其他

- `cleanUrls: true`：生成无 `.html` 后缀的干净链接
- `fileContentLoaderIgnore`：将 `tech-stack/`、`knowledge-planet/` 排除在主题文章数据集之外，保证首页文章列表与分页 total 只统计真正的博客文章
- `lang: zh-CN`：中文站点

## 本地开发

环境要求：Node.js ≥ 20，[pnpm](https://pnpm.io)。

```bash
# 安装依赖（按 pnpm-lock.yaml 锁定版本）
pnpm install

# 启动本地开发服务器（热更新）
pnpm docs:dev

# TypeScript / Vue 静态检查
pnpm typecheck

# 生产构建
pnpm docs:build

# 本地预览生产构建
pnpm docs:preview
```

### 写作约定

- 新博客文章放在 `docs/posts/<year>/<slug>/index.md`
- frontmatter 中的 `weight` 字段控制侧边栏排序（越小越靠前）
- `tech-stack/`、`knowledge-planet/` 目录下的内容不进入博客文章数据集，各自通过 `index.md` 落地页组织
- 图片等站点级静态资源放 `docs/public/`，文章专属图片放在文章目录旁

## 部署方式（Netlify Git 集成）

站点使用根路径部署（`base: /`），配合 Netlify 默认子域名无需修改 VitePress 配置。

### 首次部署

1. 登录 [Netlify](https://app.netlify.com)，选择 **Add new site → Import an existing project → Deploy with GitHub**，关联本仓库
2. 构建配置：
   - **Build command**：`pnpm docs:build`
   - **Publish directory**：`docs/.vitepress/dist`
   - **环境变量**：`NODE_VERSION` = `20`（或 `22`）；Netlify 会根据 `pnpm-lock.yaml` 自动启用 pnpm
3. 开启 **Pretty URLs**：进入 **Site configuration → Build & deploy**，启用 Pretty URLs。站点开启了 `cleanUrls: true`，该开关保证 `/path.html` 形式的请求能正确重定向到干净链接，无需在仓库中添加 `_redirects` 文件
4. 部署完成后，在 **Site overview** 查看默认站点地址：`https://<site-name>.netlify.app`（可在 Site configuration → Change site name 中修改）。如需绑定自定义域名，在 **Domain management** 中添加即可

### 更新部署

推送到默认分支（`main`）即自动触发 Netlify 构建并发布，Pull Request 会生成 deploy preview 供预览。

## 参考文档

- [VitePress 官方文档](https://vitepress.dev)
- [vitepress-theme-teek 文档](https://vp.teek.top)
- [abcjs 乐谱记法](https://abcjs.net/abcjs-editor.html)
- [markdown-it-mathjax3](https://github.com/tandpfun/markdown-it-mathjax3)
- [Netlify 文档](https://docs.netlify.com)（Git 集成 / Pretty URLs）
