<script setup lang="ts">
import { computed } from "vue";
import { useData } from "vitepress";

/**
 * 全站页脚（Theme By Teek + Copyright 2026）。
 *
 * 主题的 FooterInfo / FooterGroup 仅在 layout: home 页面渲染（见主题 Layout 的
 * isHomePage 分支），而 /posts/、/papers/ 落地页均为 layout: page，无法复用；
 * 因此通过 theme/index.ts 的 layout-bottom 插槽在全站底部注入本组件。
 *
 * 站点首页（docs/index.md，layout: home）由主题 FooterInfo 渲染页脚，
 * 本组件在 layout: home 页面不渲染，避免出现双份页脚。
 *
 * 样式对齐主题 tk-footer-info 的观感：居中一行、淡色小字、链接悬停主题色。
 */
const themeLink = "https://github.com/Kele-Bingtang/vitepress-theme-teek";

const { frontmatter } = useData();
/** 首页（layout: home）由主题 FooterInfo 渲染页脚，本组件不重复渲染 */
const hidden = computed(() => frontmatter.value["layout"] === "home");
</script>

<template>
  <footer v-if="!hidden" class="site-footer" role="contentinfo" aria-label="页脚">
    <a class="link" :href="themeLink" target="_blank" rel="noopener noreferrer" aria-label="Theme By Teek">
      Theme By <span class="hl">Teek</span>
    </a>
    <span class="divider" aria-hidden="true">·</span>
    <span class="copyright">Copyright 2026</span>
  </footer>
</template>

<style scoped>
.site-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px 16px;
  color: var(--vp-c-text-2);
  font-size: 14px;
}

.link {
  color: var(--vp-c-text-2);
  text-decoration: none;
  transition: color var(--tk-transition-duration-fast, 0.2s);
}

.link:hover {
  color: var(--tk-theme-color, var(--vp-c-brand-1));
}

.hl {
  font-weight: 600;
}

.divider {
  opacity: 0.5;
}

.copyright {
  letter-spacing: 0.2px;
}
</style>
