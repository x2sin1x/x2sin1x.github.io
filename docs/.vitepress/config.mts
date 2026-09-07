// .vitepress/config.mts
import { defineConfig } from "vitepress";
import { defineTeekConfig } from "vitepress-theme-teek/config";
// import { sidebar } from "./sidebar";

/**
 * 深度优先查找侧边栏树中第一个带 link 的条目
 */
function findFirstLink(item: any): string | undefined {
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

// Teek 主题配置
const teekConfig = defineTeekConfig({
  vitePlugins: {
    sidebarOption: {
      sidebarResolved: (sidebar) => {
        const result: Record<string, any[]> = {};
        for (const [key, value] of Object.entries(sidebar)) {
          if (!splitSectionKeys.includes(key)) {
            result[key] = value as any[];
            continue;
          }
          // 兼容两种生成结构：[{ text, items }] 包裹层 / 直接数组
          const items = value as any[];
          const stacks =
            items.length === 1 && !items[0].link && items[0].items?.length
              ? items[0].items
              : items;

          for (const stack of stacks) {
            // 分组项的 text 即子目录名（插件默认不取 md 标题），拼出侧边栏 key
            const stackKey = `${key}${stack.text}/`;
            if (!stack.items?.length) continue;
            result[stackKey] = [stack];
          }

          // 板块落地页只显示各子目录入口，不再展开完整目录树
          result[key] = stacks
            .map((stack) => {
              const stackKey = `${key}${stack.text}/`;
              if (!stack.items?.length) return undefined;
              // 优先用该子目录入口页（index.md / intro.md）的标题和链接，
              // 否则回退到目录下第一个页面
              const indexItem = (stack.items ?? []).find((i: any) =>
                /^(index|intro)$/.test(i.link?.slice(stackKey.length) ?? "")
              );
              return {
                text: indexItem?.text || stack.text,
                link: indexItem?.link || findFirstLink(stack),
              };
            })
            .filter(Boolean) as any[];
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
      { text: "技术栈", link: "/tech-stack/", activeMatch: "/tech-stack/" },
      { text: "知识星球", link: "/knowledge-planet/", activeMatch: "/knowledge-planet/" },
    ],
    socialLinks: [{ icon: "github", link: "https://github.com/bowenEI" }],
  },
  title: "Bowen's Home",
  description: "Bowen Zhou 的个人博客、技术笔记与学习资料",
  cleanUrls: true,
  markdown: {
    config(md) {
      // 将 ```abcjs 代码块渲染为 AbcScore 组件（乐谱）
      const componentFences: Record<string, string> = {
        abcjs: "AbcScore",
      };
      const defaultFence = md.renderer.rules.fence;
      md.renderer.rules.fence = (tokens, idx, options, env, self) => {
        const token = tokens[idx];
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
