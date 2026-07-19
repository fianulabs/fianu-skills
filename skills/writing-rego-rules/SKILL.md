---
name: writing-rego-rules
description: "Use when authoring OPA Rego rules for Fianu controls. Covers v1 syntax (import rego.v1, if keyword), the input.detail.* ↔ data.* mapping, and the canonical patterns: threshold check, score comparison, presence check, freshness check, multi-metric."
---

# Writing Rego Rules

## Overview

Fianu controls evaluate evidence against policy via an OPA Rego rule. The
rule consumes the evidence note's `detail` block as `input.detail.*` and
policy values as `data.*`, and emits a `pass` result the platform turns
into an attestation.

This skill is the canonical home for the Fianu Rego conventions. Load it
when designing a new control or modifying an existing one.

## v1 syntax requirement

Every Fianu Rego rule MUST begin with:

```rego
package rule
import rego.v1
```

The `import rego.v1` directive enables v1 syntax — the `if` keyword for
every rule body, `every` for quantifiers, stricter parsing. Rules written
in v0 syntax will not be accepted.

## input ↔ data mapping

| Source | Path | What it carries |
|---|---|---|
| Evidence note from the subscribed plugin | `input.detail.*` | Plugin-specific shape; see schema discovery in `working-with-evidence-plugins`. |
| Policy values for the control | `data.*` | Defined by the control's policy template; see `designing-policy-templates`. |

Every key in the policy template MUST correspond to a `data.<path>`
reference in the rule. Mismatches silently fail at evaluation time —
schema alignment is the developer's responsibility.

## Patterns

Five canonical patterns cover most Fianu controls. Full code for each
lives in `references/patterns.md`; brief descriptions:

- **Threshold check** — count something in evidence; pass if at or below a
  policy maximum (or at or above a policy minimum). Example: container scan
  with maximum vulnerabilities per severity.
- **Score comparison** — pass if evidence score meets the policy minimum.
  Example: SonarQube reliability/maintainability grades.
- **Presence check** — pass if evidence contains a required item.
  Example: artifact SBOM exists and has at least one component.
- **Freshness check** — pass if evidence was generated within a policy-
  defined time window. Example: SAST scan within the last 7 days.
- **Multi-metric** — combine multiple sub-checks; pass only if all sub-checks
  pass. Example: code quality (reliability AND maintainability AND coverage).

See `references/patterns.md` for the full code of each pattern.

## Workflow when designing a new rule

1. Pick a plugin via `working-with-evidence-plugins`. Run schema discovery
   to learn the `input.detail.*` shape.
2. Pick a pattern from `references/patterns.md` matching the requirement
   type.
3. Sketch the policy template using `designing-policy-templates`. Every
   key the rule references via `data.*` must exist in the template.
4. Write the rule, mapping plugin schema fields to `input.detail.*` paths
   and policy keys to `data.*` paths.

## See also

- `references/patterns.md` — full code for each canonical pattern.
- `writing-cel-expressions` — the asset-scoping counterpart (CEL) to this evaluation-logic skill (Rego).
- `designing-policy-templates` — the policy template that backs `data.*`.
- `working-with-evidence-plugins` — schema discovery for `input.detail.*`.
- `using-fianu-best-practices` → FIANU.md §Controls > Designing a Control
  — for the broader design tradeoffs (one rule vs. many).
