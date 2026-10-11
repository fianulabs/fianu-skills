#!/usr/bin/env python3
"""Runs every code block in the skills, so an example cannot rot.

    python3 scripts/check-code-blocks.py [--facts facts/facts.json]

rego   compiled with `opa check` the way the evaluator parses (v0, then v1),
       with Fianu's builtins declared and its removed builtins taken away. A
       block without a package line is a fragment, checked inside one.
json   parsed; jsonc is parsed after stripping // and /* */ comments.
yaml   parsed with PyYAML.
Other fences (bash, http, text, ...) are prose and are not run.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Groups: (1) the fence's own indent (a fence nested inside a list item),
# (2) the language, (3) the body. The closing fence must match the same
# indent, so a fence anchored at column 0 does not falsely close one that is
# indented, and an indented fence is still found at all.
FENCE = re.compile(r"^( {0,3})```(\w+)[^\n]*\n(.*?)^\1```", re.S | re.M)
# Keeps a quoted string's contents intact (a "//" inside a URL included) and
# only strips a comment outside of one.
JSONC = re.compile(r'("(?:\\.|[^"\\])*")|//[^\n]*|/\*.*?\*/', re.S)
FRAGMENT = "package snippet\n\nimport rego.v1\n\n"
CHECKED = ("rego", "json", "jsonc", "yaml")


def strip_jsonc(body):
    return JSONC.sub(lambda m: m.group(1) or "", body)


def capabilities(facts):
    current = subprocess.run(["opa", "capabilities", "--current"], capture_output=True, text=True, check=True)
    caps = json.loads(current.stdout)
    removed = set(facts["regoRemoved"])
    caps["builtins"] = [b for b in caps["builtins"] if b["name"] not in removed] + facts["regoBuiltins"]
    return caps


def check_rego(body, caps_path):
    source = body if body.lstrip().startswith("package") else FRAGMENT + body
    with tempfile.NamedTemporaryFile("w", suffix=".rego") as f:
        f.write(source)
        f.flush()
        error = ""
        for flags in (["--v0-compatible"], []):  # the evaluator's order: v0, then v1
            r = subprocess.run(["opa", "check", *flags, "--capabilities", caps_path, f.name],
                               capture_output=True, text=True)
            if r.returncode == 0:
                return None
            error = (r.stdout + r.stderr).strip().splitlines()[0]
        return error


def check(lang, body, caps_path):
    try:
        if lang == "rego":
            return check_rego(body, caps_path)
        if lang == "json":
            json.loads(body)
        elif lang == "jsonc":
            json.loads(strip_jsonc(body))
        elif lang == "yaml":
            list(yaml.safe_load_all(body))  # multi-document YAML (---) is valid
    except (ValueError, yaml.YAMLError) as e:
        return str(e).splitlines()[0]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", default=str(ROOT / "facts" / "facts.json"))
    args = ap.parse_args()
    facts = json.loads(pathlib.Path(args.facts).read_text())
    failures, counted = [], 0
    with tempfile.NamedTemporaryFile("w", suffix=".json") as caps:
        json.dump(capabilities(facts), caps)
        caps.flush()
        for path in sorted((ROOT / "skills").rglob("*.md")):
            text = path.read_text()
            for m in FENCE.finditer(text):
                indent, lang, body = m.group(1), m.group(2), m.group(3)
                if lang not in CHECKED:
                    continue
                counted += 1
                if indent:
                    body = re.sub(rf"(?m)^{re.escape(indent)}", "", body)
                problem = check(lang, body, caps.name)
                if problem:
                    line = text[:m.start()].count("\n") + 1
                    failures.append(f"{path.relative_to(ROOT)}:{line} ({lang}): {problem}")
    if failures:
        print("\n".join(f"FAIL: {f}" for f in failures), file=sys.stderr)
        return 1
    print(f"check-code-blocks: {counted} blocks OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
