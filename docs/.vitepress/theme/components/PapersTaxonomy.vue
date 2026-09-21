<script setup lang="ts">
import { computed } from "vue";
import { data as papersData } from "../../../@pages/papers.data.mts";
import TaxonomyPage from "./TaxonomyPage.vue";
import { buildGroups } from "./taxonomy";

/**
 * 论文板块的自建标签 / 分类页（kind 决定聚合维度）。
 * 数据来自独立的 createContentLoader 数据源（@pages/papers.data.ts，构建期仅扫描 papers 的
 * frontmatter），与博客的 usePosts 数据集、/tags /categories URL 空间完全隔离。
 */
const props = defineProps<{ kind: "tags" | "categories" }>();

// 数据源已按日期倒序排序，buildGroups 保持组内顺序
const items = computed(() =>
  buildGroups(
    papersData.map((paper) => ({
      title: paper.title || paper.url,
      url: paper.url,
      ...(paper.date === undefined ? {} : { date: paper.date }),
      tags: paper.tags,
      categories: paper.categories,
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
