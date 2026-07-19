#!/usr/bin/env sh
# Bumps the version in lockstep across all manifests.
# Usage: scripts/bump-version.sh <new-version>
# Example: scripts/bump-version.sh 0.2.0

set -eu

if [ "$#" -ne 1 ]; then
    echo "usage: $0 <new-version>" >&2
    exit 1
fi

NEW="$1"
REPO_ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"

# All six manifest files that must be updated in lockstep:
FILES="
package.json
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
.codex-plugin/plugin.json
gemini-extension.json
plugin.json
"

cd "$REPO_ROOT"

for f in $FILES; do
    if [ ! -f "$f" ]; then
        echo "missing manifest: $f" >&2
        exit 1
    fi
    # Replace every "version": "X.Y.Z" occurrence. marketplace.json has both
    # a top-level version AND a nested plugins[].version; both should match.
    tmp="$(mktemp)"
    sed -E 's/"version": "[^"]+"/"version": "'"$NEW"'"/g' "$f" > "$tmp"
    mv "$tmp" "$f"
    echo "updated $f -> $NEW"
done

# Insert a new heading at the top of CHANGELOG.md if Unreleased exists AND
# no heading for this version already exists. This makes the script idempotent.
if grep -qE "^## \\[$NEW\\]" CHANGELOG.md; then
    echo "CHANGELOG.md already has [$NEW] heading; skipping insertion"
elif grep -q '^## \[Unreleased\]$' CHANGELOG.md; then
    today="$(date -u +%Y-%m-%d)"
    awk -v ver="$NEW" -v today="$today" '
        /^## \[Unreleased\]$/ {
            print
            print ""
            print "## [" ver "] - " today
            next
        }
        { print }
    ' CHANGELOG.md > CHANGELOG.md.tmp && mv CHANGELOG.md.tmp CHANGELOG.md
    echo "inserted [$NEW] heading in CHANGELOG.md"
fi

echo "done. Review with: git diff"
