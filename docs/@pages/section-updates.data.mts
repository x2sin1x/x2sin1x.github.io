import { statSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createContentLoader } from "vitepress";

export interface SectionUpdateItem {
  url: string;
  relativePath: string;
  title: string;
  date: string;
  sortDate: number;
  frontmatter: Record<string, unknown>;
}

const docsDir = fileURLToPath(new URL("../", import.meta.url));

function formatLocalDate(value: Date | string): string {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  const pad = (part: number) => String(part).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function filePathFromUrl(url: string): string {
  const relativePath = url.slice(1);
  const markdownPath = relativePath.endsWith("/")
    ? `${relativePath}index.md`
    : `${relativePath}.md`;
  return join(docsDir, markdownPath);
}

function titleFromSource(
  url: string,
  frontmatter: Record<string, unknown>,
  source: string | undefined,
): string {
  if (typeof frontmatter["title"] === "string") return frontmatter["title"];

  const body = (source ?? "").replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, "");
  const heading = body.match(/^#\s+(.+?)\s*#*\s*$/m)?.[1];
  if (heading) return heading;

  const pathPart = url.replace(/\/$/, "").split("/").pop() ?? url;
  return basename(pathPart).replace(/^\d+\./, "");
}

function updateItem(item: {
  url: string;
  src: string | undefined;
  frontmatter: Record<string, unknown>;
}): SectionUpdateItem | undefined {
  const { frontmatter, url, src } = item;
  if (
    frontmatter["article"] === false ||
    frontmatter["articleUpdate"] === false ||
    frontmatter["layout"] === "home"
  ) {
    return undefined;
  }

  const frontmatterDate = frontmatter["date"];
  const stat = frontmatterDate ? undefined : statSync(filePathFromUrl(url));
  const rawDate = frontmatterDate || stat?.birthtime || stat?.atime || new Date(0);
  const sortDate = new Date(rawDate instanceof Date ? rawDate : String(rawDate)).getTime();

  return {
    url,
    relativePath: url,
    title: titleFromSource(url, frontmatter, src),
    date: formatLocalDate(rawDate instanceof Date ? rawDate : String(rawDate)),
    sortDate: Number.isNaN(sortDate) ? 0 : sortDate,
    frontmatter,
  };
}

// Only content articles enter the list; utility pages still display the global recent list.
export default createContentLoader(
  [
    "/posts/**/*.md",
    "/tech-stack/**/*.md",
    "/knowledge-planet/**/*.md",
    "/papers/**/*.md",
    "/repos/**/*.md",
  ],
  {
    includeSrc: true,
    transform(items) {
      return items
        .map(updateItem)
        .filter((item): item is SectionUpdateItem => item !== undefined)
        .sort((prev, next) => next.sortDate - prev.sortDate);
    },
  },
) as unknown as SectionUpdateItem[];

declare const data: SectionUpdateItem[];
export { data };
