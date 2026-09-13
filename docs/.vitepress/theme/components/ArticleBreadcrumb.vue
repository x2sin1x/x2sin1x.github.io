<!--
  自定义文章面包屑，替代 Teek 主题内置的 TkArticleBreadcrumb。

  与内置实现相比的改进：
  1. 每个层级都渲染为指向相应页面的链接：目录层级链接到该目录的落地页（index.md），
     目录没有落地页时（如 posts/<年份>/ 仅是侧边栏分组）退化为纯文本；
  2. 层级显示页面标题而非文件 / 文件夹名：标题取自构建期生成的
     「URL → 标题」映射（config.mts 的 collectBreadcrumbTitles() 注入
     themeConfig.breadcrumbTitles），优先 frontmatter title，回退正文一级标题。

  渲染位置：theme/index.ts 通过 teek-article-analyze-before 插槽挂载；
  需配合 defineTeekConfig 中 breadcrumb.enabled: false 关闭主题内置面包屑。
-->
<script setup lang="ts">
import { computed } from "vue";
import { useData, withBase } from "vitepress";
import type { DefaultTheme } from "vitepress";
import { TkBreadcrumb, TkBreadcrumbItem, TkIcon, houseIcon } from "vitepress-theme-teek";

interface BreadcrumbEntry {
  /** 层级显示文本（页面标题或目录 / 文件名回退值） */
  text: string;
  /** 层级链接（URL 不含 base）；目录无落地页时为 undefined，渲染为纯文本 */
  url?: string | undefined;
  /** 是否为当前页（渲染 aria-current="page"） */
  isCurrent: boolean;
}

const { page, theme, frontmatter } = useData();

/**
 * 构建期注入的「URL 路径 → 页面标题」映射（URL 不含 base，cleanUrls 形式）：
 * 目录页键为 /a/b/，普通页面键为 /a/b/c
 */
const titleMap = computed<Record<string, string>>(() => {
  const config = theme.value as DefaultTheme.Config & { breadcrumbTitles?: Record<string, string> };
  return config.breadcrumbTitles ?? {};
});

const entries = computed<BreadcrumbEntry[]>(() => {
  const titles = titleMap.value;
  // 以当前页源文件路径还原层级：如 tech-stack/python/decorator.md →
  // ["tech-stack", "python", "decorator"]，目录页自身为 tech-stack/python/index
  const segments = page.value.filePath.replace(/\.md$/, "").split("/");
  const result: BreadcrumbEntry[] = [];

  segments.forEach((segment, index) => {
    const path = segments.slice(0, index + 1).join("/");
    const isCurrent = index === segments.length - 1;
    // 目录层级对应落地页 URL（/a/b/ 即 a/b/index.md）；当前页对应页面自身 URL
    const rawUrl = isCurrent
      ? path.endsWith("/index")
        ? `/${path.slice(0, -"/index".length)}/`
        : `/${path}`
      : `/${path}/`;
    // 标题优先取映射（frontmatter title），当前页再回退运行时 frontmatter / 目录名
    const { title } = frontmatter.value;
    const text = titles[rawUrl] ?? (isCurrent ? (title ?? segment) : segment);
    // 目录层级只有存在落地页（映射中有该 URL）才渲染为链接，否则退化为纯文本
    const url = isCurrent || titles[rawUrl] !== undefined ? rawUrl : undefined;
    result.push({ text, url, isCurrent });
  });

  // 目录页（index.md）自身会同时命中最后一个目录层级与当前页层级，二者 URL 相同；
  // 相邻重复条目只保留后者（带 aria-current="page" 的当前页）
  return result.filter(
    (entry, index) =>
      index === result.length - 1 || entry.url === undefined || entry.url !== result[index + 1]?.url
  );
});
</script>

<template>
  <div class="tk-article-breadcrumb" role="navigation" aria-label="面包屑">
    <TkBreadcrumb separator="/">
      <TkBreadcrumbItem>
        <a :href="withBase('/')" class="home hover-color" title="首页" aria-label="首页">
          <TkIcon :icon="houseIcon" aria-hidden="true" />
        </a>
      </TkBreadcrumbItem>
      <TkBreadcrumbItem v-for="(entry, index) in entries" :key="index">
        <a
          v-if="entry.url"
          :href="withBase(entry.url)"
          :title="entry.text"
          :aria-label="entry.text"
          :aria-current="entry.isCurrent ? 'page' : undefined"
          :class="{ 'hover-color': !entry.isCurrent }"
        >
          {{ entry.text }}
        </a>
        <span v-else>{{ entry.text }}</span>
      </TkBreadcrumbItem>
    </TkBreadcrumb>
  </div>
</template>
