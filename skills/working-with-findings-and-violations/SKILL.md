---
name: working-with-findings-and-violations
description: "Use when reading Fianu violations, findings, or vulnerabilities for an asset or note (CVE/CWE/CVSS, SBOM, SAST/SCA results), or when build-info controls (Artifact Signature, Artifact Version, SBOM) come back Unknown / not-resolvable. Covers GET /evidence/assets/:asset/violations, GET /notes/:uuid/findings, GET /notes/:uuid?format=raw, and the commit-vs-artifact-vs-both series-search model the console dashboard uses."
---

# Working with Findings and Violations

## Overview

This skill is the canonical home for **reading the security detail** on an
asset or evidence note — violations (policy-breaking), findings (every
normalized vulnerability), and the raw note display — plus the **series-search
model** that decides whether you get commit evidence, artifact/digest
evidence, or both.

Load it when the user asks to list violations / findings / vulnerabilities for
an asset or note, or when build-info controls (Artifact Signature, Artifact
Version, SBOM) show up as **Unknown / not resolvable** — that is a
series-search problem, not an access problem (see `## Series search`).

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

## Series search — commit vs artifact/digest vs both

This is the model the console dashboard uses, and the fix for build-info
controls that show **Unknown**.

An asset is not evaluated at "a commit" — it is evaluated across **multiple
series**, each with a `seriesType`:

| seriesType | Keyed by | Controls that attest here (typical) |
|---|---|---|
| `commit` | git SHA | Build, Code Coverage, Code Review, SAST/SCA, Unit Tests, PR, Jira |
| `tag` | ref/tag name | tag-scoped controls |
| `artifact` / `digest` | built-artifact hash / image digest | **Artifact Signature, Artifact Version, SBOM** |

**The trap:** query only the `commit` series (pass a git SHA as `seriesId`) and
the artifact-series controls have no attestation on that series — they come back
`Unknown` / "not resolvable via API". Nothing is missing from the API; you
asked the wrong series. This is distinct from a genuine `notFound` (see below).

### Pick the search based on intent

1. **Commit evidence only** — CI/quality controls at a SHA:
   ```
   GET /evidence/assets/:asset/violations?seriesId=<commit sha>
   GET /evidence/assets/:asset/attestations/snapshot?seriesId=<commit sha>   # all results, not just violations
   ```

2. **Artifact / digest evidence only** — signature, version, SBOM:
   ```
   GET /evidence/assets/:asset/attestations/snapshot?seriesId=<artifact or digest series id>
   ```

3. **Both (dashboard parity)** — the full control picture the console shows.
   Query one series as primary and pull the linked series in via
   `associations`. This is what the web client does
   (`call_getAttestationEvidenceBySeries`):
   ```http
   POST /evidence/assets/:asset/attestations/snapshot
   { "seriesId": "<primary series id>",
     "associations": [ { "seriesName": "commit", "seriesId": "<linked series id>" } ] }
   ```
   The response merges evidence across the primary and associated series, so
   commit-series *and* artifact-series controls resolve together.

### Discovering an asset's linked series

If you only have the commit SHA and need the artifact/digest series id (or vice
versa), resolve the linked series first:

```http
POST /evidence/assets/by-series
{ "asset": "<asset uuid>", "seriesId": "<known series id>", "associations": true }
```

Then feed the discovered series id into search #2 or #3.

### Decision recipe

- User asks "violations/findings at this commit" → search #1.
- User asks about signing, provenance, SBOM, artifact version → search #2 (or #3 if they also want commit context).
- User asks for "all controls / the full status / dashboard view" → search #3, or the artifact-series controls will misreport as Unknown.

> Do **not** use `POST /evidence/assets/batch/snapshot` to reach artifact
> evidence — its `seriesType` accepts only `branch` / `commit`. It is for
> multi-asset commit/branch snapshots, not cross-series resolution.

## Unknown vs Not Found — do not conflate

| Reported | Meaning | Cause |
|---|---|---|
| **Not Found** (`notFound`) | No evidence was produced on the series you queried. | The control legitimately has no attestation there. |
| **Unknown / not resolvable** | The tool could not resolve the control because it never queried the series that control attests on. | Wrong series (usually: only searched `commit`, control lives on `artifact`). Fixable with search #2/#3. |

Report an artifact control as Unknown **only after** attempting the artifact
series. Do not tell a user evidence "isn't available via the API" when it is
on a series you did not search.

## Edge cases

- **Empty violations** — a passing asset returns `[]` from the violations
  endpoint. That is a clean result, not an error.
- **Note 404** — `:uuid` deleted or never existed; surface the missing
  reference, do not retry.
- **Findings on an attestation note** — the endpoint auto-resolves to the
  parent occurrence; you do not pre-resolve it yourself.
- **Excused violations** — a violation with an annotation is excused at
  roll-up. Result-vs-annotation logic lives in `working-with-attestations`;
  read both, never decide on `result` alone.

## Maintenance — keeping this skill accurate

Endpoint paths + the associations body are grounded in the Fianu web client
(`ui-fianu/src/functions/api.js`: `call_fetchAssetViolationsSnapshot`,
`fetchNoteFindings`, `fetchNotes`, `call_getAttestationEvidenceBySeries`,
`call_getEvidenceAssetsBySeries`) and the `../core` handlers
(`server/consulta/routes/evidence.go` violations route,
`server/consulta/routes/findings.go`, `server/consulta/routes/asset.go`
by-series). The `Finding` schema is `../core` `pkg/findings/types.go`. Response
shapes are otherwise client-observed. Before release, verify:

| Claim | Verify against |
|---|---|
| `GET /evidence/assets/:asset/violations` requires `seriesId` | `evidence.go` route + `SelectAssetViolationsArgs` |
| `Finding` fields | `pkg/findings/types.go` |
| `associations` body merges linked-series evidence | `NewAssetAttestationEvidenceSnapshotForSeriesFromBody` |
| Which `seriesType` each build-info control attests on | control definitions in `../official-controls` |

## See also

- `working-with-attestations` — result vocabulary, computed-policy meta, manual upload.
- `summarizing-evidence` — JSON summary output schema for a finding/violation.
- `working-with-release-gating` — rolling attestations up into a gate pass/fail.
