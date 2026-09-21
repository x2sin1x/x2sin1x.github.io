// .vitepress/theme/index.ts
import { h } from "vue";
import type { Theme } from "vitepress";
import Teek from "vitepress-theme-teek";
import "vitepress-theme-teek/index.css";
import "./style.css";
import AbcScore from "./components/AbcScore.vue";
import ContributeChart from "./components/ContributeChart.vue";
import Mermaid from "./components/Mermaid.vue";
import NavDropdownLink from "./components/NavDropdownLink.vue";
import ArticleBreadcrumb from "./components/ArticleBreadcrumb.vue";
import PostsTaxonomy from "./components/PostsTaxonomy.vue";
import PapersTaxonomy from "./components/PapersTaxonomy.vue";
import PermalinkRedirect from "./components/PermalinkRedirect.vue";

export default {
  extends: Teek,
  // 通过归档页顶部插槽渲染 Git 提交活跃度贡献图；
  // 标签 / 分类页已改为自建组件（PostsTaxonomy / PapersTaxonomy，layout: page），
  // 不再使用主题内置 tagsPage / categoriesPage 模板，故无需再向 home 布局注入博主卡片
  Layout: () =>
    h(Teek.Layout, null, {
      "teek-archives-top-before": () => h(ContributeChart),
      // 文章面包屑：主题内置面包屑已关闭（teekConfig breadcrumb.enabled: false），
      // 改用自定义组件（层级均可点击并显示页面标题，见 ArticleBreadcrumb.vue）
      "teek-article-analyze-before": () => h(ArticleBreadcrumb),
    }),
  enhanceApp({ app }) {
    app.component("AbcScore", AbcScore);
    // ```mermaid 图表组件（config.mts 围栏映射）：
    // 组件输出官方约定的 <pre class="mermaid">，挂载后用 mermaid.run() 渲染
    app.component("Mermaid", Mermaid);
    // 可点击的导航下拉（右上角“技术栈”/“知识星球”/“论文”）：
    // 单击标题进入总览页，hover 展开子菜单，配合 nav 中的 component 项使用
    app.component("NavDropdownLink", NavDropdownLink);
    // 自建标签 / 分类页：博客（/posts/tags、/posts/categories）与论文（/papers/tags、/papers/categories）
    // 各一套数据源与 URL 空间，渲染共用 TaxonomyPage 组件（不依赖主题内置标签 / 分类模板）
    app.component("PostsTaxonomy", PostsTaxonomy);
    app.component("PapersTaxonomy", PapersTaxonomy);
    // 旧地址 /tags、/categories 的兼容重定向（主题文章卡片硬编码链接兜底）
    app.component("PermalinkRedirect", PermalinkRedirect);
  },
} satisfies Theme;
