"""Run: python3 -m unittest scripts/test_check_code_blocks.py

Regression coverage for [007]: a jsonc block with `//` inside a string must
not be reported as a failure, multi-document YAML must parse, and a fence
indented inside a list item must still be found and checked.

Also [005]: the FIANU.md SonarQube example must actually pass on input shaped
like the real sonarqube.sca schema (numeric-string ratings under
measures.reliability/measures.maintainability), not just compile.
"""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("blocks", pathlib.Path(__file__).with_name("check-code-blocks.py"))
blocks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(blocks)

ROOT = pathlib.Path(__file__).resolve().parent.parent


class CheckTest(unittest.TestCase):
    def test_jsonc_keeps_slashes_inside_strings(self):
        self.assertIsNone(blocks.check("jsonc", '{"url": "https://x.io/a"} // trailing\n', None))

    def test_multi_document_yaml_parses(self):
        self.assertIsNone(blocks.check("yaml", "a: 1\n---\nb: 2\n", None))

    def test_indented_fence_is_found(self):
        text = "- step\n   ```json\n   {bad\n   ```\n"
        self.assertEqual([m.group(2) for m in blocks.FENCE.finditer(text)], ["json"])


@unittest.skipUnless(shutil.which("opa"), "opa is not installed")
class SonarExampleTest(unittest.TestCase):
    def test_code_quality_example_passes_on_sonar_shaped_input(self):
        text = (ROOT / "skills/using-fianu-best-practices/references/FIANU.md").read_text()
        rule = next(m.group(3) for m in blocks.FENCE.finditer(text) if "rank :=" in m.group(3))
        inp = {"detail": {"measures": {"reliability": {"reliability_rating": "1.0"},
                                        "maintainability": {"sqale_rating": "2.0"}}}}
        data = {"scores": {"reliability": {"minimum": "A"}, "maintainability": {"minimum": "B"}}}
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / "r.rego").write_text(rule)
            (p / "i.json").write_text(json.dumps(inp))
            (p / "d.json").write_text(json.dumps(data))
            out = subprocess.run(["opa", "eval", "-f", "raw", "-d", str(p / "r.rego"), "-d", str(p / "d.json"),
                                   "-i", str(p / "i.json"), "data.rule.pass"],
                                  capture_output=True, text=True, check=True)
        self.assertEqual(out.stdout.strip(), "true")


if __name__ == "__main__":
    unittest.main()
