---
name: analyzing-tickets
description: "Use when posting a factual analysis comment on a Fianu approval ticket. Fact-only: no decisions, no confidence scores, no LLM context rules, no opinions. Loads: working-with-tickets, working-with-entities, diffing-policies, using-fianu-best-practices."
---

# Analyzing Tickets

## Loads

- `working-with-tickets`
- `working-with-entities`
- `diffing-policies`
- `using-fianu-best-practices`

## Overview

`analyzing-tickets` posts a factual analysis comment on a Fianu approval
ticket. The comment surfaces what changed and what it means in plain
English, so a human reviewer can make the decision faster.

**Constraints (non-negotiable):**

- No decisions — the agent does NOT approve, deny, or escalate.
- No confidence scores — confidence belongs to `managing-ticket-approvals`.
- No LLM context rules — those are autonomous-decision inputs.
- No opinions — no "risky", "concerning", "warrants caution" language.
- Always posts a `comment` activity, never `approved` or `denied`.

If the goal is autonomous decision-making, load `managing-ticket-approvals`
instead.

## Workflow

### 1. Fetch ticket context

Via `working-with-tickets`:

```
GET /tickets/:uuid
```

Extract: `targetEntityId`, `targetEntityType`, `targetEntityPath`,
`conditions`, `createdBy`.

If the ticket is closed (`state == "closed"`), do NOT post anything.
Log and skip.

### 2. Fetch the target entity

Via `working-with-entities`, branching on `targetEntityType`:

| Type | Action |
|---|---|
| `control` | Fetch control. Extract Rego rule, policy template, subscriptions, scope. |
| `policy` | Fetch policy. Also fetch parent control. Extract data, template, variations, indexes. |
| `policy_exception` | Fetch exception. Also fetch parent policy AND parent control. Extract expiration, justification, eased values. |
| `gate` | Fetch gate. Extract referenced controls and indexes. |

### 3. Fetch change history (policies only)

Via `working-with-entities`:

```
GET /controls/:entity_key/policies/history
```

Look for patterns over recent versions (e.g. repeated relaxations,
reversals). These become factual bullets in the **Notable** section — not
opinions about whether the pattern is good or bad.

### 4. Diff analysis (policy / exception changes)

Via `diffing-policies`. Produce the per-key classified diff and the
aggregate direction (`net_relaxation`, `net_tightening`, `neutral`).
The diff feeds the **Changes** table in the output.

### 5. Fetch attestation history

Last 10 attestations for the target entity. Present as counts only
("7 passing, 3 failing"), most recent date and result, and the trend.

### 6. Post analysis comment

Via `working-with-tickets`:

```
POST /tickets/:uuid/activities
{
  "activityType": "comment",
  "body": "<rendered template>"
}
```

Render using `references/output-template.md` — pick the appropriate
variant (default policy / exception / control).

## Output format

See `references/output-template.md` for the full template and variants.

## Presentation rules

1. **No confidence scores** — never compute, mention, or display confidence.
2. **No LLM context rules** — do not fetch or reference these pods.
3. **No opinions** — no recommendations to approve, deny, or escalate.
4. **No subjective language** — banned: "risky", "concerning", "warrants caution", "should be reviewed".
5. **Explicit identifiers** — always include `entity_key`, version tag, exact dates (YYYY-MM-DD).
6. **Explicit expirations** — "2026-07-15", never "soon" or "long-duration".
7. **Tables for structured data** — tables, not paragraphs, for field changes and key-value context.
8. **Omit empty sections** — if no attestation history exists, omit the heading entirely.
9. **One-line summary first** — the first line after the heading tells the reviewer what this is about.

## Queue processing

For batch processing of open tickets, follow the procedure in
`working-with-tickets` § Queue iteration (max 10 per batch, 2s spacing,
skip already-analyzed unless conditions changed).

## Edge cases

### Ticket already closed

See `working-with-tickets`. Do not post.

### No target entity found

If the entity returns 404, post a comment noting the entity could not be
fetched and skip analysis. Do not post any decision-style activity.

### New entity (no prior version)

If no prior version exists for comparison, note in the summary: "New
entity — no prior version for comparison." Present the entity's
configuration as-is without a diff table. Omit the **Changes** section
entirely.

### Multiple pending conditions

Analysis is a comment, not an approval/denial. It does not act on
conditions. Post the analysis once per ticket, not per condition.
