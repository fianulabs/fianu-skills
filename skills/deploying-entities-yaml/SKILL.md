---
name: deploying-entities-yaml
description: Use when authoring or deploying Fianu entities as on-disk YAML packages with the `fianu console` CLI. Covers the envs/<env>/{controls,policies,indexes,gates}/ directory layout, the per-entity file matrix (spec.yaml, contents.yaml, rule.rego, detail.py, display.py, input/, data/, test/), the policy `detail.variations[]` model with CEL/index criteria, index and gate YAML, `fianu console plan/deploy/test`, and the multipart upload to /entities/artifacts/deploy.
---

# Deploying Entities (YAML / CLI)

## Overview

The YAML deploy path treats each entity as a directory or file on disk and
ships it to the Fianu Console via the `fianu console` CLI. Controls,
policies, exceptions, indexes, and gates all use the same plan / test /
deploy workflow; they differ only in the files they package. The CLI
auto-detects each entity's type from its root-level `type` field, so a
single `deploy` pass can mix all five.

Load this skill when an agent is authoring or editing on-disk entity
packages. For the Terraform path, load `deploying-entities-terraform`. For
the shared deploy semantics (idempotency, approval flow, format choice),
load the parent `deploying-entities-as-code`.

## Directory layout

```
<repo>/
├── envs/
│   ├── dev/
│   │   ├── controls/<category>/<control-key>/
│   │   │   ├── spec.yaml
│   │   │   ├── contents.yaml
│   │   │   ├── rule.rego           (or rule/rule.rego)
│   │   │   ├── rule_test.rego
│   │   │   ├── detail.py           (optional)
│   │   │   ├── display.py          (optional)
│   │   │   ├── input/*.json        (test fixtures)
│   │   │   ├── data/*.json         (test policy fixtures)
│   │   │   └── test/*.json         (test case definitions)
│   │   ├── policies/
│   │   │   ├── f.<policy-path>.yaml
│   │   │   └── f.<control-path>.exception.<id>.yaml
│   │   ├── indexes/
│   │   │   └── f.indexes.<name>.yaml
│   │   └── gates/
│   │       └── f.gate.<name>.yaml
│   ├── qa/   (same shape; controls + indexes promote, policies + gates don't)
│   └── prod/
└── templates/
    ├── controls/_template/
    ├── policies/_template.yaml
    └── exceptions/_template.yaml
```

Policies, exceptions, indexes, and gates are each a single YAML file;
controls are a directory package. The subdirectory is a convention — the
CLI routes each file by its root `type`, not by which folder it sits in.

Controls promote across environments unchanged. Policies (and exceptions)
typically differ per environment — lenient in dev, strict in prod.

## File matrix per entity

| Entity | Files |
|---|---|
| `control` | `spec.yaml` + `contents.yaml` + `rule.rego` + (optional) `detail.py`, `display.py` + `input/*.json` + `data/*.json` + `test/*.json` |
| `policy` | single YAML file, name format `f.<policy-path>.yaml`; `type: "policy"` |
| `policy_exception` | single YAML file, name format `f.<control-path>.exception.<id>.yaml`; `type: "exception"` |
| `index` | single YAML file, `type: "index"`; a reusable CEL asset-scope referenced by policy/gate criteria |
| `gate` | single YAML file, `type: "gate"`; bundles required controls/gates into a composite decision, with inline policy + pods |

Exceptions use the same `variations` + `criteria` shape as policies, with
`type: "exception"`, a narrowing criteria block, and **required**
`expiration.timestamp` and `justification.message`.

## spec.yaml — top-level shape

```yaml
name: "<Display Name>"
control:
  displayKey: "<2-4 char code>"
  fullName: "<longer name>"
  description: "<what risk this control mitigates>"
relations:
  - domain: "compliance.controls"
    collection: "<domain.type>"
    path: "<producer.path>"
    note: occurrence
    producer:
      type: plugin
      path: "<plugin-name>"
policyTemplate:
  measures:
    - name: required
      type: metric
      value: bool
    # … threshold tree
assets:
  - type: <module|repository|artifact|release>
    series:
      - name: <commit|tag|branch|scheduled>
```

For Rego rule authoring inside `rule.rego`, see `writing-rego-rules`.
For `policy_template.measures` syntax, see `designing-policy-templates`.
For domain/collection placement, see `placing-entities-in-hierarchy`.

## policy YAML — top-level shape (variations model)

```yaml
name: "<Org> Standard: <Subject>"
path: "<dot.notation.path>"
type: "policy"
detail:
  type: "standard"                 # standard | exception | target
  control:
    path: "<control-path>"         # control this policy binds to
  variations:                      # ordered list; LAST matching variation wins
    - criteria:                    # omit criteria for an all-assets catch-all
        asset: { type: repository }
      policy:                      # threshold map — matches the control's policyTemplate.measures
        required: true
        <threshold-section>:
          <metric>: <value>
    - criteria:                    # a narrower tier overrides the catch-all above
        asset: { type: repository }
        expressions:
          - expression: "asset.labels.tier == 'prod'"
        combine_with: AND          # AND (default) or OR
      effect: apply                # apply (default; run with these thresholds) | exempt (skip evaluation)
      policy:
        required: true
        <threshold-section>:
          <metric>: <override-value>
  justification:
    message: "<why this policy exists>"     # recommended
  expiration:
    timestamp: "<RFC3339>"                  # recommended
```

