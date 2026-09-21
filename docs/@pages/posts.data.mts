import { createContentLoader } from "vitepress";
import { toDateString, toStringArray } from "../.vitepress/theme/components/taxonomy";

/**
 * 博客板块的独立数据源（与论文板块的 papers.data.mts 完全对称）。
 *
 * 构建期扫描 docs/posts/ 下所有 md 的 frontmatter，仅保留轻量字段（不渲染正文），
 * 只被博客的标签 / 分类页组件引入，不进入其他页面的客户端 bundle。
 * 不再依赖主题 file-content-loader 注入的数据集（usePosts），
 * 与主题文章列表、归档等页面的数据完全解耦。
 * 落地页 index.md（layout: home，无 tags / categories）会被聚合逻辑自然忽略。
 */

export interface PostItem {
  url: string;
  title: string;
  date?: string;
  tags: string[];
  categories: string[];
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
        tags: toStringArray(frontmatter["tags"]),
        categories: toStringArray(frontmatter["categories"]),
      }))
      .sort((prev, next) => (next.date ?? "").localeCompare(prev.date ?? ""));
  },
}) as unknown as PostItem[];

// VitePress 数据加载器约定：客户端虚拟模块只有名为 data 的导出，此处仅为类型提供
declare const data: PostItem[];
export { data };
