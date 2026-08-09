---
name: using-fianu-api
description: "Use when investigating anything on the Fianu platform that no other skill covers an endpoint for — an unfamiliar path, an ad-hoc query, following a reference from one record to another, or confirming what the platform actually returned. Covers the `fianu api` CLI (auth, /api prefixing, -f/-F/--input, --paginate, --jq) and a grep-able index of every externally reachable route with its method and required feature or role."
---

# Using the Fianu API

## Overview

Every other skill in this plugin documents the handful of endpoints it owns.
That is a small slice of the platform — the proxy exposes roughly 900 routes.
When an investigation needs a path no skill documents, the answer is not to
guess a URL or to stop: it is to look the route up in the index here and call
it with `fianu api`.

This skill is the canonical home for **how to reach the API from a shell**.
It does not own the meaning of any endpoint's payload — that belongs to the
skill that owns the entity (see `using-fianu-skills` for routing).

## Prefer `fianu api` over raw HTTP

`fianu api` is a thin authenticated passthrough (the `gh api` model). It
handles the token exchange, the `/api` prefix, JSON encoding, pagination, and
exit codes. Hand-rolled `curl` reproduces all of that badly.

```bash
fianu api tickets/:uuid
```

Reach for raw HTTP only when `fianu` is not installed in the environment. The
wire-level contract for that fallback is in
`skills/using-fianu-skills/references/api-conventions.md`.

## Finding an endpoint

`references/api-index.md` lists every externally reachable route as
`METHOD  PATH  DEST  SERVICE  AUTH`.

**Grep it. Never read it whole** — it is ~140KB and will crowd out the actual
investigation.

```bash
grep -i 'exception' references/api-index.md
grep -E '^GET .*/assets/:asset/' references/api-index.md
grep -E '^(POST|PUT|PATCH) .*gates' references/api-index.md
```

Read the `AUTH` column before calling. If it names a `feature:` or `role:`
your token does not carry, the call returns **403, not 404** — that is a
permissions problem, not a wrong path, and retrying other paths will waste
the investigation.

### Two path systems — PATH vs DEST

Fianu has two names for every endpoint, and this library uses both:

- **`PATH`** — the external route on the public proxy (`/api/entities/controls/:path`). This is what you call.
- **`DEST`** — the internal route the proxy forwards to on the owning service (`/controls/:path`). This is what the service's own handler registers.

Most other skills in this library quote endpoints by **DEST**, because that is
what the `../core` handlers are named. A few quote PATH. There is no reliable
way to tell which by looking, so:

**When a path from another skill returns 404, grep the index for it before
concluding anything is broken — it is probably a DEST, and the index's PATH
column on that same row is the callable form.**

```bash
# working-with-entities documents `GET /controls/:entity_key/schemas`; calling
# that directly 404s. Grep it, and the PATH column gives the callable route:
grep 'controls/:entity_key/schemas' references/api-index.md
# GET /api/entities/controls/:entity_key/schemas  /controls/:entity_key/schemas  console  feature:controls
# GET /api/console/controls/:entity_key/schemas   /controls/:entity_key/schemas  console  feature:controls (alias)
```

Two rows, one DEST: the canonical PATH plus an alias. Either PATH works.

The reverse also holds: a route you found in the index may appear in another
skill under its DEST name. Neither form is wrong; they name different hops.

The index carries paths, methods, and auth **only**. It does not carry request
bodies or response shapes. When you need those:

1. Load the skill that owns the entity (`using-fianu-skills` routes you).
2. Failing that, `GET` a record first and read the shape off the response
   before attempting a write.

## Calling an endpoint

Pass the path **without** `/api` — it is prepended for you.

| Endpoint argument | Resolves to |
|---|---|
| `releases/list` | `${FIANU_HOST}/api/releases/list` |
| `/releases/list` | `${FIANU_HOST}/api/releases/list` |
| `/api/releases/list` | `${FIANU_HOST}/api/releases/list` (not doubled) |
| `/auth/whoami` | `${FIANU_HOST}/auth/whoami` (only `/auth` bypasses `/api`) |
| `https://other/host/path` | used as-is — **the auth header is dropped** |

### Reads

