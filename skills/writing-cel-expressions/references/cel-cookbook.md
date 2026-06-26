# CEL cookbook — worked Fianu scoping expressions

Each example is the canonical, cast-bearing wire form the runtime engine
accepts. Friendly renderings are how the same expression reads in the criteria
UI. See the parent `SKILL.md` for the grammar and operator vocabulary.

## Match one repository by path

```
$asset.path.(string) == "payments-app"
```
Friendly: `asset.path EQUALS payments-app`

## Exclude a path by regex

```
!$asset.path.(string).matches("^sandbox/")
```
Friendly: `asset.path DOES NOT MATCH ^sandbox/`

## Label / tag membership (list field)

```
$asset.labels.(list_string).contains("compliance:sox")
```
Friendly: `asset.labels CONTAINS compliance:sox`

## Production tier only

```
$asset.labels.(string).contains("tier:prod")
```

## Combine clauses — production repos owned by a team (AND)

```
$asset.labels.(string).contains("tier:prod")
$asset.properties.owner.(string).startsWith("team-")
```
`combineWith: AND` — an asset must satisfy both.

## Either of two asset types (OR)

```
$asset.path.(string).startsWith("services/")
$asset.path.(string).startsWith("apps/")
```
`combineWith: OR` — an asset matching either is in scope.

## Presence check (valueless operator)

```
$asset.properties.data_classification.(string)
```
Operator `exists` — no right-hand value. The expression is true when the
field is set. Use `not_exists` for the inverse.

## Pin to a single asset and series point (exception scoping)

```
$asset.uuid.(string) == "17932c28-2127-4c20-a886-d71abd248905"
$series.commit.(string) == "75357b7"
```
`combineWith: AND` — pins a scope to one asset at one commit (the shape an
asset-scoped exception generates; see `working-with-indexes` for how this
becomes a private index).

## Numeric comparison

```
$asset.properties.criticality.(int64) >= 3
```
Friendly: `asset.properties.criticality GREATER THAN OR EQUAL 3`

## Common mistakes

| Wrong | Why | Right |
|---|---|---|
| `asset.path == "x"` | No `$` sigil, no cast → parser `errVarType`, 400. | `$asset.path.(string) == "x"` |
| `$asset.labels.contains.(string)("x")` | Cast after the method name. | `$asset.labels.(string).contains("x")` |
| `$repository.path.(string) == "x"` | Per-type sigil rejected. | `$asset.path.(string) == "x"` |
| `$asset.tags.(string).contains("x")` on a list field | Wrong cast for a list. | `$asset.tags.(list_string).contains("x")` |
