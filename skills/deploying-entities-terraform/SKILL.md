---
name: deploying-entities-terraform
description: Use when authoring or deploying Fianu entities via the `fianulabs/fianu` Terraform provider — `fianu_control`, `fianu_policy`, `fianu_gate`, `fianu_index`, `fianu_environment`, `fianu_target`, `fianu_collection`, `fianu_notification`, `fianu_entity_pod`, and the `fianu_control_test` action. Covers OIDC vs static-bearer vs CLI-token auth, the file() pattern for evaluation cases, the X-Fianu-Raw-Content wire format, import via `<entity_type>/<entity_key>`, and the vendored provider schema docs.
---

# Deploying Entities (Terraform)

## Overview

The Terraform path uses the `fianulabs/fianu` provider to declare Fianu
entities in HCL and apply them via `terraform apply`. Resources mirror the
on-disk YAML package shape but expose every field as a typed HCL attribute,
giving plan-time validation, drift detection, and Resource Identity import.

Load this skill when an agent is authoring or applying entities via
Terraform. For the on-disk YAML path, load `deploying-entities-yaml`. For
shared deploy semantics, load `deploying-entities-as-code`.

## Read the vendored provider docs for schemas

`references/provider-docs/` is a verbatim copy of the provider's own
documentation, vendored from the newest release tag. Those pages are generated
upstream by `tfplugindocs` **from the live provider schemas**, so they are the
authoritative HCL contract — every nested attribute, every enum, plus a worked
`Example Usage` block per resource.

**This skill does not restate those schemas.** When authoring a resource, read
its page. `references/provider-docs/README.md` maps pages to resources and
stamps the release tag the copy came from.

```
references/provider-docs/index.md                  provider block + auth attributes
references/provider-docs/resources/<name>.md       fianu_<name> schema
references/provider-docs/actions/control_test.md   fianu_control_test action
```

Read the one page you need — not the set. What this skill owns instead is
everything the generated docs cannot express: auth setup, the `file()`
pattern, the test-action wiring, the wire contract, cross-entity constraints,
and the migration and edge cases below.

## Resources (provider `~> 0.3`)

All nine resources and the one action are released and available.

| Resource | Purpose | Schema page |
|---|---|---|
| `fianu_control` | Compliance control; mirrors the on-disk control-package format. | `resources/control.md` |
| `fianu_policy` | Standard and exception policies (set `detail.type = "exception"`). | `resources/policy.md` |
| `fianu_gate` | Composite gating decision. Server auto-fills evaluation logic and policy template; HCL exposes identity, config, environment bindings, native gate checks, optional inline policy. | `resources/gate.md` |
| `fianu_index` | Reusable asset-scope definitions (CEL over abstract asset types). | `resources/index.md` |
| `fianu_environment` | Named deployment stage; its `matching` CEL group decides which deployment events belong to it. | `resources/environment.md` |
| `fianu_target` | Concrete cloud destination (EKS cluster, Cloud Run service, …) bound to one or more environments. | `resources/target.md` |
| `fianu_collection` | Groups controls under a domain. `detail.domain` is the parent domain's **UUID**, not a path — domains stay Console-managed. | `resources/collection.md` |
| `fianu_notification` | Typed notification config pod on a control or gate. One resource configures one notification *bucket*, and several emitted types share a bucket. | `resources/notification.md` |
| `fianu_entity_pod` | Generic pod attachment — any pod type on any entity, `value` authored with `jsonencode`. Use when no typed resource exists; prefer `fianu_notification` for notification pods. | `resources/entity_pod.md` |
| `fianu_control_test` (action) | Runs a control's rego rules against its fixtures. | `actions/control_test.md` |

Pods (`fianu_notification`, `fianu_entity_pod`) are **living configuration** —
they change how an entity behaves without minting a new entity version. That
is the opposite of every `detail` change, which does mint one.

## Provider configuration

