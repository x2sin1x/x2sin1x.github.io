# SiYuan CLI

思源笔记内置 `siyuan` CLI，可直接访问工作空间数据，无需启动内核 HTTP 服务。适合脚本化处理、批量管理，以及配合 Agent 对本地笔记进行读写操作。

```bash
siyuan [global flags] <command> [args]
```

## Install and Locate

The executable lives under `<SiYuan install>/resources/kernel/`.

- Windows: the installer usually adds the kernel directory to `PATH`; the executable may be available as `siyuan` or `siyuan.exe`.
- macOS:

```bash
ln -s /Applications/SiYuan.app/Contents/Resources/kernel/SiYuan-Kernel /usr/local/bin/siyuan
```

- Linux:

```bash
ln -s <install-dir>/resources/kernel/SiYuan-Kernel /usr/local/bin/siyuan
```

Probe availability:

```powershell
Get-Command siyuan
siyuan --help
siyuan --version
```

## Global Flags

| Flag | Short | Default | Meaning |
| --- | --- | --- | --- |
| `--workspace` | `-w` | `SIYUAN_WORKSPACE_PATH`, registered workspace, or `~/SiYuan` | Specify workspace path |
| `--format` | `-f` | `table` | Output format: `table` or `json` |
| `--dry-run` | | `false` | Validate write operations without applying changes |

Use `--format json` for scriptable output. Use `--dry-run` before modifying or deleting data.

PowerShell argument-array pattern:

```powershell
$args = @("--workspace", "D:\SiYuan", "--format", "json", "document", "search", "关键词")
siyuan @args
```

## Argument Conventions

- Long flags start with `--` and take values separated by spaces, such as `--workspace /path`.
- Short flags can replace long flags when available, such as `-w /path`.
- Brackets in command docs mean optional parameters.
- Boolean flags are used without values, such as `--dry-run`.
- Some flags can repeat, such as `--notebook box1 --notebook box2`.

## Targeting Notes

- `--id`: target a block or document by exact block ID.
- `--hpath`: target a human-readable path, such as `/folder/document`.
- `--parent`: target a parent block/document when inserting, appending, prepending, or moving blocks.
- `--file`: read long Markdown or structured content from a local file instead of shell arguments.

When importing Markdown text, convert inline math from `\(...\)` to `$...$` first.

## Safety Workflow

For destructive or bulk operations:

1. Identify the workspace with `siyuan --format json workspace info`.
2. Create a checkpoint with `siyuan repo create --memo "before batch edit"` or export a backup with `siyuan export data --output ./full-backup.zip`.
3. Run the command with `--dry-run`.
4. Inspect the dry-run output.
5. Run the command again without `--dry-run` only when the target is correct.

Treat `sql` as read-only. Prefer `SELECT` statements.

## Help

```bash
siyuan --help
siyuan block --help
siyuan document --help
siyuan search --help
```

## Workspace

```bash
siyuan --format json workspace list
siyuan --format json workspace info
siyuan --workspace /path/to/workspace --format json workspace info
```

## Notebooks

```bash
siyuan --format json notebook list
siyuan --format json notebook create --name "我的笔记本"
siyuan --dry-run notebook remove --id notebook-id
siyuan --dry-run notebook rename --id notebook-id --name "新名称"
siyuan --format json notebook open --id notebook-id
siyuan --format json notebook close --id notebook-id
siyuan --format json notebook set-icon --id notebook-id --icon "1f4ca"
siyuan --format json notebook random-icon --id notebook-id
```

## Documents

```bash
siyuan --format json document list --notebook notebook-id
siyuan --format json document list --notebook notebook-id --hpath "/文件夹"
siyuan --format json document create --notebook notebook-id --title "新文档"
siyuan --format json document create --notebook notebook-id --title "新文档" --path "/文件夹"
siyuan --format json document create --notebook notebook-id --title "新文档" --markdown "# 标题"
siyuan --format json document get --id doc-id
siyuan --format json document info --id doc-id
siyuan --format json document search "关键词"
siyuan --dry-run document rename --id doc-id --title "新标题"
siyuan --dry-run document duplicate --id doc-id
siyuan --dry-run document move --id doc-id --notebook target-nb
siyuan --dry-run document move --id doc-id --notebook target-nb --hpath "/目标文件夹"
siyuan --dry-run document remove --id doc-id
```

## Blocks

