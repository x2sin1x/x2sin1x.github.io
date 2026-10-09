<script setup lang="ts">
import { computed } from "vue";
import { useRoute, withBase } from "vitepress";
import { TkArticleTitle, useTeekConfig } from "vitepress-theme-teek";
import { data as updates, type SectionUpdateItem } from "../../../@pages/section-updates.data.mts";

const sectionHomes: Record<string, string> = {
  posts: "/posts/",
  "tech-stack": "/tech-stack/",
  "knowledge-planet": "/knowledge-planet/",
  papers: "/papers/",
  repos: "/repos/",
};

const route = useRoute();
const { getTeekConfigRef } = useTeekConfig();
const articleConfig = getTeekConfigRef("articleUpdate", { limit: 3 });

const routeSection = computed(() => route.path.split("/").filter(Boolean)[0] ?? "");
const section = computed(() => (sectionHomes[routeSection.value] ? routeSection.value : ""));
const sectionHome = computed(() => sectionHomes[section.value] ?? "/");
const currentUrl = computed(() => route.path.replace(/\.html$/, ""));
const recentItems = computed(() => {
  const limit = articleConfig.value.limit ?? 3;
  const items = updates.filter((item) => {
    const matchesSection = !section.value || item.url.startsWith(`/${section.value}/`);
    return matchesSection && item.url !== currentUrl.value;
  });
  return items.slice(0, limit);
});

const moreItem: SectionUpdateItem = {
  url: "",
  relativePath: "",
  title: "",
  date: "",
  sortDate: 0,
  frontmatter: {},
};
</script>

<template>
  <div class="tk-article-update section-recent-updates">
    <div class="tk-article-update__title flx-align-center">
      <span class="edit-icon" aria-hidden="true">✎</span>
      <a :href="withBase(sectionHome)" class="hover-color">最近更新</a>
    </div>
    <ul>
      <li
        v-for="(item, index) in [...recentItems, moreItem]"
        :key="item.url || sectionHome"
        class="flx-center"
      >
        <span class="tk-article-update--num" aria-hidden="true">
          {{ index < recentItems.length ? String(index + 1).padStart(2, "0") : "" }}
        </span>
        <div class="tk-article-update__content">
          <a
            v-if="item.url"
            :href="withBase(item.url)"
            class="flx-1 hover-color sle"
            :aria-label="item.title"
          >
            <TkArticleTitle :post="item" :title-tag-props="{ position: 'right', size: 'small' }" />
          </a>
          <a v-else :href="withBase(sectionHome)" class="flx-1 hover-color sle">更多</a>
          <span v-if="item.date" class="tk-article-update__content--date">{{ item.date }}</span>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.edit-icon {
  margin-right: 6px;
  font-size: 14px;
}
</style>