```hcl
# versions.tf
terraform {
  backend "s3" {                       # real stacks pin a remote state backend
    bucket       = "my-org-terraform-state"
    key          = "fianu/controls/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }

  required_version = ">= 1.12.0"       # 1.12 is the provider floor; action {} needs 1.14+

  required_providers {
    fianu = {
      source  = "fianulabs/fianu"
      version = "~> 0.3.0"
    }
  }
}

# providers.tf — leave the block empty and auth via environment variables
provider "fianu" {}
```

### Authentication

`FIANU_HOST` (e.g. `https://console.dev.fianu.io`) is always required. Three
credential paths, in order of preference:

| Method | When to use | Variables (env / attribute) |
|---|---|---|
| OIDC client-credentials | Default for everything | `FIANU_CLIENT_ID` / `client_id`, `FIANU_CLIENT_SECRET` / `client_secret` |
| CLI token fallback | GitHub OIDC / WIF federated flows — no static secrets anywhere | none; the provider reads the token `fianu auth login` persisted at `~/.fianu/fianu.conf.v1` (override the dir with `FIANU_CLI_HOME_DIR`) |
| Static bearer | CI service accounts that already hold a long-lived token | `FIANU_TOKEN` / `token` |

`token` is mutually exclusive with the OIDC client-credentials fields.
`audience` defaults to `https://fianu.us.auth0.com/api/v2`; `token_url`
defaults to `https://cloudauth.fianu.io/oauth/token`. Override either only for
private deployments. Full attribute reference: `provider-docs/index.md`.

## Resource shape (common across types)

```hcl
resource "fianu_<type>" "<local_name>" {
  path = "<entity-key>"     # immutable; rename forces replacement
  name = "<display name>"

  detail = {
    full_name   = "..."
    display_key = "<2-4 char code>"
    description = "..."
    # type-specific fields — see the resource's schema page
  }
}
```

Server-managed read-only attributes available after apply:

- `id` — composite identifier `<entity_type>/<entity_key>` (used for import).
- `uuid` — server-generated, stable across versions. Pod resources reference
  their parent entity through this (`entity_uuid = fianu_control.sast.uuid`).
- `version` — nested object: `semantic`, `state`, `status`, `timestamp`,
  `uuid`. Refetched after every Create/Update so `(known after apply)` plans
  are correct.

## Authoring a control — the detail fields that matter

`resources/control.md` carries the full schema. This is the shape a real
control fills in, annotated with the skill that owns each decision:

```hcl
detail = {
  full_name   = "Terraform IaC Scan"
  display_key = "TFEX"               # 2–4 char code
  description = "…"

  documentation = [                  # optional; {title, url} link list
    { title = "tfsec", url = "https://aquasecurity.github.io/tfsec/" },
  ]

  results = {                        # which verdicts this control may emit
    fail         = true
    warn         = true
    not_required = true
  }

  relations = [{                     # data subscription(s) that feed the rule
    domain     = "compliance.controls"
    collection = "security"          # → placing-entities-in-hierarchy
    path       = "f.demo.source.terraform.iac"
    note       = "occurrence"
    is_primary = true
    producer   = { type = "plugin", path = "generic" }   # → working-with-evidence-plugins
  }]

  assets = [{                        # abstract asset types + series this applies to
    type   = "repository"
    series = [{ name = "commit" }, { name = "tag" }]
  }]

  policy_template = { measures = [ … ] }   # → designing-policy-templates

  evaluation = local.evaluation      # REQUIRED for real behavior — see file() below

  config = {
    scope               = "always"
    retries             = true
    evidence_submission = false
    manual_attestations = false
  }
}
```

`path`, `name`, and `detail` are the only required top-level attributes. A
control with no `evaluation` is deployable but evaluates nothing.

## file() pattern for rego/python content

Keep `rule.rego`, `detail.py`, `display.py`, `rule_test.rego`, and
`input/`/`data/` fixtures as standalone files so syntax highlighting,
linters, and test runners keep working. Load them into HCL via `file()`:

