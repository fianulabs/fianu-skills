# `analyzing-tickets` output template

This is the activity comment template rendered by `analyzing-tickets`.
Posted to the ticket via `POST /tickets/:uuid/activities` with
`activityType: "comment"`.

## Policy change (default)

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

## Exception variant

When `targetEntityType` is `policy_exception`, replace the **Changes**
table with:

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

## Control variant

When `targetEntityType` is `control`, replace the **Changes** table with:

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

## Layout rules

1. Lead with the one-line summary — what entity, what type of change, plain English.
2. Use a table for field-level changes — one row per changed field, columns: Field | Before | After.
3. Use key-value pairs for context — not paragraphs.
4. Compact lists for notable items — short bullets, one fact each.
5. Omit empty sections entirely (no "Attestation History" header if no history).
