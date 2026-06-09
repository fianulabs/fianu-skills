---
name: working-with-tickets
description: "Use when fetching ticket data (tickets, conditions, activities) or posting activities (comment, approved, denied). Establishes the auth-token actor pattern (never actor in body), the config.resolved_approvers lookup gotcha, and queue iteration."
---

# Working with Tickets

## Overview

The Fianu approval workflow uses tickets to gate changes to entities (controls,
policies, exceptions, gates). This skill is the canonical home for the ticket
HTTP contract: data model, read endpoints, write endpoints, the actor
convention, the approver lookup pattern, and queue iteration.

Load this skill any time an agent needs to read ticket state or post a
ticket activity. Higher-level workflows like `analyzing-tickets` and
`managing-ticket-approvals` load this skill as a dependency.

## Data Model

### Ticket (TicketReport)

| Field | Type | Description |
|---|---|---|
| `uuid` | string | Unique identifier |
| `name` | string | Ticket name |
| `identifier` | string | Human-readable identifier |
| `description` | string | Ticket description |
| `notes` | string | Additional notes |
| `state` | string | `open` or `closed` |
| `result` | string | `approved`, `rejected`, or empty (pending) |
| `targetEntityId` | string | Entity being approved |
| `targetEntityType` | string | `control`, `policy`, `policy_exception`, `gate` |
| `targetEntityPath` | string | Entity path (e.g. `security/sast`) |
| `workflowDefinitionEntityId` | string | Workflow template reference |
| `createdBy` | string | User sub who created the ticket |
| `createdByUser` | object | User info (`username`, `email`, `firstName`, `lastName`) |
| `conditions` | array | Approval steps (see below) |
| `metadata` | object | JSONB metadata |
| `createdAt` | timestamp | Creation timestamp |
| `lastModified` | timestamp | Last modification timestamp |

### Condition (ConditionReport)

| Field | Type | Description |
|---|---|---|
| `uuid` | string | Condition identifier |
| `conditionType` | string | `approval`, `prerequisite`, `external_ticket`, `manual` |
| `label` | string | Step label (e.g. "Manager Approval") |
| `config` | object | JSONB config — contains `resolved_approvers` list and other settings |
| `status` | string | `pending`, `satisfied`, `failed`, `waived`, `expired` |
| `progress` | object | JSONB progress tracking |
| `expiresAt` | timestamp | Optional expiration |
| `position` | int | Order in workflow |
| `satisfiedAt` | timestamp | When condition was satisfied (null if pending) |
| `satisfiedBy` | string | User sub who satisfied it (null if pending) |
| `satisfiedByUser` | object | User info for the satisfier |

**Gotcha:** Approvers live inside `config.resolved_approvers`, NOT as a
top-level field on the condition. The shape is:

```json
{
  "uuid": "...",
  "conditionType": "approval",
  "config": {
    "resolved_approvers": ["user1", "user2", "bot|fianu-agent"]
  }
}
```

Reading `condition.resolved_approvers` returns `undefined` — agents that do
this silently skip the approver check.

### Activity (ActivityReport)

| Field | Type | Description |
|---|---|---|
| `uuid` | string | Activity identifier |
| `ticketUuid` | string | Parent ticket UUID |
| `activityType` | string | `approved`, `denied`, `comment` |
| `actor` | string | User sub who performed the action |
| `actorUser` | object | User info (`username`, `email`, `firstName`, `lastName`) |
| `body` | string | Free-text comment (nullable) |
| `metadata` | object | JSONB metadata (nullable) |
| `conditionId` | string | Which condition this activity is for (nullable) |
| `timestamp` | timestamp | When the activity occurred |

## API Reference

### Read operations

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

### Write operations

```
POST /tickets/:uuid/activities
  Body: {
    "activityType": "approved" | "denied" | "comment",
    "conditionId": "<uuid>",       // Required for approved/denied, optional for comment
    "body": "...",                  // Comment text (use this field, NOT "comment")
    "metadata": { ... }            // Optional JSONB for audit trail
  }
```

## The actor convention

**The `actor` field is set by the auth token, NOT the request body.**

Every write request carries a bearer token. The server extracts the token's
subject via `h.User()` and records it as the activity's `actor`. The body
MUST NOT include an `actor` field — doing so is a silent bug (the server
ignores it and the agent's expectations diverge from reality).

The agent identity for autonomous platform actions is `bot|fianu-agent` and
is configured in the token issued at session start. The agent does not set
or refer to its own identity in any request body.

Worked example:

```http
POST /tickets/abc-123/activities
Authorization: Bearer <token-with-subject-bot|fianu-agent>
Content-Type: application/json

{
  "activityType": "approved",
  "conditionId": "cond-456",
  "body": "Auto-approved by Fianu Agent. See analysis comment.",
  "metadata": { "decision": "approve", "autonomous": true }
}
```

The recorded activity will have `actor: "bot|fianu-agent"`, sourced from the
token. If the body had included `"actor": "user|alice"`, that field would
have been ignored.

## Queue iteration

For batch processing of open tickets:

```
GET /tickets?state=open
```

For each open ticket with no result:

1. Check if the agent has already posted an activity (search activities for
   the agent's actor identity).
2. If not yet processed, run the workflow.
3. If already processed but conditions have changed (new activity from a
   human), re-process.

### Rate limiting

- Process at most 10 tickets per batch.
- Wait 2 seconds between tickets to avoid API overload.
- If any ticket processing fails, log the error and continue to the next ticket.

Follow cursor pagination (see `using-fianu-skills/references/api-conventions.md`)
when iterating over more tickets than fit in one page.

## Edge cases

### Ticket already closed

If the ticket is closed (`state == "closed"`), do NOT submit any activity.
Log that the ticket was already resolved and skip.

### Multiple pending conditions

If a ticket has multiple pending conditions, an agent should only act on
conditions where its actor identity appears in `config.resolved_approvers`
or where the agent has system-level authorization.

### Target entity not found

If the target entity returns 404 from `working-with-entities`, post a
comment activity noting the issue and skip the workflow. Do not approve or
deny.

### Conflicting signals

If the workflow's analysis produces mixed signals or ambiguous guidance,
default to a comment-only activity (no approval/denial). Be transparent
about the ambiguity in the comment body.
