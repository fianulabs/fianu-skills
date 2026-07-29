---
name: working-with-asset-series
description: "Use when querying evidence for an asset at a point in time — attestation snapshots, violations, findings, gate checks — and you must target the right series. Covers the series catalog (digest / uri / commit / release / jira_* / period_*), seriesName vs seriesCode vs seriesType, the snapshot endpoints, cross-series queries via associations, series discovery via /evidence/assets/by-series, and why build-info controls (Artifact Signature, Artifact Version, SBOM) read Unknown when you only search the commit series."
---

# Working with Asset Series

## Overview

Every evidence query in Fianu is keyed on a **series** — the dimension along
which an asset is tracked and attested (a git commit, an artifact digest, a
release, a Jira issue, a time period). Pick the wrong series and evidence that
exists comes back empty.

This skill is the canonical home for the **series model** and the
**series-keyed evidence queries** built on it. It is a foundation skill: load
it before reading attestations, violations, findings, or gate results for a
specific point in an asset's history.

It owns the *query*. It does not own the *result semantics* — the
`pass` / `fail` / `warn` / `notRequired` / `notFound` vocabulary, computed-policy
meta, and manual upload live in `working-with-attestations`; violation and
finding payloads live in `working-with-findings-and-violations`; gate roll-up
lives in `working-with-release-gating`.

## The series catalog

Series are a **fixed, validated set** — a lookup table (`series_catalog`), not
free-form strings. Each entry is a `seriesName` ↔ `seriesCode` pair, and the
pair must match (`commit` pairs with `2112`, never another code).

| seriesName | seriesCode | Tracks |
|---|---|---|
| `digest` | 2110 | Content digest (hash) — built artifact / image |
| `uri` | 2111 | Artifact URI |
| `commit` | 2112 | Git commit |
| `jira_issue` | 2113 | Jira issue |
| `jira_fix_version` | 2114 | Jira fix version |
| `release` | 2115 | Release version |
| `period_d` | 2116 | Daily period |
| `period_w` | 2117 | Weekly period |
| `period_m` | 2118 | Monthly period |
| `period_q` | 2119 | Quarterly period |
| `period_y` | 2120 | Yearly period |

Anything outside this list is not a series. Do not invent one, and do not pass
a name the catalog does not contain — validation rejects it.

## Three axes, three different words

These are distinct fields that all read like "series". Conflating them is the
most common source of empty results:

| Field | Vocabulary | What it is |
|---|---|---|
| `seriesName` | the catalog above (`digest`, `commit`, `release`, …) | **Which dimension** the evidence is tracked along. |
| `seriesCode` | `2110`–`2120` | The integer paired with the name. Must match its name. |
| `seriesId` | free-form value | **The point on that series** — the actual SHA, digest, release id. |
| `seriesType` | a *different* axis — `branch` \| `commit` in the batch request; `all` \| `release` \| `primary` in console routing | A coarse selector used by specific endpoints. **Not** the catalog vocabulary. |

When an endpoint asks for `seriesId`, it wants the value (the SHA, the digest).
When it asks for `seriesName`, it wants the catalog name.

## Which series does a control attest on?

A control declares its series binding in its `spec.yaml` `assets:` block —
an asset `type` plus the `series` it allows (`AllowedSeries`: name + code).
This determines where its evidence lands:

| Control | Asset type | Series | Evidence keyed on |
|---|---|---|---|
| Artifact Signature (`cosign.sign.artifact`) | `artifact` | digest, uri, commit | **`digest`** |
| Artifact Version (`ci.pipeline.artifact.version`) | `artifact` | digest, uri, commit | **`digest`** |
| SBOM Source (`ci.asset.sbom`) | `artifact` | digest, uri, commit | **`digest`** |
| Build / Coverage / Code Review / SAST / SCA / Unit Tests / PR / Jira | `module`, `repository`, `artifact` | commit (+ others) | **`commit`** |

**Consequence:** a git SHA only reaches `commit`-keyed controls. Build-info
controls are `digest`-keyed and will not appear — see `## Unknown vs Not Found`.

## The three query modes

Pick the mode that matches intent. This is the decision the console dashboard
makes on every render.

### 1. Single series — you know the series and the point

```
GET /evidence/assets/:asset/attestations/snapshot?branch=&seriesId=<value>
GET /evidence/assets/:asset/violations?branch=&seriesId=<value>          # seriesId REQUIRED
```

Use for "results at this commit" or "results for this digest". Fast, narrow,
and blind to every other series.

### 2. Cross-series — the full picture, one query

Query a primary series and pull linked series in via `associations`. This is
how the console resolves commit-keyed and digest-keyed controls together:

