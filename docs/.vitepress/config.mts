// .vitepress/config.mts
import { defineConfig } from "vitepress";
import { defineTeekConfig } from "vitepress-theme-teek/config";
// import { sidebar } from "./sidebar";

// Teek 主题配置
const teekConfig = defineTeekConfig({
  nav: [
    { text: "首页", link: "/" },
    { text: "博客", link: "/blogs/", activeMatch: "/blogs/" },
    { text: "技术栈", link: "/tech-stack/", activeMatch: "/tech-stack/" },
    { text: "知识星球", link: "/knowledge-planet/", activeMatch: "/knowledge-planet/" },
  ],
  socialLinks: [{ icon: "github", link: "https://github.com/bowenEI" }],
});

// VitePress 配置
export default defineConfig({
  extends: teekConfig,
  lang: "zh-CN",
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
