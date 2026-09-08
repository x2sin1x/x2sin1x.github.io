// .vitepress/theme/index.ts
import type { Theme } from "vitepress";
import Teek from "vitepress-theme-teek";
import "vitepress-theme-teek/index.css";
import "./style.css";
import AbcScore from "./components/AbcScore.vue";
import NavDropdownLink from "./components/NavDropdownLink.vue";

export default {
  extends: Teek,
  enhanceApp({ app }) {
    app.component("AbcScore", AbcScore);
    // 可点击的导航下拉（右上角“技术栈”/“知识星球”）：
    // 单击标题进入总览页，hover 展开子菜单，配合 nav 中的 component 项使用
    app.component("NavDropdownLink", NavDropdownLink);
  },
} satisfies Theme;
