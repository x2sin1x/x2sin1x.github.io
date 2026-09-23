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
  topArticleIcon,
  useTagColor,
} from "vitepress-theme-teek";
import { data as postsData, type PostItem } from "../../../@pages/posts.data.mts";
import { buildGroups } from "./taxonomy";

/**
 * 组装主题 TkContentData 形状的最小文章对象，供 TkArticleTitle 渲染标题
 * （该组件只读取 title 与 frontmatter.titleTag）。
 */
const toPost = (post: PostItem) => ({
  url: post.url,
  relativePath: `${post.url.replace(/^\//, "").replace(/\/$/, "")}.md`,
  title: post.title || post.url,
  frontmatter: {},
});

/**
 * 博客板块落地页（/posts/）的自建首页组件。
 *
 * 与论文板块落地页（PapersHome）保持同一实现模式：不再使用主题 home 布局
 * （layout: home），改为「主题组件 + 主题全局 CSS 类名」的等价组装——
 * - Banner 直接复用主题 TkHomeBanner（仅依赖 blogger / banner 配置）；
 * - 列表卡片按主题 HomePostItemList 的 DOM 结构与 tk- 类名渲染，
 *   文章信息行复刻 ArticleInfo 的类名与图标，分类 / 标签链接指向
 *   /posts/categories、/posts/tags；
 * - 右侧卡片列只保留「精选文章 / 文章分类 / 热门标签」三张卡片
 *   （复用主题 TkPageCard 卡片壳 + 复刻 HomeCardTopArticle / HomeCardCategory /
 *   HomeCardTag 的列表结构，不再渲染博主信息卡片等其余卡片）；
 *   数据来自独立数据源 @pages/posts.data.mts。
 *
 * 页面挂载于 docs/posts/index.md（layout: page + sidebar: false，与论文落地页一致）。
 */

// 数据源已按日期倒序排序；过滤掉落地页 index.md 自身，并复刻主题的置顶排序
// （getSortPostsByDateAndSticky：sticky 权重大的在前，其余按日期倒序）
const posts = computed(() => {
  const list = postsData.filter((post) => post.url !== "/posts/");
  return list.sort((prev, next) => {
    const prevSticky = prev.sticky;
    const nextSticky = next.sticky;
    if (prevSticky !== undefined && nextSticky !== undefined && prevSticky !== nextSticky) {
      return nextSticky - prevSticky;
    }
    if (prevSticky !== undefined) return -1;
    if (nextSticky !== undefined) return 1;
    return 0; // 日期顺序已由数据源保证，保持 sort 的稳定性即可
  });
});

/** 精选文章（frontmatter top: true），按当前列表顺序编号 */
const topPosts = computed(() => posts.value.filter((post) => post.top));

const tagGroups = computed(() =>
  buildGroups(
    posts.value.map((post) => ({
      title: post.title || post.url,
      url: post.url,
      ...(post.date === undefined ? {} : { date: post.date }),
      tags: post.tags,
      categories: post.categories,
    })),
    "tags"
  )
);

