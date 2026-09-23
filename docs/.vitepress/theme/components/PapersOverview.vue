<script setup lang="ts">
import { computed } from "vue";
import { useData, type DefaultTheme } from "vitepress";
import type { DocAnalysisData } from "vitepress-theme-teek";
import { data as papersData, type PaperItem } from "../../../@pages/papers.data.mts";

/**
 * 论文板块的自建清单页（/papers/articleOverview）。
 *
 * 与博客清单页（/articleOverview，主题 TkArticleOverviewPage 模板）结构对齐——
 * 按分类分组的 h2 标题 + 分类页跳转链接 + 表格（标题 / 日期 / 字数 / 阅读时长），
 * 表格排版复用 .vp-doc 的默认表格样式（主题清单页同样依赖它）。
 *
 * 数据源完全独立：博客清单绑定主题文章数据集（usePosts，papers 已从源头排除），
 * 这里使用 @pages/papers.data.mts（仅扫描 docs/papers/ 的 frontmatter）。
 * 字数 / 阅读时长来自主题 DocAnalysis 插件构建期注入的 docAnalysisInfo
 * （其 ignoreList 只排除 @pages 等，包含 papers 下的 md），取不到时显示 -。
 */

interface OverviewGroup {
  name: string;
  /** 该分类下的论文，保持传入顺序（日期倒序） */
  papers: PaperItem[];
}

/** DocAnalysis 插件为每个 md 文件统计的字数信息 */
interface FileWords {
  fileInfo: { relativePath: string };
  wordCount: number;
  readingTime: string;
}

/** 无分类的论文归入的兜底分组（正常 frontmatter 下不会出现） */
const UNCATALOGED = "未分类";

const { theme } = useData();

const papers = computed(() => papersData.filter((paper) => paper.url !== "/papers/"));

/** 构建期注入的站点文件字数统计（「相对路径 → 统计信息」映射，路径形如 /papers/2026/DFlash） */
const wordsMap = computed(() => {
  const config = theme.value as DefaultTheme.Config & { docAnalysisInfo?: DocAnalysisData };
  const list: FileWords[] = config.docAnalysisInfo?.eachFileWords ?? [];
  return new Map(list.map((info) => [`/${info.fileInfo.relativePath.replace(/\.md$/, "")}`, info]));
});

const wordsOf = (paper: PaperItem): FileWords | undefined => wordsMap.value.get(paper.url);

/** 按分类分组；与主题清单页一致，分组按组内最新文章日期倒序，无分类论文归入兜底分组 */
const groups = computed<OverviewGroup[]>(() => {
  const map = new Map<string, PaperItem[]>();
  const uncataloged: PaperItem[] = [];
  for (const paper of papers.value) {
    if (!paper.categories.length) {
      uncataloged.push(paper);
      continue;
    }
    for (const name of paper.categories) {
      const bucket = map.get(name) ?? [];
      bucket.push(paper);
      map.set(name, bucket);
    }
  }

  const result: OverviewGroup[] = Array.from(map, ([name, items]) => ({ name, papers: items })).sort(
    (prev, next) =>
      (next.papers[next.papers.length - 1]?.date ?? "").localeCompare(
        prev.papers[prev.papers.length - 1]?.date ?? ""
      )
  );
  if (uncataloged.length) result.push({ name: UNCATALOGED, papers: uncataloged });
  return result;
});

const total = computed(() => papers.value.length);
const categoryLink = (name: string) => `/papers/categories?category=${encodeURIComponent(name)}`;
const anchorId = (name: string) => `${name}-清单`;
</script>

<template>
  <div class="papers-overview">
    <header class="header">
      <h1>论文清单</h1>
      <span class="count">共 {{ total }} 篇论文</span>
    </header>

    <p v-if="!total" class="empty">暂无论文</p>

    <template v-else>
      <section v-for="group in groups" :key="group.name" class="group">
        <h2 :id="anchorId(group.name)">
          {{ group.name }} 清单
          <a class="header-anchor" :href="`#${anchorId(group.name)}`" :aria-label="`Permalink to '${group.name} 清单'`">#</a>
        </h2>
        <a class="category-link" :href="categoryLink(group.name)">查看「{{ group.name }}」分类</a>
        <table role="table" :aria-label="`${group.name} 清单`">
          <thead>
            <tr>
              <th scope="col">所属分类</th>
              <th scope="col">论文标题</th>
              <th scope="col">发布时间</th>
              <th scope="col">文章字数</th>
              <th scope="col">预计阅读时长</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="paper in group.papers" :key="paper.url">
              <td>{{ group.name }}</td>
              <td>
                <a :href="paper.url" :aria-label="paper.title">{{ paper.title || paper.url }}</a>
              </td>
              <td>{{ paper.date ?? "-" }}</td>
              <td>{{ wordsOf(paper)?.wordCount ?? "-" }}</td>
              <td>{{ wordsOf(paper)?.readingTime ?? "-" }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>
  </div>
</template>

<style scoped>
.header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.header h1 {
  margin: 0;
}

.count {
  color: var(--vp-c-text-2);
  font-size: 13.6px;
  font-style: oblique;
  font-weight: 300;
  opacity: 0.8;
}

.empty {
  margin: 0;
  padding: 12px 0;
  color: var(--vp-c-text-3);
  font-size: 14px;
  text-align: center;
}

/* 复刻主题清单页 tk-article-overview h2 的分隔线样式 */
.group h2 {
  padding-top: 0;
  padding-bottom: 16px;
  border-top: none;
  border-bottom: 1px solid var(--vp-c-divider);
}

.category-link {
  display: inline-block;
  margin-bottom: 16px;
  font-size: 14px;
}
</style>