Use `--data` for short content and `--file` for longer Markdown.

```bash
siyuan --format json block get --id block-id
siyuan --format json block children --id block-id
siyuan --format json block breadcrumb --id block-id
siyuan --format json block dom --id block-id
siyuan --format json block kramdown --id block-id
siyuan --format json block kramdown --id block-id --mode md
siyuan --format json block stat --id doc-id

siyuan --dry-run block insert --parent parent-id --data "# 新标题"
siyuan --dry-run block insert --parent parent-id --file ./content.md
siyuan --dry-run block insert --parent parent-id --data "段落" --previous sibling-id
siyuan --dry-run block append --parent parent-id --data "- 列表项"
siyuan --dry-run block append --parent parent-id --file ./content.md
siyuan --dry-run block prepend --parent parent-id --data "> 引用"
siyuan --dry-run block update --id block-id --data "修改后内容"
siyuan --dry-run block update --id block-id --file ./content.md
siyuan --dry-run block delete --id block-id
siyuan --dry-run block move --id block-id --parent target-id
siyuan --dry-run block move --id block-id --parent target-id --previous sibling-id

siyuan --format json block batch-get --ids "id1,id2,id3"
siyuan --format json block batch-kramdown --ids "id1,id2,id3"
```

## Outline

```bash
siyuan --format json outline get --id doc-id
```

## Search

Search supports notebook, path, block type, subtype, search method, ordering, pagination, and grouping.

```bash
siyuan --format json search "关键词"
siyuan --format json search "关键词" --notebook box1 --notebook box2
siyuan --format json search "关键词" --path "/目录"
siyuan --format json search "关键词" --type document --type heading
siyuan --format json search "关键词" --subtype o --subtype u
siyuan --format json search "关键词" --method 2
siyuan --format json search "关键词" --order-by 4 --page 1 --page-size 20
siyuan --format json search "关键词" --group-by 1
```

Common values:

- `--type`: `document`, `heading`, `paragraph`, `list`, etc.
- `--subtype`: `o` ordered list, `u` unordered list, `t` task list.
- `--method`: `0` keyword, `1` query syntax, `2` SQL, `3` regex, `4` fuzzy.
- `--group-by`: `0` no grouping, `1` group by document.

## SQL

```bash
siyuan --format json sql "SELECT * FROM blocks WHERE type='d'"
siyuan --format json sql "SELECT id, content FROM blocks WHERE type='h'" --limit 50
```

## Sync

```bash
siyuan sync push
siyuan sync pull
siyuan --format json sync status
```

## Export

```bash
siyuan export md --id doc-id
siyuan export md --id doc-id --output ./output.md
siyuan export html --id doc-id --output ./output.html
siyuan export preview --id doc-id --output ./preview.html
siyuan export docx --id doc-id --output ./output.docx
siyuan export sy --id doc-id --output ./backup.sy.zip
siyuan export md-zip --id doc-id --output ./archive.zip
siyuan export data --output ./full-backup.zip
```

## Import

```bash
siyuan import md --file ./notes --notebook notebook-id
siyuan import md --file ./doc.md --notebook notebook-id --hpath "/导入目录"
siyuan import sy --file ./backup.sy.zip --notebook notebook-id
siyuan import data --file ./full-backup.zip
```

## History

```bash
siyuan --format json history list
siyuan --format json history list --notebook notebook-id --op delete --type 0 --page 1
siyuan --format json history search "关键词" --notebook notebook-id --op update
siyuan --format json history get --path "history/..."
siyuan --dry-run history rollback --path "history/..."
siyuan --dry-run history clear
```

`--op`: `delete`, `update`, `create`.

`--type`: `0` document name, `1` content, `2` assets, `3` document ID, `4` database.

## Repo Snapshots

```bash
siyuan --format json repo list
siyuan --format json repo list --tag --page 1
siyuan repo create --memo "升级前备份"
siyuan repo tag --id snapshot-id --name "v1.0"
siyuan repo untag --name "v1.0"
siyuan --dry-run repo checkout --id snapshot-id
siyuan --format json repo diff --left id1 --right id2
siyuan --format json repo search "关键词"
siyuan repo purge
siyuan --format json repo file get --id file-id
siyuan --dry-run repo file rollback --id file-id
siyuan repo file open --id file-id
siyuan repo file export --id file-id
```

## Backlinks and Mentions

