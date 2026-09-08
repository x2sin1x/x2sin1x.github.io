// .vitepress/config.mts
import { defineConfig, type DefaultTheme } from "vitepress";
import { defineTeekConfig } from "vitepress-theme-teek/config";
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
 * 需要拆分侧边栏的板块（一级目录）：将这些目录下的一级子目录拆分为独立侧边栏，
 * 点开某个子目录页面时，左侧只显示当前子目录的目录结构
 */
const splitSectionKeys = ["/tech-stack/", "/knowledge-planet/"];

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
  vitePlugins: {
    // 将技术栈 / 知识星球排除在主题的文章数据集（vitepress-plugin-file-content-loader）之外：
    // 这些板块不是博客文章，此前靠 frontmatter 的 inHomePost: false 只能挡住首页文章列表渲染，
    // 但主题分页组件的 total 取的是未过滤的全量文章数，导致 /posts/ 出现大量空白分页。
    // 从数据源头排除后，分页 total 与实际文章数一致（侧边栏由 sidebar 插件单独生成，不受影响）。
    fileContentLoaderIgnore: ["**/tech-stack/**", "**/knowledge-planet/**"],
    sidebarOption: {
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
            result[stackKey] = mergeIndexIntoGroups([stack]);
          }

          // 板块落地页只显示各子目录入口，不再展开完整目录树
          result[key] = stacks.flatMap(
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
          );
        }
        return result;
      },
    },
  },
});

// VitePress 配置
export default defineConfig({
  extends: teekConfig,
  lang: "zh-CN",
  themeConfig: {
    nav: [
      { text: "首页", link: "/" },
      { text: "博客", link: "/posts/", activeMatch: "/posts/" },
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
            { text: "金融学", link: "/knowledge-planet/finance/" },
            { text: "马克思主义", link: "/knowledge-planet/marxism/" },
            { text: "列宁主义", link: "/knowledge-planet/leninism/" },
            { text: "毛泽东思想", link: "/knowledge-planet/maoism/" },
            { text: "乐理", link: "/knowledge-planet/music-theory/" },
            { text: "恋爱心理学", link: "/knowledge-planet/love-psychology/" },
            { text: "沈奕斐的社会学爱情思维课", link: "/knowledge-planet/sociology-love/" },
          ],
        },
      },
    ],
    socialLinks: [{ icon: "github", link: "https://github.com/bowenEI" }],
  },
  title: "Bowen's Home",
  description: "Bowen Zhou 的个人博客、技术笔记与学习资料",
  head: [
    // 站点图标，与 vp.teek.top 保持一致
    ["link", { rel: "icon", type: "image/svg+xml", href: "/teek-logo-mini.svg" }],
    ["link", { rel: "icon", type: "image/png", href: "/teek-logo-mini.png" }],
  ],
  cleanUrls: true,
  markdown: {
    // 启用数学公式渲染（行内 $...$ / $\int$，块级 $$...$$），依赖 markdown-it-mathjax3
    math: true,
    config(md) {
      // 将 ```abcjs 代码块渲染为 AbcScore 组件（乐谱）
      const componentFences: Record<string, string> = {
        abcjs: "AbcScore",
      };
      const defaultFence = md.renderer.rules.fence;
      md.renderer.rules.fence = (tokens, idx, options, env, self) => {
        const token = tokens[idx];
        if (!token) return "";

        const component = componentFences[token.info.trim()];
        if (!component) {
          return defaultFence
            ? defaultFence(tokens, idx, options, env, self)
            : self.renderToken(tokens, idx, options);
        }
        const source = Buffer.from(token.content, "utf8").toString("base64");
        return `<${component} source="${source}" />\n`;
      };
    },
  },
});
