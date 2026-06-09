---
name: parsing-framework-documents
description: Use when ingesting a compliance framework document (Excel, CSV, structured text/PDF) to extract requirements. Covers expected columns, keyword extraction, and classification (automated / manual-attestation / hybrid / informational) with confidence scoring.
---

# Parsing Framework Documents

## Overview

Compliance frameworks (SOC 2, NIST 800-53, internal standards, etc.) ship
as spreadsheets, CSV files, or structured PDFs containing rows of
requirements. This skill normalizes those rows into a structured shape
the rest of `converting-frameworks-to-controls` can act on, and classifies
each requirement by automation feasibility.

## Input formats

| Format | Parsing approach |
|---|---|
| Excel (`.xlsx`) | Read rows from the primary sheet. Headers in row 1. |
| CSV | Standard CSV parsing with header row. |
| Structured text / PDF | Extract table-like structures. May require LLM-assisted extraction for non-tabular layouts. |

## Expected columns

Column names vary by framework. The agent identifies columns by semantic
mapping:

| Semantic | Common column names |
|---|---|
| **ID** | ID, Reference, Control ID, Ref #, Number |
| **Title** | Title, Name, Control Name, Requirement |
| **Description** | Description, Details, Full Text, Guidance |
| **Category** | Category, Domain, Family, Section, Group |
| **Evidence type** | Evidence, Verification, Assessment, Test Method |

If column mapping is uncertain (e.g. ambiguous header names), flag the
ambiguity in the output and ask a human to confirm before proceeding.

## Normalized output

Each row becomes:

```json
{
  "id": "CC-7.1",
  "title": "Change Management Controls",
  "description": "The organization manages changes to infrastructure and software...",
  "category": "Change Management",
  "keywords": ["change", "infrastructure", "software", "approval", "testing"],
  "source": "SOC2-CC7",
  "rawRow": { /* original parsed row */ }
}
```

## Keyword extraction

For matching against existing controls and plugins, extract a small keyword
set from the title + description:

- Strip stopwords (the, a, an, is, are, etc.).
- Keep technical terms (vulnerability, coverage, scan, SBOM, …).
- Keep compliance-domain terms (access control, change management, …).

Aim for 5–10 keywords per requirement.

## Requirement classification

For each requirement, classify by automation feasibility:

| Category | Description | Downstream action |
|---|---|---|
| `automated-evidence` | Can be fully evaluated by a plugin + Rego rule. | Design a control. |
| `manual-attestation` | Requires human-provided evidence. | Design a control with an `api` event source. |
| `hybrid` | Automated check + manual sign-off. | Design control + note the manual component. |
| `informational` | Documentation-only; no evaluation. | Note in report; do not design a control. |

### Classification signals

| Signal | Points to |
|---|---|
| Contains measurable metric (count, percentage, score, rating) | `automated-evidence` |
| References specific tool output (scan results, test coverage) | `automated-evidence` |
| "Shall"/"must" + measurable criteria | `automated-evidence` |
| References a process or procedure (review, training, approval) | `manual-attestation` or `hybrid` |
| Requires human judgment (risk assessment, design review) | `manual-attestation` |
| Documentation requirement (maintain a policy, document procedures) | `informational` |
| "Verify that" + automated tool action | `automated-evidence` |
| "Verify that" + human action | `hybrid` |

## Classification confidence

Each classification carries a confidence score:

| Confidence | Action |
|---|---|
| `≥ 0.80` | Proceed with downstream design. |
| `0.50 – 0.79` | Flag for human confirmation before proceeding. |
| `< 0.50` | Skip automated mapping; flag for human review. |

## Edge cases

### Non-standard document layout

If the document doesn't have clear columns (e.g. narrative PDF with no
table), use LLM-assisted extraction: identify the requirement boundary
(one per row, paragraph, or section), then extract fields by context.
Flag low-confidence extractions in the output.

### Requirement too vague

If a requirement is too vague to classify:

- Mark as `manual-attestation` with confidence < 0.50.
- Flag for human review with the note "Too vague for automated mapping."

### Overlapping requirements

If multiple framework requirements describe the same control (e.g.
"NIST AC-2" and "SOC 2 CC-6.1" both map to access control):

- Note both requirement IDs in the output.
- Downstream (`matching-existing-controls` / new design) groups them under
  one control with both IDs listed in the mapping report.

## See also

- `matching-existing-controls` — next step after parsing.
- `converting-frameworks-to-controls` — orchestrates the full ingestion.
