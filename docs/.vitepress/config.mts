// .vitepress/config.mts
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { defineConfig, type DefaultTheme } from "vitepress";
import { defineTeekConfig } from "vitepress-theme-teek/config";
import { useRawContainer } from "./markdown/raw-container";
// import { sidebar } from "./sidebar";

/**
 * 深度优先查找侧边栏树中第一个带 link 的条目
 */
function findFirstLink(item: DefaultTheme.SidebarItem): string | undefined {
  if (item.link) return item.link;
  for (const child of item.items ?? []) {
    const link = findFirstLink(child);
    if (link) return link;
  }
  return undefined;
}

/**
 * 递归剔除无效的分组项：没有 link 且没有（或修剪后没有）子项的条目。
 * 插件会为每个子目录生成侧边栏分组，不检查目录内是否有 md 文件，
 * 导致仅存放图片 / drawio 源文件等资源的目录（如 images/、drawio/）变成空分组，这里统一过滤
 */
function pruneEmptyGroups(items: DefaultTheme.SidebarItem[]): DefaultTheme.SidebarItem[] {
  return items
    .map((item) => (item.items?.length ? { ...item, items: pruneEmptyGroups(item.items) } : item))
    .filter((item) => Boolean(item.link) || Boolean(item.items?.length));
}

/**
 * 递归合并分组与其目录下的 index.md 条目：
 * 插件为每个目录生成的分组标题取目录名（如 chapter1），而目录内的 index.md
 * 又会作为带标题的条目（如“第一章 xxx”）出现在分组里，导致标题重复显示。
 * 这里用 index.md 条目的标题替换分组标题，并让分组可跳转到该页，同时移除该条目
 */
function mergeIndexIntoGroups(items: DefaultTheme.SidebarItem[]): DefaultTheme.SidebarItem[] {
  return items.map((item) => {
    if (!item.items?.length) return item;
    const indexIdx = item.items.findIndex((child) => /(^|\/)index$/.test(child.link ?? ""));
    if (indexIdx === -1) return { ...item, items: mergeIndexIntoGroups(item.items) };
    const indexItem = item.items[indexIdx]!;
    const merged: DefaultTheme.SidebarItem = {
      ...item,
      items: mergeIndexIntoGroups(item.items.filter((_, i) => i !== indexIdx)),
    };
    if (indexItem.text) merged.text = indexItem.text;
    if (indexItem.link) merged.link = indexItem.link;
    return merged;
  });
}

/**
 * 递归为带子项的分组设置 collapsed: false，使分组可折叠（默认展开）。
 * VitePress 侧边栏分组仅在显式设置 collapsed（true/false）时才显示折叠按钮，
 * 省略时永远展开且无法收起
 */
function makeGroupsCollapsible(items: DefaultTheme.SidebarItem[]): DefaultTheme.SidebarItem[] {
  return items.map((item) =>
    item.items?.length
      ? { ...item, collapsed: false, items: makeGroupsCollapsible(item.items) }
      : item,
  );
}

/**
 * 扫描 docs 下所有 markdown 文件，构建「URL 路径 → 页面标题」映射，
 * 注入 themeConfig.breadcrumbTitles 供自定义面包屑组件
 * （theme/components/ArticleBreadcrumb.vue）显示层级标题。
 * 标题优先级：frontmatter title > 正文第一个一级标题 > 文件 / 目录名（去序号前缀）。
 * URL 为 cleanUrls 形式（站点未配置 base）：目录页为 /a/b/，普通页面为 /a/b/c
 */
