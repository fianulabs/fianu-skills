---
name: working-with-release-gating
description: "Use when evaluating whether a release or asset passes its gates, listing the controls a gate requires at a commit, or driving the release lifecycle (status, evidence scan / resync). Covers GET /assets/:asset/gates/policies/controls, the gate attestation summary, GET /assets/releases/:uuid/status, and POST /releases."
---

# Working with Release Gating

## Overview

A **gate** is an enforcement boundary: it bundles required controls (and
chained gates) into one composite pass/fail that gates a production
transition. `working-with-entities` owns the gate *config* read
(`GET /gates/:key` — its definition). This skill owns the **runtime** surface:
evaluating a gate against a real asset at a commit, the gate's attestation
roll-up, and the **release** lifecycle that drives evidence collection and
records the outcome.

Load this skill to answer "does this release pass its gates / why is it
blocked / what does this gate require at this commit." For the attestation
result vocabulary it rolls up, see `working-with-attestations`.

Decision semantics below are **client-observed** — the authoritative pass/fail
logic lives in the backend; see `## Maintenance`.

## Gate evaluation (runtime)

```
GET /assets/:asset/gates/policies/controls?commit=&timestamp=
GET /assets/children/:asset/gates/policies/controls?commit=&timestamp=
GET /console/gates/:gate_entity_key/policies/controls
```

| Endpoint | Use |
|---|---|
| `GET /assets/:asset/gates/policies/controls?commit=` | The gates that apply to an asset and the controls each requires **at a commit** (runtime view). |
| `GET /assets/children/:asset/gates/policies/controls?commit=` | Same, walking a release's child assets (a release bundles many assets). |
| `GET /console/gates/:gate_entity_key/policies/controls` | The **config** view — the controls a gate requires independent of any asset/commit. Contrast with the runtime views above. |

**Observed pass rule:** a gate passes for an asset when **every** required
control either has no required evidence or its attestations all resolve to
`pass` / `not required` / excused-by-annotation. A single required control
with a `fail` (and no annotation) fails the gate. A gate with no controls
defined reads as "not found" rather than pass. Read the per-control
attestations via `working-with-attestations`; do not infer from `result`
alone (annotations excuse a non-pass).

## Gate attestation summary

```
GET /gates/:gate_id/attestations/summary?limit=&orderBy=&page=&from=&to=&query=&result=&status=&gateVersion=
```

Returns the gate's attestation roll-up — paged records each carrying a
`result` and `status`. Filters: `result` (e.g. `pass`, `fail`), `status`
(e.g. `error`), `from` / `to` (RFC3339), `query`, and `gateVersion` to scope
to a specific gate version. The response is either a bare array (legacy) or an
`{ items, pagination }` envelope. The `result` / `status` values are the
attestation vocabulary owned by `working-with-attestations`.

## Release lifecycle

```
POST /releases
GET  /assets/releases/:uuid/status
POST /assets/releases/:uuid/evidence/scan
POST /assets/releases/:uuid/evidence/resync
POST /assets/releases/:uuid/evidence/modifiers
GET  /evidence/assets/release/:uuid/links/snapshot?project=results_only
```

| Endpoint | Use |
|---|---|
| `POST /releases` | Create a release (a versioned bundle of assets to gate). |
| `GET /assets/releases/:uuid/status` | The release's lifecycle state and per-gate results. States observed: `draft` \| `approved` \| `released` \| `failed`; `gates[].result` = `pass` \| `fail`. |
| `POST …/evidence/scan` | Trigger evidence collection for the release. |
| `POST …/evidence/resync` | Re-pull evidence (e.g. after a late attestation lands). |
| `POST …/evidence/modifiers` | Apply evidence modifiers (overrides / annotations) to the release. |
| `GET /evidence/assets/release/:uuid/links/snapshot?project=results_only` | The release's assets with their controls and attestations — the data behind the per-asset pass/fail cards. |

## Workflow — "is this release blocked?"

1. Resolve the release's assets + commit (`…/links/snapshot` or the release
   record).
2. For each asset, `GET /assets/children/:asset/gates/policies/controls?commit=`
   to learn the required controls per gate.
3. Fetch each required control's attestation for that asset/commit (see
   `working-with-attestations`).
4. A gate is blocked if any required control lacks a `pass` / `not required` /
   excused attestation. Report the specific failing control(s), not just the
   gate.

## Edge cases

### Evidence not yet scanned
A release with no evidence yet has no attestations to roll up — `scan` first,
then read status. Don't report "fail" for a release that simply hasn't been
evaluated.

### `commit` is required for runtime evaluation
The runtime gate endpoints scope by `commit`; omitting it returns config-level
data, not the asset's actual pass/fail. Always pass the commit you mean.

### Annotation overrides
A failing control excused by an annotation passes the gate. Reflect the
annotation in any "why did this pass?" explanation.

## Maintenance — keeping this skill accurate

Endpoint paths + params are grounded in the Fianu web client
(`src/functions/api.js`). The pass/fail and release-state semantics are
**client-observed** and the most likely to drift — confirm before release:

| Source of truth | What it grounds |
|---|---|
| `../core` handler for `/assets/:asset/gates/policies/controls` | The runtime gate→controls response shape and the composite pass/fail rule. |
| `../core` handler for `/gates/:id/attestations/summary` | The summary envelope, filters, and `result`/`status` enums. |
| `../core` handlers for `/releases` and `/assets/releases/:uuid/*` | The release lifecycle states and the evidence scan/resync/modifier contracts. |
| `../controllers/` | Gate evaluation + release orchestration — the authoritative decision path. |

## See also

- `working-with-attestations` — the per-control results this skill rolls up.
- `working-with-entities` — the gate **config** read (`GET /gates/:key`) and the draft/approval flow for editing gates.
- `working-with-indexes` — gates scope their variations with indexes.
- `using-fianu-best-practices` → FIANU.md §Gates / §Releases — enforcement semantics and the release model.
