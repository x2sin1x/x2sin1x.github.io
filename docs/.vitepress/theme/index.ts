// .vitepress/theme/index.ts
import { h } from "vue";
import type { Theme } from "vitepress";
import Teek from "vitepress-theme-teek";
import "vitepress-theme-teek/index.css";
import "./style.css";
import AbcScore from "./components/AbcScore.vue";
import BloggerCardInject from "./components/BloggerCardInject.vue";
import ContributeChart from "./components/ContributeChart.vue";
import Mermaid from "./components/Mermaid.vue";
import NavDropdownLink from "./components/NavDropdownLink.vue";
import ArticleBreadcrumb from "./components/ArticleBreadcrumb.vue";

export default {
  extends: Teek,
  // 通过归档页顶部插槽渲染 Git 提交活跃度贡献图；
  // teek-home-after 在所有 layout: home 页面（首页 / 分类 / 标签）渲染，
  // BloggerCardInject 仅在分类、标签页把博主信息卡片注入卡片列表
  Layout: () =>
    h(Teek.Layout, null, {
      "teek-archives-top-before": () => h(ContributeChart),
      "teek-home-after": () => h(BloggerCardInject),
      // 文章面包屑：主题内置面包屑已关闭（teekConfig breadcrumb.enabled: false），
      // 改用自定义组件（层级均可点击并显示页面标题，见 ArticleBreadcrumb.vue）
      "teek-article-analyze-before": () => h(ArticleBreadcrumb),
    }),
  enhanceApp({ app }) {
    app.component("AbcScore", AbcScore);
    // ```mermaid 图表组件（config.mts 围栏映射）：
    // 组件输出官方约定的 <pre class="mermaid">，挂载后用 mermaid.run() 渲染
    app.component("Mermaid", Mermaid);
    // 可点击的导航下拉（右上角“技术栈”/“知识星球”）：
    // 单击标题进入总览页，hover 展开子菜单，配合 nav 中的 component 项使用
    app.component("NavDropdownLink", NavDropdownLink);
  },
} satisfies Theme;