`detail.variations` is evaluated in array order and the **last matching
variation wins** for a given asset — so author broadest-to-narrowest:
catch-all first, most-specific last. Each variation's `policy` map MUST
shape-match the parent control's `policyTemplate.measures` tree; a key
mismatch silently fails at evaluation time. (The legacy single
`detail.policy: [...]` list shape still parses for backward compatibility,
but `variations` is the current model — author new policies with it.)

### Variation criteria — three mutually exclusive forms

1. **Inline CEL** — `asset` plus `expressions[].expression` (and optional
   `combine_with: AND|OR`). Defines the scope on the spot.
2. **Index reference** — `indexes: [{ path: "f.indexes.repos.prod" }]` (or
   `{ id: "<uuid>" }`). Reuses a named scope; omit `asset` and
   `expressions` — the linked index already carries both.
3. **Unscoped** — `asset: { type: ... }` with no `expressions` and no
   `indexes` → a catch-all for every asset of that type.

> Inline `expressions` auto-spawn a private index. On write the server
> content-hashes `(asset_type, expressions, combine_with)` and either links
> to an existing index with that hash (dedup) or materialises a new
> `visibility=private` index. Writing inline `expressions` and referencing
> `indexes:` explicitly differ only in whether you author the index up
> front. Author scope at scale as named indexes (next section).

`effect: exempt` skips evaluation entirely for matching assets (vs `apply`,
which runs the control). `locked: true` prevents downstream tenants from
overriding a variation. For the AND/OR resolution semantics when variations
collide on one asset, see `using-fianu-best-practices` → FIANU.md
§Policy Variations.

## index YAML — top-level shape

```yaml
name: "Production Repositories"
path: "f.indexes.repos.prod"
type: "index"
detail:
  description: "All prod-tier repositories owned by an engineering team."
  assetTypePath: "repository"      # Logical Asset type; immutable (rename forces replacement)
  combineWith: "AND"               # AND (intersect member sets) | OR (union). Default AND.
  expressions:
    - source: "asset.labels exists tier && asset.labels.tier == 'prod'"
    - source: "asset.properties.owner startsWith 'team-'"
```

An index names a reusable asset scope so policies and gates can reference
it by `path` or `id` instead of repeating CEL. **Mind the casing:** index
expressions use `expressions[].source` and `combineWith`; policy/gate
*criteria* use `expressions[].expression` and `combine_with`.

- `detail.kind` is **server-controlled** — the public deploy endpoint forces
  every user-authored index to `kind: write`. Leave it unset. `default`
  (the auto-managed per-asset-type catch-all) and `write-ahead` are
  reserved and cannot be set from source. Don't author `default.<asset_type>`
  catch-all indexes by hand; the server maintains one per active asset type.
- CLI deploy of an index requires the console server's index translator
  (wired at `server/console/routes.go`). Against a server without it, the
  deploy returns `deployer not registered for type index`.

## gate YAML — top-level shape

```yaml
name: "Baseline Security Gate"
path: "f.gate.security.baseline"
type: "gate"
detail:
  full_name: "Baseline Security Gate"
  display_key: "BSEC"              # short uppercase code
  environments:
    - path: "env.prod"
  policy:                          # inline policy — deploys as a separate policy keyed to the gate
    variations:
      - required_controls:
          - "terraform.example.iac.scan"
        # criteria / required_gates / effect optional — same shape as a policy variation
    override:
      asset: { types: [repository] }
  pods:                            # pipeline-automation rules
    - key: "default"
      protection_level: "enforce"  # enforce (block on failure) | check (report only)
```

A gate bundles `required_controls` (and chained `required_gates`) into one
composite pass/fail. The inline `policy` carries the requirements; the
server materialises it as a separate `policy` entity whose `control.path`
references the gate, so a gate with no policy enforces nothing.
`pods[].matching[]` carries per-scope `protection_level` overrides using
the same CEL/index criteria shape (most-restrictive wins: `enforce` >
`check`).

## CLI commands

```bash
# Test rego rules against on-disk input/data fixtures
fianu console test controls ./envs/dev/controls/
fianu console test policies ./envs/dev/policies/

# Show what would deploy (dry run; SHA256-compare to server state)
fianu console plan ./envs/dev --project <project> --repository <repo>

# Apply changes (creates drafts + opens approval tickets)
fianu console deploy ./envs/dev --project <project> --repository <repo>

# Selective deploy
fianu console deploy ./envs/dev --controls
fianu console deploy ./envs/dev --policies
fianu console deploy ./envs/dev --gates
```

The CLI dispatches each file to the right deployer from its root `type`,
so controls, policies, exceptions, indexes, and gates deploy in one pass.
The `--controls` / `--policies` / `--gates` flags are optional hints for
the legacy format where the root `type` is ambiguous; with `type` set on
every file you don't need them.