```hcl
locals {
  evaluation = [
    { type = "rule",      engine = "opa", label = "rule.rego",      content = file("${path.module}/rule.rego") },
    { type = "rule_test", engine = "opa", label = "rule_test.rego", content = file("${path.module}/rule_test.rego") },
    { type = "detail",                    label = "detail.py",      content = file("${path.module}/detail.py") },
    { type = "display",                   label = "display.py",     content = file("${path.module}/display.py") },
    { type = "input",                     content = file("${path.module}/input/occ_case_1.json") },
    { type = "data",                      content = file("${path.module}/data/policy_case_1.json") },
  ]
}

resource "fianu_control" "sast" {
  path = "checkmarx.sast.vulnerabilities"
  name = "SAST"
  detail = {
    full_name   = "Static Asset Security Analysis"
    display_key = "CHXST"
    evaluation  = local.evaluation
    # …policy_template, relations, assets, results, config…
  }
}
```

The `evaluation` list mirrors the on-disk control package one-to-one:

```
on-disk file          ↔  evaluation[type=...]
rule.rego             ↔  "rule"
rule_test.rego        ↔  "rule_test"
detail.py             ↔  "detail"
display.py            ↔  "display"
report.py             ↔  "report"
input/*.json          ↔  "input"
data/*.json           ↔  "data"
```

## Testing — fianu_control_test action

The provider exposes a Terraform Action (requires Terraform CLI ≥ 1.14,
framework ≥ 1.16) that runs a control's rego rules against its
`input` / `data` fixtures via `POST /entities/artifacts/test`. Same wire
contract as `fianu console test controls ./...`.

```hcl
action "fianu_control_test" "sast" {
  config {
    path       = "checkmarx.sast.vulnerabilities"
    name       = "SAST"
    evaluation = local.evaluation
  }
}

resource "fianu_control" "sast" {
  # …as above…

  lifecycle {
    action_trigger {
      events  = [after_create, after_update]
      actions = [action.fianu_control_test.sast]
    }
  }
}
```

Run on demand:

```bash
terraform apply -invoke=action.fianu_control_test.sast
```

Failed test cases surface as apply errors; successful runs stream `✓ occ_case_N`
progress events to the CLI. Set `entity_type = "gate_control"` on the
action to test a gate's rules instead of a control's.

## Cross-entity constraints the schema cannot catch

These bind two entities together, so no single resource's plan-time validation
sees them. Each one fails silently at evaluation time, not at apply time.

**`fianu_policy` — the encoded policy must match the control's template.**
`detail.variations[].policy` is a JSON-encoded string whose decoded shape MUST
match the parent control's `policy_template.measures` tree. The provider does
not validate the inner shape. Same constraint as the YAML path.

**`fianu_index` — `expressions` entries are keyed by `source`.** Not
`expression`. Note that gate check `matching` and policy variation `criteria`
use `expression` for their inline CEL — the key differs by surface. See
`writing-cel-expressions`.

**`fianu_index` — `kind` differs by surface.** The Terraform example sets
`kind = "write-ahead"`; the YAML/CLI public deploy endpoint forces
user-authored indexes to `kind: write` (see `deploying-entities-yaml`). Mixing
surfaces on one index produces a `kind` diff on import.

**`fianu_gate` — a gate with no policy enforces nothing.** Author the policy
inline via `detail.policy` (it deploys as a separate policy entity keyed to the
gate) or as a standalone `fianu_policy`. Either way one must exist.

## Migrating from provider 0.2.x — gate pods became `detail.gate`

**Breaking in 0.3.0.** Fianu Console removed the `gate_check_rule` entity pod.
Gate rules are now native to the gate entity, versioned with it and written in
the same deploy call instead of through separate pod API round-trips.

- `detail.pods[]` → `detail.gate.checks[]`. Each pod becomes one check, and the
  pod's `key` becomes the check's `name`.
- `detail.pod_keys` is removed from state entirely.
- `detail.gate.enabled` is new — **the gate's master switch**.
- `pods[].description` has no equivalent on a check. Drop it; it is not in the
  CHANGELOG, so a migration that keeps it fails on an unknown attribute.

