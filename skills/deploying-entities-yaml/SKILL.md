---
name: deploying-entities-yaml
description: Use when authoring or deploying Fianu entities as on-disk YAML packages with the `fianu console` CLI. Covers the envs/<env>/{controls,policies,exceptions,indexes,gates}/ directory layout, the per-entity file matrix (spec.yaml, contents.yaml, rule.rego, detail.py, display.py, input/, data/, test/), the required policy shape (`enabled`, `detail.policy[]` variation list with CEL/index criteria), exception YAML, index and gate YAML, `fianu console plan/deploy/test`, and the multipart upload to /entities/artifacts/deploy.
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
│   │   │   └── f.<policy-path>.yaml
│   │   ├── exceptions/
│   │   │   └── f.<exception-path>.yaml
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
| `policy_exception` | single YAML file under `exceptions/`, name format `f.<exception-path>.yaml`; `type: "exception"` |
| `index` | single YAML file, `type: "index"`; a reusable CEL asset-scope referenced by policy/gate criteria |
| `gate` | single YAML file, `type: "gate"`; bundles required controls/gates into a composite decision, with inline policy + pods |

Exceptions use the same `enabled` + `detail.policy[]` + `criteria` shape as
policies, with `type: "exception"` (both top-level and `detail.type`), a
narrowing criteria block on every block, and **required**
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

## policy YAML — required shape

Matches the deployed policy files and the "v2 Simplified Format" policy
template. Required fields are marked.

```yaml
enabled: true                      # REQUIRED — present in every real policy file
name: "<Org> Standard: <Subject>"  # REQUIRED
path: "<dot.notation.path>"        # REQUIRED — immutable
type: "policy"                     # REQUIRED — "policy" | "exception"
detail:
  type: "standard"                 # REQUIRED — standard | exception
  control:
    path: "<control-path>"         # REQUIRED — the control this policy binds to
  policy:                          # REQUIRED — ordered list of variation blocks
    - policy:                      # first block, no criteria → catch-all default
        required: true             # threshold map — matches control's policyTemplate.measures
        <threshold-section>:
          <metric>: <value>
    - criteria:                    # a narrower tier overrides the catch-all above
        asset: { type: repository }
        expression: "asset.scm.repository == 'payments-app'"   # singular CEL shorthand
      policy:
        required: true
        <threshold-section>:
          <metric>: <override-value>
  justification:
    message: "<why this policy exists / why it changed>"   # REQUIRED
  expiration:
    timestamp: "<RFC3339>"         # optional for standard; REQUIRED for exception
```

**The YAML key is `detail.policy:`, not `detail.variations:`.** The server
struct field is named `Variations` but carries the tag `yaml:"policy"`, so each block in
`detail.policy[]` *is* a "variation." There is no `variations:` key — a file
written with `detail.variations:` deploys an empty policy that silently
matches nothing. (The Terraform provider is the only surface that spells the
attribute `variations` — see `deploying-entities-terraform`.)

`detail.policy[]` is evaluated in array order and the **last matching
variation wins** for a given asset — author broadest-to-narrowest: catch-all
first, most-specific last. Each block's `policy` map MUST shape-match the
parent control's `policyTemplate.measures` tree; a key mismatch silently
fails at evaluation time.

### Variation criteria — three mutually exclusive forms

A block with no `criteria` is the catch-all default. When present, `criteria`
must be exactly one of (enforced by `PolicyAssetGroup.IsValid`):

1. **Inline CEL** — `asset: { type: ... }` plus either `expression: "<CEL>"`
   (singular shorthand, what the real repo uses) or `expressions: [{ expression: "<CEL>" }]`
   (plural list, with optional `combineWith: AND|OR`). `asset.type` is
   **required** whenever `expression(s)` is set.
2. **Index reference** — `indexes: [{ path: "core.applications" }]` (or
   `{ id: "<uuid>" }`). Reuses a named scope; omit `expression(s)` — the
   linked index already carries the CEL and asset type. Setting both
   `expressions` and `indexes` is rejected.
3. **Unscoped** — `asset: { type: ... }` alone → a catch-all for every asset
   of that type (links the default per-asset-type index).

> The singular `expression:` is lifted into the plural `expressions[]` by the
> server's `Prepare()` step. Inline `expression(s)` auto-spawn a private
> index: on write the server content-hashes `(asset_type, expressions)` and
> either links an existing index with that hash (dedup) or materialises a new
> `visibility=private` index. Referencing `indexes:` explicitly differs only
> in whether you author the index up front. Author scope at scale as named
> indexes (next section).

Optional per-block fields: `effect: exempt` skips evaluation entirely for
matching assets (vs the default `apply`, which runs the control); `locked: true`
prevents downstream tenants from overriding a block; `name:` labels the block.
For AND/OR resolution semantics when blocks collide on one asset, see
`using-fianu-best-practices` → FIANU.md §Policy Variations.

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
it by `path` or `id` instead of repeating CEL. **Mind the field names:** index
expressions use `expressions[].source`; policy/gate *criteria* use the singular
`expression:` shorthand or `expressions[].expression`. Both surfaces spell the
combine field `combineWith` (camelCase, per the server struct tag), not
`combine_with`.

- `detail.kind` is **server-controlled** — the public deploy endpoint forces
  every user-authored index to `kind: write`. Leave it unset. `default`
  (the auto-managed per-asset-type catch-all) and `write-ahead` are
  reserved and cannot be set from source. Don't author `default.<asset_type>`
  catch-all indexes by hand; the server maintains one per active asset type.
- CLI deploy of an index requires a server with the index deployer
  registered. Against a server without it, the
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

> ⚠️ Unlike policies/exceptions/controls, YAML gate packages are rarely used —
> the Terraform `fianu_gate` resource (see `deploying-entities-terraform`) is the
> better-trodden path for the field set. The gate's inline-policy fields use
> camelCase keys (`protectionLevel`, `requiredControls`); run
> `fianu console plan` on a hand-authored YAML gate and confirm the diff before
> deploying.

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

`--project` and `--repository` are **optional**: they tag deployed entities
with a project / repository scope for organizing them and attributing the
approval-ticket history:

```bash
fianu console deploy ./envs/dev --project my-org --repository my-entities   # attributed
fianu console deploy ./_deploy --controls                                   # unattributed
```

Pass them when you want the attribution; leave them off otherwise.

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

## See also

- `deploying-entities-as-code` — picking a format, idempotency, approval flow.
- `deploying-entities-terraform` — same entities, HCL surface.
- `writing-rego-rules` — `rule.rego` authoring.
- `writing-cel-expressions` — the CEL dialect for `criteria.expression` and index `source`.
- `working-with-indexes` — the runtime API for the index entity referenced by criteria.
- `designing-policy-templates` — `policyTemplate.measures` syntax.
- `placing-entities-in-hierarchy` — domain/collection selection.
- `working-with-evidence-plugins` — picking a plugin for `relations.producer`.
- `using-fianu-best-practices` → FIANU.md §Policy Variations, §Policy
  Layering — AND/OR variation resolution and how layered/indexed scopes
  compose.
