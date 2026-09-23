<script setup lang="ts">
import { computed } from "vue";
import { data as papersData, type PaperItem } from "../../../@pages/papers.data.mts";

/**
 * 论文板块的自建归档页（/papers/archives）。
 *
 * 与博客归档页（/archives，主题 TkArchivesPage 模板）视觉对齐，但数据源完全独立：
 * 博客归档绑定主题文章数据集（usePosts，papers 已从源头排除，见 config.mts
 * fileContentLoaderIgnore），因此这里改为按 tk-archives 的 DOM 结构与 CSS 变量
 * 自行复刻时间线（年份 sticky 头 + 月份行 + 文章行），数据来自 @pages/papers.data.mts。
 *
 * 挂载页面为 @pages/papersArchivesPage.md（默认 doc 布局 + sidebar: false，
 * 与 /papers/tags、/papers/categories 的挂载方式一致），组件内样式为 scoped，
 * 覆盖 .vp-doc 对 ul / li / a 的默认排版。
 */

/** 无日期的论文归入的兜底分组（正常 frontmatter 下不会出现） */
const UNDATED_YEAR = "未指定";

interface MonthGroup {
  /** 两位月份字符串（"01" ~ "12"），无日期时为空串 */
  month: string;
  papers: PaperItem[];
}

interface YearGroup {
  /** 四位年份字符串，无日期时为 UNDATED_YEAR */
  year: string;
  /** 该年份下的论文总数（各月份之和） */
  papers: PaperItem[];
  months: MonthGroup[];
}

// 数据源已按日期倒序排序；过滤掉落地页 index.md 自身（不属于论文）
const papers = computed(() => papersData.filter((paper) => paper.url !== "/papers/"));

const timeline = computed<YearGroup[]>(() => {
  const yearMap = new Map<string, Map<string, PaperItem[]>>();
  const undated: PaperItem[] = [];
  for (const paper of papers.value) {
    if (paper.date === undefined) {
      undated.push(paper);
      continue;
    }
    const year = paper.date.slice(0, 4);
    const month = paper.date.slice(5, 7);
    const monthMap = yearMap.get(year) ?? new Map<string, PaperItem[]>();
    const bucket = monthMap.get(month) ?? [];
    bucket.push(paper);
    monthMap.set(month, bucket);
    yearMap.set(year, monthMap);
  }

  const groups: YearGroup[] = Array.from(yearMap, ([year, monthMap]) => {
    const months: MonthGroup[] = Array.from(monthMap, ([month, items]) => ({ month, papers: items }));
    return { year, papers: months.flatMap((group) => group.papers), months };
  }).sort((prev, next) => next.year.localeCompare(prev.year));

  if (undated.length) groups.push({ year: UNDATED_YEAR, papers: undated, months: [{ month: "", papers: undated }] });
  return groups;
});

const total = computed(() => papers.value.length);
const yearLabel = (year: string) => (year === UNDATED_YEAR ? year : `${year} 年`);
const monthLabel = (month: string) => (month ? `${Number(month)} 月` : UNDATED_YEAR);
</script>

<template>
  <div class="papers-archives">
    <!-- 头部：对齐主题归档页 tk-archives__header（标题 + 总数统计） -->
    <header class="header">
      <h1>归档</h1>
      <span class="count">总共 {{ total }} 篇论文</span>
    </header>

    <p v-if="!total" class="empty">暂无论文</p>

    <!-- 时间线：对齐主题 tk-archives__timeline（sticky 年份头 + 月份行 + 文章行） -->
    <div v-else class="timeline">
      <template v-for="group in timeline" :key="group.year">
        <div class="year-row">
          <span class="year">{{ yearLabel(group.year) }}</span>
          <span class="count">{{ group.papers.length }} 篇</span>
        </div>
        <div class="months">
          <template v-for="monthGroup in group.months" :key="monthGroup.month">
            <div class="month-row">
              <span class="month">{{ monthLabel(monthGroup.month) }}</span>
              <span class="count">{{ monthGroup.papers.length }} 篇</span>
            </div>
            <ul class="paper-list" role="list">
              <li v-for="paper in monthGroup.papers" :key="paper.url">
                <a :href="paper.url" :aria-label="paper.title">
                  <span v-if="paper.date" class="date">{{ paper.date.slice(5, 10) }}</span>
                  <span class="title">{{ paper.title || paper.url }}</span>
                </a>
              </li>
            </ul>
          </template>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
/* 复刻 tk-archives__header：标题与总数两端对齐 */
.header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.header h1 {
  margin: 0;
}

/* 复刻 .count 的斜体淡色样式（主题归档页同名类） */
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

.timeline {
  margin: 32px 0;
}

/* 复刻 tk-archives__timeline--year：sticky 年份行（滚动时吸顶，与导航栏对齐） */
.year-row {
  position: sticky;
  top: var(--vp-nav-height, 64px);
  z-index: 1;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-top: 32px;
  padding: 8px 0;
  background-color: var(--tk-bg-color, var(--vp-c-bg));
  border-bottom: 1px solid var(--tk-line-color, var(--vp-c-divider));
}

.year-row .year {
  font-size: 24px;
  font-weight: 500;
}

.months {
  margin-top: 16px;
}

/* 复刻 tk-archives__timeline__m--month：月份行 */
.month-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-top: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--tk-line-color, var(--vp-c-divider));
}

.month-row .month {
  font-size: 19px;
}

/* 复刻 tk-archives__timeline__m ul：覆盖 .vp-doc 的列表默认样式 */
.paper-list {
  margin: 0;
  padding: 8px 16px;
  list-style: none;
}

.paper-list li {
  line-height: 2;
}

.paper-list li a {
  display: block;
  color: var(--vp-c-text-1);
  text-decoration: none;
  transition: padding var(--tk-transition-duration, 0.3s);
}

.paper-list li a:hover {
  padding-left: 16px;
  background: var(--tk-fill-color-light, var(--vp-c-default-soft));
  color: var(--tk-theme-color, var(--vp-c-brand-1));
}

.paper-list .date {
  margin-right: 8px;
  font-size: 13.6px;
  opacity: 0.6;
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 20px;
  }

  .year-row .year {
    font-size: 20px;
  }

  .month-row .month {
    font-size: 16px;
  }
}
</style>
