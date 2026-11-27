#!/usr/bin/env sh
# Warns when a pull request adds more than 400 hand-written lines under skills/.
#   sh scripts/check-diff-size.sh <base-ref>
# Generated text (vendored provider docs, the API index) is not counted. A big
# diff is hard to review well, so the warning asks for a split. Always exits 0.

set -eu

added="$(git diff --numstat "$1...HEAD" -- skills \
    ':(exclude)skills/*/references/provider-docs/*' \
    ':(exclude)skills/using-fianu-api/references/api-index.md' \
    | awk '{ s += $1 } END { print s + 0 }')"

if [ "$added" -gt 400 ]; then
    echo "::warning::This change adds $added hand-written lines under skills/ (over 400). Split it into smaller pull requests so each can be read end to end."
fi
exit 0
