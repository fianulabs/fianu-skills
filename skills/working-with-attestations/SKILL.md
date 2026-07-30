---
name: working-with-attestations
description: "Use when reading Fianu attestation results or history, asking why a control failed (its measured value, threshold, or failed items), submitting a manual attestation, or fetching an agent finding summary. Covers GET /notes/:uuid?format=raw, /notes/attestations/:uuid/meta, /entities/:entity_id/attestations, manual upload, and the pass / warn / fail / in progress / not required / not found result vocabulary."
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

Endpoints and payload shapes below are grounded in the `../core` handlers and
`fior` constants — see `## Maintenance`. Where a claim is still
client-observed it is marked inline.

## Result vocabulary

A control's verdict is one of **six values** — as declared in `fior`
`constants` and mirrored in `../core` `external/pkg/occ-go/v1/variables/fianu.go`:

| Result | Meaning |
|---|---|
| `pass` | Evidence satisfied the policy. |
| `fail` | Evidence violated the policy. |
| `warn` | Soft failure; surfaced but non-blocking (control must opt in via `results.warn`). |
| `in progress` | Evaluation is still running. |
| `not required` | The control did not apply to this asset/series under the active policy. |
| `not found` | No evidence was produced to evaluate. |

**There is no `unknown` and no "not resolvable" result.** If a tool reports
either, that is the tool's own artifact — never a Fianu state. A control you
cannot locate is either `not found` or on a series you did not query (see
`working-with-asset-series`).

The canonical spellings use **spaces**, not underscores. The camelCase forms
`notRequired` / `notFound` also appear in rule output and some payloads —
normalize before comparing.

`not required` / `not found` take priority over `pass` / `fail` in rule output
(see `writing-rego-rules`). Payloads also carry an execution `status`, a
separate three-value set: `complete` | `initiated` | `error`. An attestation with
**`annotations` > 0** is treated as excused — a non-`pass` result with an
annotation is rolled up as passing by the gate (see
`working-with-release-gating`).

## Read endpoints

```
GET /entities/:entity_id/attestations?limit=&orderBy=&page=
GET /notes/attestations/:uuid/policies
GET /notes/attestations/:uuid/meta
GET /notes/:uuid?format=raw
GET /notes/:uuid/chain
```

| Endpoint | Returns |
|---|---|
| `GET /entities/:entity_id/attestations` | Paged attestation history for a control entity. `orderBy` = `desc` \| `asc`. Use for the "last N results" trend cited by `analyzing-tickets`. Through the public proxy this is reachable as `/api/controls/:entity_id/attestations`; the param is the entity **id**, not the entity key. |
| `GET /notes/attestations/:uuid/policies` | The policy (and variation) that applied to this attestation. |
| `GET /notes/attestations/:uuid/meta` | **Policy provenance only.** The asset, the policy hierarchy (each level with its requirements and indexes), the `computedPolicy` with server-computed provenance under `computedPolicy.sections`, asset properties, and integrity. See the warning below. |
| `GET /notes/:uuid?format=raw` | The complete note — `detail`, `display`, `policy`, `parent`. **This is where measured values and violation rows live.** |
| `GET /notes/:uuid/chain` | The whole origin → occurrence → attestation chain in one call. |

### `/meta` does NOT contain the result or the evidence

`PolicyMeta` has no `detail`, no `display`, and **no `result`** field. It answers
"how was this policy assembled", nothing else. Asking it for a measured value
or a failure reason returns policy thresholds and looks like the platform
never stored the measurement — it did (see below). Do not reach for `/meta`
when the question is "what happened"; reach for `?format=raw`.

## Reading the measured value and the failure detail

A control's numeric measurement **is** persisted on the attestation. The
evaluation writes the transform output to both the occurrence and the
attestation, so:

```
GET /notes/<attestationUuid>?format=raw
```

| What you want | JSON path |
|---|---|
| The measured value | `$.detail.*` — e.g. `$.detail.overall_coverage` = `0.5` |
| The threshold it was compared against | `$.policy.data.*` — e.g. `$.policy.data.overall_coverage.minimum` = `0.8` |
| The comparison, in words | `$.policy.evaluation.logs[]` — e.g. `comparing overall count '0.5' against policy minimum '0.8'` |
| Failed items (when the control records them) | `$.display.violations.rows` |
| The parent occurrence (raw tool output) | `$.parent.uuid`, then fetch that note |

**`?format=raw` is mandatory for this.** The default `pretty` rendering keeps
`detail` but reduces `display` to `{tag, color}` and drops `policy.evaluation`
entirely — so without `format=raw` you lose both the violation rows and the
comparison log.

### Threshold controls have no "failed items"

Two shapes of failure, and asking for the wrong one yields nothing:

| Control shape | Where the failure detail is | Example |
|---|---|---|
| **Threshold / scalar** — the rule compares one number | `$.detail.*` vs `$.policy.data.*`, narrated in `$.policy.evaluation.logs[]`. `violations.rows` comes back **empty** — no shipped threshold rule records rows (see `working-with-findings-and-violations`). | Code Coverage (`overall_coverage`, `new_coverage`) |
| **Item-based** — the rule records each offending item | `$.display.violations.rows`, one row per failed item | container scans, commit signature, JUnit results |

