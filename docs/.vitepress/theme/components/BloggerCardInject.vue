<script setup lang="ts">
import { computed } from "vue";
import { useData } from "vitepress";
import { TkHomeCardMy } from "vitepress-theme-teek";

/**
 * 主题的 HomeCard 只在首页（isHomePage）渲染博主信息卡片（avatar 块），
 * 分类 / 标签页（layout: home + categoriesPage / tagsPage）会渲染卡片列表
 * （.tk-home-card，纵向 flex 布局）但缺少该卡片。
 * 这里通过 Teleport 把主题自带的 TkHomeCardMy 注入卡片列表顶部，
 * 复用主题组件以保证样式、社交图标、国际化行为与首页完全一致。
 */
const { frontmatter } = useData();
const enabled = computed(() => Boolean(frontmatter.value["categoriesPage"] || frontmatter.value["tagsPage"]));
</script>

<template>
  <ClientOnly>
    <Teleport v-if="enabled" to=".tk-home-card">
      <div class="tk-home-card-inject-my">
        <TkHomeCardMy />
      </div>
    </Teleport>
  </ClientOnly>
</template>

<style>
/* 卡片列表为纵向 flex 布局，用 order 置顶，与首页卡片顺序（my 最先）保持一致 */
.tk-home-card-inject-my {
  order: -1;
}
</style>
