#!/usr/bin/env python3
"""Bidirectional, path-mapped synchronization for SiYuan and VitePress."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import unquote


STATE_VERSION = 2
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+?)\s*#*\s*$", re.MULTILINE)
IMAGE_RE = re.compile(r"(!\[[^\]]*\]\()([^)]*)(\))")
LINK_RE = re.compile(r"(?<!!)(\[[^\]]*\]\()([^)]*)(\))")
SIYUAN_URL_RE = re.compile(r"siyuan://(?:blocks?/)?([\w-]+)")
SIYUAN_ASSET_SUFFIX_RE = re.compile(r"-\d{14}-[a-z0-9]{7}(?=\.[^.]+$)")
UNSUPPORTED_PATTERNS = (
    (re.compile(r"\{\{\s*select\b", re.IGNORECASE), "block query/embed"),
    (re.compile(r"data-type=[\"']NodeAttributeView", re.IGNORECASE), "database view"),
    (re.compile(r"<iframe\b", re.IGNORECASE), "embedded iframe/widget"),
    (re.compile(r"\{:\s+[^}]*\bid=", re.IGNORECASE), "SiYuan block attributes"),
)
NAV_START = "// sync-siyuan-vitepress:sidebar:start"
NAV_END = "// sync-siyuan-vitepress:sidebar:end"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip() + "\n"


def split_frontmatter(text: str) -> tuple[str | None, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    return match.group(0), text[match.end() :]


def split_markdown_target(target: str) -> tuple[str, str]:
    value = target.strip()
    if value.startswith("<") and ">" in value:
        end = value.index(">")
        return value[1:end], value[end + 1 :]
    match = re.match(r'([^\s]+)(\s+["\'].*)?$', value)
    return (match.group(1), match.group(2) or "") if match else (value, "")


def asset_parts(target: str) -> PurePosixPath | None:
    path_part, _ = split_markdown_target(target)
    clean = unquote(path_part.split("#", 1)[0].split("?", 1)[0]).replace("\\", "/")
    if clean.startswith(("http://", "https://", "data:")):
        return None
    parts = list(PurePosixPath(clean).parts)
    if "assets" not in parts:
        return None
    index = len(parts) - 1 - parts[::-1].index("assets")
    result = PurePosixPath(*parts[index + 1 :])
    if not result.parts or ".." in result.parts:
        return None
    return result


def semantic_hash(text: str) -> str:
    """Hash note content while ignoring VitePress frontmatter and SiYuan asset IDs."""
    _, body = split_frontmatter(text)

    def normalize_asset(match: re.Match[str]) -> str:
        parts = asset_parts(match.group(2))
        if parts is None:
            return match.group(0)
        name = parts.name
        while SIYUAN_ASSET_SUFFIX_RE.search(name):
            name = SIYUAN_ASSET_SUFFIX_RE.sub("", name)
        logical = PurePosixPath(*parts.parts[:-1], name).as_posix()
        return match.group(1) + "asset://" + logical + match.group(3)

    canonical = IMAGE_RE.sub(normalize_asset, normalize_newlines(body))
    canonical = LINK_RE.sub(normalize_asset, canonical)
    return sha256(canonical.encode("utf-8"))


def title_for(text: str, path: Path) -> str:
    match = H1_RE.search(split_frontmatter(text)[1])
    if match:
        return re.sub(r"[*_`]", "", match.group(1)).strip()
    if path.name.lower() == "index.md" and path.parent.name:
        return path.parent.name
    return path.stem.replace("-", " ").replace("_", " ").strip() or "Untitled"


def frontmatter_for(text: str, path: Path, existing: str | None) -> str:
    if existing:
        current, _ = split_frontmatter(existing)
        if current:
            return current.rstrip() + "\n\n"
    source_frontmatter, _ = split_frontmatter(text)
    if source_frontmatter:
        return source_frontmatter.rstrip() + "\n\n"
    title = title_for(text, path).replace("\\", "\\\\").replace('"', '\\"')
    return f'---\ntitle: "{title}"\n---\n\n'


def report_unsupported(text: str, rel: Path, warnings: list[str]) -> None:
    for pattern, label in UNSUPPORTED_PATTERNS:
        if pattern.search(text):
            warnings.append(f"{rel.as_posix()}: preserved unsupported {label}")


def locate_asset(
    target: str,
    markdown_file: Path,
    source_root: Path,
    asset_root: Path | None,
) -> Path | None:
    path_part, _ = split_markdown_target(target)
    clean = unquote(path_part.split("#", 1)[0].split("?", 1)[0])
    parts = asset_parts(target)
    candidates: list[Path] = []
    if not clean.startswith("/"):
        candidates.append(markdown_file.parent / Path(clean))
    if parts is not None:
        candidates.append(source_root / "assets" / Path(*parts.parts))
        if asset_root is not None:
            candidates.append(asset_root / Path(*parts.parts))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def display_asset_target(path: PurePosixPath, suffix: str) -> str:
    value = "./assets/" + path.as_posix()
    if " " in value:
        value = f"<{value}>"
    return value + suffix


def transform_publish(
    text: str,
    rel: Path,
    source_file: Path,
    source_root: Path,
    asset_root: Path | None,
    existing: str | None,
    planned: dict[Path, bytes],
    warnings: list[str],
) -> str:
    _, body = split_frontmatter(text)
    report_unsupported(body, rel, warnings)

    def replace_image(match: re.Match[str]) -> str:
        target, suffix = split_markdown_target(match.group(2))
        if SIYUAN_URL_RE.search(target):
            warnings.append(f"{rel.as_posix()}: unresolved SiYuan block link {target}")
            return match.group(0)
        parts = asset_parts(target)
        if parts is None:
            return match.group(0)
        asset = locate_asset(target, source_file, source_root, asset_root)
        if asset is None:
            warnings.append(f"{rel.as_posix()}: missing asset {target}")
            return match.group(0)
        output = rel.parent / "assets" / Path(*parts.parts)
        data = asset.read_bytes()
        if output in planned and planned[output] != data:
            raise SystemExit(f"Asset collision with different content: {output.as_posix()}")
        planned[output] = data
        return match.group(1) + display_asset_target(parts, suffix) + match.group(3)

    body = IMAGE_RE.sub(replace_image, body)

    def normalize_link(match: re.Match[str]) -> str:
        target, suffix = split_markdown_target(match.group(2))
        if SIYUAN_URL_RE.search(target):
            warnings.append(f"{rel.as_posix()}: unresolved SiYuan block link {target}")
            return match.group(0)
        if target.split("#", 1)[0].split("?", 1)[0].endswith(".sy"):
            warnings.append(f"{rel.as_posix()}: unsupported .sy link {target}")
            return match.group(0)
        parts = asset_parts(target)
        if parts is not None:
            asset = locate_asset(target, source_file, source_root, asset_root)
            if asset is None:
                warnings.append(f"{rel.as_posix()}: missing asset {target}")
                return match.group(0)
            output = rel.parent / "assets" / Path(*parts.parts)
            data = asset.read_bytes()
            if output in planned and planned[output] != data:
                raise SystemExit(f"Asset collision with different content: {output.as_posix()}")
            planned[output] = data
            return match.group(1) + display_asset_target(parts, suffix) + match.group(3)
        return match.group(1) + target.replace("\\", "/") + suffix + match.group(3)

    body = LINK_RE.sub(normalize_link, body)
    return frontmatter_for(text, rel, existing) + normalize_newlines(body)


def transform_import(text: str) -> str:
    _, body = split_frontmatter(text)
    body = re.sub(r"\\\((.+?)\\\)", r"$\1$", body)
    return normalize_newlines(body)


def safe_extract(archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as bundle:
        root = destination.resolve()
        for member in bundle.infolist():
            target = (root / member.filename).resolve()
            try:
                target.relative_to(root)
            except ValueError as exc:
                raise SystemExit(f"Unsafe zip member: {member.filename}") from exc
        bundle.extractall(root)


def prepare_source(source: Path, stack: ExitStack) -> Path:
    if source.is_file() and source.suffix.lower() == ".zip":
        temp_dir = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="siyuan-vitepress-")))
        safe_extract(source, temp_dir)
        return temp_dir
    return source


def collect_markdown(source: Path) -> dict[Path, Path]:
    if source.is_file():
        if source.suffix.lower() not in {".md", ".markdown"}:
            raise SystemExit("A file source must be Markdown or .zip")
        return {Path(source.name).with_suffix(".md"): source}
    return {
        path.relative_to(source).with_suffix(".md"): path
        for path in source.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".markdown"}
    }


def read_state(path: Path) -> dict:
    if not path.exists():
        return {"version": STATE_VERSION, "vitepress_root": None, "documents": {}, "managed": {}}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read state file {path}: {exc}")
    if state.get("version") == 1 and isinstance(state.get("files"), dict):
        managed = dict(state["files"])
        documents = {
            rel: {"siyuan_hash": None, "vitepress_hash": digest, "hpath": None}
            for rel, digest in managed.items()
            if rel.lower().endswith(".md")
        }
        return {
            "version": STATE_VERSION,
            "vitepress_root": state.get("destination"),
            "documents": documents,
            "managed": managed,
        }
    if state.get("version") != STATE_VERSION:
        raise SystemExit(f"Unsupported state file version: {path}")
    if not isinstance(state.get("documents"), dict) or not isinstance(state.get("managed"), dict):
        raise SystemExit(f"Invalid state file: {path}")
    return state


def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def ensure_separate(source: Path, dest: Path) -> None:
    if source == dest or source in dest.parents or dest in source.parents:
        raise SystemExit("Source and destination must be separate")


def validate_state_mapping(
    state: dict,
    vitepress_root: Path,
    notebook: str | None,
    hpath_root: str | None,
) -> None:
    recorded_root = state.get("vitepress_root")
    if recorded_root and Path(recorded_root).resolve() != vitepress_root.resolve():
        raise SystemExit("State file belongs to a different VitePress root")
    recorded_notebook = state.get("notebook")
    if recorded_notebook and notebook and recorded_notebook != notebook:
        raise SystemExit("State file belongs to a different SiYuan notebook")
    recorded_hpath = state.get("hpath_root")
    if recorded_hpath and hpath_root and normalize_hpath(recorded_hpath) != normalize_hpath(hpath_root):
        raise SystemExit("State file belongs to a different SiYuan root path")


def nav_items(markdown: dict[Path, Path], rendered: dict[Path, bytes]) -> list[dict]:
    root: dict = {"files": [], "dirs": {}}
    for rel in sorted(markdown, key=lambda path: path.as_posix().lower()):
        node = root
        for part in rel.parent.parts:
            node = node["dirs"].setdefault(part, {"files": [], "dirs": {}})
        node["files"].append((rel, title_for(rendered[rel].decode("utf-8"), rel)))

    def build(node: dict, prefix: PurePosixPath) -> list[dict]:
        items: list[dict] = []
        indexes = [(rel, title) for rel, title in node["files"] if rel.name.lower() == "index.md"]
        for rel, title in node["files"]:
            if rel.name.lower() != "index.md":
                items.append({"text": title, "link": "/" + rel.with_suffix("").as_posix()})
        for name, child in sorted(node["dirs"].items(), key=lambda pair: pair[0].lower()):
            child_prefix = prefix / name
            child_index = next(
                ((rel, title) for rel, title in child["files"] if rel.name.lower() == "index.md"),
                None,
            )
            entry: dict = {"text": child_index[1] if child_index else name}
            if child_index:
                entry["link"] = "/" + child_prefix.as_posix().lstrip("./") + "/"
            children = build(child, child_prefix)
            if children:
                entry["items"] = children
            items.append(entry)
        if prefix == PurePosixPath("."):
            for _, title in indexes:
                items.insert(0, {"text": title, "link": "/"})
        return items

    return build(root, PurePosixPath("."))


def find_matching_brace(text: str, open_at: int) -> int | None:
    depth = 0
    quote: str | None = None
    escaped = False
    line_comment = False
    block_comment = False
    i = open_at
    while i < len(text):
        char = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
        elif block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                i += 1
        elif quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in "'\"`":
            quote = char
        elif char == "/" and nxt == "/":
            line_comment = True
            i += 1
        elif char == "/" and nxt == "*":
            block_comment = True
            i += 1
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def sidebar_block(items: list[dict], indent: str) -> str:
    payload = json.dumps(items, ensure_ascii=False, indent=2)
    payload = ("\n" + indent).join(payload.splitlines())
    return f"{indent}{NAV_START}\n{indent}sidebar: {payload},\n{indent}{NAV_END}"


def plan_sidebar(config: Path, items: list[dict], warnings: list[str]) -> bytes | None:
    if not config.is_file():
        warnings.append(f"sidebar not updated: config not found at {config}")
        return None
    text = config.read_text(encoding="utf-8")
    start = text.find(NAV_START)
    end = text.find(NAV_END)
    if (start >= 0) != (end >= 0) or (start >= 0 and end < start):
        warnings.append("sidebar not updated: incomplete managed markers")
        return None
    if start >= 0:
        line_start = text.rfind("\n", 0, start) + 1
        indent = text[line_start:start]
        line_end = text.find("\n", end)
        line_end = len(text) if line_end < 0 else line_end
        return (text[:line_start] + sidebar_block(items, indent) + text[line_end:]).encode("utf-8")

    match = re.search(r"\bthemeConfig\s*:\s*\{", text)
    if not match:
        warnings.append("sidebar not updated: no safely recognizable themeConfig object")
        print("SIDEBAR SNIPPET:\n" + sidebar_block(items, "  "), file=sys.stderr)
        return None
    open_at = text.find("{", match.start())
    close_at = find_matching_brace(text, open_at)
    if close_at is None:
        warnings.append("sidebar not updated: unterminated themeConfig object")
        return None
    theme_body = text[open_at + 1 : close_at]
    if re.search(r"(^|\n)\s*sidebar\s*:", theme_body):
        warnings.append("sidebar not updated: existing sidebar is not managed by this skill")
        print("SIDEBAR SNIPPET:\n" + sidebar_block(items, "    "), file=sys.stderr)
        return None
    line_start = text.rfind("\n", 0, match.start()) + 1
    base_indent = re.match(r"\s*", text[line_start:match.start()]).group(0)
    insertion = "\n" + sidebar_block(items, base_indent + "  ") + "\n"
    return (text[: open_at + 1] + insertion + text[open_at + 1 :]).encode("utf-8")


def locate_config(site_root: Path) -> Path:
    for name in ("config.ts", "config.mts", "config.js", "config.mjs"):
        candidate = site_root / ".vitepress" / name
        if candidate.is_file():
            return candidate
    return site_root / ".vitepress" / "config.ts"


def normalize_hpath(value: str) -> str:
    clean = "/" + "/".join(part for part in PurePosixPath(value.replace("\\", "/")).parts if part != "/")
    return clean.rstrip("/") or "/"


def markdown_hpath(rel: Path, root: str) -> str:
    base = [part for part in PurePosixPath(normalize_hpath(root)).parts if part != "/"]
    relative = list(PurePosixPath(rel.as_posix()).parts)
    if relative[-1].lower() == "index.md":
        relative = relative[:-1]
    else:
        relative[-1] = PurePosixPath(relative[-1]).stem
    result = "/" + "/".join(base + relative)
    return result.rstrip("/") or "/"


def publish(args: argparse.Namespace) -> int:
    original_source = args.source.resolve()
    dest = args.dest.resolve()
    if not original_source.exists():
        raise SystemExit(f"Source does not exist: {original_source}")
    ensure_separate(original_source, dest)
    state_path = (args.state or dest / ".siyuan-sync.json").resolve()
    old = read_state(state_path)
    validate_state_mapping(old, dest, args.notebook, args.hpath)
    asset_root = args.asset_root.resolve() if args.asset_root else None
    if asset_root is not None and not asset_root.is_dir():
        raise SystemExit(f"Asset root is not a directory: {asset_root}")

    with ExitStack() as stack:
        source = prepare_source(original_source, stack)
        markdown = collect_markdown(source)
        if not markdown:
            raise SystemExit("No Markdown files found in source")
        source_root = source if source.is_dir() else source.parent
        planned: dict[Path, bytes] = {}
        source_hashes: dict[str, str] = {}
        warnings: list[str] = []
        for rel, src in sorted(markdown.items(), key=lambda item: item[0].as_posix()):
            target = dest / rel
            existing = target.read_text(encoding="utf-8") if target.is_file() else None
            raw = src.read_text(encoding="utf-8")
            source_hashes[rel.as_posix()] = semantic_hash(raw)
            planned[rel] = transform_publish(
                raw, rel, src, source_root, asset_root, existing, planned, warnings
            ).encode("utf-8")

        config: Path | None = None
        config_data: bytes | None = None
        if args.nav == "auto":
            config = args.config.resolve() if args.config else locate_config(dest)
            config_data = plan_sidebar(config, nav_items(markdown, planned), warnings)

        actions: list[tuple[str, Path, bytes | None]] = []
        conflicts: list[str] = []
        skipped_local: set[str] = set()
        old_docs = old["documents"]
        old_managed = old["managed"]
        new_docs: dict[str, dict] = {}
        new_managed: dict[str, str] = {}

        for rel, data in sorted(planned.items(), key=lambda item: item[0].as_posix()):
            key = rel.as_posix()
            target = (dest / rel).resolve()
            if not inside(target, dest):
                raise SystemExit(f"Refusing path outside destination: {target}")
            desired_hash = sha256(data)
            current_hash = sha256(target.read_bytes()) if target.is_file() else None
            baseline = old_managed.get(key)
            source_changed = desired_hash != baseline if baseline else True
            local_changed = current_hash != baseline if baseline else current_hash is not None
            if current_hash == desired_hash:
                pass
            elif baseline is None and current_hash is not None:
                conflicts.append(f"untracked destination exists: {key}")
                continue
            elif local_changed and source_changed:
                conflicts.append(f"both sides changed: {key}")
                continue
            elif local_changed and not source_changed:
                warnings.append(f"preserved VitePress-only change: {key}")
                skipped_local.add(key)
                continue
            else:
                actions.append(("add" if current_hash is None else "update", target, data))
            new_managed[key] = desired_hash

        planned_keys = {rel.as_posix() for rel in planned}
        if args.prune:
            for key in sorted(set(old_managed) - planned_keys):
                target = (dest / key).resolve()
                if not inside(target, dest):
                    continue
                baseline = old_managed[key]
                if target.is_file() and sha256(target.read_bytes()) != baseline:
                    conflicts.append(f"refusing to prune locally changed file: {key}")
                elif target.is_file():
                    actions.append(("delete", target, None))

        for rel in markdown:
            key = rel.as_posix()
            old_entry = old_docs.get(key, {})
            if key in skipped_local:
                new_docs[key] = old_entry
                continue
            hpath = old_entry.get("hpath")
            if args.hpath:
                hpath = markdown_hpath(rel, args.hpath)
            new_docs[key] = {
                "siyuan_hash": source_hashes[key],
                "vitepress_hash": semantic_hash(planned[rel].decode("utf-8")),
                "hpath": hpath,
            }

        if config is not None and config_data is not None:
            current = config.read_bytes() if config.is_file() else None
            if current != config_data:
                actions.append(("add" if current is None else "update", config, config_data))

        if conflicts:
            print("CONFLICTS:", file=sys.stderr)
            for item in conflicts:
                print(f"- {item}", file=sys.stderr)
            print("No files were changed.", file=sys.stderr)
            return 2

        for action, target, data in actions:
            print(f"{action.upper():6} {target}")
            if not args.dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                if action == "delete":
                    target.unlink()
                else:
                    target.write_bytes(data or b"")

        for item in warnings:
            print(f"WARNING {item}", file=sys.stderr)
        if not args.dry_run:
            for key in skipped_local:
                if key in old_managed:
                    new_managed[key] = old_managed[key]
            state = {
                "version": STATE_VERSION,
                "vitepress_root": str(dest),
                "notebook": args.notebook or old.get("notebook"),
                "hpath_root": args.hpath or old.get("hpath_root"),
                "documents": new_docs,
                "managed": new_managed,
            }
            write_state(state_path, state)
        print(f"{len(actions)} file action(s); {len(warnings)} warning(s); 0 conflict(s)")
    return 0


def command_prefix(command: str) -> list[str]:
    path = Path(command)
    if path.suffix.lower() == ".py" and path.is_file():
        return [sys.executable, str(path)]
    return [command]


def response_id(data: object) -> str:
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        if isinstance(data.get("id"), str):
            return data["id"]
        nested = data.get("data")
        if isinstance(nested, str):
            return nested
        if isinstance(nested, dict) and isinstance(nested.get("id"), str):
            return nested["id"]
    return ""


class SiYuanCLI:
    def __init__(self, executable: str, workspace: Path | None):
        self.prefix = command_prefix(executable)
        self.workspace = workspace
        self.cache: dict[str, list[dict]] = {}

    def run(self, *args: str, json_output: bool = False) -> str | object:
        command = list(self.prefix)
        if self.workspace:
            command += ["--workspace", str(self.workspace)]
        if json_output:
            command += ["--format", "json"]
        command += list(args)
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        if result.returncode:
            raise SystemExit(
                f"SiYuan command failed ({result.returncode}): {' '.join(command)}\n{result.stderr.strip()}"
            )
        if not json_output:
            return result.stdout
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"SiYuan returned invalid JSON: {result.stdout.strip()}") from exc

    def children(self, notebook: str, hpath: str) -> list[dict]:
        key = normalize_hpath(hpath)
        if key not in self.cache:
            data = self.run(
                "document", "list", "--notebook", notebook, "--hpath", key, json_output=True
            )
            if not isinstance(data, list):
                raise SystemExit("Unexpected SiYuan document list response")
            self.cache[key] = data
        return self.cache[key]

    def find(self, notebook: str, hpath: str) -> dict | None:
        parts = [part for part in PurePosixPath(normalize_hpath(hpath)).parts if part != "/"]
        parent = "/"
        found = None
        for part in parts:
            found = next((doc for doc in self.children(notebook, parent) if doc.get("name") == part), None)
            if found is None:
                return None
            parent = normalize_hpath(str(PurePosixPath(parent) / part))
        return found

    def create(self, notebook: str, parent_hpath: str, title: str) -> dict:
        parent_doc = self.find(notebook, parent_hpath) if parent_hpath != "/" else None
        parent_path = str(parent_doc.get("path")) if parent_doc else "/"
        data = self.run(
            "document",
            "create",
            "--notebook",
            notebook,
            "--title",
            title,
            "--path",
            parent_path,
            json_output=True,
        )
        self.cache.clear()
        doc_id = response_id(data)
        return {"id": doc_id} if doc_id else {}

    def ensure_parent(self, notebook: str, hpath: str) -> None:
        current = "/"
        for part in [p for p in PurePosixPath(normalize_hpath(hpath)).parts if p != "/"]:
            next_path = normalize_hpath(str(PurePosixPath(current) / part))
            if self.find(notebook, next_path) is None:
                created = self.create(notebook, current, part)
                if not created.get("id") and self.find(notebook, next_path) is None:
                    raise SystemExit(f"Could not create parent document: {next_path}")
            current = next_path

    def export(self, doc_id: str) -> str:
        with tempfile.TemporaryDirectory(prefix="vitepress-siyuan-export-") as folder:
            output = Path(folder) / "document.md"
            self.run("export", "md", "--id", doc_id, "--output", str(output))
            return output.read_text(encoding="utf-8")

    def update(self, doc_id: str, markdown: str) -> None:
        with tempfile.TemporaryDirectory(prefix="vitepress-siyuan-import-") as folder:
            source = Path(folder) / "document.md"
            source.write_text(markdown, encoding="utf-8")
            self.run("block", "update", "--id", doc_id, "--file", str(source))

    def upload(self, doc_id: str, files: list[Path]) -> dict[str, str]:
        if not files:
            return {}
        command = ["asset", "upload", "--id", doc_id]
        for path in files:
            command += ["--file", str(path)]
        data = self.run(*command, json_output=True)
        if not isinstance(data, dict):
            raise SystemExit("Unexpected SiYuan asset upload response")
        nested = data.get("data") if isinstance(data.get("data"), dict) else data
        result = nested.get("succMap", {})
        return result if isinstance(result, dict) else {}


def local_assets(text: str, markdown_file: Path) -> list[Path]:
    result: list[Path] = []
    for pattern in (IMAGE_RE, LINK_RE):
        for match in pattern.finditer(text):
            target, _ = split_markdown_target(match.group(2))
            parts = asset_parts(target)
            if parts is None:
                continue
            candidate = markdown_file.parent / "assets" / Path(*parts.parts)
            if candidate.is_file() and candidate.resolve() not in result:
                result.append(candidate.resolve())
    return result


def rewrite_uploaded_assets(text: str, mapping: dict[str, str]) -> str:
    by_name = {Path(key).name: value for key, value in mapping.items()}

    def replace(match: re.Match[str]) -> str:
        target, suffix = split_markdown_target(match.group(2))
        parts = asset_parts(target)
        if parts is None or parts.name not in by_name:
            return match.group(0)
        return match.group(1) + by_name[parts.name].replace("\\", "/") + suffix + match.group(3)

    return LINK_RE.sub(replace, IMAGE_RE.sub(replace, text))


@dataclass
class ImportPlan:
    rel: Path
    source_file: Path
    hpath: str
    body: str
    existing: dict | None
    action: str


def import_to_siyuan(args: argparse.Namespace) -> int:
    source = args.source.resolve()
    if not source.exists():
        raise SystemExit(f"Source does not exist: {source}")
    root = normalize_hpath(args.hpath)
    if root == "/":
        raise SystemExit("--hpath must name an explicit non-root destination")
    source_root = source if source.is_dir() else source.parent
    state_path = (args.state or source_root / ".siyuan-sync.json").resolve()
    state = read_state(state_path)
    validate_state_mapping(state, source_root, args.notebook, root)
    cli = SiYuanCLI(args.siyuan, args.workspace.resolve() if args.workspace else None)
    markdown = collect_markdown(source)
    if not markdown:
        raise SystemExit("No Markdown files found in source")

    targets: dict[str, Path] = {}
    plans: list[ImportPlan] = []
    conflicts: list[str] = []
    warnings: list[str] = []
    for rel, path in sorted(markdown.items(), key=lambda item: (len(item[0].parts), item[0].as_posix())):
        hpath = markdown_hpath(rel, root)
        if hpath in targets:
            conflicts.append(f"multiple Markdown files map to {hpath}: {targets[hpath]} and {rel}")
            continue
        targets[hpath] = rel
        text = path.read_text(encoding="utf-8")
        body = transform_import(text)
        report_unsupported(body, rel, warnings)
        existing = cli.find(args.notebook, hpath)
        entry = state["documents"].get(rel.as_posix())
        vp_hash = semantic_hash(text)
        if existing:
            sy_text = cli.export(str(existing["id"]))
            sy_hash = semantic_hash(sy_text)
            if entry:
                vp_changed = vp_hash != entry.get("vitepress_hash")
                sy_changed = entry.get("siyuan_hash") is not None and sy_hash != entry.get("siyuan_hash")
                if vp_changed and sy_changed:
                    conflicts.append(f"both sides changed: {rel.as_posix()} <-> {hpath}")
                    continue
                if not vp_changed:
                    plans.append(ImportPlan(rel, path, hpath, body, existing, "skip"))
                    continue
            else:
                warnings.append(f"{rel.as_posix()}: no baseline for existing SiYuan document {hpath}")
            action = "skip" if semantic_hash(body) == sy_hash else "update"
        else:
            action = "create"
        plans.append(ImportPlan(rel, path, hpath, body, existing, action))

    if conflicts:
        print("CONFLICTS:", file=sys.stderr)
        for item in conflicts:
            print(f"- {item}", file=sys.stderr)
        print("No SiYuan documents were changed.", file=sys.stderr)
        return 2

    for plan in plans:
        print(f"{plan.action.upper():6} {plan.rel.as_posix()} -> {plan.hpath}")
    for item in warnings:
        print(f"WARNING {item}", file=sys.stderr)
    action_count = sum(plan.action != "skip" for plan in plans)
    if args.dry_run:
        print(f"{action_count} document action(s); {len(warnings)} warning(s); 0 conflict(s)")
        return 0

    documents = dict(state["documents"])
    for plan in plans:
        doc = plan.existing
        if plan.action == "create":
            parent = normalize_hpath(str(PurePosixPath(plan.hpath).parent))
            cli.ensure_parent(args.notebook, parent)
            doc = cli.create(args.notebook, parent, PurePosixPath(plan.hpath).name)
            if not doc.get("id"):
                doc = cli.find(args.notebook, plan.hpath)
            if not doc or not doc.get("id"):
                raise SystemExit(f"Could not resolve newly created document: {plan.hpath}")
        if plan.action in {"create", "update"}:
            uploaded = cli.upload(str(doc["id"]), local_assets(plan.body, plan.source_file))
            cli.update(str(doc["id"]), rewrite_uploaded_assets(plan.body, uploaded))
        current = cli.export(str(doc["id"])) if doc else plan.body
        documents[plan.rel.as_posix()] = {
            "siyuan_hash": semantic_hash(current),
            "vitepress_hash": semantic_hash(plan.source_file.read_text(encoding="utf-8")),
            "hpath": plan.hpath,
        }

    new_state = {
        **state,
        "version": STATE_VERSION,
        "vitepress_root": str(source_root),
        "notebook": args.notebook,
        "hpath_root": root,
        "documents": documents,
    }
    write_state(state_path, new_state)
    print(f"{action_count} document action(s); {len(warnings)} warning(s); 0 conflict(s)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    publish_parser = subparsers.add_parser("publish", help="publish a SiYuan Markdown export to VitePress")
    publish_parser.add_argument("--source", required=True, type=Path)
    publish_parser.add_argument("--dest", required=True, type=Path, help="VitePress source root, usually docs")
    publish_parser.add_argument("--asset-root", type=Path, help="SiYuan workspace data/assets directory")
    publish_parser.add_argument("--state", type=Path)
    publish_parser.add_argument("--notebook", help="record the notebook ID for later reverse import")
    publish_parser.add_argument("--hpath", help="record the mapped SiYuan root path")
    publish_parser.add_argument("--prune", action="store_true", help="remove unchanged files recorded by this state only")
    publish_parser.add_argument("--nav", choices=("auto", "none"), default="auto")
    publish_parser.add_argument("--config", type=Path, help="explicit VitePress config path")
    publish_parser.add_argument("--dry-run", action="store_true")
    publish_parser.set_defaults(handler=publish)

    import_parser = subparsers.add_parser("import", help="import VitePress Markdown into an explicit SiYuan target")
    import_parser.add_argument("--source", required=True, type=Path)
    import_parser.add_argument("--workspace", type=Path)
    import_parser.add_argument("--notebook", required=True)
    import_parser.add_argument("--hpath", required=True, help="explicit non-root SiYuan destination path")
    import_parser.add_argument("--state", type=Path)
    import_parser.add_argument("--siyuan", default="siyuan", help="SiYuan CLI executable")
    import_parser.add_argument("--dry-run", action="store_true")
    import_parser.set_defaults(handler=import_to_siyuan)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
