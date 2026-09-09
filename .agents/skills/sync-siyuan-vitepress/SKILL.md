---
name: sync-siyuan-vitepress
description: Bidirectionally synchronize selected SiYuan Note documents and a VitePress or Teek documentation site using path mapping, conflict detection, local asset copying, managed sidebar generation, incremental state, and dry-run safeguards. Use for SiYuan-to-VitePress publishing or explicit VitePress-to-SiYuan import; do not use for ordinary VitePress authoring or unrelated note management.
---

# VitePress and SiYuan synchronization

Use this skill for controlled synchronization between a SiYuan document tree and Markdown under a VitePress source root. It supports standard VitePress and the Teek theme. The usual direction is **SiYuan -> VitePress**; reverse import is an explicit operation because it writes to SiYuan.

## Before syncing

1. Locate the VitePress source root. It is commonly `docs/`, but may be a configured `srcDir`; do not treat the repository root as the destination without checking.
2. Identify the SiYuan workspace, notebook, and human-readable root path. Read `C:/Users/zhoub/.codex/skills/siyuan-note/CLI.md` before invoking `siyuan`; prefer `--format json` and pass `--workspace` when ambiguous.
3. Read [references/sync-protocol.md](references/sync-protocol.md) before configuring a new mapping, importing into SiYuan, resolving a conflict, or changing sidebar behavior.
4. Keep the Markdown export outside the VitePress destination. For a document tree use `siyuan export md-zip`; for one document use `siyuan export md`.

## Publish to VitePress

Always run the exact command with `--dry-run` first, review conflicts, warnings, deletes, and sidebar changes, then repeat without it.

```powershell
python scripts/sync.py publish `
  --source $exportZip `
  --dest $vitepressSourceRoot `
  --asset-root $workspace\data\assets `
  --notebook $notebookId `
  --hpath $siyuanRootPath `
  --dry-run
```

Publishing preserves relative Markdown paths and existing destination frontmatter. If a page has no frontmatter, it receives a minimal `title`. Each page's referenced files are copied beside that page under `./assets/`, and links are rewritten accordingly.

Sidebar generation is enabled by default. The script inserts or updates a marked block inside a recognizable `themeConfig` object. If a manual `sidebar` already exists without managed markers, it prints a snippet and leaves the config untouched. Use `--nav none` to disable navigation changes or `--config <path>` when the config is not under `<source-root>/.vitepress/`.

Use `--prune` only when the export scope is authoritative. It removes only files recorded by this mapping's state, and refuses to remove a file changed since the last successful sync.

## Import into SiYuan

Reverse import must be explicitly requested and must include a notebook ID and a non-root human-readable path. It never deletes SiYuan documents.

```powershell
python scripts/sync.py import `
  --source $vitepressSourceRoot `
  --workspace $workspace `
  --notebook $notebookId `
  --hpath /Published/Site `
  --dry-run
```

Path mapping is deterministic: `guide/page.md` maps to `<hpath>/guide/page`, while `guide/index.md` maps to `<hpath>/guide`. Missing parent documents are created only during a non-dry-run import after the notebook and destination path are explicit. VitePress frontmatter is not inserted into the SiYuan document body. Local `./assets/` images are uploaded through the SiYuan CLI and their links are rewritten from the CLI response.

Before a reverse import or other bulk note mutation, create a SiYuan repo snapshot or export backup. Do not infer a notebook, use `/` as the import path, or turn a VitePress deletion into a SiYuan deletion.

## Conflict and content rules

- The state file stores the last successful semantic hash for each side. If both sides changed, stop the whole batch before writing anything and report the mapped path.
- Preserve a VitePress-only edit during publishing rather than overwriting it. Import it explicitly if it should become the SiYuan version.
- Preserve and report unresolved `siyuan://` links, block queries, block attributes, widgets, database views, and missing assets. Do not silently discard constructs that cannot be represented in VitePress Markdown.
- Preserve VitePress/Teek Markdown extensions and frontmatter on the site side. Convert inline math `\(...\)` to `$...$` before importing into SiYuan.
- Treat the state file as mapping-specific. Do not reuse it with another destination, notebook, or root path.

After publishing, run the site's existing package-manager build and, when useful, preview it. Check routes, internal links, images, code blocks, frontmatter-driven Teek features, and generated navigation.