```http
POST /evidence/assets/:asset/attestations/snapshot
{
  "seriesId": "<primary series value>",
  "associations": [ { "seriesName": "commit", "seriesId": "<linked value>" } ]
}
```

`associations[]` entries are `{ seriesName, seriesId }` — the catalog name plus
the point. Use this whenever the user wants "all controls" or "the dashboard
view"; mode 1 will silently under-report.

### 3. Discovery — you have one series, need the others

```http
POST /evidence/assets/by-series
{ "asset": "<asset uuid>", "seriesId": "<known value>", "associations": true }
```

Returns the asset's note refs with `seriesID` / `seriesCode` / `seriesName` /
`seriesType` and their `associations` — i.e. the linked series values. Use it
to turn a commit SHA into the digest (or vice versa), then feed mode 1 or 2.

### Multi-asset: batch snapshot

```http
POST /evidence/assets/batch/snapshot
{ "items": [ … ], "project": "" | "summary" | "overview", "page": 1, "limit": 20 }
```

Each item is **either** pinned — `{ assetUuid, seriesId, seriesType }` — **or**
last-N — `{ assetUuid, limit (1–10), defaultBranchOnly?, branch? }`. Modes are
mutually exclusive per item. If any item uses last-N the whole response is
grouped by asset. `project`: `""` = per-control rows, `"summary"` = per-asset
envelope, `"overview"` = counts only (rejected when any item uses last-N).

> **Ceiling:** batch `seriesType` accepts only `branch` | `commit`. Batch
> **cannot** reach digest-keyed evidence. It is for multi-asset commit/branch
> sweeps — use mode 2 or 3 for cross-series resolution.

## Decision recipe

| User intent | Mode |
|---|---|
| "violations / results at this commit" | 1, `seriesId` = SHA |
| "is this artifact signed / SBOM / artifact version" | 3 to get the digest, then 1 |
| "all controls", "full status", "what the console shows" | 2 (or 3 → 2) |
| "these 20 assets on their default branch" | batch, last-N |

## Unknown vs Not Found

| Reported | Meaning | Cause |
|---|---|---|
| **Not Found** (`notFound`) | No evidence was produced on the series you queried. | The control legitimately has no attestation there. |
| **Unknown / not resolvable** | The tool never queried the series that control attests on. | Wrong series — usually searched only `commit` while the control is `digest`-keyed. Fix with mode 2 or 3. |

Report a build-info control as unavailable **only after** querying its
`digest` series. Never tell a user evidence "isn't accessible via the API"
when it is sitting on a series you did not search.

## Edge cases

- **`seriesId` omitted on violations** — 400. The parameter is required; there is no implicit "latest".
- **Name/code mismatch** — `commit` + `2110` is rejected. Pairs are validated.
- **`tag` is not a series** — it does not appear in the catalog. Some control `spec.yaml` files list `tag` alongside `commit`; that is a spec-level construct, not a catalog series, and is unresolved — see `## Maintenance`. Do not pass `tag` as a `seriesName`.
- **Empty result vs wrong series** — an empty snapshot is only meaningful once you know you queried the right series. Check the binding before reporting "no evidence".

## Maintenance — keeping this skill accurate

The series catalog is grounded in `../core`
`external/db/series/constants.go` (+ `external/db/series/CLAUDE.md`): 11
name/code pairs, `ValidSeriesNames` / `ValidSeriesCodes`, `IsValidSeriesPair`.
Control bindings verified against `../official-controls` spec.yaml `assets:`
blocks. Endpoint paths grounded in the `../core` handlers
(`server/consulta/routes/evidence.go`, `evidence_batch.go`, `asset.go`
by-series) and the web client (`ui-fianu/src/functions/api.js`:
`call_getAttestationEvidenceBySeries`, `call_getEvidenceAssetsBySeries`,
`fetchBatchSnapshot`). Request/response shapes are otherwise client-observed.

| Open question | Resolve against |
|---|---|
| What `series: [commit, tag]` in control `spec.yaml` resolves to — `tag` is not in `series_catalog` | `../core` control spec parsing + `AllowedSeries` validation at the handler level |
| Whether `seriesType` has a catalog of its own beyond `branch`/`commit`/`all`/`release`/`primary` | `NoteAssetRef.SeriesType` producers in `../core` |

## See also

- `working-with-attestations` — result vocabulary, computed-policy meta, manual upload.
- `working-with-findings-and-violations` — violation / finding payloads and the `Finding` schema.
- `working-with-release-gating` — rolling series-scoped attestations up into a gate decision.
