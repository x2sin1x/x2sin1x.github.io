from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("sync.py")
SPEC = importlib.util.spec_from_file_location("vitepress_siyuan_sync", SCRIPT)
SYNC = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SYNC
SPEC.loader.exec_module(SYNC)


class SyncTests(unittest.TestCase):
    def run_sync(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def make_site(self, root: Path, config: str = "export default { themeConfig: {} }\n") -> Path:
        site = root / "site"
        (site / ".vitepress").mkdir(parents=True)
        (site / ".vitepress" / "config.ts").write_text(config, encoding="utf-8")
        return site

    def make_fake_siyuan(self, root: Path) -> tuple[Path, Path]:
        state = root / "fake-state.json"
        state.write_text(
            json.dumps(
                {
                    "next": 10,
                    "docs": {
                        "/Published": {"id": "d0", "path": "/d0.sy", "content": ""},
                        "/Published/Site": {"id": "d1", "path": "/d1.sy", "content": "# Old\n"},
                    },
                }
            ),
            encoding="utf-8",
        )
        executable = root / "fake-siyuan.py"
        executable.write_text(
            r'''import json
import posixpath
import sys
from pathlib import Path

STATE = Path(__file__).with_name("fake-state.json")
args = sys.argv[1:]
while args and args[0].startswith("--"):
    if args[0] in {"--workspace", "--format", "--log-level"}:
        args = args[2:]
    else:
        args = args[1:]
data = json.loads(STATE.read_text(encoding="utf-8"))
docs = data["docs"]

def value(flag):
    return args[args.index(flag) + 1]

def save():
    STATE.write_text(json.dumps(data), encoding="utf-8")

command = tuple(args[:2])
if command == ("document", "list"):
    parent = value("--hpath").rstrip("/") or "/"
    rows = []
    for hpath, doc in docs.items():
        if (posixpath.dirname(hpath) or "/") == parent:
            row = {"name": posixpath.basename(hpath), **doc}
            row["subFileCount"] = sum(1 for candidate in docs if (posixpath.dirname(candidate) or "/") == hpath)
            rows.append(row)
    print(json.dumps(rows))
elif command == ("export", "md"):
    doc_id = value("--id")
    output = Path(value("--output"))
    content = next(doc["content"] for doc in docs.values() if doc["id"] == doc_id)
    output.write_text(content, encoding="utf-8")
elif command == ("document", "create"):
    title = value("--title")
    parent_path = value("--path")
    parent = "/" if parent_path == "/" else next(h for h, doc in docs.items() if doc["path"] == parent_path)
    hpath = (parent.rstrip("/") + "/" + title) if parent != "/" else "/" + title
    doc_id = "d" + str(data["next"])
    data["next"] += 1
    docs[hpath] = {"id": doc_id, "path": "/" + doc_id + ".sy", "content": ""}
    save()
    print(json.dumps({"id": doc_id}))
elif command == ("block", "update"):
    doc_id = value("--id")
    content = Path(value("--file")).read_text(encoding="utf-8")
    next(doc for doc in docs.values() if doc["id"] == doc_id)["content"] = content
    save()
elif command == ("asset", "upload"):
    files = [Path(args[index + 1]) for index, item in enumerate(args) if item == "--file"]
    mapping = {path.name: "assets/" + path.stem + "-20260101000000-abcdefg" + path.suffix for path in files}
    print(json.dumps({"succMap": mapping}))
else:
    print("unsupported " + " ".join(args), file=sys.stderr)
    raise SystemExit(3)
''',
            encoding="utf-8",
        )
        return executable, state

    def test_publish_assets_frontmatter_sidebar_and_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "export"
            (source / "assets").mkdir(parents=True)
            (source / "guide" / "assets").mkdir(parents=True)
            (source / "index.md").write_text("# Home\n\n![logo](assets/logo.png)\n", encoding="utf-8")
            (source / "assets" / "logo.png").write_bytes(b"logo")
            (source / "guide" / "start.md").write_text(
                "---\ntags: [demo]\n---\n\n# Start\n\n![chart](assets/chart.png)\n\n[download](assets/file.pdf)\n",
                encoding="utf-8",
            )
            (source / "guide" / "assets" / "chart.png").write_bytes(b"chart")
            (source / "guide" / "assets" / "file.pdf").write_bytes(b"pdf")
            site = self.make_site(root)

            dry = self.run_sync("publish", "--source", source, "--dest", site, "--dry-run")
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertFalse((site / "index.md").exists())
            self.assertNotIn(SYNC.NAV_START, (site / ".vitepress" / "config.ts").read_text())

            result = self.run_sync("publish", "--source", source, "--dest", site)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('title: "Home"', (site / "index.md").read_text(encoding="utf-8"))
            guide = (site / "guide" / "start.md").read_text(encoding="utf-8")
            self.assertIn("tags: [demo]", guide)
            self.assertIn("![chart](./assets/chart.png)", guide)
            self.assertIn("[download](./assets/file.pdf)", guide)
            self.assertEqual((site / "guide" / "assets" / "chart.png").read_bytes(), b"chart")
            self.assertEqual((site / "guide" / "assets" / "file.pdf").read_bytes(), b"pdf")
            config = (site / ".vitepress" / "config.ts").read_text(encoding="utf-8")
            self.assertIn(SYNC.NAV_START, config)
            self.assertIn('"link": "/guide/start"', config)
            second = self.run_sync("publish", "--source", source, "--dest", site)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(
                (site / ".vitepress" / "config.ts").read_text(encoding="utf-8").count(SYNC.NAV_START),
                1,
            )
            self.assertEqual(json.loads((site / ".siyuan-sync.json").read_text())["version"], 2)

    def test_zip_prune_conflict_and_safe_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source"
            source.mkdir()
            (source / "a.md").write_text("# A\n", encoding="utf-8")
            (source / "b.md").write_text("# B\n", encoding="utf-8")
            archive = root / "export.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.write(source / "a.md", "a.md")
                bundle.write(source / "b.md", "b.md")
            site = self.make_site(root)
            result = self.run_sync("publish", "--source", archive, "--dest", site, "--nav", "none")
            self.assertEqual(result.returncode, 0, result.stderr)
            (site / "manual.md").write_text("user owned", encoding="utf-8")

            (source / "b.md").unlink()
            archive.unlink()
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.write(source / "a.md", "a.md")
            prune = self.run_sync(
                "publish", "--source", archive, "--dest", site, "--nav", "none", "--prune"
            )
            self.assertEqual(prune.returncode, 0, prune.stderr)
            self.assertFalse((site / "b.md").exists())
            self.assertTrue((site / "manual.md").exists())

            (source / "a.md").write_text("# Changed upstream\n", encoding="utf-8")
            archive.unlink()
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.write(source / "a.md", "a.md")
            (site / "a.md").write_text("# Changed locally\n", encoding="utf-8")
            conflict = self.run_sync("publish", "--source", archive, "--dest", site, "--nav", "none")
            self.assertEqual(conflict.returncode, 2)
            self.assertIn("both sides changed", conflict.stderr)
            self.assertEqual((site / "a.md").read_text(encoding="utf-8"), "# Changed locally\n")

            malicious = root / "malicious.zip"
            with zipfile.ZipFile(malicious, "w") as bundle:
                bundle.writestr("../escape.md", "bad")
            unsafe = self.run_sync("publish", "--source", malicious, "--dest", site, "--nav", "none")
            self.assertNotEqual(unsafe.returncode, 0)
            self.assertIn("Unsafe zip member", unsafe.stderr)
            self.assertFalse((root / "escape.md").exists())

    def test_unmanaged_sidebar_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source"
            source.mkdir()
            (source / "index.md").write_text("# Home\n", encoding="utf-8")
            original = "export default { themeConfig: {\n  sidebar: [{ text: 'Manual', link: '/' }]\n} }\n"
            site = self.make_site(root, original)
            result = self.run_sync("publish", "--source", source, "--dest", site)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("existing sidebar is not managed", result.stderr)
            self.assertEqual((site / ".vitepress" / "config.ts").read_text(encoding="utf-8"), original)

    def test_mapping_and_import_transform(self) -> None:
        self.assertEqual(SYNC.markdown_hpath(Path("index.md"), "/Published/Site"), "/Published/Site")
        self.assertEqual(
            SYNC.markdown_hpath(Path("guide/index.md"), "/Published/Site"),
            "/Published/Site/guide",
        )
        self.assertEqual(
            SYNC.markdown_hpath(Path("guide/start.md"), "/Published/Site"),
            "/Published/Site/guide/start",
        )
        converted = SYNC.transform_import("---\ntitle: T\n---\n\nValue \\(x\\)\n")
        self.assertNotIn("title: T", converted)
        self.assertIn("Value $x$", converted)

    def test_reverse_import_dry_run_update_create_assets_and_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            site = root / "site"
            (site / "assets").mkdir(parents=True)
            (site / "guide").mkdir()
            (site / "index.md").write_text(
                "---\ntitle: Home\n---\n\n# New\n\n![logo](./assets/logo.png)\n",
                encoding="utf-8",
            )
            (site / "assets" / "logo.png").write_bytes(b"logo")
            (site / "guide" / "page.md").write_text("# Page\n", encoding="utf-8")
            fake, fake_state = self.make_fake_siyuan(root)
            common = (
                "import",
                "--source",
                site,
                "--notebook",
                "notebook-id",
                "--hpath",
                "/Published/Site",
                "--siyuan",
                fake,
            )

            before = fake_state.read_text(encoding="utf-8")
            dry = self.run_sync(*common, "--dry-run")
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertIn("UPDATE index.md -> /Published/Site", dry.stdout)
            self.assertIn("CREATE guide/page.md -> /Published/Site/guide/page", dry.stdout)
            self.assertEqual(fake_state.read_text(encoding="utf-8"), before)

            result = self.run_sync(*common)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(fake_state.read_text(encoding="utf-8"))
            self.assertIn("/Published/Site/guide", data["docs"])
            self.assertIn("/Published/Site/guide/page", data["docs"])
            content = data["docs"]["/Published/Site"]["content"]
            self.assertNotIn("title: Home", content)
            self.assertIn("assets/logo-20260101000000-abcdefg.png", content)

            (site / "index.md").write_text("# Changed in VitePress\n", encoding="utf-8")
            data["docs"]["/Published/Site"]["content"] = "# Changed in SiYuan\n"
            fake_state.write_text(json.dumps(data), encoding="utf-8")
            conflict = self.run_sync(*common, "--dry-run")
            self.assertEqual(conflict.returncode, 2)
            self.assertIn("both sides changed", conflict.stderr)


if __name__ == "__main__":
    unittest.main()