```bash
fianu api tickets                                  # GET is the default
fianu api tickets -f status=open -f limit=50       # non-body method: fields become query params
fianu api tickets --paginate                       # follow Link rel=next to exhaustion
fianu api tickets/abc-123 --jq '.conditions[].name'
fianu api tickets/abc-123 -i                       # include status line + response headers
```

### Writes

**Supplying any of `-f`, `-F`, or `--input` flips the default method to POST.**
This is the single most common surprise: `fianu api tickets/:uuid/activities
-f body=hello` is a POST, not a GET with query params. For any other verb, be
explicit with `-X`.

```bash
fianu api tickets/abc-123/activities -f activityType=comment -f body='...'
fianu api entities/artifacts/deploy --input package.json
echo '{"...": "..."}' | fianu api some/endpoint --input -
fianu api some/endpoint -X PUT -F enabled=true -F threshold=3
```

`-f` sends every value as a string. `-F` types it: `true`/`false` → bool,
`null` → null, an integer literal → number, `@path` → the contents of that
file (`@-` reads stdin). Use `-F` whenever the server expects a non-string.

### Flags worth knowing

| Flag | Effect |
|---|---|
| `-X, --request` | HTTP method. Defaults to GET, or POST when a body source is present. |
| `-f, --raw-field` | `KEY=VALUE` string field. Repeatable. Query param on GET/DELETE, JSON body otherwise. |
| `-F, --field` | Same, but typed (bool / null / int / `@file`). Repeatable. |
| `--input` | Read the raw body from a file path; `-` reads stdin. |
| `-H, --header` | `KEY:VALUE`. Repeatable. `Content-Type: application/json` is set for you when there is a body. |
| `--paginate` | Follow `Link rel=next` until exhausted. Capped; a warning goes to stderr if the cap is hit. |
| `-q, --jq` | Filter the JSON response with a jq expression. Mutually exclusive with `--template`. |
| `-t, --template` | Format the JSON response with a Go template. |
| `-i, --include` | Print the status line and headers before the body. |
| `--silent` | Discard the body; the exit code still reflects the status. |
| `--hostname` | Override the Fianu host for one call. |

### Exit codes

A non-2xx response prints the body and **exits non-zero**. In a script, that
means `set -e` will stop on an API error rather than silently continuing with
an error payload — and that `if fianu api ... >/dev/null; then` is a valid
existence check.

## Auth

`fianu api` resolves credentials in this order, first match wins:

1. `--login` + `--client-id` → authorization code
2. `--wif`, or `--client-id` + `--organization` with no secret → Workload
   Identity Federation (auto-detects the CI OIDC token)
3. `--password` set → password grant
4. `--client-id` + `--secret` → client credentials
5. A token stored by a prior `fianu auth login`

Every flag has an environment-variable default: `FIANU_USERNAME`,
`FIANU_PASSWORD`, `FIANU_CLIENT_ID`, `FIANU_CLIENT_SECRET`,
`FIANU_ASSET_TOKEN`. The target host comes from `FIANU_HOST`.

In an interactive session the credentials are almost always already present —
try the call before asking the user for any of these. Confirm who the token
acts as with:

```bash
fianu api /auth/whoami
```

**The token's subject is the `actor` on every write.** Never put an `actor`
field in a request body. See `working-with-tickets` for the full write
contract.

## Investigation loop

1. `grep` the index for the resource noun (`ticket`, `attestation`, `gate`,
   `index`, `exception`, `violation`, …).
2. Pick the narrowest `GET` that could answer the question; check its `AUTH`.
3. Call it with `--jq` to project only the fields you need — full payloads are
   large and most of the payload is not the answer.
4. Follow identifiers from that response into the next route.
5. If a write is required, load the owning skill for the body contract
   **before** issuing it.

Just under half the routes in the index are `GET`. Prefer them; a wrong GET
costs nothing, a wrong POST mutates a customer's compliance record.

## Maintenance

`references/api-index.md` is **generated** from the core repo's proxy config —
`cmd/proxy/kodata/config/proxies/*/proxies.yaml`, which is what actually
decides whether a route is externally reachable and what it admits on.

```bash
./scripts/gen-api-index.sh              # uses ../core, or $FIANU_CORE_REPO
./scripts/gen-api-index.sh /path/to/core
```

Never hand-edit the index. Regenerate it at every `bump-version.sh`; the
header stamps the core commit it was built from, so drift is visible at a
glance.
