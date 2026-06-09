---
name: deploying-entities-yaml
description: Use when authoring or deploying Fianu entities as on-disk YAML packages with the `fianu console` CLI. Covers the envs/<env>/{controls,policies}/ directory layout, the per-entity file matrix (spec.yaml, contents.yaml, rule.rego, detail.py, display.py, input/, data/, test/), `fianu console plan/deploy/test`, and the multipart upload to /entities/artifacts/deploy.
---

# Deploying Entities (YAML / CLI)

## Overview

The YAML deploy path treats each entity as a directory of files on disk and
ships them to the Fianu Console via the `fianu console` CLI. Controls,
policies, and exceptions all use the same plan / test / deploy workflow;
they differ only in the files they package.

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
│   │   └── policies/
│   │       ├── f.<policy-path>.yaml
│   │       └── f.<control-path>.exception.<id>.yaml
│   ├── qa/   (same shape; controls promote, policies don't)
│   └── prod/
└── templates/
    ├── controls/_template/
    ├── policies/_template.yaml
    └── exceptions/_template.yaml
```

Controls promote across environments unchanged. Policies (and exceptions)
typically differ per environment — lenient in dev, strict in prod.

## File matrix per entity

| Entity | Files |
|---|---|
| `control` | `spec.yaml` + `contents.yaml` + `rule.rego` + (optional) `detail.py`, `display.py` + `input/*.json` + `data/*.json` + `test/*.json` |
| `policy` | single YAML file, name format `f.<policy-path>.yaml` |
| `policy_exception` | single YAML file, name format `f.<control-path>.exception.<id>.yaml`; `type: "exception"` in the body |

Exceptions are policies with `type: "exception"`, a narrowing `criteria`
block, and a required `expiration.timestamp`.

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

## policy YAML — top-level shape

```yaml
name: "<Org> Standard: <Subject>"
path: "<dot.notation.path>"
type: "policy"
detail:
  type: "standard"        # or "exception"
  control:
    path: "<control-path>"
  policy:
    - policy:             # default (no criteria)
        required: true
        <threshold-section>:
          <metric>: <value>
    - criteria:           # optional asset-specific override
        expression: asset.scm.repository == "repo-name"
      policy:
        required: true
        <threshold-section>:
          <metric>: <override-value>
  assets:
    - path: repository
  justification:
    message: "<why this policy exists>"
  expiration:
    timestamp: "<RFC3339>"   # required for exceptions
```

The policy's `policy[].policy` map MUST shape-match the parent control's
`policyTemplate.measures` tree — keys mismatch silently fails at evaluation
time. The agent's responsibility is to keep them aligned.

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

The on-disk YAML format is owned by the `entities-as-code` directory in
core. When updating this skill, refresh from:

| Source-of-truth file (in `../core/entities-as-code/`) | What it controls |
|---|---|
| `templates/controls/_template/spec.yaml` | Control `spec.yaml` shape and field documentation. |
| `templates/controls/_template/contents.yaml` | The contents manifest. |
| `templates/policies/_template.yaml` | Policy YAML shape. |
| `templates/exceptions/_template.yaml` | Exception YAML shape (a policy with `type: "exception"`). |
| `docs/cheat-sheet.md` | Quick reference for common patterns (producer paths, asset/series types, policyTemplate value types). |
| `docs/getting-started/concepts.md` | The five control results (`pass` / `fail` / `warn` / `notFound` / `notRequired`) and the scanner → occurrence → control data flow. |

Re-read these files before changing this skill's tables. They change
frequently and there is no compile-time check against this SKILL.md.

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
