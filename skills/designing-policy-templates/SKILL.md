---
name: designing-policy-templates
description: "Use when designing a YAML policy template for a control. Enforces key-naming syntax (alphanumeric + underscore, no leading digit, case-sensitive), readability conventions, and alignment with the Rego rule's data.* paths."
---

# Designing Policy Templates

## Overview

A control's policy template defines the YAML schema users fill in to set
policy values. The template has four jobs:

1. Provides a schema the control's Rego rule references via `data.*` paths.
2. Drives the GUI form for users creating policies through the dashboard.
3. Defines the YAML schema for policy-as-code users.
4. Enforces value types when users set policy values.

This skill is the canonical home for template authoring rules.

## Key syntax rules

Every policy template key MUST conform to:

- Cannot start with a number.
- Alphanumeric characters only.
- Case-sensitive.
- No spaces or special characters, **except** `_` (underscore).
- Words separated with underscore (e.g. `vulnerability_count`).

Invalid examples:

- `1st-check` (leading number, hyphen)
- `coverage minimum` (space)
- `coverage.minimum` (period)
- `coverage-minimum` (hyphen)

Valid:

- `coverage_minimum`
- `vulnerability_count`
- `reliability`

## Readability conventions

The template should read as close to a sentence as possible. The user sees
this template every time they set or review a policy; clarity here saves
hours of confusion downstream.

### Good — self-evident

```yaml
vulnerabilities:
  critical:
    maximum: 0
  high:
    maximum: 0
```

A reader knows: critical and high vulnerabilities, with a maximum count.

### Acceptable — terse but unclear

```yaml
critical:
  max: 0
high:
  max: 0
```

The reader knows there's a `max` value for critical and high, but
critical/high of WHAT? Vulnerabilities? Severity levels? Customer tiers?

### Bad — opaque

```yaml
critical: 0
high: 0
```

The reader has no way to know what's being measured or whether the value
is a target, a limit, or an exact match.

## Schema alignment with Rego

Every key in the template MUST correspond to a `data.<path>` reference in
the control's Rego rule. Mismatches fail silently at evaluation time:

```yaml
# template
coverage:
  overall:
    minimum: 0.8
```

```rego
# rule  — references data.coverage.overall.minimum
pass if {
    input.detail.coverage.overall >= data.coverage.overall.minimum
}
```

If the template uses `coverage.overall.threshold` but the rule references
`data.coverage.overall.minimum`, the rule reads `undefined` and the
attestation result is undefined behavior. Cross-check before publishing.

## Workflow

1. Identify what the control will evaluate.
2. Choose readable, sentence-like key names following the syntax rules.
3. Write the template.
4. Pair with the Rego rule in `writing-rego-rules` — ensure every
   `data.*` reference in the rule maps to a template key.

## See also

- `writing-rego-rules` — the rule that consumes `data.*` from this
  template.
- `using-fianu-best-practices` → FIANU.md §Controls > Creating a Policy
  Template — for additional examples and rationale.
