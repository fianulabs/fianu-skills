---
name: deploying-entities-terraform
description: Use when authoring or deploying Fianu entities via the `fianulabs/fianu` Terraform provider — `fianu_control`, `fianu_policy`, `fianu_gate`, `fianu_index` resources, the `fianu_control_test` action, OIDC vs static-bearer auth, the file() pattern for evaluation cases, the X-Fianu-Raw-Content wire format, and import via `<entity_type>/<entity_key>`.
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

## Resources (provider `~> 0.2`)

| Resource | Status | Notes |
|---|---|---|
| `fianu_control` | ✅ Available | Mirrors the on-disk control-package format. |
| `fianu_policy` | ✅ Available | Standard and exception policies (set `detail.type = "exception"`). |
| `fianu_gate` | ✅ Available | Server auto-fills evaluation logic + policy template; HCL exposes identity, config, env bindings, pods, optional inline policy. |
| `fianu_index` | ✅ Available | Reusable asset-scope definitions (CEL over abstract asset types). |
| `fianu_environment` | ⏳ v0.1.x | Not yet released. |
| `fianu_target` | ⏳ v0.1.x | Not yet released. |
| `fianu_collection` | ⏳ v0.1.x | Not yet released. |

The provider also ships one action — `fianu_control_test` — for running
rego rules against on-disk fixtures (see "Testing" below).

## Provider configuration

This mirrors the real working stack in
`../fianu-cloud/environments/fianu-dev/controls/` (`versions.tf` +
`providers.tf`):

```hcl
# versions.tf
terraform {
  backend "s3" {                       # real stacks pin a remote state backend
    bucket       = "fianu-terraform-state"
    key          = "fianu-dev/controls/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }

  required_version = ">= 1.12.0"       # 1.12 is the provider floor; action {} needs 1.14+

  required_providers {
    fianu = {
      source  = "fianulabs/fianu"
      version = "~> 0.2.0"             # current published surface
    }
  }
}

# providers.tf — the real stack leaves the block empty and auths via env vars
provider "fianu" {}
```

### Authentication

The real stack supplies credentials through environment variables rather than
inline attributes. Attributes still work if you prefer them:

| Method | When to use | Variables (env / attribute) |
|---|---|---|
| OIDC client-credentials (preferred) | All non-CI use, and CI clients that can hold a long-lived secret | `FIANU_CLIENT_ID` / `client_id`, `FIANU_CLIENT_SECRET` / `client_secret`, optional `FIANU_TOKEN_URL` / `token_url`, optional `FIANU_AUDIENCE` / `audience` |
| Static bearer | CI service accounts that already hold a long-lived token | `FIANU_TOKEN` / `token` |

`FIANU_HOST` (e.g. `https://console.dev.fianu.io`) is always required.
`audience` defaults to `https://fianu.us.auth0.com/api/v2`; override only for
private deployments. `token_url` defaults to
`https://cloudauth.fianu.io/oauth/token`.

## Resource shape (common across types)

```hcl
resource "fianu_<type>" "<local_name>" {
  path = "<entity-key>"     # immutable; rename forces replacement
  name = "<display name>"

  detail = {
    full_name   = "..."
    display_key = "<2-4 char code>"
    description = "..."
    # type-specific fields below
  }
}
```

Server-managed read-only attributes available after apply:

- `id` — composite identifier `<entity_type>/<entity_key>` (used for import).
- `uuid` — server-generated, stable across versions.
- `version` — nested object: `semantic`, `state`, `status`, `timestamp`, `uuid`. Refetched after every Create/Update so `(known after apply)` plans are correct.

## fianu_control — minimum viable example

```hcl
resource "fianu_control" "sast" {
  path = "checkmarx.sast.vulnerabilities"
  name = "SAST"

  detail = {
    full_name   = "Static Asset Security Analysis"
    display_key = "CHXST"
    description = "Validate SAST findings from Checkmarx."
  }
}
```

`path`, `name`, and `detail` are the only required top-level attributes;
inside `detail`, only `evaluation` is required for a control that actually
evaluates. The minimal block above is deployable but evaluates nothing.

### detail fields expected in a real control

