/**
 * 自建标签 / 分类系统的公共类型与聚合逻辑。
 *
 * 博客（/posts/）与论文（/papers/）各自拥有独立的标签 / 分类体系：
 * - 博客数据来自主题 file-content-loader 注入的文章数据集（usePosts，papers 已从源头排除）；
 * - 论文数据来自独立的 createContentLoader 数据源（docs/@pages/papers.data.ts）；
 * - 两者都通过 buildGroups 聚合、由 TaxonomyPage 组件渲染，但 URL 空间完全隔离
 *   （/tags、/categories 与 /papers/tags、/papers/categories）。
 */

export interface TaxonomySourceItem {
  title: string;
  url: string;
  date?: string;
  /** 原始标签数据（可能是字符串、字符串数组或嵌套数组，统一由 buildGroups 扁平化） */
  tags?: unknown;
  categories?: unknown;
}

export interface TaxonomyGroup {
  name: string;
  /** 该标签 / 分类下的文章，按传入顺序（日期倒序）排列 */
  posts: { title: string; url: string; date?: string }[];
}

/** 把任意 frontmatter 值安全地扁平化为字符串数组（单字符串 / 数组 / 嵌套数组）；
 *  也供数据加载器（@pages/papers.data.mts、@pages/posts.data.mts）复用 */
export function toStringArray(value: unknown): string[] {
  if (typeof value === "string") return value ? [value] : [];
  if (!Array.isArray(value)) return [];
  return value.flatMap((entry) => toStringArray(entry));
}

/** YAML 的 date 字段会被 gray-matter 解析为 Date 对象（UTC 零点），统一取日期部分；
 *  也供数据加载器复用 */
export function toDateString(value: unknown): string | undefined {
  if (value instanceof Date) return value.toISOString().slice(0, 10);
  if (typeof value === "string") return value.slice(0, 10);
  return undefined;
}

/**
 * 按 kind（tags / categories）把文章聚合为分组，组内文章保持传入顺序，
 * 分组按文章数倒序、同名次序按字典序稳定排列。传入列表需预先按日期倒序排序。
 */
export function buildGroups(items: TaxonomySourceItem[], kind: "tags" | "categories"): TaxonomyGroup[] {
  const map = new Map<string, TaxonomyGroup["posts"]>();
  for (const item of items) {
    // exactOptionalPropertyTypes：date 为 undefined 时不能显式赋给可选属性
    const post =
      item.date === undefined
        ? { title: item.title, url: item.url }
        : { title: item.title, url: item.url, date: item.date };
    for (const name of toStringArray(item[kind])) {
      const group = map.get(name);
      if (group) group.push(post);
      else map.set(name, [post]);
    }
  }
  return Array.from(map, ([name, posts]) => ({ name, posts })).sort(
    (prev, next) => next.posts.length - prev.posts.length || prev.name.localeCompare(next.name, "zh-CN")
  );
}