```bash
siyuan --format json ref backlinks --id block-id
siyuan --format json ref backlinks --id block-id --keyword "过滤词" --sort 4
siyuan --format json ref mentions --id block-id
siyuan ref refresh --id block-id
```

`--sort`: `0` updated desc, `1` updated asc, `2` created desc, `3` created asc, `4` name desc, `5` name asc, `6` natural desc, `7` natural asc.

## Tags

```bash
siyuan --format json tag list
siyuan --format json tag list --keyword "项目"
siyuan --dry-run tag remove --label "待办"
siyuan --dry-run tag rename --old "旧" --new "新"
```

## Attributes

```bash
siyuan --format json attr get --id block-id
siyuan --dry-run attr set --id block-id --attr icon=1f4ca
siyuan --dry-run attr set --id block-id --attr tags="标签1, 标签2" --attr custom-key=custom-value
siyuan --format json attr batch-get --ids "id1,id2,id3"
```

## Assets

```bash
siyuan asset upload --id doc-id --file ./image.png --file ./doc.pdf
siyuan --format json asset unused
siyuan --dry-run asset clean
siyuan --dry-run asset clean --path "assets/xxx.png"
siyuan --format json asset stat --path "assets/image/xxx.png"
```

## Bookmarks

```bash
siyuan --format json bookmark list
siyuan --format json bookmark labels
siyuan --dry-run bookmark remove --label "书签名"
siyuan --dry-run bookmark rename --old "旧" --new "新"
```

## Databases

```bash
siyuan --format json database search "关键词"
siyuan --format json database get --av db-id
siyuan --format json database render --av db-id --view view-id --query "筛选" --page 1 --size 50
siyuan --format json database keys --av db-id

siyuan --dry-run database key add --av db-id --name "状态" --type select
siyuan --dry-run database key add --av db-id --name "金额" --type number --icon 1f4b0
siyuan --dry-run database key add --av db-id --name "备注" --type text --prev previous-key-id
siyuan --dry-run database key remove --av db-id --key key-id --remove-relation-dest

siyuan --format json database unused
siyuan --dry-run database clean
siyuan --dry-run database clean --av db-id

siyuan --dry-run database item add --av db-id
siyuan --dry-run database item add --av db-id --block block-id --content "文本"
siyuan --dry-run database item add --av db-id --view view-id --previous prev-id
siyuan --dry-run database item remove --av db-id --ids "item1,item2"
siyuan --dry-run database item update --av db-id --key key-id --item item-id --value '{"content": "新值"}'
```

Field types include `block`, `text`, `number`, `date`, `select`, `mSelect`, `url`, `email`, `phone`, `mAsset`, `template`, `created`, `updated`, `checkbox`, `relation`, `rollup`, and `lineNumber`.

## Daily Notes

```bash
siyuan --format json dailynote create --notebook notebook-id
siyuan --dry-run dailynote append --notebook notebook-id --data "- [ ] 待办"
siyuan --dry-run dailynote append --notebook notebook-id --file ./content.md
siyuan --dry-run dailynote prepend --notebook notebook-id --data "## 今日重点"
```

## Templates

Template paths are relative to `data/templates`.

```bash
siyuan --format json template search
siyuan --format json template search "会议"
siyuan template get --path templates/周报.md
siyuan --dry-run template create --name "周报" --data "# 周报"
siyuan --dry-run template create --name "周报" --file ./weekly.md
siyuan --dry-run template create --name "周报" --data "# 周报" --overwrite
siyuan template render --path templates/周报.md --id doc-id
siyuan --dry-run template save-as --id doc-id --name "会议纪要"
siyuan --dry-run template save-as --id doc-id --name "会议纪要" --overwrite
siyuan --dry-run template remove --path templates/周报.md
```

## Workspace Files

All paths are workspace-relative.

```bash
siyuan --format json file list /temp
siyuan file read /temp/readme.md
siyuan file write /temp/new.txt --file ./localfile.txt
siyuan --dry-run file delete /temp/temp
siyuan --dry-run file rename /temp/old /temp/new
siyuan --dry-run file copy /temp/src /temp/dst
siyuan file grep --pattern "TODO" --path /temp
siyuan file grep --pattern "func " --path /temp --include "*.go" --context 2
siyuan file find /temp --include "*.md"
siyuan --format json file stat /temp/readme.md
```

## System

```bash
siyuan --format json system current-time
```