function collectBreadcrumbTitles(): Record<string, string> {
  const titles: Record<string, string> = {};
  // 静态资源与构建产物目录不参与扫描；其余无 md 内容的目录（assets/ 等）自然不会产生条目
  const ignoredDirs = new Set([".vitepress", "public", "node_modules"]);
  const walk = (dir: string, prefix: string): void => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const abs = join(dir, entry.name);
      if (entry.isDirectory()) {
        if (ignoredDirs.has(entry.name)) continue;
        walk(abs, `${prefix}${entry.name}/`);
        continue;
      }
      if (!entry.name.endsWith(".md")) continue;

      const content = readFileSync(abs, "utf-8");
      // 先剥离 frontmatter，避免正文一级标题匹配受其干扰
      const frontmatterBlock = content.match(/^---\r?\n[\s\S]*?\r?\n---/)?.[0] ?? "";
      const body = content.slice(frontmatterBlock.length);
      const fmTitle = frontmatterBlock.match(/^title:\s*(.+?)\s*$/m)?.[1]?.replace(/^["']|["']$/g, "");
      const h1Title = body.match(/^#\s+(.+?)\s*$/m)?.[1];
      const name = entry.name.replace(/\.md$/, "").replace(/^\d+\./, "");

      const rel = `${prefix}${entry.name}`.replace(/\.md$/, "");
      const url = rel === "index" ? "/" : rel.endsWith("/index") ? `/${rel.slice(0, -"index".length)}` : `/${rel}`;
      titles[url] = fmTitle || h1Title || name;
    }
  };
  // prefix 从空串起步，叶子节点处统一拼出形如 /a/b 的 URL，避免根目录出现重复斜杠
  walk(docsDir, "");
  return titles;
}

/**
 * 需要拆分侧边栏的板块（一级目录）：将这些目录下的一级子目录拆分为独立侧边栏，
 * 点开某个子目录页面时，左侧只显示当前子目录的目录结构
 */
const splitSectionKeys = ["/tech-stack/", "/knowledge-planet/"];

/**
 * docs 目录：优先从仓库根目录推断，兼容直接以 docs/ 为工作目录启动 VitePress 的情况
 */
const docsDir = existsSync(join(process.cwd(), "docs", ".vitepress"))
  ? join(process.cwd(), "docs")
  : process.cwd();

/**
 * 读取页面 frontmatter 中的 weight 字段（沿用旧 Hugo 站点的排序约定），用于侧边栏排序。
 * 侧边栏插件 vitepress-plugin-sidebar-resolve 原生只支持 sidebarSort 字段，
 * 这里在 sidebarResolved 钩子里自行按 weight 排序，文件名与 URL 无需加入序号前缀
 */
const weightCache = new Map<string, number | undefined>();
const NO_WEIGHT = Number.MAX_SAFE_INTEGER;

function readPageWeight(link: string): number {
  // 兼容 cleanUrls 下带 / 不带 .md 的链接形式，目录链接回退到其 index.md
  const clean = link.replace(/\.html$/, "").replace(/\/+$/, "");
  const candidates = [join(docsDir, `${clean}.md`), join(docsDir, clean, "index.md")];
  for (const filePath of candidates) {
    if (weightCache.has(filePath)) {
      const cached = weightCache.get(filePath);
      if (cached !== undefined) return cached;
      continue;
    }
    let weight: number | undefined;
    try {
      const frontmatter = readFileSync(filePath, "utf-8").match(/^---\r?\n([\s\S]*?)\r?\n---/)?.[1];
      const raw = frontmatter?.match(/^weight:\s*(\d+)\s*$/m)?.[1];
      if (raw) weight = Number(raw);
    } catch {
      // 文件不存在或不可读时按无 weight 处理
    }
    weightCache.set(filePath, weight);
    if (weight !== undefined) return weight;
  }
  return NO_WEIGHT;
}

/**
 * 同层侧边栏条目按 weight 升序稳定排序，无 weight 的条目排在有 weight 的条目之后
 */
function sortByWeight(items: DefaultTheme.SidebarItem[]): DefaultTheme.SidebarItem[] {
  return items
    .map((item, index) => ({ item, index, weight: item.link ? readPageWeight(item.link) : NO_WEIGHT }))
    .sort((a, b) => a.weight - b.weight || a.index - b.index)
    .map(({ item }) => item);
}

/**
 * 递归按 weight 排序侧边栏树的每一层
 */
function sortTreeByWeight(items: DefaultTheme.SidebarItem[]): DefaultTheme.SidebarItem[] {
  return sortByWeight(
    items.map((item) => (item.items?.length ? { ...item, items: sortTreeByWeight(item.items) } : item))
  );
}

// 博客板块（一级目录）：侧边栏展示为 <year>/<slug> 两级结构
const postsKey = "/posts/";

/**
 * 博客侧边栏：将插件生成的 <year>/<slug>/index.md 三层结构，
 * 压平为 <year> 分组 + 文章链接的两级结构（年份倒序，最新在前）
 */
function buildPostsSidebar(items: DefaultTheme.SidebarItem[]): DefaultTheme.SidebarItem[] {
  const [wrapper] = items;
  // 兼容 [{ text, items }] 包裹层 / 直接数组两种生成结构；
  // 包裹层内除年份分组外还含落地页 index.md 条目（带 link），过滤掉
  const yearGroups = (wrapper && !wrapper.link ? wrapper.items : items) ?? [];
  return yearGroups
    .filter((year) => !year.link && year.items?.length)
    .map((year) => {
      const yearItem: DefaultTheme.SidebarItem = { collapsed: true };
      if (year.text) yearItem.text = year.text;
      yearItem.items = (year.items ?? [])
        .map((slug) => {
          // slug 分组内只有 index.md 一个页面，取其标题与链接；无子项时回退用 slug 名
          const post = slug.link ? slug : slug.items?.[0];
          const postItem: DefaultTheme.SidebarItem = {};
          const text = post?.text || slug.text;
          if (text) postItem.text = text;
          postItem.link = post?.link ?? `${postsKey}${year.text}/${slug.text}/`;
          return postItem;
        })
        .filter((post) => Boolean(post.link));
      return yearItem;
    })
    .reverse();
}

// Teek 主题配置
const teekConfig = defineTeekConfig({
  // 博主信息（首页 Banner 中的头像与昵称）：暂用站点 Logo 作为头像，
  // 替换为个人头像时把图片放入 docs/public/ 后修改 avatar 路径即可
  blogger: {
    name: "Nenifindo",
    avatar: "/nenifindo.png",
    shape: "circle",
  },
  // 关闭主题内置面包屑（仅显示文件 / 目录名且多数层级无链接），
  // 改由 theme/index.ts 通过 teek-article-analyze-before 插槽渲染自定义面包屑组件
  breadcrumb: {
    enabled: false,
  },
  // 自定义 markdown 渲染：必须放在 defineTeekConfig 的 markdown.config 里，
  // Teek 会先注册自身的 markdown 扩展（imgCard / shareCard / navCard / note 容器等），
  // 再回调本函数；若写在 defineConfig 的 markdown.config 会因 extends 合并时函数覆盖
  // 导致 Teek 的所有 markdown 扩展失效
  markdown: {
    config(md) {
      // ::: mermaid / ::: abcjs 容器（与主题 imgCard / note 等容器的 ::: 语法一致，
      // 冒号与容器名之间以空格分隔），
      // 替代原 ``` 围栏方案：容器内容原样提取后渲染为对应组件，
      // 组件内部按官方文档约定经 mermaid.run() 等渲染（见 theme/components）
      const containers: Record<string, string> = {
        mermaid: "Mermaid",
        abcjs: "AbcScore",
      };
      for (const [name, component] of Object.entries(containers)) {
        useRawContainer(md, name, (source) => {
          // 源码经 base64 编码内联，避免 HTML 转义与语法内容冲突
          const encoded = Buffer.from(source, "utf8").toString("base64");
          return `<${component} source="${encoded}" />\n`;
        });
      }
    },
  },
  vitePlugins: {
    // 将技术栈 / 知识星球排除在主题的文章数据集（vitepress-plugin-file-content-loader）之外：
    // 这些板块不是博客文章，此前靠 frontmatter 的 inHomePost: false 只能挡住首页文章列表渲染，
    // 但主题分页组件的 total 取的是未过滤的全量文章数，导致 /posts/ 出现大量空白分页。
    // 从数据源头排除后，分页 total 与实际文章数一致（侧边栏由 sidebar 插件单独生成，不受影响）。
    fileContentLoaderIgnore: ["**/tech-stack/**", "**/knowledge-planet/**"],
    sidebarOption: {
      // 文章封面等图片与 md 同目录存放，插件扫到非 .md 文件会告警且不会进侧边栏，
      // 这里按扩展名忽略常见静态资源，避免每次 dev/build 刷警告
      ignoreList: [/\.(jpe?g|png|gif|webp|svg|avif|ico|mp4|drawio|vsdx|ipynb|py|ya?ml|csv|xlsx|sh)$/i],
      sidebarResolved: (sidebar) => {
        if (Array.isArray(sidebar)) return sidebar;

        const result: DefaultTheme.SidebarMulti = {};
        for (const [key, value] of Object.entries(sidebar)) {
          // 兼容两种生成结构：[{ text, items }] 包裹层 / 直接数组，
          // 并剔除无 md 内容的空分组（如 images/、drawio/ 等资源目录）
          const items = pruneEmptyGroups(Array.isArray(value) ? value : value.items);
          if (key === postsKey) {
            // 博客板块：恢复侧边栏，按 <year>/<slug> 结构展示
            result[key] = buildPostsSidebar(items);
            continue;
          }
          if (!splitSectionKeys.includes(key)) {
            result[key] = items;
            continue;
          }
          const [rootItem] = items;
          const stacks =
            items.length === 1 &&
            rootItem &&
            !rootItem.link &&
            rootItem.items?.length
              ? rootItem.items
              : items;

          for (const stack of stacks) {
            // 分组项的 text 即子目录名（插件默认不取 md 标题），拼出侧边栏 key
            const stackKey = `${key}${stack.text}/`;
            if (!stack.items?.length) continue;
            result[stackKey] = makeGroupsCollapsible(sortTreeByWeight(mergeIndexIntoGroups([stack])));
          }

          // 板块落地页只显示各子目录入口，不再展开完整目录树（按各子目录 index.md 的 weight 排序）
          result[key] = sortByWeight(
            stacks.flatMap(
            (stack): DefaultTheme.SidebarItem[] => {
              const stackKey = `${key}${stack.text}/`;
              if (!stack.items?.length) return [];
              // 优先用该子目录入口页（index.md / intro.md）的标题和链接，
              // 否则回退到目录下第一个页面
              const indexItem = (stack.items ?? []).find((item) =>
                /^(index|intro)$/.test(item.link?.slice(stackKey.length) ?? "")
              );
              const text = indexItem?.text || stack.text;
              const link = indexItem?.link || findFirstLink(stack);
              const sidebarItem: DefaultTheme.SidebarItem = {};
              if (text) sidebarItem.text = text;
              if (link) sidebarItem.link = link;
              return [sidebarItem];
            }
          ));
        }
        return result;
      },
    },
  },
});

// 全站「URL → 标题」映射（见 collectBreadcrumbTitles），供自定义面包屑组件显示层级标题；
// 以变量展开方式合并进 themeConfig，避免字面量未知键触发 VitePress 类型检查报错
const breadcrumbTitleData = { breadcrumbTitles: collectBreadcrumbTitles() };

// VitePress 配置
export default defineConfig({
  extends: teekConfig,
  lang: "zh-CN",
  themeConfig: {
    nav: [
      { text: "首页", link: "/" },
      // “博客”使用自定义 NavDropdownLink 组件（见 theme/index.ts）：
      // 单击标题进入博客总览页，hover 展开功能页子菜单。
      // 功能页 permalink 定义在 docs/@pages/ 下的 frontmatter 中；由于 permalink 仅在客户端重定向，
      // activeMatch 需同时匹配 @pages 源文件路径，才能在功能页上正确高亮
      {
        component: "NavDropdownLink",
        props: {
          text: "博客",
          link: "/posts/",
          activeMatch: "/posts/",
          items: [
            { text: "归档", link: "/archives", activeMatch: "^/(archives|@pages/archivesPage)" },
            { text: "清单", link: "/articleOverview", activeMatch: "^/(articleOverview|@pages/articleOverviewPage)" },
          ],
        },
      },
      // “技术栈”/“知识星球”使用自定义 NavDropdownLink 组件（见 theme/index.ts）：
      // 单击标题进入总览页，hover 展开子菜单（不再单独放“总览”项）
      {
        component: "NavDropdownLink",
        props: {
          text: "技术栈",
          link: "/tech-stack/",
          activeMatch: "/tech-stack/",
          items: [
            { text: "Python", link: "/tech-stack/python/" },
            { text: "Git", link: "/tech-stack/git/" },
            { text: "Linux", link: "/tech-stack/linux/" },
            { text: "MongoDB", link: "/tech-stack/mongo/" },
            { text: "爬虫与逆向", link: "/tech-stack/crawler/" },
            { text: "NumPy", link: "/tech-stack/numpy/" },
            { text: "Pandas", link: "/tech-stack/pandas/" },
            { text: "Matplotlib", link: "/tech-stack/matplotlib/" },
          ],
        },
      },
      {
        component: "NavDropdownLink",
        props: {
          text: "知识星球",
          link: "/knowledge-planet/",
          activeMatch: "/knowledge-planet/",
          items: [
            { text: "算法分析与设计", link: "/knowledge-planet/algorithm/" },
            { text: "凸优化", link: "/knowledge-planet/convex-optimization/" },
            { text: "CS336：从零开始的语言模型", link: "/knowledge-planet/cs336/" },
            { text: "金融学", link: "/knowledge-planet/finance/" },
            { text: "马克思主义", link: "/knowledge-planet/marxism/" },
            { text: "列宁主义", link: "/knowledge-planet/leninism/" },
            { text: "毛泽东思想", link: "/knowledge-planet/maoism/" },
            { text: "乐理", link: "/knowledge-planet/music-theory/" },
            { text: "和声", link: "/knowledge-planet/harmony/" },
            { text: "曲式", link: "/knowledge-planet/musical-form/" },
            { text: "配器", link: "/knowledge-planet/orchestration/" },
            { text: "复调", link: "/knowledge-planet/counterpoint/" },
            { text: "恋爱心理学", link: "/knowledge-planet/love-psychology/" },
            { text: "沈奕斐的社会学爱情思维课", link: "/knowledge-planet/sociology-love/" },
          ],
        },
      },
    ],
    socialLinks: [{ icon: "github", link: "https://github.com/bowenEI" }],
    // 内置本地搜索（基于 MiniSearch，构建时索引全站文本，无需外部服务）。
    // Teek 主题继承默认主题 Layout 并已适配 VPNavBarSearch 样式，开箱即用
    search: {
      provider: "local",
      options: {
        locales: {
          // 本站未启用 i18n，全部页面属于 root locale，这里汉化搜索 UI 文案
          root: {
            translations: {
              button: { buttonText: "搜索文章", buttonAriaLabel: "搜索文章" },
              modal: {
                noResultsText: "未找到相关结果",
                resetButtonTitle: "清除查询条件",
                footer: { selectText: "选择", navigateText: "切换", closeText: "关闭" },
              },
            },
          },
        },
      },
    },
    // 导航栏左上角标题前显示站点图标（Nenifindo.svg，与 favicon 同源）
    logo: "/favicon.svg",
    ...breadcrumbTitleData,
  },
  title: "Nenifindo's Home",
  description: "Nenifindo 的个人博客、技术笔记与学习资料",
  head: [
    // 站点图标：Nenifindo.svg（源文件在仓库根目录，副本发布到 /favicon.svg）
    ["link", { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }],
  ],
  cleanUrls: true,
  markdown: {
    // 启用数学公式渲染（行内 $...$ / $\int$，块级 $$...$$），依赖 markdown-it-mathjax3
    math: true,
  },
});
