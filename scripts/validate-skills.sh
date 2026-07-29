#!/usr/bin/env sh
# Validates SKILL.md files:
#   1. Every skills/<dir>/ contains a SKILL.md.
#   2. Every SKILL.md begins with YAML frontmatter containing `name:` and `description:`.
#   3. `name:` matches the directory name.
#   4. Canonical-home canaries: if a canary string appears anywhere in skills/*/SKILL.md
#      it MUST be in its declared owner. Missing entirely is OK (warns) — that just
#      means the canonical owner's body hasn't been written yet.
#   5. Agent manifest: every skill named in manifests/agent-contexts.json resolves
#      to an existing skills/<name>/SKILL.md.
#
# Exits non-zero on any violation.

set -eu

REPO_ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$REPO_ROOT"

FAIL=0

# Each canary line below is "<canary string><TAB><expected owner skill>". The
# script fails if the canary appears in a SKILL.md outside its expected owner.
# If the canary does not appear anywhere, that's a warning (the owner's body is
# still a stub). TAB delimiter is required because some canaries contain pipes.
CANARIES="$(printf '%s\t%s\n' \
    'config.resolved_approvers' 'working-with-tickets' \
    'bot|fianu-agent'           'working-with-tickets' \
    'GET /pods/entities'        'working-with-llm-context-rules' \
    'import rego.v1'            'writing-rego-rules' \
    '/internal/upload'          'working-with-attestations' \
    '/assets/releases/'         'working-with-release-gating' \
    'recomputeStatus'           'working-with-indexes' \
    '.(list_string)'            'writing-cel-expressions' \
    '/notes/:uuid/findings'     'working-with-findings-and-violations' \
    '/evidence/assets/by-series' 'working-with-findings-and-violations' \
)"

# --- Check 1+2+3: frontmatter ---
if [ ! -d skills ]; then
    echo "FAIL: skills/ directory does not exist" >&2
    exit 1
fi

skill_dirs="$(find skills -mindepth 1 -maxdepth 1 -type d | sort)"
if [ -z "$skill_dirs" ]; then
    echo "FAIL: skills/ contains no skill directories" >&2
    exit 1
fi

# Iterate via for-loop (not pipeline) so FAIL=1 stays in the parent shell.
# Skill directory names are kebab-case with no whitespace, so word-splitting is safe.
for dir in $skill_dirs; do
    name="$(basename "$dir")"
    skill="$dir/SKILL.md"

    if [ ! -f "$skill" ]; then
        echo "FAIL: missing $skill" >&2
        FAIL=1
        continue
    fi

    # Frontmatter must be the first line and be `---`.
    if ! head -n 1 "$skill" | grep -qx -- "---"; then
        echo "FAIL: $skill missing YAML frontmatter (must start with ---)" >&2
        FAIL=1
        continue
    fi

    declared="$(head -n 10 "$skill" | sed -n 's/^name: *//p' | head -n 1)"
    if [ -z "$declared" ]; then
        echo "FAIL: $skill missing 'name:' in frontmatter" >&2
        FAIL=1
        continue
    fi
    if [ "$declared" != "$name" ]; then
        echo "FAIL: $skill declares name=$declared but directory is $name" >&2
        FAIL=1
    fi

    desc="$(head -n 10 "$skill" | sed -n 's/^description: *//p' | head -n 1)"
    if [ -z "$desc" ]; then
        echo "FAIL: $skill missing or empty 'description:' in frontmatter" >&2
        FAIL=1
    fi
done

# --- Check 4: canary strings ---
# Canaries are scanned in SKILL.md BODIES only — everything after the closing
# `---` of the YAML frontmatter. Descriptions in frontmatter are load-trigger
# text and naturally reference canonical keywords; only the body content
# carries the canonical-home obligation.
#
# TAB-separated; use printf to declare the separator portably.
TAB="$(printf '\t')"
echo "$CANARIES" | while IFS="$TAB" read -r canary owner; do
    [ -z "$canary" ] && continue

    # Build a list of SKILL.md files whose BODY contains the canary.
    hits=""
    for d in $skill_dirs; do
        s="$d/SKILL.md"
        [ -f "$s" ] || continue
        # Body = everything after the second `---` line.
        body="$(awk 'NR>1 && /^---$/ {found=1; next} found' "$s")"
        if printf '%s' "$body" | grep -qF -- "$canary"; then
            hits="$hits $s"
        fi
    done

    if [ -z "$hits" ]; then
        echo "WARN: canary '$canary' not found in any SKILL.md body (expected owner: $owner)" >&2
        continue
    fi

    for h in $hits; do
        dir="$(basename "$(dirname "$h")")"
        if [ "$dir" != "$owner" ]; then
            echo "FAIL: canary '$canary' appears in skills/$dir/SKILL.md body but canonical home is skills/$owner/SKILL.md" >&2
            echo "_FAIL_" > /tmp/validate-skills.fail
        fi
    done
done

if [ -f /tmp/validate-skills.fail ]; then
    rm -f /tmp/validate-skills.fail
    FAIL=1
fi

# --- Check 5: agent manifest resolves ---
# Every skill named in the agent manifest must map to an existing SKILL.md.
# Value lines are bare quoted strings (optionally comma-terminated); key lines
# end with ": [" and are excluded by the trailing anchor. Names are kebab-case
# with no whitespace, so word-splitting the result is safe.
MANIFEST="manifests/agent-contexts.json"
if [ -f "$MANIFEST" ]; then
    manifest_names="$(sed -n 's/^[[:space:]]*"\([a-z0-9-]*\)"[,]*[[:space:]]*$/\1/p' "$MANIFEST")"
    for mname in $manifest_names; do
        if [ ! -f "skills/$mname/SKILL.md" ]; then
            echo "FAIL: $MANIFEST references '$mname' but skills/$mname/SKILL.md does not exist" >&2
            FAIL=1
        fi
    done
fi

if [ "$FAIL" -eq 0 ]; then
    echo "validate-skills: OK"
fi
exit "$FAIL"
