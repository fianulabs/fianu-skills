---
name: working-with-findings-and-violations
description: "Use when reading Fianu violations, findings, or vulnerabilities for an asset or note — CVE/CWE/CVSS detail, SAST/SCA/SBOM results, the policy-breaking subset vs every vulnerability. Covers GET /evidence/assets/:asset/violations, GET /notes/:uuid/findings, GET /notes/:uuid?format=raw, and the normalized Finding schema."
---

# Working with Findings and Violations

## Loads

- `working-with-asset-series`

## Overview

This skill is the canonical home for **reading the security detail** on an
asset or evidence note — violations (policy-breaking), findings (every
normalized vulnerability), and the raw note display.

Load it when the user asks to list violations / findings / vulnerabilities for
an asset or note.

Every read here is **series-keyed**: you must target the right series or
evidence that exists returns empty. The series model, the three query modes,
and the missing-control diagnosis are owned by
`working-with-asset-series` — load it first; this skill does not restate it.

For the attestation **result vocabulary** (`pass` / `fail` / `warn` /
`notRequired` / `notFound`), the computed-policy meta, and manual upload, load
`working-with-attestations` — this skill does not restate them. For the JSON
**summary output schema**, load `summarizing-evidence`.

Response shapes below are grounded in the `../core` route handlers and the
Fianu web client (`ui-fianu/src/functions/api.js`) — see `## Maintenance`.

## Findings vs violations — two independent pipelines

These are **not** subset and superset. They are produced by different
mechanisms at different times, and either can exist without the other.

| Term | What it is | Produced by |
|---|---|---|
| **Violation** | An arbitrary object a Rego rule chose to record when it failed. Untyped (`map[string]any`) — its shape is whatever the rule author wrote. | `fianu.record_violation()` at **evaluation** time, landing in `display.violations.rows` on the attestation |
| **Finding** | A *normalized, typed* item extracted from the occurrence's plugin data. | Plugin **schema annotations** at **read** time, when you call `/notes/:uuid/findings` |

**"Every violation is a finding" is false.** The two are joined only by an
opt-in, best-effort correlation performed **at read time**: when you call
`/findings`, the service derives match keys from the plugin schema's match-key
mappings, stamps `_finding_match_key` onto the violation objects in memory, and
pairs them with findings whose `matchKey` equals it. Nothing is pre-stamped
during evaluation, and the rule author does not emit this field. If the schema
has no findings annotations, or the derived keys don't line up, you get
violations with zero correlated findings.

Consequences that will bite you:

- **Findings are opt-in per plugin.** A plugin whose schema has no
  `x-findings-*` annotations yields an **empty** findings array no matter how
  much evidence exists. SonarQube is one such plugin today — coverage and
  code-scan data will **not** appear via `/findings`. Read it off the raw note
  instead (see `working-with-attestations`).
- **`isViolation` is only populated when `:uuid` is an attestation.** Pass an
  occurrence UUID and every finding comes back without it, even when
  violations exist.

When the user says "violations", read `display.violations.rows` or the
violations endpoint. When they say "all vulnerabilities", try `/findings` — and
if it returns empty, fall back to the raw note rather than reporting no data.

## Read endpoints

```
GET /evidence/assets/:asset/violations?seriesId=      seriesId REQUIRED
GET /notes/:uuid/findings
GET /notes/:uuid?format=raw
```

| Endpoint | Returns | Notes |
|---|---|---|
| `GET /evidence/assets/:asset/violations?seriesId=` | `assetViolationSnapshotV001[]` — each entry: `control` / `collection` / `domain` refs + one `attestation` (`uuid`, `result`, `status`, `timestamp`, `policyType`, `display`). | **`seriesId` is required** — 400 without it. Only attestations whose `display.violations.rows` is a non-empty array are returned. **Controls only** — gate attestations are excluded. A clean asset yields `[]` (never `null`). There is **no `branch` parameter** — the route ignores it; the web client sends one anyway. |
| `GET /notes/:uuid/findings` | `findingsResponse` = `{ findings: Finding[], metadata: { producerTool, noteUUID, total } }`. | Requires plugin schema findings annotations — returns `{ findings: [] }` when absent. If `:uuid` is an attestation it resolves to the parent occurrence first. |
| `GET /notes/:uuid?format=raw` | The complete note: `detail`, `display`, `policy`, `parent`. | Violation rows are at `$.display.violations.rows`. `format=raw` is required — the default `pretty` strips `display` to `{tag, color}`. |

## The Finding schema

`GET /notes/:uuid/findings` returns normalized findings:

