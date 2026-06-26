---
name: working-with-attestations
description: "Use when reading Fianu attestation results, history, or the computed-policy meta for an attestation; submitting a manual attestation; or fetching an agent finding summary. Covers GET /notes/attestations/:uuid/meta, /controls/:key/attestations, manual upload, and the pass / fail / warn / notRequired / notFound result vocabulary."
---

# Working with Attestations

## Overview

An **attestation** is the evidence note a control produces when it evaluates
an asset at a point in its series (a commit, tag, digest, …). It carries the
control's verdict, the asset and series it covered, the policy that applied,
and any findings. Attestations are what the rest of the platform reads to
answer "did this pass?" — gates roll them up, the evidence panel summarises
them, and approval tickets cite their history.

This skill is the canonical home for the attestation data model, the read
endpoints, the **manual upload** producer path, and the **result vocabulary**.
It does NOT own the summary *output schema* (that is `summarizing-evidence`)
or the gate-level roll-up (that is `working-with-release-gating`).

Response shapes below are **client-observed** (grounded in the Fianu web
client's API calls), not confirmed against backend structs — see
`## Maintenance`.

## Result vocabulary

A control's verdict is one of:

| Result | Meaning |
|---|---|
| `pass` | Evidence satisfied the policy. |
| `fail` | Evidence violated the policy. |
| `warn` | Soft failure; surfaced but non-blocking (control must opt in via `results.warn`). |
| `notRequired` | The control did not apply to this asset/series under the active policy. |
| `notFound` | No evidence was produced to evaluate. |

`notRequired` / `notFound` take priority over `pass` / `fail` in rule output
(see `writing-rego-rules`). Runtime payloads have been observed to spell these
`not required` / `not_run` and to carry an execution `status` of
`complete` | `in_progress` | `error` alongside `result`. An attestation with
**`annotations` > 0** is treated as excused — a non-`pass` result with an
annotation is rolled up as passing by the gate (see
`working-with-release-gating`).

## Read endpoints

```
GET /controls/:entity_key/attestations?limit=&orderBy=&page=
GET /notes/attestations/:uuid/policies
GET /notes/attestations/:uuid/meta
```

| Endpoint | Returns |
|---|---|
| `GET /controls/:entity_key/attestations` | Paged attestation history for a control. `orderBy` = `desc` \| `asc`. Use for the "last N results" trend cited by `analyzing-tickets`. |
| `GET /notes/attestations/:uuid/policies` | The policy (and variation) that applied to this attestation. |
| `GET /notes/attestations/:uuid/meta` | Consolidated meta: the asset, the policy hierarchy (each level with its requirements and indexes), the `computedPolicy` plus server-computed provenance under `computedPolicy.sections`, asset properties, and integrity. Prefer this over the per-policy fan-out. |

## Manual attestation upload

For controls with a manual / `api` event source (the `manual-attestation`
classification in `parsing-framework-documents`), evidence is submitted
directly rather than produced by a plugin:

```
POST /internal/upload/:controlPath/attestations/manual      (multipart/form-data)
```

The multipart body carries a `payload` part (JSON) plus one part per evidence
file (appended by filename):

```json
{
  "attestation": { "result": "pass" },              // pass | fail | warn | …
  "series":      { "commit": "<commit sha>" },       // the series point covered
  "asset":       { "uuid": "<asset uuid>" },
  "user":        { "uuid": "", "email": "", "name": "", "role": "" }
}
```

The submitting identity is carried in `user` and by the auth token. Treat the
exact `payload` shape as **provisional** — the web client marks this call a
scaffold; confirm against the `core` handler before relying on it (see
`## Maintenance`).

## Agent finding summary

The in-product evidence panel's per-finding summary is fetched / regenerated
through a dedicated agent endpoint:

```
GET  /agent/notes/attestations/:uuid/findings/:findingId/summarize    (cached summary)
POST /agent/notes/attestations/:uuid/findings/:findingId/summarize    (regenerate)
```

This skill owns the **endpoint**; the **output schema and content rules** for
the summary itself live in `summarizing-evidence`. Load that skill when
producing the summary text.

## Edge cases

### Attestation not yet computed
A freshly evaluated asset may have no attestation yet. Treat a missing note as
"no evidence" (`notFound`), not as a failure. Do not retry tightly.

### Note 404
If `:uuid` returns 404 the note was deleted or never existed — surface the
missing reference and skip; do not retry.

### Result vs. annotation
When rolling results up (e.g. for a gate), a non-`pass` result with
`annotations` > 0 is excused. Read both fields; never decide on `result`
alone.

## Maintenance — keeping this skill accurate

Endpoint paths + params are grounded in the Fianu web client
(`src/functions/api.js`). Response shapes are client-observed. Before release,
verify against the backend:

| Source of truth | What it grounds |
|---|---|
| `../core` handlers for `/notes/attestations/:uuid/{meta,policies}` and `/controls/:key/attestations` | Read-endpoint response shapes, the `computedPolicy.sections` provenance block. |
| `../core` handler for `/internal/upload/:controlPath/attestations/manual` | The manual-upload `payload` contract (currently provisional). |
| `../core` handler for `/agent/notes/attestations/:uuid/findings/:id/summarize` | The finding-summary request/response (output rules stay in `summarizing-evidence`). |
| `../controllers/` | Attestation / evaluation orchestration — how a control run becomes a note. |

There is no compile-time check that this skill matches backend state — grep
the sibling repos when in doubt.

## See also

- `summarizing-evidence` — the JSON output schema for the finding summary this skill fetches.
- `working-with-release-gating` — how attestations roll up into a gate decision and a release status.
- `working-with-entities` — controls (which produce attestations) and their read/write contract.
- `working-with-evidence-plugins` — the plugins that emit automated attestations.
- `using-fianu-best-practices` → FIANU.md §Controls / §Attestations — the domain semantics.
