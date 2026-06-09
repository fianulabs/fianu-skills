---
name: converting-frameworks-to-controls
description: Use when ingesting a compliance framework and mapping requirements to Fianu controls (existing or new). Loads parsing, matching, plugin selection, Rego authoring, policy templates, hierarchy placement, and produces a mapping report for human review before creating any drafts.
---

# Converting Frameworks to Controls

## Loads

- `parsing-framework-documents`
- `matching-existing-controls`
- `working-with-evidence-plugins`
- `writing-rego-rules`
- `designing-policy-templates`
- `placing-entities-in-hierarchy`
- `working-with-entities`
- `using-fianu-best-practices`

## Overview

Ingests a compliance framework document and produces a mapping report
that proposes how each requirement should land in Fianu — reused via
existing controls, designed as new controls, or flagged for human
review. **The agent halts after the report is generated**. Drafts are
only created after a human approves the report.

Accuracy over speed. Every mapping carries a confidence score; low-
confidence mappings are flagged rather than silently committed.

## Workflow

### 1. Parse the document

Via `parsing-framework-documents`. Produces normalized requirements with
keywords and classifications.

Validate before proceeding:

- At least one requirement parsed (else abort with "no requirements
  detected").
- Column mapping confidence acceptable (else flag in the report).

### 2. Classify requirements

Via `parsing-framework-documents`. Distribution feeds the **Summary**
section of the report.

### 3. Match against existing controls

Via `matching-existing-controls`. For each `automated-evidence` / `hybrid`
requirement, search active published controls. Score, threshold,
categorize.

### 4. Design new controls (for unmatched automated/hybrid requirements only)

Process each unmatched requirement with classification confidence ≥ 0.80:

1. **Pick a plugin** via `working-with-evidence-plugins`.
2. **Discover the schema** via `working-with-evidence-plugins` →
   schema discovery, against the chosen plugin.
3. **Write the Rego rule** via `writing-rego-rules`. Pick the right
   pattern (threshold / score / presence / freshness / multi-metric).
4. **Design the policy template** via `designing-policy-templates`.
   Ensure every `data.*` reference in the Rego rule maps to a template
   key.
5. **Pick the scope** (repository / module / artifact / release /
   abstract). See `using-fianu-best-practices` → FIANU.md §Controls >
   Control Scope.
6. **Place in hierarchy** via `placing-entities-in-hierarchy`.
7. **Assign confidence** for the generated design.

### 5. Generate the mapping report

See `references/report-template.md`. Sections:

- **Summary** — distribution of classifications, match counts.
- **Existing Control Matches** — requirements reused (similarity ≥ 0.80).
- **New Controls to Create** — designed by step 4.
- **Requires Human Review** — possible matches (0.50 – 0.79) and
  low-classification-confidence rows (< 0.80).
- **No Automated Path** — manual-attestation and informational requirements.

### 6. Human review — HALT

Present the report. The human reviews and approves, modifies, or rejects
each row. Do NOT proceed to create drafts until explicit approval.

This halt is non-negotiable — the platform's promise to enterprise
customers is that frameworks are mapped *with* humans, not *by* agents.

### 7. Create approved controls

For each approved row in **New Controls to Create**, via
`working-with-entities`:

```
POST /create/control      → creates draft + opens approval ticket
POST /create/policy       → creates default policy draft + opens approval ticket
```

Controls are created in `draft` state. They are NOT published until the
generated approval tickets are themselves approved (either by humans or
by `managing-ticket-approvals`).

## Quality checks (before producing the report)

1. **No duplicate controls** — if two requirements map to the same
   suggested control, consolidate.
2. **Rego rule validity** — every generated rule uses OPA v1 syntax.
   See `writing-rego-rules` for the required header and patterns.
3. **Policy template consistency** — keys follow the syntax rules. See
   `designing-policy-templates`.
4. **Scope appropriateness** — source-level evidence → repository;
   build/scan evidence → artifact; cross-asset → release; etc.
5. **Plugin existence** — every referenced plugin actually appears in
   the catalog and is queryable.
6. **Hierarchy validity** — proposed domains/collections are sensible
   and not duplicating existing.

## Edge cases

### Non-standard framework format

See `parsing-framework-documents` § Edge cases. Use LLM-assisted
extraction; flag low-confidence rows.

### Requirement too vague

Classify as `manual-attestation` with confidence < 0.50; flag for
human review with "too vague" note.

### No matching plugin

If a requirement is classified as automated but no plugin in the catalog
can provide the evidence, recommend an **API-sourced control** (custom
integration). Flag the gap in the report.

### Overlapping requirements

If multiple framework requirements map to the same control, group them
under a single control entry with all requirement IDs listed. Do not
duplicate.

## See also

- `references/report-template.md` — the mapping-report markdown template.
