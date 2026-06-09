# Fianu Ticket Analysis

Entry-point skill for factual ticket analysis. Produces structured, fact-based comments. No decisions, no confidence scores, no opinions.

**Loads**: `fianu-shared.md`, `fianu-policies.md`, `fianu-controls.md`, `fianu-default-analysis-guidance.md`

---

## 1. Purpose

This skill receives an approval workflow ticket and:
1. Gathers all relevant context (target entity, change details, compliance history)
2. Presents explicit, factual information about what changed and what it means
3. Posts a structured analysis comment to the ticket

The analysis is purely informational. It does NOT:
- Make approve/deny decisions
- Compute or display confidence scores
- Reference LLM context rule pods (those are auto-approval criteria)
- Give opinions or recommendations
- Tell the reviewer what to do

**Domain Source of Truth**: FIANU.md at the project root is the authoritative reference for entity hierarchies, policy layering, asset relationships, control design, and naming conventions. Use it to contextualize every analysis.

---

## 2. Ticket Data Model

### Ticket (TicketReport)

| Field | Type | Description |
|-------|------|-------------|
| uuid | string | Unique identifier |
| name | string | Ticket name |
| identifier | string | Human-readable identifier |
| description | string | Ticket description |
| notes | string | Additional notes |
| state | string | `open` or `closed` |
| result | string | `approved`, `rejected`, or empty (pending) |
| targetEntityId | string | Entity being approved |
| targetEntityType | string | `control`, `policy`, `policy_exception`, `gate` |
| targetEntityPath | string | Entity path (e.g., "security/sast") |
| workflowDefinitionEntityId | string | Workflow template reference |
| createdBy | string | User sub who created the ticket |
| createdByUser | object | User info (username, email, firstName, lastName) |
| conditions | array | Approval steps (see below) |
| metadata | object | JSONB metadata |
| createdAt | timestamp | Creation timestamp |
| lastModified | timestamp | Last modification timestamp |

### Condition (ConditionReport)

| Field | Type | Description |
|-------|------|-------------|
| uuid | string | Condition identifier |
| conditionType | string | `approval`, `prerequisite`, `external_ticket`, `manual` |
| label | string | Step label (e.g., "Manager Approval") |
| config | object | JSONB config (contains `resolved_approvers` list and other settings) |
| status | string | `pending`, `satisfied`, `failed`, `waived`, `expired` |
| progress | object | JSONB progress tracking |
| expiresAt | timestamp | Optional expiration |
| position | int | Order in workflow |
| satisfiedAt | timestamp | When condition was satisfied (null if pending) |
| satisfiedBy | string | User sub who satisfied it (null if pending) |
| satisfiedByUser | object | User info for the satisfier |

**Note**: Approvers are inside `config.resolved_approvers`, not a top-level field.

### Activity (ActivityReport)

| Field | Type | Description |
|-------|------|-------------|
| uuid | string | Activity identifier |
| ticketUuid | string | Parent ticket UUID |
| activityType | string | `approved`, `denied`, `comment` |
| actor | string | User sub who performed the action |
| actorUser | object | User info (username, email, firstName, lastName) |
| body | string | Free-text comment (nullable) |
| metadata | object | JSONB metadata (nullable) |
| conditionId | string | Which condition this activity is for (nullable) |
| timestamp | timestamp | When the activity occurred |

---

## 3. API Reference

### Read Operations

```
GET /tickets
  Query params: targetEntityId, targetEntityType, state (open|closed), result (approved|rejected)
  Returns: Array of TicketReport with inline conditions

GET /tickets/:uuid
  Returns: Full TicketReport with all conditions

GET /tickets/:uuid/activities
  Query params: activityType, conditionId, actor
  Returns: Array of ActivityReport

GET /tickets/:uuid/conditions
  Query params: conditionType, status
  Returns: Array of ConditionReport
```

### Write Operations

```
POST /tickets/:uuid/activities
  Body: {
    "activityType": "comment",
    "body": "...",
    "metadata": { ... }
  }

  NOTE: The "actor" is NOT set in the request body. It is automatically extracted
  from the authenticated user's permission token (h.User()). The agent's bot identity
  (bot|fianu-agent) must be set in the auth token, not the request payload.
```

---

## 4. Analysis Workflow

### Step 1: Fetch Ticket Context

```
GET /tickets/:uuid
```

Extract: `targetEntityId`, `targetEntityType`, `targetEntityPath`, `conditions`, `createdBy`

### Step 2: Fetch Target Entity

Branch on `targetEntityType`:

| Type | Action |
|------|--------|
| `control` | Fetch control via `GET /controls/:entity_key`. Extract Rego rule, policy template, subscriptions, scope. |
| `policy` | Fetch policy via `GET /policies/:entity_key`. Also fetch parent control. Extract policy data, template, variations, indexes. |
| `policy_exception` | Fetch exception details. Also fetch parent policy AND parent control. Extract expiration, justification, eased values. |
| `gate` | Fetch gate via `GET /gates/:entity_key`. Extract referenced controls and indexes. |

### Step 3: Fetch Change History (for policies)

```
GET /controls/:entity_key/policies/history
```

Review recent policy changes for the same control to identify patterns (e.g., repeated relaxations, recent reversals).

### Step 4: Diff Analysis (for policy/exception changes)

Use the fianu-policies skill's diffing methodology:
1. Compare current vs proposed values at each key path
2. Classify each change (threshold relaxed, tightened, new key, key removed, etc.)
3. Note aggregate direction (net relaxation or net tightening)

