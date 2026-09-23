import { createContentLoader } from "vitepress";
import { toDateString, toStringArray } from "../.vitepress/theme/components/taxonomy";

/**
 * 博客板块的独立数据源（与论文板块的 papers.data.mts 完全对称）。
 *
 * 构建期扫描 docs/posts/ 下所有 md 的 frontmatter，仅保留轻量字段（不渲染正文），
 * 被博客的标签 / 分类页组件与自建首页组件（PostsHome）引入，
 * 不再依赖主题 file-content-loader 注入的数据集（usePosts），
 * 与主题文章列表、归档等页面的数据完全解耦。
 * 落地页 index.md（无 tags / categories）会被聚合逻辑自然忽略，
 * 文章列表（PostsHome 组件）按 url 过滤掉落地页自身。
 */

export interface PostItem {
  url: string;
  title: string;
  date?: string;
  /** frontmatter description，供 PostsHome 列表卡片渲染摘要（与博客文章卡片的 excerpt 行为一致） */
  description?: string;
  tags: string[];
  categories: string[];
  /** frontmatter top：精选文章（/posts/ 首页右侧「精选文章」卡片读取） */
  top?: boolean;
  /** frontmatter sticky：置顶权重（列表内置顶文章靠前，数值大者优先） */
  sticky?: number;
}

// createContentLoader 的 transform 已将返回值收窄为 PostItem[]，这里统一断言供组件引用
// eslint-disable-next-line import/no-mixed-default-export
export default createContentLoader("/posts/**/*.md", {
  transform(items) {
    return items
      .map(({ url, frontmatter }) => ({
        url,
        // frontmatter 为索引签名类型，需用方括号访问（noPropertyAccessFromIndexSignature）
        title: typeof frontmatter["title"] === "string" ? frontmatter["title"] : "",
        date: toDateString(frontmatter["date"]),
        description:
          typeof frontmatter["description"] === "string" ? frontmatter["description"] : undefined,
        tags: toStringArray(frontmatter["tags"]),
        categories: toStringArray(frontmatter["categories"]),
        top: frontmatter["top"] === true,
        // sticky 应为数字权重，非法值一律视为未置顶（exactOptionalPropertyTypes：不赋 undefined）
        ...(typeof frontmatter["sticky"] === "number"
          ? { sticky: frontmatter["sticky"] }
          : {}),
      }))
      .sort((prev, next) => (next.date ?? "").localeCompare(prev.date ?? ""));
  },
}) as unknown as PostItem[];

// VitePress 数据加载器约定：客户端虚拟模块只有名为 data 的导出，此处仅为类型提供
declare const data: PostItem[];
export { data };
