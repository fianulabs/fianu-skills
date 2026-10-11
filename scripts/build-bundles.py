#!/usr/bin/env python3
"""Builds one prompt bundle per agent entry point and fails on any pointer a
bundle cannot satisfy.

    python3 scripts/build-bundles.py [--out dist/bundles] [--version main] [--check]

A bundle is what the in-cluster agent sends as its system prompt, before core
appends its scaffolding: every SKILL.md body the manifest lists for the entry
point, frontmatter stripped, in manifest order, then every file those bodies
point at, once each, in first-mention order.

Pointers recognised in SKILL.md bodies:
  references/<file>.md               a file in the same skill's references/
  <skill>/references/<file>.md       a file in another skill's references/
  `<skill>` -> <file>.md             the same, in prose (the arrow is -> or U+2192)
  <file>.md §<A> > <B> / §<C>        every section named must be a heading in <file>
A pointer sits on one line. It dangles when its file is missing, its skill is
not in the same entry point, or a section it names is not a heading. §<...>
placeholders are ignored.

Each bundle is written as <entry>.<sha256 prefix>.md. index.json records the
version, the commit (suffixed -dirty when the tree had uncommitted changes) and,
per entry point, that file, its sha256 and its size, which the agent verifies
and logs at boot. Because names follow content, an older index still names
bundles that exist, so a publish uploads bundles first and index.json last and
never deletes a bundle. Nothing is written unless every bundle built. --check
builds in memory and only reports.
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
POINTER = re.compile(
    r"(?:`(?P<skill>[a-z0-9-]+)`\s*(?:->|→)\s*|(?P<pathskill>[a-z0-9-]+)/(?=references/))?"
    r"(?:references/)?(?P<file>[A-Za-z0-9_-]+\.md)"
    r"(?P<sections>(?:\s*/?\s*§[^§\n|`]+)*)")
SECTION = re.compile(r"§([^§\n|`/]+)")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.M)
PROSE_TAIL = re.compile(r"\s+(?:—|for)\s.*$")
JOINER = "\n\n---\n\n"


def body(path):
    """SKILL.md text below its YAML frontmatter."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1:])
    return text


def sections_of(raw):
    """§Controls > Designing a Control / §Gates -> [["Controls", "Designing a Control"], ["Gates"]]."""
    out = []
    for m in SECTION.finditer(raw or ""):
        text = PROSE_TAIL.sub("", m.group(1)).strip().rstrip(".").strip()
        if text.startswith("<"):
            continue  # a §<Section Title> placeholder in prose about the convention
        out.append([part.strip() for part in text.split(">")])
    return out


def pointers(skill, text):
    """(skill dir, file name, section paths) for every pointer in a body."""
    for m in POINTER.finditer(text):
        name = m.group("file")
        if name == "SKILL.md":
            continue
        yield m.group("skill") or m.group("pathskill") or skill, name, sections_of(m.group("sections"))


def build(root, entry, skills):
    """Returns (bundle text, dangling pointer messages)."""
    parts, refs, problems = [], {}, []
    for skill in skills:
        text = body(root / "skills" / skill / "SKILL.md")
        parts.append(f"<!-- skill: {skill} -->\n{text.strip()}")
        for owner, name, sections in pointers(skill, text):
            where = f"{entry}: skills/{skill}/SKILL.md -> {owner}/{name}"
            if owner not in skills:
                problems.append(f"{where}: skill {owner!r} is not in this entry point's manifest list")
                continue
            path = root / "skills" / owner / "references" / name
            if not path.is_file():
                problems.append(f"{where}: skills/{owner}/references/{name} does not exist")
                continue
            content = path.read_text(encoding="utf-8")
            headings = set(HEADING.findall(content))
            for section in sections:
                missing = [s for s in section if not s or s not in headings]
                if missing:
                    problems.append(f"{where}: section {' > '.join(section)!r} has no heading {missing[0]!r}")
            refs.setdefault(f"skills/{owner}/references/{name}", content)
    for key, content in refs.items():
        parts.append(f"<!-- reference: {key} -->\n# Reference: {key}\n\n{content.strip()}")
    return JOINER.join(parts) + "\n", problems


def build_all(root, version, commit):
    """Every entry point's bundle, in memory: (index, bundle bytes by file name,
    dangling pointer messages)."""
    manifest = json.loads((root / "manifests" / "agent-contexts.json").read_text(encoding="utf-8"))
    index = {"version": version, "commit": commit, "bundles": {}}
    files, problems = {}, []
    for entry, skills in sorted(manifest.items()):
        text, found = build(root, entry, skills)
        problems += found
        data = text.encode("utf-8")
        digest = hashlib.sha256(data).hexdigest()
        name = f"{entry}.{digest[:12]}.md"
        index["bundles"][entry] = {"file": name, "sha256": digest, "bytes": len(data)}
        files[name] = data
    return index, files, problems


def write_bundles(root, out, version, commit):
    """Builds every bundle and moves the set into out, or writes nothing when a
    pointer dangles. Returns (index, problems)."""
    index, files, problems = build_all(root, version, commit)
    if problems:
        return index, problems
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out.parent) as tmp:  # beside out, so each move is a rename
        staged = pathlib.Path(tmp)
        for name, data in files.items():
            (staged / name).write_bytes(data)
        (staged / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
        for name in [*files, "index.json"]:  # bundles first: out never holds an index naming a bundle it lacks
            os.replace(staged / name, out / name)
    return index, problems


def commit_of(root):
    """HEAD, suffixed -dirty when the tree has uncommitted changes, untracked
    files included whatever status.showUntrackedFiles says: the commit alone
    would not reproduce the bundles."""
    def git(*args):
        return subprocess.run(["git", "--no-optional-locks", "-C", str(root), *args],
                              capture_output=True, encoding="utf-8", check=True).stdout.strip()
    head = git("rev-parse", "HEAD")
    return head + "-dirty" if git("status", "--porcelain", "--untracked-files=normal") else head


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "dist" / "bundles"))
    ap.add_argument("--version", default="main")
    ap.add_argument("--check", action="store_true")
    # A tree laid out like this repo (skills/, manifests/agent-contexts.json),
    # e.g. this repo's skills merged with a downstream repo's own.
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--commit", help="commit to record; default: HEAD of --root")
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    commit = args.commit or commit_of(root)
    if args.check:
        index, _, problems = build_all(root, args.version, commit)
    else:
        index, problems = write_bundles(root, pathlib.Path(args.out), args.version, commit)
    if problems:
        print("\n".join(f"FAIL: {p}" for p in problems), file=sys.stderr)
        return 1
    for entry, meta in index["bundles"].items():
        print(f"{entry}: {meta['file']} ({meta['bytes']} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
