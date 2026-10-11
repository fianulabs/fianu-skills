"""Run: python3 -m unittest scripts/test_validate_skills.py

Regression coverage for [004]: validate-skills.sh's facts-region strip must
not be greedy across two regions on one line, and an unclosed opening marker
must not hide every canary after it.
"""
import pathlib
import subprocess
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).with_name("validate-skills.sh")
SKILL = "---\nname: {name}\ndescription: d\n---\n{body}\n"


def tree(files):
    root = pathlib.Path(tempfile.mkdtemp())
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def run_validate(root):
    dest = root / "scripts" / "validate-skills.sh"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    dest.chmod(0o755)
    return subprocess.run(["sh", str(dest)], cwd=root, capture_output=True, text=True)


class ValidateSkillsTest(unittest.TestCase):
    def test_a_canary_between_two_same_line_regions_is_still_detected(self):
        root = tree({
            "skills/a/SKILL.md": SKILL.format(name="a", body="record_violation"),
            "skills/b/SKILL.md": SKILL.format(name="b", body=(
                "<!-- facts:measure-types -->x<!-- /facts:measure-types --> "
                "record_violation "
                "<!-- facts:result-keys -->y<!-- /facts:result-keys -->")),
        })
        result = run_validate(root)
        out = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, out)
        self.assertIn("skills/b/SKILL.md", out)

    def test_an_unclosed_marker_does_not_hide_a_later_canary(self):
        root = tree({
            "skills/a/SKILL.md": SKILL.format(name="a", body="record_violation"),
            "skills/b/SKILL.md": SKILL.format(name="b", body=(
                "<!-- facts:measure-types -->x and no close\n"
                "record_violation\n")),
        })
        result = run_validate(root)
        out = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, out)
        self.assertIn("skills/b/SKILL.md", out)


if __name__ == "__main__":
    unittest.main()
