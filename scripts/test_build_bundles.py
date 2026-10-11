"""Run: python3 -m unittest scripts/test_build_bundles.py"""
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).with_name("build-bundles.py")
spec = importlib.util.spec_from_file_location("bundles", SCRIPT)
bundles = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundles)

SKILL = "---\nname: {name}\ndescription: d\n---\n{body}\n"
MANIFEST = '{"entry": ["a"]}'
# Fixture repositories ignore the machine's git config (signing, hooks, identity).
GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.com",
           "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.com"}


def tree(files):
    root = pathlib.Path(tempfile.mkdtemp())
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def repo(files):
    """tree(files), committed to a new git repository."""
    root = tree(files)
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "fixture"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=GIT_ENV)
    return root


class BuildTest(unittest.TestCase):
    def test_inlines_references_once_and_strips_frontmatter(self):
        root = tree({
            "skills/a/SKILL.md": SKILL.format(name="a", body="See `references/X.md` and references/X.md."),
            "skills/a/references/X.md": "# X\nfacts",
            "skills/b/SKILL.md": SKILL.format(name="b", body="See `a` -> X.md §X for more."),
        })
        text, problems = bundles.build(root, "entry", ["a", "b"])
        self.assertEqual(problems, [])
        self.assertEqual(text.count("# Reference: skills/a/references/X.md"), 1)
        self.assertNotIn("description: d", text)
        self.assertLess(text.index("<!-- skill: a -->"), text.index("<!-- skill: b -->"))

    def test_reports_every_kind_of_dangling_pointer(self):
        root = tree({
            "skills/a/SKILL.md": SKILL.format(name="a", body="\n".join([
                "missing file: references/Nope.md",
                "missing section: `a` → X.md §Controls > Creating a Policy",
                "skill outside the entry: `c` -> Y.md",
                "placeholder is prose: `a` -> X.md §<Section Title>.",
            ])),
            "skills/a/references/X.md": "# Controls\n## Creating a Policy Template\n",
            "skills/c/references/Y.md": "# Y",
        })
        _, problems = bundles.build(root, "entry", ["a"])
        self.assertEqual(len(problems), 3, problems)
        self.assertIn("references/Nope.md does not exist", problems[0])
        self.assertIn("has no heading 'Creating a Policy'", problems[1])
        self.assertIn("skill 'c' is not in this entry point's manifest list", problems[2])


class WriteTest(unittest.TestCase):
    def test_bundles_are_content_addressed_and_the_index_names_them(self):
        root = tree({"skills/a/SKILL.md": SKILL.format(name="a", body="body"), "manifests/agent-contexts.json": MANIFEST})
        out = root / "dist" / "bundles"
        index, problems = bundles.write_bundles(root, out, "v1", "c0ffee")
        self.assertEqual(problems, [])
        meta = index["bundles"]["entry"]
        self.assertEqual(meta["file"], f"entry.{meta['sha256'][:12]}.md")
        self.assertEqual(hashlib.sha256((out / meta["file"]).read_bytes()).hexdigest(), meta["sha256"])
        self.assertEqual(json.loads((out / "index.json").read_text(encoding="utf-8")), index)

    def test_a_build_with_a_dangling_pointer_writes_nothing(self):
        root = tree({"skills/a/SKILL.md": SKILL.format(name="a", body="references/Nope.md"),
                     "manifests/agent-contexts.json": MANIFEST})
        out = root / "dist" / "bundles"
        _, problems = bundles.write_bundles(root, out, "v1", "c0ffee")
        self.assertEqual(len(problems), 1, problems)
        self.assertFalse(out.exists(), "a failed build must not leave new bundles beside an older index")

    def test_every_file_is_read_and_written_as_utf8(self):
        # With these flags any open() that falls back to the locale's encoding raises.
        out = pathlib.Path(tempfile.mkdtemp()) / "bundles"
        run = subprocess.run([sys.executable, "-X", "warn_default_encoding", "-W", "error::EncodingWarning",
                              str(SCRIPT), "--out", str(out)], capture_output=True, encoding="utf-8")
        self.assertEqual(run.returncode, 0, run.stderr)


class CommitTest(unittest.TestCase):
    def test_uncommitted_changes_mark_the_commit_dirty(self):
        root = repo({"skills/a/SKILL.md": "x"})
        head = bundles.commit_of(root)
        self.assertRegex(head, r"^[0-9a-f]{40}$")
        (root / "skills/a/new.md").write_text("new", encoding="utf-8")
        self.assertEqual(bundles.commit_of(root), head + "-dirty", "an untracked file")
        (root / "skills/a/new.md").unlink()
        (root / "skills/a/SKILL.md").write_text("y", encoding="utf-8")
        self.assertEqual(bundles.commit_of(root), head + "-dirty", "an edited file")

    def test_untracked_files_mark_the_commit_dirty_whatever_the_status_config(self):
        root = repo({"skills/a/SKILL.md": "x"})
        subprocess.run(["git", "-C", str(root), "config", "status.showUntrackedFiles", "no"],
                       check=True, capture_output=True, env=GIT_ENV)
        head = bundles.commit_of(root)
        (root / "skills/a/new.md").write_text("new", encoding="utf-8")
        self.assertEqual(bundles.commit_of(root), head + "-dirty")


if __name__ == "__main__":
    unittest.main()