The working example in `../fianu-cloud/environments/fianu-dev/controls/`
(`terraform.example.iac.scan`) fills these out — copy this shape when
generating a new control:

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
    collection = "security"
    path       = "f.demo.source.terraform.iac"
    note       = "occurrence"
    is_primary = true
    producer   = { type = "plugin", path = "generic" }
  }]

  assets = [{                        # abstract asset types + series this applies to
    type   = "repository"            # repository | module | artifact | release
    series = [{ name = "commit" }, { name = "tag" }]
  }]

  policy_template = { measures = [ … ] }   # threshold schema; see designing-policy-templates

  evaluation = local.terraform_example_evaluation   # REQUIRED for real behavior

  config = {                         # operational options
    scope               = "always"
    retries             = true
    evidence_submission = false
    manual_attestations = false
  }
}
```

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

## fianu_policy — example

```hcl
resource "fianu_policy" "iac_scan_strict" {
  path = "f.policy.security.iac.strict"
  name = "Strict IaC Scan Policy"

  detail = {
    type = "standard"   # or "exception"

    control = {
      path = "terraform.example.iac.scan"
    }

    variations = [
      {
        criteria = { asset = { type = "repository" } }
        policy = jsonencode({
          required        = true
          vulnerabilities = {
            critical = { maximum = 0 }
            high     = { maximum = 0 }
            medium   = { maximum = 5 }
            low      = { maximum = 20 }
          }
        })
      },
    ]
  }
}
```

`detail.variations[].policy` is a JSON-encoded string whose decoded shape
MUST match the parent control's `policy_template.measures` tree. The
provider does not validate the inner shape — mismatches silently fail at
evaluation time. (Same constraint as the YAML path.)

## fianu_gate — example

Required inside `detail`: `environments` (≥1), `policy`, and `pods` (≥1).
This mirrors the real `terraform.example.iac.scan` gate:

```hcl
resource "fianu_gate" "terraform_iac_scan" {
  path = "f.gate.security.terraform.iac.scan"
  name = "Terraform IaC Scan Gate"

  detail = {
    full_name   = "Terraform IaC Scan Gate"
    display_key = "TFGS"
    description = "…"

    environments = [{ path = "env.prod" }]   # REQUIRED — ≥1 live environment

    policy = {                               # REQUIRED — gate enforces nothing without it
      variations = [                         # priority-ordered; each names required controls/gates
        {                                    # tier 1 — explicit index
          criteria          = { indexes = [{ path = fianu_index.terraform_prod_repos.path }] }
          required_controls = ["terraform.example.iac.scan"]
        },
        {                                    # tier 2 — inline criteria (auto-creates an index)
          criteria          = {
            asset       = { type = "repository" }
            expressions = [{ expression = "asset.uuid == '…0002'" }]
          }
          required_controls = ["terraform.example.iac.scan"]
        },
        { required_controls = ["terraform.example.iac.scan"] },   # tier 3 — catch-all
      ]
      override = { asset = { types = ["repository"] } }   # binds gate variations to asset type(s)
    }

    pods = [{                                # REQUIRED — ≥1 pipeline-automation rule
      key              = "default"
      name             = "Default enforcement"
      protection_level = "enforce"           # enforce (block) | check (report only)
      enabled          = true
      matching = [                           # optional per-scope protection_level overrides
        {
          protection_level = "check"
          asset            = { type = "repository" }
          expressions      = [{ expression = "asset.uuid == '…0002'" }]
        },
        {
          protection_level = "enforce"
          indexes          = [{ path = fianu_index.terraform_prod_repos.path }]
        },
      ]
    }]
  }
}
```

Each gate variation must carry at least one of `required_controls` or
`required_gates`. Because gates bind via `policy.override.asset.types`, gate
variations may omit per-variation `asset` (unlike policy variations, which
require `asset.type`). The server auto-fills the gate's evaluation logic and
policy template via `applyGateDefaults`; HCL exposes identity, `config`,
`environments`, `pods`, and the inline `policy` (which deploys as a separate
`fianu_policy` keyed to the gate). For the gate to enforce anything, a policy
must exist on it — inline (as above) or as a separate `fianu_policy`.

## fianu_index — example

```hcl
resource "fianu_index" "terraform_prod_repos" {
  path = "f.indexes.terraform.prod_repos.v3"
  name = "Terraform IaC — Production Repos"

  detail = {
    description = "Production repositories under the Terraform IaC scan policy."
    asset_type  = "repository"          # REQUIRED — immutable (rename forces replacement)
    kind        = "write-ahead"         # optional; the real example sets this
    expressions = [                     # REQUIRED — note the key is `source`, not `expression`
      { source = "asset.uuid == '…0001'" },
    ]
  }
}
```

Required in `detail`: `asset_type` and `expressions` (each entry keyed by
`source`). Indexes are referenced from policy / gate variations by `path` or
`id`. The real Terraform example sets `kind = "write-ahead"`; note that the
YAML/CLI public deploy endpoint instead forces user-authored indexes to
`kind: write` (see `deploying-entities-yaml`) — if you mix surfaces, expect a
`kind` diff on import.

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
terraform import fianu_control.sast    control/checkmarx.sast.vulnerabilities
terraform import fianu_policy.strict   policy/f.policy.security.iac.strict
terraform import fianu_gate.security   gate/f.gate.security
terraform import fianu_index.prod_repos index/f.indexes.repos.prod
```

