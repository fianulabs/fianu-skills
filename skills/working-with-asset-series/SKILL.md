---
name: working-with-asset-series
description: "Use when querying evidence for an asset at a point in time — attestation snapshots, violations, findings, gate checks — and you must target the right series. Covers the series catalog (digest / uri / commit / tag / release / timestamp / period_*), seriesName vs seriesCode vs seriesId vs seriesType, the snapshot and export endpoints, cross-series queries via associations, series discovery, and why build-info controls (Artifact Signature, Artifact Version, SBOM) come back empty when you only search the commit series."
---

# Working with Asset Series

## Overview

Every evidence query in Fianu is keyed on a **series** — the dimension along
which an asset is tracked and attested (a git commit, an artifact digest, a
tag, a release, a time period). Pick the wrong series and evidence that exists
comes back empty.

This skill is the canonical home for the **series model** and the
**series-keyed evidence queries** built on it. It is a foundation skill: load
it before reading attestations, violations, findings, or gate results for a
specific point in an asset's history.

It owns the *query*. It does not own the *result semantics* — the
`pass` / `fail` / `warn` / `notRequired` / `notFound` vocabulary and the
policy-provenance endpoint live in `working-with-attestations`; violation and
finding payloads live in `working-with-findings-and-violations`; gate roll-up
lives in `working-with-release-gating`.

## The series catalog

Series are a lookup table (`series_catalog`), each row a `seriesName` ↔
`seriesCode` pair.

| seriesName | seriesCode | Tracks |
|---|---|---|
| `digest` | 2110 | Content digest (hash) — built artifact / image |
| `uri` | 2111 | Artifact URI |
| `commit` | 2112 | Git commit |
| `tag` | 2113 | Git tag / ref |
| `release` | 2116 | Release version |
| `timestamp` | 2117 | Point in time |
| `period_d` | 2118 | Daily period |
| `period_w` | 2119 | Weekly period |
| `period_m` | 2120 | Monthly period |
| `period_q` | 2121 | Quarterly period |
| `period_y` | 2122 | Yearly period |

**Do not trust `external/db/series/constants.go` in `../core`.** That package is
dead code — its only importer is a test — and its codes disagree with the rows
actually seeded (`jira_issue`/`jira_fix_version` are not seeded at all; it
places `release` at 2115 and omits `tag` and `timestamp`). The table above
follows the seeded catalog and `external/db/variables/types.go`. See
`## Maintenance`.

**Unknown series names are rejected at entity-deploy time**, with a clear
message: `series[N]: unknown series name '<x>' - cannot resolve code`, returned
as a 400. This fires whenever a control spec supplies a series `name` and omits
`code` — which is what every prod spec does, so it is the normal path.

Two gaps worth knowing:

- Supply a bogus `name` **together with** a non-zero `code` and the resolver is
  skipped. The backstop is then a composite foreign key into `series_catalog`,
  whose error is sanitized to `cannot perform operation due to related
  resource constraints` — technically enforced, practically opaque.
- `IsValidSeriesPair` in `../core` is dead code: its only caller is
  test-only, and on mismatch it returns `nil` silently rather than erroring.
  Do not treat it as the enforcement point.

Nothing validates a `seriesId` **value** — only non-empty is checked.

## Four axes, four different words

These all read like "series". Conflating them is the most common cause of empty
results:

| Field | Vocabulary | What it is |
|---|---|---|
| `seriesName` | the catalog above (`digest`, `commit`, `tag`, …) | **Which dimension** evidence is tracked along. |
| `seriesCode` | `2110`–`2122` | The integer paired with the name. |
| `seriesId` | free-form string | **The point on that series** — the actual SHA, digest, release id. No format validation; only non-empty is enforced. |
| `seriesType` | `primary` \| `association` (the real DB enum) — but `branch` \| `commit` in the batch request | A different axis entirely. See below. |

`seriesType` is genuinely two unrelated vocabularies depending on where you
are:

- **On stored evidence** (`note_to_series.series_type`, and `NoteAssetRef.seriesType`
  in responses) it is the Postgres enum `series_type` = `primary` | `association`.
  An attestation has at most one `primary` row; linked series are `association`
  rows. This is what the API *emits*.
- **In the batch-snapshot request** it is a resolution-mode switch validated
  against `branch` | `commit` only. This is what that one endpoint *accepts*.

When an endpoint asks for `seriesId` it wants the value. When it asks for
`seriesName` it wants the catalog name.

## Which series does an attestation land on?

A control's `spec.yaml` `assets:` block lists an asset `type` plus the series
it allows. **Listing three series does not mean the attestation lands on all
three.** At evaluation the platform picks one, in this order:

