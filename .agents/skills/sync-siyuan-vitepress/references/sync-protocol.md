# Synchronization protocol

This reference defines the mapping and safety rules used by `scripts/sync.py`. It is intentionally narrower than the VitePress and SiYuan manuals.

## Commands and state

The script has two explicit subcommands:

- `publish`: Markdown file, directory, or SiYuan Markdown zip -> VitePress source root.
- `import`: VitePress Markdown file or directory -> one explicit SiYuan notebook and non-root human-readable path.

The default state file is `.siyuan-sync.json` under the VitePress source root. State version 2 contains the VitePress root, notebook, mapped SiYuan root, per-document `siyuan_hash`, `vitepress_hash`, and `hpath`, plus hashes of files managed by publishing. State version 1 is accepted as a read-only migration source and is rewritten as version 2 after a successful non-dry-run operation. A state file belongs to one mapping; do not share it between sites or notebook roots.

## Path mapping

Paths, rather than SiYuan block IDs, are the stable public mapping:

| VitePress path | SiYuan root `/Published/Site` |
| --- | --- |
| `index.md` | `/Published/Site` |
| `guide/index.md` | `/Published/Site/guide` |
| `guide/start.md` | `/Published/Site/guide/start` |

Publishing retains export-relative Markdown paths. Reverse import strips the `.md` suffix; an `index.md` represents its directory document. The notebook and root path must be supplied explicitly before creating missing documents. Reverse import never deletes notes.

Renaming or moving a path appears as removal plus creation because path mapping intentionally does not use a hidden document ID. Review such changes before using `--prune` or importing the new path.

## Conflict rules

Each successful sync records semantic hashes of both versions. Semantic hashing ignores VitePress frontmatter and normalizes the generated suffix in SiYuan asset filenames so equivalent document bodies compare consistently.

- Only the SiYuan/export side changed: `publish` may update VitePress.
- Only VitePress changed: `publish` preserves it; explicit `import` may update SiYuan.
- Both changed: stop the entire batch with exit code `2`; write neither content, state, nor sidebar.
- An untracked VitePress destination already exists: publishing stops instead of adopting or overwriting it.
- An existing SiYuan path without a baseline may be updated only through explicit reverse import; dry-run reports the missing baseline.

Conflicts are never resolved using modification timestamps. Resolve the content manually, establish a common version, and rerun the dry-run.

## Markdown and frontmatter

On publish, existing destination YAML frontmatter wins, allowing Teek-specific metadata such as categories, tags, cover settings, or layout options to remain site-owned. Otherwise exported frontmatter is retained; if neither side has it, a quoted `title` is derived from the first H1 or filename.

On import, VitePress frontmatter is removed from the note body. Standard Markdown and compatible VitePress/Teek extensions are otherwise preserved. Inline math written as `\(...\)` is converted to `$...$` for SiYuan import.

The following constructs are preserved but reported for review because they may not render equivalently: unresolved `siyuan://` block links and `.sy` links; block queries or embeds; block attribute syntax; database/attribute views; iframe or custom widget content; and missing local assets.

## Assets

On publish, a page reference such as `assets/chart.png` is located relative to the exported page, export root, or explicit `--asset-root`. The copied form is page-local:

```text
guide/topic.md
guide/assets/chart.png
```

The Markdown reference becomes `./assets/chart.png`. Two different files may not claim the same page-local output path; such a collision stops the run.

On import, page-local images under `./assets/` are uploaded with `siyuan asset upload --id <document-id>`. The document body is updated only after successful upload, using the returned `assets/...` path. Remote and data URLs are not copied.

## Sidebar management

Publishing derives a nested VitePress sidebar from the Markdown tree. Folder `index.md` files supply folder labels and links; other pages become children. Path sorting is deterministic and remains compatible with Teek's directory-oriented knowledge-base layout.

The generated property is bounded by:

```ts
// sync-siyuan-vitepress:sidebar:start
sidebar: [],
// sync-siyuan-vitepress:sidebar:end
```

The script may insert this block when exactly one recognizable `themeConfig: { ... }` exists and no manual sidebar property is present. Later runs replace only the marked block. If parsing is unsafe, markers are incomplete, or an unmanaged sidebar already exists, the script prints a snippet and does not modify the config. `--nav none` disables this behavior.

## Safety and verification

1. Keep source and VitePress destination in separate directories.
2. Run the complete command with `--dry-run`; a dry run writes neither content, state, config, nor notes.
3. Review conflicts, unsupported constructs, sidebar output, and every planned delete.
4. Create a SiYuan repo snapshot or data export before reverse import.
5. Run without `--dry-run` only when the mapping and plan are correct.
6. Build and preview VitePress; verify routes, images, internal links, code blocks, and Teek frontmatter behavior.

## Authoritative documentation

- VitePress: <https://vitepress.dev/zh/>
- VitePress routing: <https://vitepress.dev/zh/guide/routing>
- VitePress frontmatter: <https://vitepress.dev/zh/guide/frontmatter>
- VitePress asset handling: <https://vitepress.dev/zh/guide/asset-handling>
- Teek theme: <https://vp.teek.top/>
- SiYuan overview: <https://siyuannote.com/about>
- SiYuan API: <https://github.com/siyuan-note/siyuan/blob/master/API.md>

When installed CLI behavior differs from examples, trust `siyuan <command> --help` on the user's machine.