Import blocks (`import { to = …; id = "…" }`) also work.

## Edge cases

### "Unexpected Identity Change" on first apply after import

If you import an entity that was originally deployed via the CLI, the
first apply may show every detail field as changed because the provider's
canonical form differs from the CLI's normalization. Decide which format
owns the entity going forward — don't mix.

### Plan shows `(known after apply)` on every apply

This is expected. The provider does not pin `version.uuid` /
`version.semantic` / `version.timestamp` via `UseStateForUnknown` because
the server bumps them on every partial update; the resource is refetched
post-deploy to populate from server truth.

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

## Maintenance — keeping this skill accurate

The Terraform surface is owned by the `terraform-provider-fianu` repo.
When updating this skill, refresh from:

| Source-of-truth file (in `../terraform-provider-fianu/`) | What it controls |
|---|---|
| `README.md` | Resource matrix, auth methods, the file() / action pattern, the import-id contract. |
| `docs/resources/control.md` | Full `fianu_control` schema (regenerated from the provider — authoritative). |
| `docs/resources/policy.md` | Full `fianu_policy` schema, including variations / criteria / override. |
| `docs/resources/gate.md` | Full `fianu_gate` schema, including pods, environments, inline policy. |
| `docs/resources/index.md` | Full `fianu_index` schema, asset-type taxonomy, CEL expression rules. |
| `docs/actions/control_test.md` | `fianu_control_test` action schema. |
| `internal/resources/<type>/` | Authoritative resource implementations — read when a schema field's runtime semantics aren't clear from the docs. |
| `examples/resources/fianu_control/` | Provider-repo example controls — copy-paste starting points. |
| `CHANGELOG.md` | Version-to-version surface changes (new resources, attribute renames, behaviour fixes). |

The closest thing to a customer-grade, end-to-end working stack lives **outside**
the provider repo, in `fianu-cloud`:

| Real-world stack | What it grounds |
|---|---|
| `../fianu-cloud/environments/fianu-dev/controls/` | A live stack that pulls `fianulabs/fianu ~> 0.2.0` from the public registry and deploys a `fianu_control` + `fianu_policy` + `fianu_gate` + `fianu_index` for `terraform.example.iac.scan`. `versions.tf` / `providers.tf` show the real backend + env-var auth; `main.tf` shows the `locals` + `file()` + `action_trigger` wiring; `README.md` documents prerequisites and the apply flow. This is the canonical "what should the Terraform look like" reference. |

The `docs/resources/*.md` files are auto-generated from the provider
schema by `tfplugindocs` — they are the closest thing to a machine-readable
contract for HCL authoring. Re-read them before changing this skill's
example blocks. The provider schema changes more often than the CLI
format does.

The wire contract (base64 → `X-Fianu-Raw-Content` → POST
`/entities/artifacts/deploy`) lives in
`../terraform-provider-fianu/internal/resources/base/` and the server
counterpart in `../core/pkg/entities_files/handler.go`. Refresh only
if the deploy endpoint or request shape changes.

## See also

- `deploying-entities-as-code` — picking a format, idempotency, approval flow.
- `deploying-entities-yaml` — same entities, on-disk YAML surface.
- `writing-rego-rules` — `rule.rego` authoring.
- `designing-policy-templates` — `policy_template.measures` syntax.
- `placing-entities-in-hierarchy` — domain/collection selection for relations.
- `working-with-evidence-plugins` — picking a plugin for subscription relations.
