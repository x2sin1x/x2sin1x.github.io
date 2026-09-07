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
 * 需要拆分侧边栏的板块（一级目录）：将这些目录下的一级子目录拆分为独立侧边栏，
 * 点开某个子目录页面时，左侧只显示当前子目录的目录结构
 */
const splitSectionKeys = ["/tech-stack/", "/knowledge-planet/"];

// 不展示侧边栏的板块（一级目录）：博客文章按时间流浏览，无需目录树
const hideSidebarKeys = ["/blogs/"];

// Teek 主题配置
const teekConfig = defineTeekConfig({
  vitePlugins: {
    sidebarOption: {
      sidebarResolved: (sidebar) => {
        if (Array.isArray(sidebar)) return sidebar;

        const result: DefaultTheme.SidebarMulti = {};
        for (const [key, value] of Object.entries(sidebar)) {
          if (hideSidebarKeys.includes(key)) {
            // 置空以隐藏该板块的侧边栏
            result[key] = [];
            continue;
          }
          if (!splitSectionKeys.includes(key)) {
            result[key] = value;
            continue;
          }
          // 兼容两种生成结构：[{ text, items }] 包裹层 / 直接数组
          const items = Array.isArray(value) ? value : value.items;
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
            result[stackKey] = [stack];
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
      { text: "博客", link: "/blogs/", activeMatch: "/blogs/" },
      {
        text: "技术栈",
        activeMatch: "/tech-stack/",
        items: [
          { text: "总览", link: "/tech-stack/" },
          { text: "Python", link: "/tech-stack/python/" },
          { text: "Git", link: "/tech-stack/git/" },
          { text: "Linux", link: "/tech-stack/linux/" },
          { text: "MongoDB", link: "/tech-stack/mongo/" },
          { text: "NumPy", link: "/tech-stack/numpy/" },
          { text: "Pandas", link: "/tech-stack/pandas/" },
          { text: "Matplotlib", link: "/tech-stack/matplotlib/" },
        ],
      },
      {
        text: "知识星球",
        activeMatch: "/knowledge-planet/",
        items: [
          { text: "总览", link: "/knowledge-planet/" },
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
    ],
    socialLinks: [{ icon: "github", link: "https://github.com/bowenEI" }],
  },
  title: "Bowen's Home",
  description: "Bowen Zhou 的个人博客、技术笔记与学习资料",
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
