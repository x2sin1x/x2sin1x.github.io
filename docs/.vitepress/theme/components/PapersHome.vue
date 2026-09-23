<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import {
  calendarIcon,
  categoryIcon,
  collectionTagIcon,
  folderOpenedIcon,
  tagIcon,
  TkArticleTitle,
  TkHomeBanner,
  TkIcon,
  TkPageCard,
  TkPagination,
  useTagColor,
} from "vitepress-theme-teek";
import { data as papersData } from "../../../@pages/papers.data.mts";
import { buildGroups } from "./taxonomy";

/**
 * 组装主题 TkContentData 形状的最小文章对象，供 TkArticleTitle 渲染标题
 * （该组件只读取 title 与 frontmatter.titleTag）。
 */
const toPost = (paper: (typeof papersData)[number]) => ({
  url: paper.url,
  relativePath: `${paper.url.replace(/^\//, "").replace(/\/$/, "")}.md`,
  title: paper.title || paper.url,
  frontmatter: {},
});

/**
 * 论文板块落地页（/papers/）的自建首页组件。
 *
 * 目标：信息结构与视觉风格与博客首页（/posts/，Teek layout: home）保持一致——
 * 顶部 Banner、左侧论文列表卡片（文章列表样式）、右侧标签 / 分类卡片列。
 *
 * 与博客首页的区别仅在于数据源：论文板块已从主题的文章数据集
 * （file-content-loader，见 config.mts fileContentLoaderIgnore）中排除，
 * 主题的 HomePost / HomeCardTag / HomeCardCategory 均绑定 usePosts（博客数据），
 * 无法直接复用；因此这里改为「主题组件 + 主题全局 CSS 类名」的等价组装：
 * - Banner 直接复用主题 TkHomeBanner（仅依赖 blogger / banner 配置，与数据源无关）；
 * - 列表卡片按主题 HomePostItemList 的 DOM 结构与 tk- 类名渲染，
 *   文章信息行复刻 ArticleInfo 的类名与图标，但分类 / 标签链接指向
 *   /papers/categories、/papers/tags（ArticleInfo 内部硬编码了博客的 /tags、/categories）；
 * - 标签 / 分类卡片复用主题 TkPageCard 卡片壳，内部复刻 HomeCardTag /
 *   HomeCardCategory 的列表结构与类名，数据来自独立数据源 @pages/papers.data.mts。
 *
 * 页面挂载于 docs/papers/index.md（layout: page + sidebar: false，与博客首页同样无侧边栏）。
 */

// 数据源已按日期倒序排序；过滤掉落地页 index.md 自身（有 title 但无标签 / 分类，不属于论文）
const papers = computed(() => papersData.filter((paper) => paper.url !== "/papers/"));

const tagGroups = computed(() =>
  buildGroups(
    papers.value.map((paper) => ({
      title: paper.title || paper.url,
      url: paper.url,
      ...(paper.date === undefined ? {} : { date: paper.date }),
      tags: paper.tags,
      categories: paper.categories,
    })),
    "tags"
  )
);

const categoryGroups = computed(() =>
  buildGroups(
    papers.value.map((paper) => ({
      title: paper.title || paper.url,
      url: paper.url,
      ...(paper.date === undefined ? {} : { date: paper.date }),
      tags: paper.tags,
      categories: paper.categories,
    })),
    "categories"
  )
);

/** 主题 tagColor 色板（可经 teekConfig.tagColor 覆盖），下标循环取色保证同一标签颜色稳定 */
const tagColor = useTagColor();
const tagColorIndex = computed(() => new Map(tagGroups.value.map((group, index) => [group.name, index])));
const chipStyle = (name: string) => {
  const palette = tagColor.value;
  const index = tagColorIndex.value.get(name) ?? 0;
  // noUncheckedIndexedAccess：取不到时回退到首项（正常配置下色板非空）
  const color = palette[index % palette.length] ?? palette[0];
  if (!color) return {};
  // 与主题 HomeCardTag 的 getTagStyle 一致：同步设置主题 CSS 变量供 active 态投影使用
  return {
    "--tk-home-tag-bg-color": color.bg,
    backgroundColor: color.bg,
    color: color.text,
    borderColor: color.border,
  };
};

const tagLink = (name: string) => `/papers/tags?tag=${encodeURIComponent(name)}`;
const categoryLink = (name: string) => `/papers/categories?category=${encodeURIComponent(name)}`;

/** 卡片标题（与主题首页卡片一致：图标 + 文案，经 TkPageCard 的 innerHTML 渲染） */
const tagCardTitle = `${tagIcon}热门标签`;
const categoryCardTitle = `${categoryIcon}文章分类`;

// ---------- 分页（对齐主题 HomePost：?page= 查询参数 + 翻页后滚动） ----------

/** 与主题 post 配置的默认值一致：list 样式每页 10 篇 */
const pageSize = 10;
const pageNum = ref(1);

const syncPageFromLocation = () => {
  const value = Number(new URL(window.location.href).searchParams.get("page")) || 1;
  pageNum.value = value;
};

const handlePageChange = () => {
  const { pathname, searchParams } = new URL(window.location.href);
  searchParams.delete("page");
  if (pageNum.value > 1) searchParams.append("page", String(pageNum.value));
  const query = searchParams.toString();
  window.history.pushState({}, "", pathname + (query ? `?${query}` : ""));
  document.querySelector("html")?.scrollTo({ top: 0, behavior: "smooth" });
};

