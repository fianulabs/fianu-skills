---
name: working-with-entities
description: Use when fetching or creating Fianu entities — controls, policies, policy exceptions, gates — or reading their version history. Covers GET /controls/:key, /policies/:key, /gates/:key, /policy_exceptions/:key, history endpoints, and POST /create/control / /create/policy.
---

# Working with Entities

## Overview

Fianu entities are versioned, access-controlled configuration items. This
skill is the canonical home for the HTTP contract that reads and writes
them: controls, policies, policy exceptions, and gates. `POST /create/<type>`
saves the entity directly. `POST /request/<type>` (control, gate, policy,
policy_exception) saves a draft and opens an approval ticket that a human,
or `managing-ticket-approvals`, acts on.

Load this skill when an agent needs to fetch entity data, look up version
history, discover an evidence schema, or kick off a create.

For design rules (control naming, scope selection, template syntax), load
`using-fianu-best-practices` instead.

## Entity types

| Type | Parent | Lifecycle states | Notes |
|---|---|---|---|
| `control` | one or many `collections` | `status × state (below)` | Subscribes to event sources; OPA Rego rule produces attestations. |
| `policy` | one `control` | `status × state (below)` | Sets threshold values; layered per asset hierarchy. |
| `policy_exception` | one `policy` | `status × state (below)` + `expiresAt` | Temporary easing of a policy; carries an expiration. |
| `gate` | none directly; references controls + indexes | `status × state (below)` | Enforcement boundary; pass/fail gates production transitions. |

Lifecycle has two axes:
<!-- facts:entity-lifecycle -->
| Axis | Values |
| --- | --- |
| `status` | `draft`, `staging`, `active`, `inactive`, `archived` |
| `state` | `draft`, `published`, `staging`, `rejected` |
<!-- /facts:entity-lifecycle -->

See `using-fianu-best-practices` → FIANU.md §Controls / §Policies & Exceptions / §Gates for design rules.

## Read endpoints

```
GET /controls/:entity_key
GET /policies/:entity_key
GET /policy_exceptions/:entity_key
GET /gates/:entity_key
GET /controls/:entity_key/policies/history
GET /controls/:entity_key/schemas?producer={pluginPath}
GET /controls?status=active&state=published
```

### Branching by `targetEntityType`

When called from a ticket workflow, branch on the ticket's `targetEntityType`:

| `targetEntityType` | Action |
|---|---|
| `control` | Fetch via `GET /controls/:entity_key`. Extract Rego rule, policy template, subscriptions, scope. |
| `policy` | Fetch via `GET /policies/:entity_key`. Also fetch parent control. Extract policy data, template, variations, indexes. |
| `policy_exception` | Fetch exception. Also fetch parent policy AND parent control. Extract expiration, justification, eased values. |
| `gate` | Fetch via `GET /gates/:entity_key`. Extract referenced controls and indexes. |

### Change history (policies)

```
GET /controls/:entity_key/policies/history
```

Returns the chronological list of policy versions for a control. Useful for
detecting patterns (repeated relaxations, recent reversals) in
`analyzing-tickets` and `managing-ticket-approvals`.

### Schema discovery

```
GET /controls/:entity_key/schemas?producer={pluginPath}
```

Returns the field paths and types available in the plugin's evidence output.
Used by `writing-rego-rules` to map evidence onto `input.detail.*` paths.
See `working-with-evidence-plugins` for plugin selection.

## Write endpoints

```
POST /create/control            → saves the entity directly
POST /create/policy             → saves the entity directly
POST /create/policy_exception   → saves the entity directly
POST /request/control           → saves a draft + opens an approval ticket
POST /request/policy            → saves a draft + opens an approval ticket
POST /request/policy_exception  → saves a draft + opens an approval ticket
POST /request/gate              → saves a draft + opens an approval ticket
```

Two distinct routes per type, not one:

- `POST /create/<type>` persists the entity immediately. No approval ticket.
  (`gate` has no `/create` route — every gate goes through `/request/gate`.)
- `POST /request/<type>` creates the entity in `draft` state and the
  platform automatically opens an approval ticket targeting it (the
  ticket's `targetEntityType` is `control`, `policy`, `policy_exception`,
  or `gate`). The entity is NOT `published` until a human (or agent via
  `managing-ticket-approvals`) approves the ticket.

Skills MUST NOT assume an entity is queryable as `published` immediately
after a `/request/<type>` POST. If a downstream operation requires the
published state, wait for the approval ticket to close with
`result == "approved"`.

## Version semantics

Entities are immutable per version. Edits produce new versions; the change-
history endpoint surfaces the chronology. When `working-with-tickets`
references a `targetEntityId`, it refers to a specific version.

## Edge cases

### Entity 404

If the target entity returns 404, the consuming workflow should post a
comment noting the missing reference and skip. Do not retry.

### 409 CONFLICT on update

A 409 means the entity was updated by another writer between read and
write. Re-fetch and re-attempt, or surface to a human if the workflow
cannot reconcile the conflict.

### Draft not yet approved

If an entity is in `draft` state, downstream operations that require the
`published` version will fail. Either wait for the approval ticket or
operate against the most recent published version.

## See also

- `working-with-attestations` — the attestations a control produces when it evaluates.
- `working-with-release-gating` — the **runtime** gate evaluation and release lifecycle (this skill owns only the gate *config* read, `GET /gates/:key`).
- `working-with-indexes` — the index entity that gates and policy criteria reference.
- `using-fianu-best-practices` → FIANU.md §Controls / §Policies & Exceptions / §Gates — design rules.