### Step 5: Fetch Attestation History

Review the last 10 attestations to understand compliance trends. Present as numbers (e.g., "7/10 passing").

### Step 6: Post Analysis Comment

Post the structured analysis as a comment activity on the ticket. Use the output format in Section 5.

---

## 5. Output Format

The output is designed for human reviewers scanning a ticket. It must be compact, scannable, and fact-only.

### Layout Rules

1. **Lead with a one-line summary** — what entity, what type of change, in plain English
2. **Use a table for field-level changes** — one row per changed field, columns: Field | Before | After
3. **Use key-value pairs for context** — not paragraphs. `Control:` Code Coverage, `Scope:` Repository
4. **Use a compact list for notable items** — short bullet points, one fact each
5. **No headers for empty sections** — if there's no attestation history, omit that section entirely

### Template

```markdown
## Analysis: {one-line plain-English summary}

**{entity_type}** `{entity_path}` | **Version** `{version_tag}` | **Created by** {username}

---

### Changes

| Field | Before | After |
|-------|--------|-------|
| `coverage.overall.minimum` | `0.8` | `0.5` |
| `coverage.branch.minimum` | — | `0.6` (new) |

Direction: net relaxation / net tightening / neutral

---

### Context

| | |
|---|---|
| **Control** | Code Coverage (`quality/code_coverage`) |
| **Domain** | Application Compliance |
| **Collection** | Quality |
| **Scope** | Repository |
| **Index** | `asset.cmdb.custom == true` |
| **Applies to** | Custom-developed applications only |

---

### Computed Policy (before → after)

| Key | Before | After |
|-----|--------|-------|
| `coverage.overall.minimum` | `0.8` | `0.5` |
| `coverage.new.minimum` | `0.85` | `0.85` (unchanged, inherited) |

---

### Attestation History

Last 10: **7 passing**, 3 failing | Most recent: FAIL (2026-03-15) | Trend: declining

---

### Notable

- Third relaxation to this control in 60 days
- No index on proposed policy — applies to all repositories
- Prior version had 90% pass rate; current version has 70%

---
*Fianu Agent v1.0 | Analysis*
```

### Exception-Specific Output

When the target entity is a `policy_exception`, replace the Changes table with:

```markdown
### Exception

| | |
|---|---|
| **Entity** | `{entity_key}` |
| **Control** | `{parent_control_path}` |
| **Expires** | 2026-07-15 |
| **Justification** | "{verbatim justification text}" |
| **Action** | acknowledge / acknowledge_and_request_waiver |

### Eased Values

| Field | Policy Value | Exception Value |
|-------|-------------|-----------------|
| `coverage.overall.minimum` | `0.8` | `0.5` |

### Scope

Index: `asset.cmdb.internet_facing == true` — internet-facing repositories only
```

### Control-Specific Output

When the target entity is a `control`, replace the Changes table with:

````markdown
### Control Configuration

| | |
|---|---|
| **Name** | Code Coverage |
| **Scope** | Repository |
| **Subscriptions** | Plugin: `sonarqube.measures` |
| **Evaluation** | Score comparison (coverage >= minimum) |

### Policy Template

```yaml
coverage:
  overall:
    minimum: 0.5
  new:
    minimum: 0.85
```

### Changes from Prior Version

| Component | Change |
|-----------|--------|
| Rego rule | Modified — added branch coverage check |
| Policy template | New key: `coverage.branch.minimum` |
| Subscriptions | Unchanged |
| Scope | Unchanged |
````

---

## 6. Presentation Rules

These rules are non-negotiable:

1. **No confidence scores** — never compute, mention, or display confidence
2. **No LLM context rules** — do not fetch or reference LLM context rule pods
3. **No opinions** — do not recommend approval, denial, or escalation
4. **No subjective language** — do not use "risky", "concerning", "should be reviewed", "warrants caution"
5. **Explicit identifiers** — always include entity_key, version tag, exact dates (YYYY-MM-DD)
6. **Explicit expirations** — "2026-07-15", never "soon" or "long-duration"
7. **Tables for structured data** — use tables, not paragraphs, for field changes and key-value context
8. **Omit empty sections** — if no attestation history exists, do not include the section
9. **One-line summary first** — the first line after the heading tells the reviewer what this is about

---

## 7. Queue Processing

To process multiple tickets in batch:

```
GET /tickets?state=open
```

For each open ticket with no result:
1. Check if the agent has already posted an analysis (search activities for `actor: "bot|fianu-agent"`)
2. If not yet analyzed, run the full analysis workflow
3. If already analyzed but conditions changed (new activity from a human), re-analyze

### Rate Limiting
- Process max 10 tickets per batch
- Wait 2 seconds between tickets to avoid API overload
- If any ticket analysis fails, log the error and continue to the next ticket

---

## 8. Edge Cases

### Ticket Already Closed
If the ticket is closed (state = "closed"), do NOT submit any activity. Log that the ticket was already resolved.

### Multiple Pending Conditions
Analysis is posted as a comment, not as an approval/denial. It does not act on conditions.

### No Target Entity Found
If the target entity cannot be fetched (404), post a comment noting the entity could not be found and skip analysis.

### New Entity (No Prior Version)
If no prior version exists for comparison, note in the summary: "New entity — no prior version for comparison." Present the entity's configuration as-is without a diff table.