onMounted(() => {
  syncPageFromLocation();
  window.addEventListener("popstate", syncPageFromLocation);
});
onBeforeUnmount(() => window.removeEventListener("popstate", syncPageFromLocation));

const pagedPapers = computed(() => papers.value.slice((pageNum.value - 1) * pageSize, pageNum.value * pageSize));
</script>

<template>
  <div class="papers-home">
    <!-- 顶部 Banner：直接复用主题首页的 HomeBanner 组件（读取 blogger / banner 配置） -->
    <TkHomeBanner />

    <!-- 内容区：结构与主题 HomeMain 一致（左侧列表 + 右侧卡片列） -->
    <div class="tk-home-main">
      <div class="tk-home-main__content flx-start-justify-center">
        <div class="tk-home-main__content__post">
          <!-- 论文列表：复刻 HomePost 的列表结构（ul > li > 卡片）与类名 -->
          <div class="tk-home-post is-list">
            <p v-if="!papers.length" class="empty">暂无论文</p>
            <ul v-else aria-label="文章列表">
              <li v-for="paper in pagedPapers" :key="paper.url">
                <div class="tk-post-item-list">
                  <div class="list flx">
                    <div class="tk-post-item-list__left">
                      <!-- 标题：复用主题 ArticleTitle（与博客文章卡片同一组件） -->
                      <a class="tk-post-item-list__left__title hover-color sle" :href="paper.url" :aria-label="paper.title">
                        <TkArticleTitle :post="toPost(paper)" />
                      </a>
                      <!-- 文章信息行：复刻 ArticleInfo（scope=post）的类名与图标，
                           但分类 / 标签链接指向论文板块独立的标签 / 分类页 -->
                      <div class="tk-post-item-list__left__footer">
                        <div class="tk-article-info post" role="group" aria-label="文章信息">
                          <span v-if="paper.date" class="tk-article-info__item" role="group" aria-label="创建时间">
                            <TkIcon :icon="calendarIcon" class="tk-article-info__icon" aria-hidden="true" />
                            <span class="hover-color">{{ paper.date }}</span>
                          </span>
                          <span v-if="paper.categories.length" class="tk-article-info__item" role="group" aria-label="分类">
                            <TkIcon :icon="folderOpenedIcon" class="tk-article-info__icon" aria-hidden="true" />
                            <a
                              v-for="name in paper.categories"
                              :key="`cat-${name}`"
                              class="or hover-color"
                              :href="categoryLink(name)"
                            >
                              {{ name }}
                            </a>
                          </span>
                          <span v-if="paper.tags.length" class="tk-article-info__item" role="group" aria-label="标签">
                            <TkIcon :icon="collectionTagIcon" class="tk-article-info__icon" aria-hidden="true" />
                            <a v-for="name in paper.tags" :key="`tag-${name}`" class="or hover-color" :href="tagLink(name)">
                              {{ name }}
                            </a>
                          </span>
                        </div>
                      </div>
                      <!-- 摘要行（bottom 位置，与主题 post 配置默认一致） -->
                      <div v-if="paper.description" class="tk-post-item-list__left__excerpt bottom">
                        <div class="excerpt">{{ paper.description }}</div>
                        <a class="more" :href="paper.url" aria-label="文章摘要">阅读全文 ></a>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            </ul>
            <div
              v-if="papers.length >= pageSize"
              class="tk-home-post__pagination flx-justify-center"
              aria-label="分页导航"
            >
              <TkPagination v-model:current-page="pageNum" :page-size="pageSize" :total="papers.length" @current-change="handlePageChange" />
            </div>
          </div>
        </div>

        <div class="tk-home-main__content__info is-right">
          <div class="tk-home-card flx-column">
            <!-- 标签卡片：TkPageCard 卡片壳 + 复刻 HomeCardTag 的标签云（含主题色板与 active 样式） -->
            <TkPageCard :title="tagCardTitle" title-link="/papers/tags" class="tk-tag" aria-label="首页标签卡片">
              <p v-if="!tagGroups.length" class="tk-tag--empty">暂无标签</p>
              <div v-else class="tk-tag__list" aria-label="标签列表">
                <a
                  v-for="group in tagGroups"
                  :key="group.name"
                  class="tk-pointer"
                  :style="chipStyle(group.name)"
                  :href="tagLink(group.name)"
                  :aria-label="group.name"
                >
                  <span>{{ group.name }}</span>
                  <span class="num">{{ group.posts.length }}</span>
                </a>
              </div>
            </TkPageCard>

            <!-- 分类卡片：TkPageCard 卡片壳 + 复刻 HomeCardCategory 的行式列表 -->
            <TkPageCard
              :title="categoryCardTitle"
              title-link="/papers/categories"
              class="tk-category"
              aria-label="首页分类卡片"
            >
              <p v-if="!categoryGroups.length" class="tk-category--empty">暂无分类</p>
              <div v-else class="tk-category__list flx-column" aria-label="分类列表">
                <a
                  v-for="group in categoryGroups"
                  :key="group.name"
                  class="hover-color"
                  :href="categoryLink(group.name)"
                  :aria-label="group.name"
                >
                  <span class="sle">{{ group.name }}</span>
                  <span>{{ group.posts.length }}</span>
                </a>
              </div>
            </TkPageCard>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 组件自身只补充极少量样式，其余全部复用主题的 tk- 全局类（与博客首页同一套 CSS） */
.empty {
  padding: 24px 0;
  color: var(--vp-c-text-3);
  font-size: 14px;
  text-align: center;
}
</style>
