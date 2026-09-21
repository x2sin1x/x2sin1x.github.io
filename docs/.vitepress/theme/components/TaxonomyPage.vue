<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { categoryIcon, tagIcon, useTagColor } from "vitepress-theme-teek";
import type { TaxonomyGroup } from "./taxonomy";

/**
 * 自建标签 / 分类页的通用渲染组件（博客与论文板块共用，但不依赖任何主题模板）。
 *
 * 视觉风格对齐 Teek 主题原生页面：
 * - 卡片容器复刻 tk-page-card（背景 / 圆角 / 阴影 / 标题图标均取主题 CSS 变量）；
 * - variant="tags" 时为彩色标签云，色板来自主题 tagColor 配置（与首页标签卡片一致），
 *   hover / active 的位移、缩放、阴影复刻 HomeCardTag 的 tk-tag__list 样式；
 * - variant="categories" 时为分类行列表，复刻 tk-category__list（左侧色条、悬停填充、
 *   选中反色高亮）；
 * - 文章列表行复刻归档页 tk-archives__timeline（悬停填充 + 缩进 + 主题色）。
 *
 * 挂载页面为默认 doc 布局（如 @pages/tagsPage.md）：内容处于 .vp-doc 容器内，
 * 边距 / 宽度 / 标题排版与 docs/posts、docs/papers 下的普通文档页保持一致；
 * 组件内的链接需显式覆盖 .vp-doc a 的下划线与品牌色样式。
 *
 * 交互：点击切换筛选；支持 ?tag= / ?category= 查询参数直达
 * （文章卡片上的标签 chip 链接即 /posts/tags?tag=xxx 形式）。
 */
const props = withDefaults(
  defineProps<{
    /** 分组数据（buildGroups 产出，文章数倒序） */
    items: TaxonomyGroup[];
    /** URL 查询参数名：标签页为 tag，分类页为 category */
    queryKey: string;
    /** 标签 / 分类在文案中的称呼，如「标签」「分类」 */
    unitLabel: string;
    /** 视觉风格：tags 为彩色标签云，categories 为分类行列表 */
    variant: "tags" | "categories";
    /** 无任何数据时的空态文案 */
    emptyLabel?: string;
  }>(),
  { emptyLabel: "暂无内容" }
);

const selected = ref("");

const total = computed(() => props.items.reduce((sum, item) => sum + item.posts.length, 0));
const activeGroup = computed(() => props.items.find((item) => item.name === selected.value));

/** 卡片标题图标（与主题标签 / 分类卡片一致的 emoji 图标） */
const iconHtml = computed(() => (props.variant === "tags" ? tagIcon : categoryIcon));

/** 主题 tagColor 色板（可经 teekConfig.tagColor 覆盖），下标循环取色保证同一标签颜色稳定 */
const tagColor = useTagColor();
const chipStyle = (index: number) => {
  const palette = tagColor.value;
  // noUncheckedIndexedAccess：取不到时回退到首项（正常配置下色板非空）
  const color = palette[index % palette.length] ?? palette[0];
  if (!color) return {};
  // --chip-bg 供 active 态的投影复用（同主题 --tk-home-tag-bg-color 的用法）
  return {
    backgroundColor: color.bg,
    color: color.text,
    borderColor: color.border,
    "--chip-bg": color.bg,
  };
};

/** 从当前 URL 恢复选中状态（处理外部链接 ?tag=xxx 直达与浏览器前进后退） */
const syncFromLocation = () => {
  const value = new URL(window.location.href).searchParams.get(props.queryKey) ?? "";
  selected.value = props.items.some((item) => item.name === value) ? value : "";
};

const select = (name = "") => {
  const { pathname, searchParams } = new URL(window.location.href);
  searchParams.delete(props.queryKey);
  if (name) searchParams.set(props.queryKey, name);
  const query = searchParams.toString();
  window.history.pushState({}, "", pathname + (query ? `?${query}` : ""));
  selected.value = name;
};