```hcl
# 0.2.x — no longer accepted
detail = {
  pods = [{ key = "default", name = "Default enforcement", protection_level = "enforce", enabled = true }]
}

# 0.3.x
detail = {
  gate = {
    enabled = true                          # REQUIRED IN PRACTICE — see below
    checks = [{
      name             = "default"          # was the pod's `key`
      protection_level = "enforce"          # enforce (block) | check (report only)
    }]
  }
}
```

`checks[].matching`, `protection_level`, and the per-scope override semantics
carry over unchanged from `pods[]`. `gating_sources` and `completion_action`
are new per-check fields — see `resources/gate.md`.

## Edge cases

### `detail.gate.enabled` omitted means OFF

The gate-level `enabled` defaults to **off**, matching the server. A gate
migrated from 0.2.x pods without setting it applies cleanly, plans clean, and
silently never activates. This is the most likely migration failure and it
produces no error.

Note the inverted default one level down: `checks[].enabled` omitted means
**enabled**, because a check only exists if someone authored it.

### "Unexpected Identity Change" on first apply after import

If you import an entity that was originally deployed via the CLI, the
first apply may show every detail field as changed because the provider's
canonical form differs from the CLI's normalization. Decide which format
owns the entity going forward — don't mix.

### Plan shows `(known after apply)` on every apply

Expected. The provider does not pin `version.uuid` / `version.semantic` /
`version.timestamp` via `UseStateForUnknown` because the server bumps them on
every partial update; the resource is refetched post-deploy to populate from
server truth.

### Missing `audience` causes `access_denied: No audience parameter`

Auth0 M2M clients whose tenant has no Default Audience set must have the
provider's `audience` field configured (or `FIANU_AUDIENCE`). The default
matches the production Fianu API audience — override only for private
deployments.

### `path` rename

`path` is immutable. Changing it produces a `forces replacement` plan
that destroys-then-creates. For non-disposable entities, deploy a new
entity at the new path first, migrate referrers, then archive the old one
manually.

## Wire contract

`terraform apply` for a Fianu resource:

1. Provider builds the entity Go struct (`*entities.Control`, `*entities.Policy`, …) from HCL.
2. JSON-marshals the struct.
3. Base64-encodes the JSON into the `X-Fianu-Raw-Content` request header.
4. POSTs an empty body to `/entities/artifacts/deploy`.
5. Server runs the SHA256 idempotency check. Unchanged input returns
   `action: "skipped"`; changed input drafts a new version and opens an
   approval ticket.

Same endpoint, same idempotency, same approval flow as the CLI path. See
`deploying-entities-as-code` for the shared semantics.

## Import

Resource Identity (Terraform 1.12+, framework 1.15+) is supported. The
composite ID is `<entity_type>/<entity_key>`:

```bash
terraform import fianu_control.sast     control/checkmarx.sast.vulnerabilities
terraform import fianu_policy.strict    policy/f.policy.security.iac.strict
terraform import fianu_gate.security    gate/f.gate.security
terraform import fianu_index.prod_repos index/f.indexes.repos.prod
```

Import blocks (`import { to = …; id = "…" }`) also work. Each resource's page
carries its own `import.sh` example.

## See also

- `deploying-entities-as-code` — picking a format, idempotency, approval flow.
- `deploying-entities-yaml` — same entities, on-disk YAML surface.
- `working-with-indexes` — the runtime API for the `fianu_index` entity.
- `writing-cel-expressions` — the CEL dialect used in index / policy / gate criteria.
- `writing-rego-rules` — `rule.rego` authoring.
- `designing-policy-templates` — `policy_template.measures` syntax.
- `placing-entities-in-hierarchy` — domain/collection selection for relations.
- `working-with-evidence-plugins` — picking a plugin for subscription relations.
- `using-fianu-api` — inspecting deployed entities over the API after apply.
