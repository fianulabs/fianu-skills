# Fianu Auto-Approval Manager

Entry-point skill for autonomous approval and denial of workflow tickets using LLM context rules and confidence scoring.

**Loads**: `fianu-shared.md`, `fianu-policies.md`, `fianu-controls.md`

> **Scope**: This skill is for autonomous approve/deny decisions only. For factual ticket analysis without decisions, use `fianu-analysis.md`.

---

## 1. Overview

This skill receives an approval workflow ticket and:
1. Gathers all relevant context (target entity, change details, LLM decision rules)
2. Evaluates the change against entity-specific LLM context rules
3. Produces a structured decision with confidence scoring
4. Takes autonomous action (approve/deny) when confidence is sufficient, or posts advisory comment when not

Every action is auditable -- the agent posts its full reasoning as a ticket activity.

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
    "activityType": "approved" | "denied" | "comment",
    "conditionId": "<uuid>",       // Required for approved/denied, optional for comment
    "body": "...",                  // Comment text (use this field, NOT "comment")
    "metadata": { ... }            // Optional JSONB metadata for audit trail
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

### Step 3: Fetch LLM Context Rules

```
GET /pods/entities/{targetEntityId}?type=llm_context_rule    # List all LLM rules for entity
GET /pods/entities/{targetEntityId}/llm_context_rule/{key}   # Get specific rule by key
```

The `content` field contains raw markdown guidance from the entity owner. If the target is a policy or exception, also fetch the parent control's LLM context rule pod -- guidance may exist at either level.

If no pod is found, note this -- the agent will operate in advisory-only mode (max confidence 0.70).

### Step 4: Fetch Change History (for policies)

```
GET /controls/:entity_key/policies/history
```

Review recent policy changes for the same control to understand trends. Is this the third relaxation in a row? Is it reverting a previous tightening?

### Step 5: Diff Analysis (for policy/exception changes)

Use the fianu-policies skill's diffing methodology:
1. Compare current vs proposed values at each key path
2. Classify each change (threshold relaxed, tightened, new key, key removed, etc.)
3. Compute aggregate risk direction

### Step 6: Produce Decision

Synthesize all context into a structured analysis:

```
Decision: approve | deny | escalate | comment
Confidence: 0.0 - 1.0
Justification: Human-readable reasoning (2-5 sentences)
Rules Applied: Which LLM context rules were relevant and how they influenced the decision
Impact Summary: Affected assets, risk direction, scope
Change Summary: What specifically changed (for policy tickets)
```

**Decision logic:**
1. Read the LLM context rule content carefully -- it contains the entity owner's explicit guidance
2. If the guidance says to deny this type of change, deny it (cite the specific rule)
3. If the guidance says to escalate, escalate (cite the specific rule)
4. If the guidance approves this type of change, approve (cite the specific rule)
5. If no guidance covers this scenario, analyze based on:
   - Risk direction (relaxing = higher scrutiny)
   - Blast radius (all assets = higher scrutiny)
   - Exception duration (long = higher scrutiny)
   - Control criticality (SOX/compliance-critical = higher scrutiny)

### Step 7: Apply Confidence Gate

See fianu-shared.md Section 7 for the confidence framework.

| Confidence | Action |
|-----------|--------|
| >= 0.90 | Submit approval/denial activity on the appropriate condition |
| 0.75-0.89 | Submit approval/denial + post notification |
| 0.50-0.74 | Post comment with analysis only (human decides) |
| < 0.50 | Post comment flagging for human review |

### Step 8: Submit Activity

Always post a comment with the full analysis, regardless of confidence level.

If confidence >= threshold for autonomous action, ALSO submit an approval or denial activity on the pending condition.

---

## 5. Activity Comment Format

Every agent activity uses this template:

```markdown
## Agent Analysis

**Decision:** {Approve | Deny | Escalate | Advisory}
**Confidence:** {0.XX}

### Change Summary
{What changed -- for policy tickets, the specific values that were modified}

### Reasoning
{2-5 sentences explaining the decision, citing specific LLM context rules and FIANU.md best practices}

### LLM Context Rules Applied
{List each rule from the entity's llm_context_rule pod that was relevant}
- "{quoted rule text}" -> {how it influenced the decision}

### Impact Assessment
- **Affected scope**: {asset type and index, or "all assets"}
- **Risk direction**: {Relaxing (higher risk) | Tightening (lower risk) | Neutral}
- **Control criticality**: {Critical | Standard | Non-critical}

---
*Fianu Agent v1.0 | Confidence: {0.XX}*
```

### Approval/Denial Activity

When taking autonomous action (actor is set via auth token, NOT in body):

```json
{
  "activityType": "approved",
  "conditionId": "<first pending condition UUID>",
  "body": "Auto-approved by Fianu Agent (confidence: 0.94). See analysis comment above.",
  "metadata": {
    "agent_version": "1.0",
    "confidence": 0.94,
    "decision": "approve",
    "autonomous": true
  }
}
```

For denial:
```json
{
  "activityType": "denied",
  "conditionId": "<condition UUID>",
  "body": "Denied by Fianu Agent. See analysis comment above.",
  "metadata": {
    "agent_version": "1.0",
    "confidence": 0.91,
    "decision": "deny",
    "autonomous": true
  }
}
```

---

## 6. Queue Processing

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

## 7. Edge Cases

### Ticket Already Closed
If the ticket is closed (state = "closed"), do NOT submit any activity. Log that the ticket was already resolved.

### Multiple Pending Conditions
If a ticket has multiple pending conditions, the agent should only act on conditions where `bot|fianu-agent` appears in `config.resolved_approvers` or where the agent has system-level authorization (which it does by default).

### Conflicting Signals
If the LLM context rule guidance is ambiguous or the agent's analysis produces mixed signals:
- Always default to advisory comment (do not take autonomous action)
- Be transparent about the ambiguity in the comment
- Suggest what a human reviewer should focus on

### No Target Entity Found
If the target entity cannot be fetched (404), post a comment noting the issue and skip analysis. Do not approve or deny.