const onPopState = () => syncFromLocation();
onMounted(() => {
  syncFromLocation();
  window.addEventListener("popstate", onPopState);
});
onBeforeUnmount(() => window.removeEventListener("popstate", onPopState));
</script>

<template>
  <div class="taxonomy">
    <section class="panel">
      <header class="panel-header">
        <h2 class="panel-title">
          <!-- 主题图标为 SVG 字符串，经 v-html 注入后需用 :deep() 命中 -->
          <span class="panel-icon" aria-hidden="true" v-html="iconHtml" />
          {{ props.unitLabel }}
        </h2>
        <span v-if="items.length" class="count">
          共 {{ items.length }} 个{{ props.unitLabel }} · 覆盖 {{ total }} 篇文章
        </span>
      </header>

      <p v-if="!items.length" class="empty">{{ props.emptyLabel }}</p>

      <!-- 标签云（对齐主题 HomeCardTag 的彩色标签） -->
      <div v-else-if="props.variant === 'tags'" class="cloud" role="list">
        <a
          v-for="(item, index) in items"
          :key="item.name"
          role="listitem"
          href="javascript:"
          class="chip"
          :class="{ active: item.name === selected }"
          :style="chipStyle(index)"
          :aria-label="`${item.name}（${item.posts.length} 篇文章）`"
          @click="select(selected === item.name ? '' : item.name)"
        >
          {{ item.name }}<span class="num">{{ item.posts.length }}</span>
        </a>
      </div>

      <!-- 分类列表（对齐主题 tk-category__list 的行式布局） -->
      <div v-else class="cat-list" role="list">
        <a
          v-for="item in items"
          :key="item.name"
          role="listitem"
          href="javascript:"
          class="cat"
          :class="{ active: item.name === selected }"
          :aria-label="`${item.name}（${item.posts.length} 篇文章）`"
          @click="select(selected === item.name ? '' : item.name)"
        >
          <span class="name">{{ item.name }}</span>
          <span class="num">{{ item.posts.length }}</span>
        </a>
      </div>
    </section>

    <section v-if="activeGroup" class="panel list-panel">
      <header class="panel-header">
        <h2 class="panel-title">「{{ selected }}」下的 {{ activeGroup.posts.length }} 篇文章</h2>
        <a href="javascript:" class="reset" @click="select()">查看全部</a>
      </header>
      <div class="post-list">
        <a v-for="post in activeGroup.posts" :key="post.url" class="post" :href="post.url">
          <span class="title">{{ post.title }}</span>
          <span v-if="post.date" class="date">{{ post.date }}</span>
        </a>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* 卡片容器：复刻 tk-page-card 的观感，但宽度铺满页面 */
.panel {
  margin-top: 12px;
  padding: var(--tk-home-card-padding, 16px 20px);
  background-color: var(--tk-bg-color-elm, var(--vp-c-bg-soft));
  border-radius: var(--tk-home-card-border-radius, 8px);
  box-shadow: var(--tk-card-shadow);
  transition: box-shadow var(--tk-transition-duration-slow, 0.5s);
}

.panel:hover {
  box-shadow: var(--tk-hover-shadow);
}

.panel-header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 12px;
}

.panel-title {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: var(--vp-c-text-1);
  font-size: var(--tk-home-font-size-large, 20px);
  font-weight: 600;
  line-height: 1.4;
}

.panel-icon {
  display: inline-flex;
}

.panel-icon :deep(svg) {
  width: 20px;
  height: 20px;
}

