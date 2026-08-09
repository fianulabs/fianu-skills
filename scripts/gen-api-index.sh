#!/usr/bin/env bash
# Regenerates skills/using-fianu-api/references/api-index.md from the core repo's
# proxy config, which is the authoritative list of externally reachable /api routes.
#
#   ./scripts/gen-api-index.sh [--check] [path-to-core-repo]
#
# --check regenerates to a temp file and diffs; non-zero exit means the shipped
# index has drifted from the core repo (or someone hand-edited it).
#
# Core repo location resolves in this order:
#   1. $1
#   2. $FIANU_CORE_REPO
#   3. ../core (sibling checkout)
#
# The index is GENERATED. Never hand-edit it — edit this script or the upstream
# proxies.yaml and re-run. Re-run at every `bump-version.sh`; the header stamps
# the core commit it was built from so staleness is visible.
set -euo pipefail

CHECK=0
if [ "${1:-}" = "--check" ]; then
    CHECK=1
    shift
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CORE="${1:-${FIANU_CORE_REPO:-$REPO_ROOT/../core}}"
PROXIES="$CORE/cmd/proxy/kodata/config/proxies"
SHIPPED="$REPO_ROOT/skills/using-fianu-api/references/api-index.md"
OUT="$SHIPPED"
if [ "$CHECK" -eq 1 ]; then
    OUT="$(mktemp)"
    trap 'rm -f "$OUT"' EXIT
fi

if [ ! -d "$PROXIES" ]; then
    echo "FAIL: proxy config not found at $PROXIES" >&2
    echo "      pass the core repo path as \$1 or set FIANU_CORE_REPO" >&2
    exit 1
fi

CORE_SHA="$(git -C "$CORE" rev-parse --short HEAD 2>/dev/null || echo unknown)"

mkdir -p "$(dirname "$OUT")"
PROXIES="$PROXIES" CORE_SHA="$CORE_SHA" OUT="$OUT" python3 - <<'PY'
import glob, os, yaml

proxies, sha, out = os.environ["PROXIES"], os.environ["CORE_SHA"], os.environ["OUT"]


def auth_of(adm):
    """One-token summary of a proxy admission block."""
    if not adm:
        return "token"
    if adm.get("disabled"):
        # Proxy admission bypassed. The downstream service may still authenticate,
        # so this is "not gated at the proxy", NOT "callable without a token".
        return "ungated"
    if adm.get("roles"):
        return "role:" + ",".join(r["name"] for r in adm["roles"])
    if adm.get("features"):
        return ",".join(f["name"] for f in adm["features"])
    return "token"


rows = set()
for path in sorted(glob.glob(os.path.join(proxies, "*", "proxies.yaml"))):
    doc = yaml.safe_load(open(path)) or {}
    for p in doc.get("proxies") or []:
        auth = auth_of(p.get("admission"))
        service = p.get("service", "?")
        # The internal path the proxy forwards to. Other skills in this library
        # document endpoints by dest, not by external path, so this column is
        # the join key between the index and the rest of the library.
        dest = p.get("dest", "")
        # aliases are alternate external paths onto the same handler; an agent
        # grepping for a path must find it whether it is canonical or an alias.
        paths = [(p.get("path", ""), "")]
        # Both spellings occur upstream: `aliases:` on most entries, `alias:` on
        # at least one. Reading only the plural silently drops that route.
        for key in ("aliases", "alias"):
            v = p.get(key)
            for a in v if isinstance(v, list) else ([v] if v else []):
                paths.append((a, " (alias)"))
        for route, tag in paths:
            if not route:
                continue
            for method in p.get("methods") or ["GET"]:
                rows.add((route, method, service, auth + tag, dest))

lines = [
    f"{m:<6} {r:<62} {d:<52} {s:<16} {a}".rstrip()
    for r, m, s, a, d in sorted(rows)
]

header = f"""# Fianu API index

GENERATED — do not hand-edit. Regenerate with `./scripts/gen-api-index.sh`.

Source: `core@{sha}` `cmd/proxy/kodata/config/proxies/*/proxies.yaml`
Routes: {len(lines)}

**Grep this file. Do not read it whole** — it is ~{sum(len(l) + 1 for l in lines) // 1024}KB.

    grep -i ticket references/api-index.md
    grep -E '^GET .*/attestations' references/api-index.md

Columns: `METHOD  PATH  DEST  SERVICE  AUTH`

- `PATH` is the external path — what you call. Pass it to `fianu api`
  **without** the leading `/api`; that prefix is added for you.
- `DEST` is the internal path the proxy forwards to. You never call it, but
  **other skills in this library document endpoints by DEST**, so this column
  is how you match a path quoted elsewhere to a callable one. Grep both.
- `AUTH` is what the **proxy** admits on: `feature:<name>` (token needs
  read/write on that feature), `role:<name>`, `token` (any valid token), or
  `ungated` (proxy does not gate it — the service behind it may still require a
  token, so always send one). A `feature:` or `role:` you lack is a 403, not a 404.
- `(alias)` marks an alternate path onto the same handler.

This index carries paths, methods, and auth only — **not** request bodies or
response shapes. For those, load the skill that owns the endpoint (see
`using-fianu-skills`), or probe with a GET first.

```
"""

with open(out, "w") as fh:
    fh.write(header)
    fh.write("\n".join(lines))
    fh.write("\n```\n")

print(f"wrote {out} ({len(lines)} routes, core@{sha})")
PY

if [ "$CHECK" -eq 1 ]; then
    # The `Source:` line stamps the core commit, which moves on every core commit
    # whether or not any route changed. Drift means the ROUTES differ.
    if diff -u <(grep -v '^Source:' "$SHIPPED") <(grep -v '^Source:' "$OUT"); then
        echo "gen-api-index --check: OK"
    else
        echo "FAIL: api-index.md has drifted; run ./scripts/gen-api-index.sh" >&2
        exit 1
    fi
fi
