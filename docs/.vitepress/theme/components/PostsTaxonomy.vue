<script setup lang="ts">
import { computed } from "vue";
import { data as postsData } from "../../../@pages/posts.data.mts";
import TaxonomyPage from "./TaxonomyPage.vue";
import { buildGroups } from "./taxonomy";

/**
 * 博客板块的自建标签 / 分类页（kind 决定聚合维度）。
 * 数据来自独立的 createContentLoader 数据源（@pages/posts.data.mts，构建期仅扫描 posts 的
 * frontmatter），与主题的 usePosts 数据集、论文板块的 /papers/tags URL 空间完全隔离；
 * 数据加载、聚合、渲染逻辑与 PapersTaxonomy 完全对称。
 */
const props = defineProps<{ kind: "tags" | "categories" }>();

// 数据源已按日期倒序排序，buildGroups 保持组内顺序
const items = computed(() =>
  buildGroups(
    postsData.map((post) => ({
      title: post.title || post.url,
      url: post.url,
      ...(post.date === undefined ? {} : { date: post.date }),
      tags: post.tags,
      categories: post.categories,
    })),
    props.kind
  )
);
</script>

<template>
  <TaxonomyPage
    :items="items"
    :query-key="props.kind === 'tags' ? 'tag' : 'category'"
    :unit-label="props.kind === 'tags' ? '标签' : '分类'"
    :variant="props.kind"
    :empty-label="props.kind === 'tags' ? '暂无标签' : '暂无分类'"
  />
</template>
