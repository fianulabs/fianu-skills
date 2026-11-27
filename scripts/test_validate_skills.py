"""Run: python3 -m unittest scripts/test_validate_skills.py

Regression coverage for [004]: validate-skills.sh's facts-region strip must
not be greedy across two regions on one line, and an unclosed opening marker
must not hide every canary after it.
"""
import os
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


def run_validate(root, env=None):
    dest = root / "scripts" / "validate-skills.sh"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    dest.chmod(0o755)
    return subprocess.run(["sh", str(dest)], cwd=root, capture_output=True, text=True,
                          env={**os.environ, **(env or {})})


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


def skill_of(lines, name="a", description="d"):
    """A SKILL.md of exactly `lines` newline-terminated lines."""
    head = f"---\nname: {name}\ndescription: {description}\n---\n"
    return head + "x\n" * (lines - 4)


class SizeLimitTest(unittest.TestCase):
    def test_501_lines_fails_and_names_the_file(self):
        result = run_validate(tree({"skills/a/SKILL.md": skill_of(501)}))
        out = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, out)
        self.assertIn("skills/a/SKILL.md", out)
        self.assertIn("501 lines", out)

    def test_500_lines_passes(self):
        result = run_validate(tree({"skills/a/SKILL.md": skill_of(500)}))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_1025_character_description_fails(self):
        result = run_validate(tree({"skills/a/SKILL.md": skill_of(10, description="d" * 1025)}))
        out = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, out)
        self.assertIn("1025 characters", out)

    def test_a_1024_character_description_passes(self):
        result = run_validate(tree({"skills/a/SKILL.md": skill_of(10, description="d" * 1024)}))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_501_lines_without_a_trailing_newline_fails(self):
        result = run_validate(tree({"skills/a/SKILL.md": skill_of(501).rstrip("\n")}))
        out = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, out)
        self.assertIn("501 lines", out)

    def test_a_description_is_counted_in_characters_in_any_locale(self):
        text = skill_of(10, description="\u2014" + "d" * 1023)  # 1024 characters, 1026 bytes
        for locale in ("C", "en_US.UTF-8"):
            result = run_validate(tree({"skills/a/SKILL.md": text}), env={"LC_ALL": locale})
            self.assertEqual(result.returncode, 0, locale + result.stdout + result.stderr)

    def test_a_description_spread_over_lines_fails(self):
        for value in (">-\n  " + "d" * 2000, '"first line\n  second line"'):
            result = run_validate(tree({"skills/a/SKILL.md": skill_of(10, description=value)}))
            out = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, out)
            self.assertIn("one line", out)

    def test_emphasis_words_outside_code_fences_warn_and_still_pass(self):
        body = "You MUST do this.\nNEVER skip that. ALWAYS check.\nMUSTARD is fine.\n```\nIMPORTANT in code\n```\n"
        result = run_validate(tree({"skills/a/SKILL.md": SKILL.format(name="a", body=body)}))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("skills/a/SKILL.md: 2 lines", result.stderr)


if __name__ == "__main__":
    unittest.main()
