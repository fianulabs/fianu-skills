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
and the Unknown-vs-notFound distinction are owned by
`working-with-asset-series` — load it first; this skill does not restate it.

For the attestation **result vocabulary** (`pass` / `fail` / `warn` /
`notRequired` / `notFound`), the computed-policy meta, and manual upload, load
`working-with-attestations` — this skill does not restate them. For the JSON
**summary output schema**, load `summarizing-evidence`.

Response shapes below are grounded in the `../core` route handlers and the
Fianu web client (`ui-fianu/src/functions/api.js`) — see `## Maintenance`.

## Findings vs violations — they are not the same thing

| Term | What it is | Where it comes from |
|---|---|---|
| **Finding** | One normalized item extracted from a note's plugin data — a vulnerability, a code-scan hit, a dependency issue. The **superset**: all of them, whether or not they break policy. | `GET /notes/:uuid/findings` |
| **Violation** | The **policy-breaking subset** — a finding (or attestation) that the active policy failed on. Every violation is a finding; most findings are not violations. | `GET /evidence/assets/:asset/violations`, or the violation rows inside the raw note |

A finding carries `isViolation: true` when it is also a violation. When the
user says "violations", give the policy-breaking set; when they say "findings"
or "all vulnerabilities", give the full set.

## Read endpoints

```
GET /evidence/assets/:asset/violations?branch=&seriesId=      seriesId REQUIRED
GET /notes/:uuid/findings
GET /notes/:uuid?format=raw
```

| Endpoint | Returns | Notes |
|---|---|---|
| `GET /evidence/assets/:asset/violations?seriesId=` | `assetViolationSnapshotV001[]` — each entry: `control` / `collection` / `domain` refs + one `attestation` (`result`, `status`, `timestamp`, `policyType`, `display`). | **`seriesId` is required** (400 without it). Only attestations whose display has non-empty violations are returned — a clean asset yields `[]`. `branch` optional. |
| `GET /notes/:uuid/findings` | `findingsResponse` = `{ findings: Finding[], metadata: { producerTool, noteUUID, total } }`. | The **expansive** view: every vulnerability, not just violations. If `:uuid` is an attestation note it resolves to the parent occurrence first, then extracts findings via the plugin schema annotations. |
| `GET /notes/:uuid?format=raw` | The raw note display payload. | Violation rows live inside the display. Use when you need the producer's exact structure rather than the normalized `Finding` shape. |

## The Finding schema

`GET /notes/:uuid/findings` returns normalized findings:

```jsonc
{
  "id": "CVE-2023-1234",
  "title": "…",
  "severity": "high",              // critical | high | medium | low | …
  "category": "…",                 // e.g. vulnerability, license, secret
  "source": { "package": "", "file": "", "line": 0, "commit": "", "packageManager": "", "scope": "" },
  "identifiers": [ { "type": "CVE", "value": "CVE-2023-1234" },
                   { "type": "CWE", "value": "CWE-79" } ],
  "scores":   { "cvss": 9.8, "cvssVector": "…" },
  "versions": { "vulnerable": "<2.17.0", "fixed": "2.17.0" },
  "remediation": { "guidance": "…", "links": [ { "label": "…", "url": "…" } ] },
  "isViolation": true,             // this finding is also a policy violation
  "violation": { … },              // present when isViolation
  "context": { … }, "raw": { … }
}
```

Cite `id`, `identifiers` (CVE/CWE/GHSA), `scores.cvss`, and
`versions.fixed` when summarizing — never invent them. When the reader wants a
JSON summary of one of these, hand off to `summarizing-evidence` for the output
contract.

## Targeting the right series

The violations endpoint requires a `seriesId`, and it only returns what exists
**on that series**. A finding or violation is invisible from the wrong series.

Load `working-with-asset-series` for the series catalog, the three query modes
(single-series, cross-series, and series discovery), and the
Unknown-vs-notFound distinction. Two consequences matter most here:

- Passing a git SHA reaches **`commit`**-keyed controls only. SBOM, artifact
  signature, and artifact version are **`digest`**-keyed and will not appear.
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

Endpoint paths are grounded in the Fianu web client
(`ui-fianu/src/functions/api.js`: `call_fetchAssetViolationsSnapshot`,
`fetchNoteFindings`, `fetchNotes`) and the `../core` handlers
(`server/consulta/routes/evidence.go` violations route,
`server/consulta/routes/findings.go`). The `Finding` schema is `../core`
`pkg/findings/types.go`. Response shapes are otherwise client-observed. Before
release, verify:

| Claim | Verify against |
|---|---|
| `GET /evidence/assets/:asset/violations` requires `seriesId` | `evidence.go` route + `SelectAssetViolationsArgs` |
| `Finding` fields | `pkg/findings/types.go` |
| Violations returns only attestations with non-empty violation display | `SelectAssetViolations` query |

Series mechanics are **not** maintained here — see `working-with-asset-series`.

## See also

- `working-with-asset-series` — the series catalog and the three query modes every read here depends on.
- `working-with-attestations` — result vocabulary, computed-policy meta, manual upload.
- `summarizing-evidence` — JSON summary output schema for a finding/violation.
- `working-with-release-gating` — rolling attestations up into a gate pass/fail.