1. **Exact asset-type match** to the evaluation's target type wins first.
2. **Lowest `seriesCode`** breaks the tie.
3. Only series the incoming occurrence **actually carries** are candidates.

Since `digest`(2110) < `uri`(2111) < `commit`(2112), a control declaring
`[digest, uri, commit]` lands on `digest` **only when the occurrence carries a
digest**. If the plugin supplied a commit and no digest, the same control lands
on `commit`. The DB enforces at most one `primary` series row per attestation.

Two caveats: when the occurrence carries **none** of the declared series the
version is left unchanged rather than reduced, and a control declaring no
assets at all falls back to a legacy scope path. Step 1 is currently a no-op
across `../official-controls` — no prod control declares different series per
asset type — but do not rely on code ordering alone as the rule.

**So "keyed on digest" is a property of the ingested evidence, not of the
spec.** 19 prod controls declare `[digest, uri, commit]` on `type: artifact` —
including Artifact Signature, Artifact Version, SBOM, every container scan
(Wiz, Prisma, Tenable, Lacework, Trivy), and all five JFrog Xray controls.
Whether each lands on digest or commit depends on what its plugin emitted.

**The primary series predicate matches on the `seriesId` value only** — string
equality against `note_to_series.series_id`, never on name or code. (Association
entries are different: they *do* filter on `seriesName` / `seriesCode` when you
supply them, plus a `LIKE` branch when the value looks like a URL.)

Consequence: a digest-landed attestation that also carries a `commit`
association row *is* returned by a plain commit query. Whether one exists is a
per-plugin data question, not something you can read off the spec.

## Query modes

### 1. Single series

```
GET /evidence/assets/:asset/attestations/snapshot?seriesId=<value>
GET /evidence/assets/:asset/violations?seriesId=<value>          # seriesId REQUIRED → 400
```

Asymmetry to know: on **violations**, `seriesId` is required and omitting it is
a 400. On **snapshot**, omitting it silently falls back to *the asset's latest
commit* from commit_manager. Never rely on that implicit default — pass the
series you mean.

`branch` is accepted by neither in a useful way: the violations route never
extracts it, and on snapshot it only applies when `seriesId` is absent. The web
client sends `?branch=…&seriesId=…` anyway; that is a client vestige, not a
filter.

### 2. Cross-series — widen beyond one series

```http
POST /evidence/assets/:asset/attestations/snapshot
{
  "seriesId": "<primary value>",
  "associations": [ { "seriesName": "commit", "seriesId": "<linked value>" } ]
}
```

Association entries are `{ seriesName?, seriesCode?, seriesId }`.

**Read this carefully — it is counter-intuitive.** Two separate things happen:

- Supplying a **non-empty** `associations` array flips the query onto a
  related-series path that admits evidence from any series linked to the same
  notes. That is where the widening comes from — the array being non-empty, not
  its contents.
- Each **entry** then adds a conjunctive `AND EXISTS(...)` filter. Every
  returned note must match **every** entry. Entries *narrow*.

So one association widens; a second association can only shrink the result
relative to the first. Do not add associations expecting a union.

### 3. Discovery — one series to the others

```http
POST /evidence/assets/by-series
{ "asset": "<asset uuid>", "seriesId": "<known value>", "associations": "true" }
```

**`associations` is a JSON string, not a boolean.** Send `"true"`; sending
`true` is a decode error → 400. (The web client sends a real boolean and is
wrong; a guard test in `../core` pins the string behavior.) Only `seriesId` is
required.

Returns note refs with `seriesID` / `seriesCode` / `seriesName` / `seriesType`
plus `associations[]` — i.e. the linked series values. Note the top-level key
is `seriesID` (capital D) while association entries use `seriesId`.

### 4. Every control at a commit — the export endpoint

```
GET /assets/:asset/attestations/export?commit=<git sha>
```

**The parameter is `commit`, not `seriesId`.** Passing `seriesId` is silently
ignored — the series predicate then binds an empty string and you get
`attestations: []` with no error. Same for the POST form, whose body keys are
`asset` / `commit` / `domains` / `controls`.

The response is an **object**, not an array:

```jsonc
{ "summary": { … }, "attestations": [ { …, "raw": { … } } ] }
```

Each entry carries the **full raw note** under `raw`, so one call yields results
*and* measured values *and* violation rows:

- `$.attestations[].raw.detail.*` — the measured values
- `$.attestations[].raw.display.violations.rows` — failed items
- `$.attestations[].raw.policy.data.*` — the thresholds

This is the right call for "list all control results for this app at this
gitsha, with the failing details." Prefer it over fanning out per attestation.

