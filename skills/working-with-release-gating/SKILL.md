---
name: working-with-release-gating
description: "Use when evaluating whether a release or asset passes its gates, listing the controls a gate requires, or driving the release lifecycle (status, evidence scan / resync). Covers GET /assets/:asset/gates/policies/controls, the gate attestation summary, GET /assets/releases/:uuid/status, and POST /releases."
---

# Working with Release Gating

## Overview

A **gate** is an enforcement boundary: it bundles required controls (and
chained gates) into one composite pass/fail that gates a production
transition. `working-with-entities` owns the gate *config* read
(`GET /gates/:key` — its definition). This skill owns the **runtime** surface:
evaluating a gate against a real asset, the gate's attestation
roll-up, and the **release** lifecycle that drives evidence collection and
records the outcome.

Load this skill to answer "does this release pass its gates / why is it
blocked / what does this gate require at this commit." For the attestation
result vocabulary it rolls up, see `working-with-attestations`.

Decision semantics below are **client-observed** — the authoritative pass/fail
logic lives in the backend.

## Gate evaluation (runtime)

```
GET /assets/:asset/gates/policies/controls
GET /assets/children/:asset/gates/policies/controls
GET /console/gates/:gate_entity_key/policies/controls
```

| Endpoint | Use |
|---|---|
| `GET /assets/:asset/gates/policies/controls` | The gates that apply to an asset (by its index membership) and the controls each requires (runtime view). |
| `GET /assets/children/:asset/gates/policies/controls` | Same, walking a release's child assets (a release bundles many assets). |
| `GET /console/gates/:gate_entity_key/policies/controls` | The **config** view — the controls a gate requires independent of any asset/commit. Contrast with the runtime views above. |

**Observed pass rule:** a gate passes for an asset when **every** required
control either has no required evidence or its attestations all resolve to
`pass` / `warn` / `not required` / excused-by-annotation. A single required control
with a `fail` (and no annotation) fails the gate. A gate with no controls
defined reads as "not found" rather than pass. Read the per-control
attestations via `working-with-attestations`; do not infer from `result`
alone (annotations excuse a non-pass).

## Gate attestation summary

```
GET /gates/:gate_id/attestations/summary?limit=&orderBy=&page=&from=&to=&query=&result=&status=&entityVersion=&commit=&asset=&branch=
```

Returns the gate's attestation roll-up — paged records each carrying a
`result` and `status`. Filters: `result` (e.g. `pass`, `fail`), `status`
(e.g. `error`), `from` / `to` (RFC3339), `query`, and `entityVersion` to scope
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
| `GET /assets/releases/:uuid/status` | The release's lifecycle `status`, plus `approvalState` / `approvalResult` and its approval `tickets`. It does not carry per-gate results — read those via the gate endpoints above. |
| `POST …/evidence/scan` | Trigger evidence collection for the release. |
| `POST …/evidence/resync` | Re-pull evidence (e.g. after a late attestation lands). |
| `POST …/evidence/modifiers` | Apply evidence modifiers (overrides / annotations) to the release. |
| `GET /evidence/assets/release/:uuid/links/snapshot?project=results_only` | The release's assets with their controls and attestations — the data behind the per-asset pass/fail cards. |

## Workflow — "is this release blocked?"

1. Resolve the release's assets + commit (`…/links/snapshot` or the release
   record).
2. For each asset, `GET /assets/children/:asset/gates/policies/controls`
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

### The runtime gate endpoints do not take a `commit`
They list the required controls for the asset; they do not evaluate pass/fail.
Scope to a commit when you read the attestations (see
`working-with-attestations`).

### Annotation overrides
A failing control excused by an annotation passes the gate. Reflect the
annotation in any "why did this pass?" explanation.

## See also

- `working-with-attestations` — the per-control results this skill rolls up.
- `working-with-asset-series` — picking the series a gate check queries (series-scoped evidence reads, not the gate control listing).
- `working-with-entities` — the gate **config** read (`GET /gates/:key`) and the draft/approval flow for editing gates.
- `working-with-indexes` — gates scope their variations with indexes.
- `using-fianu-best-practices` → FIANU.md §Gates / §Releases — enforcement semantics and the release model.