`--project` and `--repository` are required on `plan` / `deploy`. They
correlate with the project / repository scope the server uses to organize
deployed entities and to attribute the approval-ticket history.

## Wire contract

`fianu console deploy`:

1. Tars the entity directory.
2. Multipart-POSTs to `/entities/artifacts/deploy`:
   - `payload`: JSON metadata (entity type, path, project, repository).
   - `file`: binary tar archive.
3. Server's `BuildControlFromFiles` extracts the archive, constructs the
   entity, runs the SHA256 idempotency check, then either drafts a new
   version + opens an approval ticket or returns `action: "skipped"`.

Same endpoint, same idempotency, same approval flow as the Terraform path.
See `deploying-entities-as-code` for the shared semantics.

## Test fixture format

Each `test/<name>.json` references an input and a data fixture and asserts
an expected result:

```json
{
  "inputRef": "occ_case_1.json",
  "dataRef":  "policy_case_1.json",
  "expectedResult": "pass"
}
```

Valid `expectedResult` values: `pass`, `fail`, `notRequired`, `notFound`.
The `notRequired` / `notFound` results take priority over `pass` / `fail`
in the rule output — see `writing-rego-rules` for the priority rules.

## Edge cases

### contents.yaml drift

If `contents.yaml` declares a `mappers.detail` or `mappers.display` path
that doesn't exist on disk (or vice versa), the CLI fails the package
build before upload. Keep `contents.yaml` in sync after any
add/rename/delete of `detail.py` / `display.py`.

### Mapper imports

`detail.py` and `display.py` run in a server-side Python sandbox with a
limited standard library. They cannot import third-party packages. Keep
the mapper self-contained.

### Multi-env deploy

`plan` and `deploy` operate on one env directory at a time. To promote
dev → qa → prod, run the command three times against
`envs/dev`, `envs/qa`, `envs/prod`. Controls SHA-match across envs and
return `action: "skipped"`; policies typically differ and create new
drafts in each env.

## Maintenance — keeping this skill accurate

The customer-facing spec is owned by the documentation repo; the on-disk
package mechanics are owned by the `entities-as-code` directory in core.
When updating this skill, refresh from:

| Source of truth | What it controls |
|---|---|
| `../core/documentation/fianu/console/entities_as_code.md` | **Authoritative** customer-facing spec for the policy `variations` model, the index YAML, and the gate YAML. The docs lead the repo templates. |
| `../core/entities-as-code/templates/controls/_template/spec.yaml` | Control `spec.yaml` shape and field documentation. |
| `../core/entities-as-code/templates/controls/_template/contents.yaml` | The contents manifest. |
| `../core/entities-as-code/templates/policies/_template.yaml` | Policy YAML — see the warning below. |
| `../core/entities-as-code/templates/exceptions/_template.yaml` | Exception YAML — see the warning below. |
| `../core/entities-as-code/docs/cheat-sheet.md` | Quick reference for common patterns (producer paths, asset/series types, policyTemplate value types). |
| `../core/entities-as-code/docs/getting-started/concepts.md` | The five control results (`pass` / `fail` / `warn` / `notFound` / `notRequired`) and the scanner → occurrence → control data flow. |

> ⚠️ As of this writing the `templates/policies/_template.yaml` and
> `templates/exceptions/_template.yaml` files still show the **legacy**
> `detail.policy: [...]` list shape (pre-variations, `criteria.expression`
> singular). The server still parses that shape for backward compatibility,
> but the `variations` model documented above is current. Follow the docs,
> not the lagging templates, when authoring new policies.

The server-side grounding for the entity shapes:

| Server source (in `../core/core/`) | What it grounds |
|---|---|
| `external/db/types/fianu/entities/policy.go` | The policy `detail.Variations` model (effect default `apply`, criteria, locked); serializes variations under the `policy` JSON key. |
| `external/db/types/fianu/entities/indexes.go` | Index detail + the criteria converter that content-hashes scope and dedups inline expressions onto a private index. |
| `pkg/entities_files/handler.go` | Deployer registration for control, policy, exception, and gate (`EntityTypeGateControl`). |
| `server/console/routes.go` | Index deployer registration (`EntityTypeIndex`) with the CEL compile hook — the wiring the CLI index deploy depends on. |

Re-read these before changing this skill's tables. They change frequently
and there is no compile-time check against this SKILL.md.

The wire contract itself (multipart-POST to `/entities/artifacts/deploy`)
is shared with the Terraform path and lives in
`../core/core/pkg/entities_files/handler.go`. Refresh only if the deploy
endpoint or request shape changes.

## See also

- `deploying-entities-as-code` — picking a format, idempotency, approval flow.
- `deploying-entities-terraform` — same entities, HCL surface.
- `writing-rego-rules` — `rule.rego` authoring.
- `designing-policy-templates` — `policyTemplate.measures` syntax.
- `placing-entities-in-hierarchy` — domain/collection selection.
- `working-with-evidence-plugins` — picking a plugin for `relations.producer`.
- `using-fianu-best-practices` → FIANU.md §Policy Variations, §Policy
  Layering — AND/OR variation resolution and how layered/indexed scopes
  compose.
