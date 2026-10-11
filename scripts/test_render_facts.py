"""Run: python3 -m unittest scripts/test_render_facts.py"""
import importlib.util
import pathlib
import unittest

spec = importlib.util.spec_from_file_location("facts", pathlib.Path(__file__).with_name("render-facts.py"))
facts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(facts)

FACTS = {
    "measureTypes": ["section", "metric"],
    "resultPrecedence": ["pass", "inProgress", "warn", "notRequired", "notFound", "fail"],
    "entityStatuses": ["draft", "active"],
    "entityStates": ["draft", "published"],
}


class RenderTest(unittest.TestCase):
    def test_fills_regions_and_keeps_the_markers(self):
        text = "Types: <!-- facts:measure-types -->stale<!-- /facts:measure-types -->."
        self.assertEqual(facts.render(text, FACTS, "x.md"),
                         "Types: <!-- facts:measure-types -->`section`, `metric`<!-- /facts:measure-types -->.")

    def test_rendering_is_idempotent(self):
        once = facts.render("<!-- facts:result-precedence --><!-- /facts:result-precedence -->", FACTS, "x.md")
        self.assertEqual(facts.render(once, FACTS, "x.md"), once)
        self.assertIn("`pass` > `inProgress`", once)

    def test_block_regions_render_tables(self):
        out = facts.render("<!-- facts:entity-lifecycle -->\n<!-- /facts:entity-lifecycle -->", FACTS, "x.md")
        self.assertIn("| `status` | `draft`, `active` |", out)

    def test_unknown_region_fails(self):
        with self.assertRaises(SystemExit):
            facts.render("<!-- facts:nope --><!-- /facts:nope -->", FACTS, "x.md")

    def test_mismatched_closing_marker_fails(self):
        with self.assertRaises(SystemExit):
            facts.render("<!-- facts:measure-types -->x<!-- /facts:measure-type -->", FACTS, "x.md")

    def test_unclosed_marker_fails(self):
        with self.assertRaises(SystemExit):
            facts.render("<!-- facts:measure-types -->x and no close", FACTS, "x.md")

    def test_a_typo_never_swallows_prose(self):
        text = ("<!-- facts:measure-types -->a<!-- /facts:measure-typo --> KEEP "
                "<!-- facts:measure-types -->b<!-- /facts:measure-types -->")
        with self.assertRaises(SystemExit):
            facts.render(text, FACTS, "x.md")


if __name__ == "__main__":
    unittest.main()
