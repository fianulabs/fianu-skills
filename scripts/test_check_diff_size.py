"""Run: python3 -m unittest scripts/test_check_diff_size.py"""
import pathlib
import subprocess
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).with_name("check-diff-size.sh")


def git(root, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=root, check=True, capture_output=True)


class CheckDiffSizeTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)
        git(self.root, "init", "-q", "-b", "main")
        self.add("skills/a/SKILL.md", 1)
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "base")
        git(self.root, "checkout", "-qb", "feature")

    def add(self, rel, lines):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n" * lines)

    def run_check(self):
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "change")
        result = subprocess.run(["sh", str(SCRIPT), "main"], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_401_hand_written_lines_warn(self):
        self.add("skills/a/references/new.md", 401)
        out = self.run_check()
        self.assertIn("::warning::", out)
        self.assertIn("401", out)

    def test_400_lines_do_not_warn(self):
        self.add("skills/a/references/new.md", 400)
        self.assertNotIn("::warning::", self.run_check())

    def test_generated_lines_do_not_count(self):
        self.add("skills/a/references/provider-docs/big.md", 600)
        self.add("skills/using-fianu-api/references/api-index.md", 400)
        self.assertNotIn("::warning::", self.run_check())


if __name__ == "__main__":
    unittest.main()