```jsonc
{
  "id": "CVE-2023-1234",
  "title": "…",
  "severity": "high",              // lowercased; NOT an enum — see below
  "category": "vulnerability",     // vulnerability | sast | secret | misconfiguration
                                   //  | license | quality | process | test
  "source": { "package": "log4j-core", "file": "pom.xml", "line": 42,
              "commit": "…", "packageManager": "maven", "scope": "…" },
  "identifiers": [ { "type": "CVE", "value": "CVE-2023-1234" },
                   { "type": "CWE", "value": "CWE-79" } ],
  "scores":   { "cvss": 9.8, "cvssVector": "…" },
  "versions": { "vulnerable": "<2.17.0", "fixed": "2.17.0" },
  "remediation": { "guidance": "…", "links": [ { "label": "…", "url": "…" } ] },
  "matchKey": "…",                 // the key violations correlate against
  "isViolation": true,             // ABSENT when false, never `false`
  "violation": { … },              // present when isViolation
  "context": { … }, "raw": { … }
}
```

Shape gotchas, all `omitempty`:

- `source`, `scores`, `versions`, `remediation` are **pointers** — the whole
  object is absent rather than present-and-empty. Their inner fields are
  `omitempty` too, so you will never see `""` or `line: 0`; those keys just
  vanish. `source.line` is a nullable int.
- `isViolation` is `omitempty` on a bool — **absent means false.** Do not
  test for `=== false`.
- `matchKey` is the join key between findings and violations. Correlation uses
  it **exclusively** — a finding with an empty `matchKey` is skipped, and there
  is no `id` fallback. (`id` is only a fallback for the separate single-finding
  lookup `/findings/:finding_id`.)

**`severity` is not an enumerated set.** It is lowercased and otherwise passed
through verbatim from the plugin schema's value map, so unmapped values survive
as-is. `critical` / `high` / `medium` / `low` / `info` are commonly seen, but
nothing in the platform constrains it — do not branch on an assumed closed set.
`category` *is* backed by real constants (the eight listed above), though it is
also an unvalidated pass-through in practice.

Cite `id`, `identifiers` (CVE/CWE/GHSA), `scores.cvss`, and
`versions.fixed` when summarizing — never invent them. When the reader wants a
JSON summary of one of these, hand off to `summarizing-evidence` for the output
contract.

## Targeting the right series

The violations endpoint requires a `seriesId`, and it only returns what exists
**on that series**. A finding or violation is invisible from the wrong series.

Load `working-with-asset-series` for the series catalog and the query modes.
Two consequences matter most here:

- An attestation lands on **exactly one** series — the lowest-coded one the
  occurrence actually carried. A git SHA reaches commit-landed attestations;
  artifact-oriented controls often land on `digest` and will not appear.
- An empty violations array means "no violations **on the series you asked
  for**" — not "this asset is clean". Confirm the series before reporting it.

## Edge cases

- **Empty violations** — `[]` means no violations on the series you queried.
  Clean result, not an error — but confirm the series before calling the asset
  clean (see `## Targeting the right series`).
- **Note 404** — `:uuid` deleted or never existed; surface the missing
  reference, do not retry.
- **Findings on an attestation note** — the endpoint auto-resolves to the
  parent occurrence; you do not pre-resolve it yourself.
- **Excused violations** — a violation with an annotation is excused at
  roll-up. Result-vs-annotation logic lives in `working-with-attestations`;
  read both, never decide on `result` alone.

## Maintenance — keeping this skill accurate

Grounded in the `../core` Go handlers, **not** the web client — the client sends
a `branch` param the violations route ignores, so do not re-ground this skill
against `ui-fianu`.

| Claim | Source |
|---|---|
| Violations / findings routes | `server/consulta/routes/evidence.go`, `server/consulta/routes/findings.go` |
| `GET /evidence/assets/:asset/violations` requires `seriesId` → 400 | `external/db/evidence/args.go` (`SelectAssetViolationsArgs.IsValid`) |
| Only non-empty `display.violations.rows`; controls only, gates excluded | `external/db/evidence/v1/violations.go` |
| `Finding` fields, `omitempty` behavior, `matchKey` | `pkg/findings/types.go` |
| Violations come from Rego, findings from schema extraction; correlation is opt-in | `pkg/rego/customfunctions.go` (`fianu.record_violation`), `pkg/findings/service.go`, `pkg/findings/correlate.go` |
| `isViolation` set only for attestation UUIDs | `pkg/findings/service.go` (correlation guarded on `attestation != nil`) |
| `severity` unenumerated, lowercased; `category` constants | `pkg/findings/extract.go`, `pkg/findings/types.go` |
| Findings empty without `x-findings-*` annotations (e.g. SonarQube) | `../fianu-plugins/kodata/schemas/` |
| `[]` not `null` | `pkg/queries/consulta/route.go` |

Series mechanics are **not** maintained here — see `working-with-asset-series`.

## See also

- `working-with-asset-series` — the series catalog and the query modes every read here depends on.
- `working-with-attestations` — result vocabulary, and reading measured values / failure detail off a raw note.
- `summarizing-evidence` — JSON summary output schema for a finding/violation.
- `working-with-release-gating` — rolling attestations up into a gate pass/fail.
