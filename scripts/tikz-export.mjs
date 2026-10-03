// TikZ 离线导出脚本：将目录下的 *.tex（裸 tikzpicture 源码）编译为同名 .webp 图片。
//
// 用法：pnpm tikz:export <包含 .tex 文件的目录>
// 例如：pnpm tikz:export docs/posts/2022/challenge-2022-gaokao-national-paper-b-math-final-problem/tikz-src
//
// 管线：node-tikzjax（WASM TeX，无需本机 TeX Live / ghostscript）→ SVG → sharp 栅格化 → webp。
// 注意：.tex 是临时源文件，导出完成后应删除；正式的 TikZ 源码以文章中图片下方的
// 代码块为准（修改图示时：先临时写出 .tex → 导出 → 同步更新文章代码块 → 删除 .tex）。
// 文字使用 BaKoMA Computer Modern 字体（标准 Unicode 编码）。SVG 栅格化依赖 fontconfig
// 按字体族名（cmmi10 等）解析文字，脚本会在缺失时把随包的 TTF 安装到 ~/.fonts。
import { readdirSync, readFileSync, existsSync, mkdirSync, copyFileSync } from "node:fs";
import { execSync } from "node:child_process";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import sharp from "sharp";

const require = createRequire(import.meta.url);
const tikzjax = await import("node-tikzjax");
const tex2svg = tikzjax.default?.default ?? tikzjax.default ?? tikzjax;
const pkgDir = path.dirname(require.resolve("node-tikzjax/package.json"));
const bakomaDir = path.join(pkgDir, "css", "bakoma", "ttf");

const dir = process.argv[2];
if (!dir) {
  console.error("Usage: pnpm tikz:export <dir-with-tex-files>");
  process.exit(1);
}

/** 确保 BaKoMA CM 字体对 fontconfig 可见（librsvg 栅格化 SVG 文字所需）。 */
function ensureFonts() {
  const probe = () => {
    try {
      return execSync("fc-list", { encoding: "utf8" }).includes("cmmi10");
    } catch {
      return true; // 无 fontconfig（如 Windows），交由系统字体回退，不阻塞导出
    }
  };
  if (probe()) return;
  const target = path.join(os.homedir(), ".fonts");
  mkdirSync(target, { recursive: true });
  for (const file of readdirSync(bakomaDir).filter((f) => f.endsWith(".ttf"))) {
    copyFileSync(path.join(bakomaDir, file), path.join(target, file));
  }
  execSync("fc-cache -f", { stdio: "ignore" });
  console.log("已安装 BaKoMA Computer Modern 字体到 ~/.fonts");
}

ensureFonts();

for (const file of readdirSync(dir).filter((f) => f.endsWith(".tex"))) {
  const name = path.basename(file, ".tex");
  const body = readFileSync(path.join(dir, file), "utf8");
  // node-tikzjax 内部已使用 standalone 文档类包装，输入只需 \begin{document} ... \end{document}
  const source = `\\begin{document}\n${body}\n\\end{document}\n`;
  const svg = await tex2svg(source);
  if (!svg.includes("<svg")) {
    console.error(`✗ ${name}: 未生成 SVG`);
    process.exitCode = 1;
    continue;
  }
  await sharp(Buffer.from(svg), { density: 300 })
    .flatten({ background: "#ffffff" })
    .webp({ quality: 90 })
    .toFile(path.join(dir, `${name}.webp`));
  console.log(`✓ ${name}.webp`);
}
