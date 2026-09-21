import { createContentLoader } from "vitepress";
import { toDateString, toStringArray } from "../.vitepress/theme/components/taxonomy";

/**
 * 论文板块的独立数据源（与博客板块的 posts.data.mts 完全对称）。
 *
 * 构建期扫描 docs/papers/ 下所有 md 的 frontmatter，仅保留轻量字段（不渲染正文），
 * 只被论文的标签 / 分类页组件引入，不会进入其他页面的客户端 bundle。
 * 落地页（无 title）与未写标签 / 分类的内容会被聚合逻辑自然忽略。
 */

export interface PaperItem {
  url: string;
  title: string;
  date?: string;
  tags: string[];
  categories: string[];
}

// VitePress 数据加载器约定：构建后客户端虚拟模块只有名为 data 的导出；
// 这里用 declare + export 提供类型，默认导出 createContentLoader 供构建期加载
// eslint-disable-next-line import/no-mixed-default-export
export default createContentLoader("/papers/**/*.md", {
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
}) as unknown as PaperItem[];

declare const data: PaperItem[];
export { data };
