#!/usr/bin/env python3
"""Create a lightweight, read-only inventory of a source repository."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Iterable


GENERATED_DIRECTORIES = {
    ".git",
    ".next",
    ".nuxt",
    ".output",
    ".turbo",
    ".vitepress/cache",
    ".vitepress/dist",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}

MANIFEST_NAMES = {
    "Cargo.toml",
    "CMakeLists.txt",
    "Dockerfile",
    "Gemfile",
    "Makefile",
    "Package.swift",
    "build.gradle",
    "build.gradle.kts",
    "composer.json",
    "deno.json",
    "deno.jsonc",
    "go.mod",
    "justfile",
    "mix.exs",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
    "setup.cfg",
    "setup.py",
    "tsconfig.json",
}

ENTRYPOINT_STEMS = {
    "__main__",
    "app",
    "cli",
    "index",
    "main",
    "mod",
    "server",
}

LANGUAGES = {
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".cs": "C#",
    ".css": "CSS",
    ".cu": "CUDA",
    ".dart": "Dart",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".go": "Go",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".html": "HTML",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".lua": "Lua",
    ".md": "Markdown",
    ".php": "PHP",
    ".proto": "Protocol Buffers",
    ".py": "Python",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".scala": "Scala",
    ".sh": "Shell",
    ".sol": "Solidity",
    ".sql": "SQL",
    ".swift": "Swift",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".vue": "Vue",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".zig": "Zig",
}


def run_git(root: Path, *arguments: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def is_generated(relative_path: Path) -> bool:
    normalized = relative_path.as_posix()
    return any(
        normalized == directory or normalized.startswith(f"{directory}/")
        for directory in GENERATED_DIRECTORIES
    )


def tracked_files(root: Path, include_generated: bool) -> list[Path]:
    listed = run_git(root, "ls-files", "-z")
    if listed is not None:
        candidates = [Path(item) for item in listed.split("\0") if item]
    else:
        candidates = [path.relative_to(root) for path in root.rglob("*") if path.is_file()]

    files = []
    for relative_path in candidates:
        if not include_generated and is_generated(relative_path):
            continue
        if (root / relative_path).is_file():
            files.append(relative_path)
    return sorted(files, key=lambda path: path.as_posix().lower())


def count_lines(path: Path) -> tuple[int, bool]:
    if path.stat().st_size > 5 * 1024 * 1024:
        return 0, True
    try:
        content = path.read_bytes()
    except OSError:
        return 0, True
    if b"\0" in content[:8192]:
        return 0, True
    return content.count(b"\n") + (1 if content and not content.endswith(b"\n") else 0), False


def looks_like_test(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    name = path.name.lower()
    return bool(
        lowered_parts & {"__tests__", "spec", "specs", "test", "tests"}
        or name.startswith("test_")
        or ".test." in name
        or ".spec." in name
        or "_test." in name
    )


def looks_like_docs(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    return path.suffix.lower() in {".md", ".mdx", ".rst"} or bool(
        lowered_parts & {"doc", "docs", "documentation", "examples"}
    )


def limited_paths(paths: Iterable[Path], limit: int = 80) -> list[str]:
    return [path.as_posix() for path in list(paths)[:limit]]


def build_inventory(root: Path, include_generated: bool) -> dict[str, object]:
    git_root = run_git(root, "rev-parse", "--show-toplevel")
    if git_root:
        root = Path(git_root).resolve()

    files = tracked_files(root, include_generated)
    language_files: Counter[str] = Counter()
    language_lines: Counter[str] = Counter()
    top_level: Counter[str] = Counter()
    skipped_line_counts = 0

    for relative_path in files:
        top_level[relative_path.parts[0]] += 1
        language = LANGUAGES.get(relative_path.suffix.lower())
        if language is None:
            continue
        language_files[language] += 1
        line_count, skipped = count_lines(root / relative_path)
        language_lines[language] += line_count
        skipped_line_counts += int(skipped)

    manifests = [path for path in files if path.name in MANIFEST_NAMES]
    entrypoints = [
        path
        for path in files
        if path.stem.lower() in ENTRYPOINT_STEMS
        and path.suffix.lower() in LANGUAGES
        and path.suffix.lower() not in {".md", ".yaml", ".yml"}
    ]
    tests = [path for path in files if looks_like_test(path)]
    docs = [path for path in files if looks_like_docs(path)]

    languages = [
        {
            "language": language,
            "files": language_files[language],
            "lines": language_lines[language],
        }
        for language in sorted(
            language_files,
            key=lambda item: (language_lines[item], language_files[item]),
            reverse=True,
        )
    ]

    return {
        "root": str(root),
        "git": {
            "remote": run_git(root, "remote", "get-url", "origin"),
            "branch": run_git(root, "branch", "--show-current"),
            "commit": run_git(root, "rev-parse", "HEAD"),
            "dirty": bool(run_git(root, "status", "--porcelain")),
        },
        "summary": {
            "files": len(files),
            "test_files": len(tests),
            "documentation_files": len(docs),
            "skipped_line_counts": skipped_line_counts,
            "generated_files_included": include_generated,
        },
        "languages": languages,
        "top_level": [
            {"path": path, "files": count}
            for path, count in sorted(top_level.items(), key=lambda item: (-item[1], item[0]))
        ],
        "manifests": limited_paths(manifests),
        "entrypoint_candidates": limited_paths(entrypoints),
        "test_samples": limited_paths(tests),
        "documentation_samples": limited_paths(docs),
    }


def render_markdown(inventory: dict[str, object]) -> str:
    git = inventory["git"]
    summary = inventory["summary"]
    lines = [
        "# Repository Inventory",
        "",
        f"- Root: `{inventory['root']}`",
        f"- Remote: `{git['remote'] or 'unknown'}`",
        f"- Branch: `{git['branch'] or 'detached/unknown'}`",
        f"- Commit: `{git['commit'] or 'not a git repository'}`",
        f"- Dirty: `{str(git['dirty']).lower()}`",
        f"- Files considered: `{summary['files']}`",
        f"- Test files: `{summary['test_files']}`",
        f"- Documentation files: `{summary['documentation_files']}`",
        "",
        "## Languages",
        "",
        "| Language | Files | Lines |",
        "|---|---:|---:|",
    ]
    for item in inventory["languages"]:
        lines.append(f"| {item['language']} | {item['files']} | {item['lines']} |")

    sections = (
        ("Top-Level Areas", "top_level", True),
        ("Manifests", "manifests", False),
        ("Entrypoint Candidates", "entrypoint_candidates", False),
        ("Test Samples", "test_samples", False),
        ("Documentation Samples", "documentation_samples", False),
    )
    for title, key, counted in sections:
        lines.extend(["", f"## {title}", ""])
        items = inventory[key]
        if not items:
            lines.append("- None detected")
            continue
        for item in items:
            if counted:
                lines.append(f"- `{item['path']}`: {item['files']} files")
            else:
                lines.append(f"- `{item}`")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path, help="Repository path")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--include-generated",
        action="store_true",
        help="Include common generated and vendored directories",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.repo.resolve()
    if not root.is_dir():
        raise SystemExit(f"Repository path is not a directory: {root}")

    inventory = build_inventory(root, args.include_generated)
    if args.format == "json":
        print(json.dumps(inventory, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(inventory), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