/* 数量统计：对齐归档页 .count 的斜体淡色样式 */
.count {
  margin-left: auto;
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

/* ---------- 标签云（tk-tag__list 风格） ---------- */

.cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.chip {
  display: inline-flex;
  align-items: baseline;
  gap: 3px;
  height: 26px;
  padding: 0 9px;
  border: 1px solid transparent;
  border-radius: 3px;
  color: inherit;
  font-size: 14px;
  font-weight: 400;
  line-height: 24px;
  text-decoration: none;
  cursor: pointer;
  user-select: none;
  transition: transform var(--tk-transition-duration, 0.3s) cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow var(--tk-transition-duration, 0.3s) cubic-bezier(0.4, 0, 0.2, 1);
}

.chip:hover {
  transform: translateY(-2px) scale(1.05);
}

.chip.active {
  /* 投影取标签自身背景色，与主题 --tk-home-tag-bg-color 的用法一致 */
  box-shadow: 0 5px 10px -5px var(--chip-bg, currentColor);
  transform: scale(1.15);
}

.chip .num {
  position: relative;
  top: -1px;
  font-size: 12px;
  opacity: 0.75;
}

/* 暗色模式下柔和降低彩签亮度，避免过曝 */
:global(.dark) .chip {
  opacity: 0.88;
}

/* ---------- 分类列表（tk-category__list 风格） ---------- */

.cat-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2px 20px;
  margin-top: 4px;
}

.cat {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 6px 8px;
  border-left: 2px solid transparent;
  border-radius: 2px;
  color: var(--vp-c-text-1);
  font-size: 15px;
  font-weight: 400;
  text-decoration: none;
  transition: background-color var(--tk-transition-duration-fast, 0.2s),
    border-color var(--tk-transition-duration-fast, 0.2s),
    color var(--tk-transition-duration-fast, 0.2s), padding var(--tk-transition-duration-fast, 0.2s);
}

.cat:hover {
  background-color: var(--tk-fill-color-light, var(--vp-c-default-soft));
  border-left-color: var(--tk-theme-color, var(--vp-c-brand-1));
  color: var(--tk-theme-color, var(--vp-c-brand-1));
}

.cat.active {
  background-color: var(--tk-theme-color, var(--vp-c-brand-1));
  border-left-color: transparent;
  color: var(--tk-bg-color, var(--vp-c-bg));
  padding-left: 13px;
}

.cat.active:hover {
  color: var(--tk-bg-color, var(--vp-c-bg));
}

.cat .name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cat .num {
  flex-shrink: 0;
  font-size: 12.8px;
  opacity: 0.65;
}

.cat.active .num {
  opacity: 0.9;
}

/* ---------- 文章列表（归档页 tk-archives__timeline 风格） ---------- */

.list-panel {
  margin-top: 20px;
}

.list-panel .panel-header {
  align-items: center;
}

.list-panel .panel-title {
  font-size: var(--tk-home-font-size-middle, 17px);
}

.reset {
  margin-left: auto;
  color: var(--vp-c-text-2);
  font-size: 13px;
  font-weight: 400;
  text-decoration: none;
}

.reset:hover {
  color: var(--tk-theme-color, var(--vp-c-brand-1));
}

.post-list {
  display: flex;
  flex-direction: column;
}

.post {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  padding: 8px 10px;
  border-radius: 6px;
  color: var(--vp-c-text-1);
  font-size: 15px;
  font-weight: 400;
  text-decoration: none;
  transition: background-color var(--tk-transition-duration, 0.3s),
    padding var(--tk-transition-duration, 0.3s), color var(--tk-transition-duration, 0.3s);
}

.post:hover {
  background-color: var(--tk-fill-color-light, var(--vp-c-default-soft));
  color: var(--tk-theme-color, var(--vp-c-brand-1));
  padding-left: 16px;
}

.post .title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post .date {
  flex-shrink: 0;
  font-size: 13px;
  opacity: 0.6;
}

@media (max-width: 768px) {
  .panel {
    padding: 14px 16px;
  }

  .cat-list {
    grid-template-columns: 1fr;
  }

  /* 移动端缩放悬停无意义，去掉避免误触时的跳动 */
  .chip:hover,
  .chip.active {
    transform: none;
  }

  .post {
    flex-direction: column;
    gap: 2px;
  }
}
</style>