const categoryGroups = computed(() =>
  buildGroups(
    posts.value.map((post) => ({
      title: post.title || post.url,
      url: post.url,
      ...(post.date === undefined ? {} : { date: post.date }),
      tags: post.tags,
      categories: post.categories,
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

/** 精选文章卡片的序号底色（与主题 HomeCardTopArticle 的 getStyle 一致，1 起始取色） */
const numStyle = (num: number) => {
  const palette = tagColor.value;
  const color = palette[num % palette.length] ?? palette[0];
  return color ? { "--tk-num-bg-color": color.text } : {};
};

const tagLink = (name: string) => `/posts/tags?tag=${encodeURIComponent(name)}`;
const categoryLink = (name: string) => `/posts/categories?category=${encodeURIComponent(name)}`;

/** 卡片标题（与主题首页卡片一致：图标 + 文案，经 TkPageCard 的 innerHTML 渲染） */
const topArticleCardTitle = `${topArticleIcon}精选文章`;
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

const pagedPosts = computed(() => posts.value.slice((pageNum.value - 1) * pageSize, pageNum.value * pageSize));
</script>

<template>
  <div class="posts-home">
    <!-- 顶部 Banner：直接复用主题首页的 HomeBanner 组件（读取 blogger / banner 配置） -->
    <TkHomeBanner />

    <!-- 内容区：结构与主题 HomeMain 一致（左侧列表 + 右侧卡片列） -->
    <div class="tk-home-main">
      <div class="tk-home-main__content flx-start-justify-center">
        <div class="tk-home-main__content__post">
          <!-- 文章列表：复刻 HomePost 的列表结构（ul > li > 卡片）与类名 -->
          <div class="tk-home-post is-list">
            <p v-if="!posts.length" class="empty">暂无文章</p>
            <ul v-else aria-label="文章列表">
              <li v-for="post in pagedPosts" :key="post.url">
                <div class="tk-post-item-list">
                  <div class="list flx">
                    <div class="tk-post-item-list__left">
                      <!-- 标题：复用主题 ArticleTitle（与博客文章卡片同一组件） -->
                      <a class="tk-post-item-list__left__title hover-color sle" :href="post.url" :aria-label="post.title">
                        <TkArticleTitle :post="toPost(post)" />
                      </a>
                      <!-- 文章信息行：复刻 ArticleInfo（scope=post）的类名与图标，
                           分类 / 标签链接指向博客板块的标签 / 分类页 -->
                      <div class="tk-post-item-list__left__footer">
                        <div class="tk-article-info post" role="group" aria-label="文章信息">
                          <span v-if="post.date" class="tk-article-info__item" role="group" aria-label="创建时间">
                            <TkIcon :icon="calendarIcon" class="tk-article-info__icon" aria-hidden="true" />
                            <span class="hover-color">{{ post.date }}</span>
                          </span>
                          <span v-if="post.categories.length" class="tk-article-info__item" role="group" aria-label="分类">
                            <TkIcon :icon="folderOpenedIcon" class="tk-article-info__icon" aria-hidden="true" />
                            <a
                              v-for="name in post.categories"
                              :key="`cat-${name}`"
                              class="or hover-color"
                              :href="categoryLink(name)"
                            >
                              {{ name }}
                            </a>
                          </span>
                          <span v-if="post.tags.length" class="tk-article-info__item" role="group" aria-label="标签">
                            <TkIcon :icon="collectionTagIcon" class="tk-article-info__icon" aria-hidden="true" />
                            <a v-for="name in post.tags" :key="`tag-${name}`" class="or hover-color" :href="tagLink(name)">
                              {{ name }}
                            </a>
                          </span>
                        </div>
                      </div>
                      <!-- 摘要行（bottom 位置，与主题 post 配置默认一致） -->
                      <div v-if="post.description" class="tk-post-item-list__left__excerpt bottom">
                        <div class="excerpt">{{ post.description }}</div>
                        <a class="more" :href="post.url" aria-label="文章摘要">阅读全文 ></a>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            </ul>
            <div
              v-if="posts.length >= pageSize"
              class="tk-home-post__pagination flx-justify-center"
              aria-label="分页导航"
            >
              <TkPagination v-model:current-page="pageNum" :page-size="pageSize" :total="posts.length" @current-change="handlePageChange" />
            </div>
          </div>
        </div>

        <div class="tk-home-main__content__info is-right">
          <div class="tk-home-card flx-column">
            <!-- 精选文章卡片：TkPageCard 卡片壳 + 复刻 HomeCardTopArticle 的带序号列表 -->
            <TkPageCard :title="topArticleCardTitle" class="tk-top-article" aria-label="首页精选文章卡片">
              <p v-if="!topPosts.length" class="tk-top-article--empty">暂无精选文章</p>
              <ul v-else class="tk-top-article__list flx-column" aria-label="精选文章列表">
                <li
                  v-for="(post, index) in topPosts"
                  :key="post.url"
                  class="tk-top-article__list__item"
                  :style="numStyle(index + 1)"
                  :aria-label="post.title"
                >
                  <span class="num">{{ index + 1 }}</span>
                  <div class="tk-top-article__list__item__info">
                    <a class="hover-color flx-align-center" :href="post.url" :aria-label="post.title">
                      <TkArticleTitle :post="toPost(post)" />
                    </a>
                    <div class="date">{{ post.date ?? "" }}</div>
                  </div>
                </li>
              </ul>
            </TkPageCard>

            <!-- 分类卡片：TkPageCard 卡片壳 + 复刻 HomeCardCategory 的行式列表 -->
            <TkPageCard
              :title="categoryCardTitle"
              title-link="/posts/categories"
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

            <!-- 标签卡片：TkPageCard 卡片壳 + 复刻 HomeCardTag 的标签云（含主题色板与 active 样式） -->
            <TkPageCard :title="tagCardTitle" title-link="/posts/tags" class="tk-tag" aria-label="首页标签卡片">
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 组件自身只补充极少量样式，其余全部复用主题的 tk- 全局类（与主题首页同一套 CSS） */
.empty {
  padding: 24px 0;
  color: var(--vp-c-text-3);
  font-size: 14px;
  text-align: center;
}
</style>
