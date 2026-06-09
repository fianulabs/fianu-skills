# `converting-frameworks-to-controls` report template

The mapping report is the artifact presented to a human reviewer BEFORE
any drafts are created. Each section provides a different view of the
ingestion outcome.

```markdown
# Framework Mapping Report: {Framework Name}

## Summary
- Total requirements: {N}
- Automated: {N} | Manual: {N} | Hybrid: {N} | Informational: {N}
- Matched to existing controls: {N}
- New controls designed: {N}
- Requires human review: {N}
- Gap (no automated path): {N}

## Existing Control Matches
| Requirement | Existing Control | Confidence |
|------------|-----------------|------------|
| CC-7.1 | Change Management (entity_key: ...) | 0.92 |

## New Controls to Create
| Requirement | Suggested Name | Scope | Plugin | Confidence |
|------------|---------------|-------|--------|------------|
| CC-8.1 | Container Image Scan | artifact | prisma | 0.85 |

## Requires Human Review
| Requirement | Reason |
|------------|--------|
| CC-9.1 | Low classification confidence (0.55) |
| CC-9.2 | Possible match but uncertain (0.62) |

## No Automated Path (Manual/Informational)
| Requirement | Classification | Recommendation |
|------------|---------------|----------------|
| CC-10.1 | manual-attestation | Create API-sourced control for manual upload |
| CC-10.2 | informational | Document in governance collection |
```

## Usage

1. Generate the report after Steps 1–5 of the workflow.
2. Present to a human. Halt — do NOT proceed to create drafts.
3. Once approved, iterate the **New Controls to Create** rows and call
   `POST /create/control` and `POST /create/policy` per row.
