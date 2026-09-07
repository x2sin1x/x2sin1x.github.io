// .vitepress/config.mts
import { defineConfig } from "vitepress";
import { defineTeekConfig } from "vitepress-theme-teek/config";

// Teek 主题配置
const teekConfig = defineTeekConfig({
  nav: [
    { text: "首页", link: "/" },
    { text: "Markdown 示例", link: "/markdown-examples" },
  ],
  sidebar: [
    {
      text: "示例",
      items: [
        { text: "Markdown 示例", link: "/markdown-examples" },
        { text: "运行时 API 示例", link: "/api-examples" },
      ],
    },
  ],
  socialLinks: [{ icon: "github", link: "https://github.com/Kele-Bingtang/vitepress-theme-teek" }],
});

// VitePress 配置
export default defineConfig({
  extends: teekConfig,
  title: "My Awesome Project",
  description: "A VitePress Site",
});