So for a failing Code Coverage control the answer is *"measured 0.5, policy
minimum 0.8"* — there is no list of items to enumerate. Do not report the
absence of `violations.rows` as missing data.

### All controls at a commit, in one call

To answer "list every control result for this app at this gitsha, with failing
detail", do not fan out per attestation. Use the export endpoint, which returns
the full raw note for each — see `working-with-asset-series`.

## Manual attestation upload

For controls with a manual / `api` event source (the `manual-attestation`
classification in `parsing-framework-documents`), evidence is submitted
directly rather than produced by a plugin:

```
POST /internal/upload/:control_entity_key/attestations/:action     (multipart/form-data)
```

`:action` is `manual` for this flow. The multipart body carries a `payload`
part (JSON) plus one part per evidence file (appended by filename):

```json
{
  "attestation": { "result": "pass" },               // any result value above
  "series":      { "commit": "<commit sha>" },        // the series point covered
  "asset":       { "uuid": "<asset uuid>" },
  "user":        { "uuid": "", "email": "", "name": "", "role": "" }
}
```

The submitting identity is carried in `user` and by the auth token. Quirk: the
backing struct's user field has **no JSON tag**, so it marshals as `"User"` on
the way out; case-insensitive decoding means `"user"` works on input.

## Agent finding summary

The in-product evidence panel's per-finding summary is fetched / regenerated
through a dedicated agent endpoint:

```
GET  /agent/notes/attestations/:uuid/findings/:finding_id/summarize    (cached summary)
POST /agent/notes/attestations/:uuid/findings/:finding_id/summarize    (regenerate)
```

This skill owns the **endpoint**; the **output schema and content rules** for
the summary itself live in `summarizing-evidence`. Load that skill when
producing the summary text.

## Edge cases

### Attestation not yet computed
A freshly evaluated asset may have no attestation yet. Treat a missing note as
"no evidence" (`not found`), not as a failure. Do not retry tightly.

### Note 404
If `:uuid` returns 404 the note was deleted or never existed — surface the
missing reference and skip; do not retry.

### Result vs. annotation
When rolling results up (e.g. for a gate), a non-`pass` result with
`annotations` > 0 is excused. Read both fields; never decide on `result`
alone.

## Maintenance — keeping this skill accurate

Grounded in the `../core` handlers and `fior`, **not** the web client — the
client's calls include parameters the backend ignores, so do not re-ground this
skill against `ui-fianu/src/functions/api.js`.

| Claim | Source |
|---|---|
| Six result values, exact spellings (spaces, not underscores); no `unknown` | `fior` `constants` + `external/pkg/occ-go/v1/variables/fianu.go` |
| Execution `status` = `complete` \| `initiated` \| `error` | same |
| `PolicyMeta` carries no `result` / `detail` / `display`; does carry `computedPolicy.sections` | `external/transport/http/policy_meta.go`, `pkg/evidence/policy_meta.go` |
| Measured value written to the attestation's `detail` | `pkg/evaluation/evaluate.go` (`att.WithDetail`) |
| `policy.evaluation.logs` populated from the Rego rule's `log()` calls | `pkg/evaluation/evaluate.go` + `fior` `policy/…/evaluation.go` |
| `pretty` strips `display` to `{tag,color}` and drops `policy.evaluation` | `fior` `pretty/` mappers |
| Raw-note JSON paths (`detail`, `display`, `policy`, `parent`) | `fior` `v3.0.0/note.go`, `display/…/violations.go`, `parent/…/parent.go` |
| Attestation-history route is `/entities/:entity_id/attestations` | `server/consulta/routes/controls.go` + the proxy config mapping `/api/controls/…` |
| Manual upload path params `:control_entity_key` / `:action`, payload shape | `pkg/upload/routes.go`, `pkg/upload/handler.go`, `external/transport/http/v1/notes.go` (`ManualEvidenceSubmission`) |
| Threshold controls record no violation rows (convention, not enforced) | `../official-controls/envs/prod/controls/unit.test.coverage/**/rule.rego` |
| `/agent/notes/attestations/:uuid/findings/:finding_id/summarize` | `server/agent/routes.go` |
| Attestation / evaluation orchestration | `../controllers/` |

There is no compile-time check that this skill matches backend state — grep
the sibling repos when in doubt.

## See also

- `working-with-asset-series` — the series model and the series-keyed evidence queries (snapshots, `export`, cross-series `associations`, series discovery). Load it when targeting evidence at a commit / digest / release, or when a control is missing from results.
- `working-with-findings-and-violations` — reading violations / findings / vulnerabilities off an asset or note.
- `summarizing-evidence` — the JSON output schema for the finding summary this skill fetches.
- `working-with-release-gating` — how attestations roll up into a gate decision and a release status.
- `working-with-entities` — controls (which produce attestations) and their read/write contract.
- `working-with-evidence-plugins` — the plugins that emit automated attestations.
- `using-fianu-best-practices` → FIANU.md §Controls / §Attestations — the domain semantics.
