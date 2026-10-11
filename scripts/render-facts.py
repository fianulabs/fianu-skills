#!/usr/bin/env python3
"""Renders platform facts into marked regions of the skills.

    python3 scripts/render-facts.py [--facts facts/facts.json] [--check]

facts/facts.json is generated from the platform source, never by hand. A region
is a pair of HTML comments and everything between them is generated:

    <!-- facts:measure-types -->`section`, `metric`<!-- /facts:measure-types -->

An unknown region name fails, so a typo cannot hide a stale fact. --check exits
1 when any file would change; CI runs it on every PR.
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Region content cannot contain another marker: a typo'd closing name (which
# would otherwise never match, so neither render nor --check sees it) and a
# mismatched pair (whose lazy body would run past the real closing marker,
# swallowing everything between — prose, and even the next opening marker)
# both fail loudly instead of silently rendering nothing or eating content.
# MARKER re-counts every marker in the file so an unclosed or unpaired one
# cannot slip through undetected.
REGION = re.compile(r"<!-- facts:([a-z0-9-]+) -->((?:(?!<!-- /?facts:).)*)<!-- /facts:([a-z0-9-]+) -->", re.S)
MARKER = re.compile(r"<!-- /?facts:")
SCHEMA_VERSION = 1


def codes(values):
    return ", ".join(f"`{v}`" for v in values or [])


def table(header, rows):
    lines = ["", "| " + " | ".join(header) + " |", "|" + " --- |" * len(header)]
    return "\n".join(lines + ["| " + " | ".join(r) + " |" for r in rows] + [""])


RENDER = {
    "measure-types": lambda f: codes(f["measureTypes"]),
    "measure-values": lambda f: codes(f["measureValues"]),
    "measure-name-pattern": lambda f: f"`{f['measureNamePattern']}`",
    "result-keys": lambda f: codes(f["resultKeys"]),
    "result-precedence": lambda f: " > ".join(f"`{k}`" for k in f["resultPrecedence"]),
    "entity-lifecycle": lambda f: table(["Axis", "Values"], [
        ["`status`", codes(f["entityStatuses"])],
        ["`state`", codes(f["entityStates"])],
    ]),
    "rego-parsers": lambda f: (
        "The evaluator parses a rule as Rego " + ", then ".join(f"`{v}`" for v in f["regoParsers"])
        + ", so both syntaxes work. Write new rules with `import rego.v1`."),
    "rego-builtins": lambda f: table(["Builtin", "Arguments"], [
        [f"`{b['name']}`", str(len(b["decl"]["args"]))] for b in f["regoBuiltins"]
    ]),
    "rego-removed": lambda f: codes(f["regoRemoved"]),
    "series-names": lambda f: codes(f["seriesNames"]),
    "asset-types": lambda f: codes(f["assetTypes"]),
    "producer-catalog": lambda f: table(["Plugin", "Relation path", "Detail fields"], [
        [f"`{p['plugin']}`", f"`{p['relationPath'] or '(default)'}`", codes(p["detailFields"])] for p in f.get("producers", [])
    ]),
}


def render(text, facts, where):
    matched = 0

    def fill(m):
        nonlocal matched
        name, closing = m.group(1), m.group(3)
        if name != closing:
            raise SystemExit(f"FAIL: {where}: region {name!r} closed by {closing!r}")
        if name not in RENDER:
            raise SystemExit(f"FAIL: {where}: unknown facts region {name!r}")
        matched += 1
        return f"<!-- facts:{name} -->{RENDER[name](facts)}<!-- /facts:{name} -->"

    out = REGION.sub(fill, text)
    if len(MARKER.findall(text)) != 2 * matched:
        raise SystemExit(f"FAIL: {where}: unpaired facts marker")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", default=str(ROOT / "facts" / "facts.json"))
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    facts = json.loads(pathlib.Path(args.facts).read_text())
    if facts.get("schemaVersion") != SCHEMA_VERSION:
        raise SystemExit(f"FAIL: facts schemaVersion {facts.get('schemaVersion')} != {SCHEMA_VERSION}; update this script")
    # Render every file into memory first; a SystemExit on a later file must
    # not leave earlier files already rewritten and later ones untouched.
    stale = []
    rendered = {}
    for path in sorted((ROOT / "skills").rglob("*.md")):
        text = path.read_text()
        out = render(text, facts, path.relative_to(ROOT))
        if out != text:
            stale.append(str(path.relative_to(ROOT)))
            rendered[path] = out
    if not args.check:
        for path, out in rendered.items():
            path.write_text(out)
    if args.check and stale:
        print("\n".join(f"FAIL: {p} is out of date with {args.facts}; run scripts/render-facts.py" for p in stale), file=sys.stderr)
        return 1
    print(f"render-facts: {len(stale)} file(s) {'stale' if args.check else 'updated'}; facts from core {facts.get('core', '?')[:7]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
