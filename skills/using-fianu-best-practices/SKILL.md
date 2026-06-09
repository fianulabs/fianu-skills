---
name: using-fianu-best-practices
description: Use when reasoning about Fianu entities, assets, hierarchy, or compliance semantics (controls, policies, exceptions, gates, attestations, releases, policy layering). Loads the FIANU.md source of truth and the per-entity best-practices guidance.
---

# Using Fianu Best Practices

## Overview

This skill loads the authoritative Fianu domain reference (`references/FIANU.md`,
905 lines) and acts as a topical navigator. When another skill needs to make
a decision aligned with Fianu's domain model — entity hierarchy, asset taxonomy,
policy layering semantics, control design rules, naming conventions — load this
skill and jump to the relevant section of `references/FIANU.md`.

## When to load

- Designing a new control, policy, exception, or gate
- Picking a scope (repository / module / artifact / release / logical asset)
- Naming a control (do not name after a vendor)
- Writing a policy template (key syntax, readability)
- Reasoning about policy layering when multiple policies apply
- Placing entities under domains and collections
- Understanding release lifecycle, immutability, closure

## Section index

`references/FIANU.md` is organized as follows. Jump directly to the section
you need:

| Topic | Section in FIANU.md |
|---|---|
| Asset taxonomy (fixed / logical / releases) | `## Assets` |
| Asset hierarchy table and parent-child model | `### Asset Hierarchy` |
| Release lifecycle and immutability | `### Releases` |
| Compliance flow (Domains → Collections → Controls → Policies → Indexes) | `### Compliance` |
| Domain best practices (3–6 for large enterprises; 1–3 for small) | `#### Domains > Best Practices` |
| Collection best practices (5–20 collections) | `#### Collections > Best Practices` |
| Designing a control (one-vs-many evaluations) | `#### Controls > Designing a Control` |
| Creating a policy template (key syntax + readability examples) | `#### Controls > Creating a Policy Template` |
| Naming a control (do not name after vendors) | `#### Controls > Naming a Control` |
| Choosing event sources (Plugin / API / Control) | `#### Controls > Choosing Sources` |
| Control scope (repository / module / artifact / release / abstract) | `#### Controls > Control Scope` |
| Policy layering semantics + override operator | `##### Policy Layering` |
| Policy variations and the AND/OR resolution | `##### Policy Variations` |
| Gates, integrations (vendors/platforms/instances/tools/plugins), deployments | `### Enforcement`, `### Integration`, `### Deployments` |

## How other skills cite this skill

When another skill needs a fact from FIANU.md, the convention is:

```
See `using-fianu-best-practices` → FIANU.md §<Section Title>.
```

Do not re-state the fact in the consuming skill. Single canonical home.
