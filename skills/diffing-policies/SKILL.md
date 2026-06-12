---
name: diffing-policies
description: Use when comparing two versions of a policy or exception to classify changes (threshold relaxed/tightened, key added/removed) and compute aggregate direction. Used by analysis, approval, and any change-review workflow.
---

# Diffing Policies

## Overview

A policy diff compares two versions of a policy (or policy exception) and
produces a structured classification of what changed and in which
direction. Used by `analyzing-tickets` (to render a factual change table)
and `managing-ticket-approvals` (to feed the decision logic).

## Methodology

Three steps:

### 1. Compare at each key path

Walk both policy YAML documents and collect every leaf key path. For each
path, capture `before` and `after` values. Missing paths (present in one
side, absent in the other) are treated as `null` on the missing side.

### 2. Classify each change

For each (path, before, after) tuple, assign a classification:

| Classification | Condition |
|---|---|
| `threshold_relaxed` | Numeric value moved in the direction that makes compliance easier (e.g. `minimum` decreased, `maximum` increased, `must_have` removed). |
| `threshold_tightened` | Numeric value moved in the direction that makes compliance harder (e.g. `minimum` increased, `maximum` decreased). |
| `key_added` | Key present in `after` but not in `before`. |
| `key_removed` | Key present in `before` but not in `after`. |
| `value_changed_neutral` | Non-numeric change with no clear relax/tighten direction (e.g. label/string change). |
| `unchanged` | `before == after`. |

The relax-vs-tighten distinction depends on the semantics of the key. Most
Fianu policy keys follow a convention: `*.minimum` means "value must be at
least"; `*.maximum` means "value must be at most". A decrease in `minimum`
is a relaxation; a decrease in `maximum` is a tightening.

### 3. Compute aggregate direction

Sum the classifications:

- `net_relaxation` — more relaxed changes than tightened.
- `net_tightening` — more tightened changes than relaxed.
- `neutral` — equal counts, or no relax/tighten changes (only adds/removes/neutral).

Aggregate direction surfaces in analysis and approval workflows as a
one-line summary: "Direction: net relaxation".

## Variation-aware diffing

Modern policies carry `detail.variations[]` rather than a single threshold
block, so a naive whole-document key-path walk is wrong: variations are an
ordered array, and matching them by array index reports spurious
relax/tighten changes whenever a variation is inserted or reordered.

Diff variations like this:

1. **Match by criteria identity, not array position.** Pair a `before`
   variation with the `after` variation whose `criteria` resolves to the
   same scope (same `asset.type` + same `expressions`/`combine_with`, or
   the same `indexes` reference). An unmatched variation is `key_added` /
   `key_removed` (a whole tier appeared or disappeared).
2. **Diff each matched variation's `policy` map** with the key-path method
   above.
3. **Classify variation-level field changes:**

| Field change | Classification |
|---|---|
| `effect: apply → exempt` | `threshold_relaxed` — the control stops running for matching assets. |
| `effect: exempt → apply` | `threshold_tightened` — the control now runs. |
| `criteria` widened (fewer/looser expressions, broader index) | `threshold_relaxed` — more assets fall under any relaxed thresholds; narrowed criteria is the inverse. |
| `criteria` re-pointed to a different scope with no clear widen/narrow | `value_changed_neutral`. |
| `locked: false → true` | `value_changed_neutral` (governance, not threshold direction). |

Aggregate across all variations as before. Exception policies diff the
same way; an exception's `effect: exempt` variation removed is a
tightening (assets return to the standard policy).

## Output format

The diff produces a structured object the consumer iterates over:

```json
{
  "changes": [
    {
      "path": "coverage.overall.minimum",
      "before": 0.8,
      "after": 0.5,
      "classification": "threshold_relaxed"
    },
    {
      "path": "coverage.branch.minimum",
      "before": null,
      "after": 0.6,
      "classification": "key_added"
    }
  ],
  "aggregate": "net_relaxation"
}
```

For human-facing output, consumers render this as a table:

| Field | Before | After |
|---|---|---|
| `coverage.overall.minimum` | `0.8` | `0.5` |
| `coverage.branch.minimum` | — | `0.6` (new) |

## Worked example

**Before:**

```yaml
coverage:
  overall:
    minimum: 0.8
  new:
    minimum: 0.85
```

**After:**

```yaml
coverage:
  overall:
    minimum: 0.5
  new:
    minimum: 0.85
  branch:
    minimum: 0.6
```

**Diff:**

| Path | Before | After | Classification |
|---|---|---|---|
| `coverage.overall.minimum` | 0.8 | 0.5 | `threshold_relaxed` |
| `coverage.new.minimum` | 0.85 | 0.85 | `unchanged` |
| `coverage.branch.minimum` | — | 0.6 | `key_added` |

Aggregate: `net_relaxation` (1 relaxation, 0 tightenings).

## See also

- `using-fianu-best-practices` → FIANU.md §Policy Layering — for the
  override operator that governs how layered policies compose. When
  diffing the *computed* policy (after layering), compute both
  before-layered and after-layered values per asset.
- `using-fianu-best-practices` → FIANU.md §Policy Variations — when a
  diff crosses a variation boundary, the change set is per-variation.
- `analyzing-tickets` — primary consumer (factual table).
- `managing-ticket-approvals` — primary consumer (decision input).