**Commit-series only.** `../core` carries an explicit note that raw-snapshot
reporting is supported at the commit series level only. Handing it a digest
still matches attestations, but `summary.git.commit` / `tag` resolve through
commit_manager and come back null. For digest-landed evidence use mode 1 or 3.

### Multi-asset: batch snapshot

```http
POST /evidence/assets/batch/snapshot
{ "items": [ … ], "project": "" | "summary" | "overview", "page": 1, "limit": 20 }
```

Each item is **either** pinned — `{ assetUuid, seriesId, seriesType }` — **or**
last-N — `{ assetUuid, limit (1–10), defaultBranchOnly?, branch? }`. Mutually
exclusive per item; max 100 items. `project`: `""` = per-control rows,
`"summary"` = per-asset envelope, `"overview"` = counts only (400 when any item
uses last-N). Any last-N item makes the whole response grouped by asset.

Batch `seriesType` is validated to `branch` | `commit`. That restricts the
**label**, not the value — with `seriesType: "commit"` the `seriesId` is passed
through verbatim, so handing it a digest does resolve digest-keyed evidence.
The real ceiling is different: **batch never populates `associations`**, so it
cannot expand one series into another. It can query a digest; it cannot turn
your commit into a digest for you.

## Decision recipe

| User intent | Call |
|---|---|
| "all control results at this gitsha", with failing detail | mode 4 (`export`) |
| "violations at this commit" | mode 1, violations |
| "is this artifact signed / SBOM / version" | mode 3 to find the digest, then mode 1 — or just mode 4 |
| "the full picture the console shows" | mode 2 (one association), or mode 4 |
| "these 20 assets on their default branch" | batch, last-N |

## When a control looks missing

A control absent from your results is one of:

1. **Wrong series** — it landed on `digest` and you asked for a commit. Use
   mode 3 or 4.
2. **Genuinely no evidence** — `notFound`, a real result value.

Do not report evidence as unavailable via the API until you have queried the
series the attestation actually landed on, or used `export`. There is **no
"unknown" or "not resolvable" result** in Fianu — the vocabulary is
`pass` / `warn` / `fail` / `in progress` / `not required` / `not found`
(owned by `working-with-attestations`). If a tool prints "Unknown", that is the
tool's own artifact, not a platform state.

## Edge cases

- **`seriesId` omitted** — 400 on violations; silent latest-commit fallback on snapshot.
- **Name/code pairs** — enforced only by DB foreign keys at entity-deploy time, as an opaque 400. Not validated on reads.
- **`tag` is a real series** (2113) and is declared by `ci.build.pipeline` among others. Earlier drafts of this skill wrongly said otherwise.
- **Empty result** — meaningless until you know you queried the right series.

## Maintenance — keeping this skill accurate

Grounded in `../core` at these exact locations:

| Claim | Source |
|---|---|
| Series catalog rows/codes | `internal/testing/integration/db/scripts/a_2_series_catalog.sh` (seeded rows) + `external/db/variables/types.go` (`SeriesCatalog`) |
| `series_type` enum = primary/association | `internal/testing/integration/db/scripts/a_types.sh` |
| One winning series by lowest code | `pkg/evaluation/evaluate.go` (`filterVersionBySeries`, `assignVersionV2`) |
| Query matches series **value** only | `external/db/evidence/v1/shared.go` (the `note_to_series.series_id = …` EXISTS clause; the `seriesName` param is dead) |
| `associations` widens by non-emptiness, entries narrow | `external/db/evidence/v1/shared.go` + the `get_related_series_ids` SQL function |
| violations requires `seriesId` → 400 | `external/db/evidence/args.go` (`SelectAssetViolationsArgs.IsValid`) |
| snapshot latest-commit fallback | `external/db/evidence/v1/asset_evidence.go` |
| by-series `associations` is a string | `pkg/queries/postgresql/assets.go` + `assets_by_series_test.go` |
| batch validation (modes, 100 cap, overview rejection, seriesType enum) | `external/db/evidence/args.go` |
| `export` returns full raw notes | `server/consulta/routes/evidence.go` (`/assets/:asset/attestations/export`) + `external/db/evidence/reporting.go` |
| 19 controls declare `[digest, uri, commit]` | `../official-controls/envs/prod/controls/**/spec.yaml` |
| No `unknown` result value | `fior` `constants` + `external/pkg/occ-go/v1/variables/fianu.go` |

`external/db/series/` and its `CLAUDE.md` are **stale dead code** — do not
re-ground this skill against them.

## See also

- `working-with-attestations` — result vocabulary, the policy-provenance endpoint, reading measured values off a raw note.
- `working-with-findings-and-violations` — violation / finding payloads and the `Finding` schema.
- `working-with-release-gating` — rolling series-scoped attestations up into a gate decision.
