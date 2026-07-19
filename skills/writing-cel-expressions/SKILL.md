---
name: writing-cel-expressions
description: "Use when authoring the CEL expressions inside Fianu policy criteria or index scopes — the $asset.field.(cast).method() dialect. Covers the required type-cast grammar, the operator vocabulary (==, contains, startsWith, matches, in, exists …), negation, $series fields, and combineWith AND / OR."
---

# Writing CEL Expressions

## Overview

Fianu scopes a policy variation or an index to a set of assets with a **CEL
expression**. Where `writing-rego-rules` covers the control's *evaluation*
logic (does the evidence pass?), this skill covers the *scoping* logic (which
assets does this apply to?). The two are independent halves of a control's
behaviour.

This skill is the canonical home for the **Fianu CEL dialect** — the field
reference grammar and operator vocabulary. It does NOT own the YAML/HCL
envelope those expressions sit in (`deploying-entities-yaml`,
`deploying-entities-terraform`) or the index entity's API
(`working-with-indexes`).

## The field-cast grammar (required)

A field reference is the asset sigil, a dotted field path, and a **type
cast**:

```
$asset.<field path>.(<type>)
```

The cast is **not optional**. The backend's runtime CEL parser
(`core/external/pkg/cel/cel.go::parseExpressionString`) requires it; without
it the parser returns `errVarType` and the whole policy-evaluation pipeline
returns 400 (this was the CORE-2747 "stored expression fails compile" bug).
The Fianu UI authors the cast form and persists it verbatim.

| Cast | For |
|---|---|
| `.(string)` | text fields (the default; most asset fields are string) |
| `.(list_string)` | list-of-string fields (labels, tags) |
| `.(int64)` / `.(int)` | integer fields |
| `.(bool)` | boolean fields |

- The primary asset is always `$asset`. The engine accepts `$asset.<field>`
  and **rejects** per-type forms like `$repository.<field>`.
- For string-method operators the cast sits **before** the method call:
  `$asset.labels.(string).contains("sox")` — never
  `$asset.labels.contains.(string)(…)`.
- Negate with a leading `!`: `!$asset.path.(string).matches("^x")`.
- Series fields use the `$series` sigil: `$series.commit.(string) == '…'`.

> **Dialect note.** Some YAML examples in `deploying-entities-yaml` show an
> un-cast shorthand (`asset.scm.repository == 'payments-app'`). The runtime
> engine canonical form is the casted `$asset.…(type)` shape above. If you
> author un-cast CEL through a deploy surface, verify it is normalized
> server-side (see `## Maintenance`); when in doubt, write the cast form.

## Operator vocabulary

Operators carry a canonical underscore value, a CEL rendering, and a friendly
label:

| Operator (value) | CEL form | Friendly label |
|---|---|---|
| `equals` | `==` | Equals |
| `not_equals` | `!=` | Not equals |
| `greater_than` | `>` | Greater than |
| `greater_or_equal` | `>=` | Greater than or equal |
| `less_than` | `<` | Less than |
| `less_or_equal` | `<=` | Less than or equal |
| `starts_with` | `.startsWith( )` | Starts with |
| `ends_with` | `.endsWith( )` | Ends with |
| `contains` | `.contains( )` | Contains |
| `matches` | `.matches( )` | Matches (regex) |
| `not_matches` | `!…​.matches( )` | Does not match |
| `in` | `in` | In |
| `not_in` | `!… in` | Not in |
| `exists` | — | Exists |
| `not_exists` | — | Does not exist |

- `exists` / `not_exists` are **valueless** — they take no right-hand operand.
  Every other operator requires a value.
- The string-method operators (`contains` / `startsWith` / `endsWith` /
  `matches`) and their negations apply to `.(string)` (or each element of a
  `.(list_string)`).
- When the field is a date, the six comparison operators read as
  `On / Not on / After / On or after / Before / On or before` — a display
  convenience only; the CEL form is unchanged.

## Combining expressions

A criterion or index may hold multiple expressions joined by `combineWith`:

- `AND` — an asset must satisfy every expression (intersection).
- `OR` — an asset satisfies any expression (union).

`combineWith` is camelCase (matching the server struct tag), default `AND`.
Note the field-name seam between surfaces: **index** expressions use
`expressions[].source`; **policy criteria** use the singular `expression:`
shorthand or `expressions[].expression` — see `deploying-entities-yaml`.

## Authoring workflow

1. Pick the asset field and its type → choose the cast.
2. Pick the operator from the table above; supply a value (unless it's
   `exists` / `not_exists`).
3. Assemble `$asset.<field>.(<cast>)` + operator + value, negating with `!`
   where needed.
4. For multi-clause scopes, list the expressions and set `combineWith`.
5. To turn a scope into a reusable named index, see `working-with-indexes`;
   to embed it inline in a policy/gate, see `deploying-entities-yaml`.

See `references/cel-cookbook.md` for worked examples.

## Maintenance — keeping this skill accurate

The dialect is grounded in the Fianu web client's CEL authoring path
(`src/stores/entities/mappers/celCasts.js`,
`src/modules/policyCriteriaNode/operatorLabels.js`). Confirm against the
backend before release:

| Source of truth | What it grounds |
|---|---|
| `../core/external/pkg/cel/cel.go::parseExpressionString` | The required cast grammar, accepted field forms (`$asset` only), and the `errVarType` failure mode. |
| `../core/external/db/types/fianu/entities/policy.go::PolicyAssetGroup` | How a criterion's expressions are stored and validated. |
| `../core/external/db/types/fianu/entities/indexes.go` | Index `expressions[].source` shape and `combineWith`. |

## See also

- `writing-rego-rules` — the evaluation-logic counterpart (Rego); CEL is the asset-scoping counterpart.
- `working-with-indexes` — turning a CEL scope into a materialized, reusable index.
- `deploying-entities-yaml` — the policy criteria / index YAML envelope these expressions sit in.
- `references/cel-cookbook.md` — worked examples.
- `using-fianu-best-practices` → FIANU.md §Policy Variations — how scoped variations resolve.
