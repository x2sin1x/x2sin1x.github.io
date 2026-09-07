# Repository Guidelines

## Project Structure & Module Organization

This is a pnpm-managed VitePress site. Dated articles live in `docs/blogs/`, technical notes in `docs/tech-stack/`, and subject collections in `docs/knowledge-planet/`. Site configuration is in `docs/.vitepress/config.mts`; theme extensions, Vue components, and CSS belong under `docs/.vitepress/theme/`. Put files requiring stable root-relative URLs in `docs/public/`; keep article-specific images beside their article. Do not edit or commit generated `docs/.vitepress/cache/` or `docs/.vitepress/dist/` content.

## Build, Test, and Development Commands

- `pnpm install` installs the locked dependencies from `pnpm-lock.yaml`.
- `pnpm docs:dev` starts the local VitePress server with live reload.
- `pnpm typecheck` runs strict static checks for TypeScript and Vue files.
- `pnpm docs:build` produces the production site and catches broken compilation or configuration.
- `pnpm docs:preview` serves the production build for final inspection.

Run commands from the repository root. Use pnpm so resolution remains consistent with the lockfile.

## Coding Style & Naming Conventions

Use two-space indentation, double-quoted TypeScript strings, semicolons, and trailing commas in multiline objects. TypeScript must satisfy `tsconfig.json`: avoid implicit `any`, use library-provided types, and narrow unions before access. Never silence errors with `@ts-ignore` or broad `any` casts. Name Vue components in PascalCase, such as `AbcScore.vue`. Use kebab-case for English content directories and `index.md` for landing pages. Use YAML front matter when metadata is needed and root-relative links such as `/tech-stack/python/`.

## Testing Guidelines

There is currently no unit-test framework or coverage target. Every Agent must run both `pnpm typecheck` and `pnpm docs:build` after code, configuration, or dependency changes and before reporting completion. Fix all diagnostics; never deliver with known static-check failures. For navigation, theme, component, or CSS changes, also run `pnpm docs:preview` and inspect affected pages at desktop and mobile widths. Verify internal links, images, code blocks, math, and custom `abcjs` fences where relevant. If a required check cannot run, state the exact blocker in the handoff.

## Commit & Pull Request Guidelines

Recent history uses concise Conventional Commit subjects, primarily `feat: ...`. Continue with imperative prefixes such as `feat:`, `fix:`, `docs:`, or `chore:` and keep each commit focused. Pull requests should explain the user-visible result, identify affected sections, link related issues, and report `pnpm docs:build` results. Include before/after screenshots for layout, theme, or rendered-content changes, and avoid checking in generated build output.
