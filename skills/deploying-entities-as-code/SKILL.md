---
name: deploying-entities-as-code
description: Use when deploying Fianu entities from source — controls, policies, exceptions, gates, indexes — via either the `fianu console deploy` CLI (on-disk YAML packages) or the Terraform provider (`fianu_control`, `fianu_policy`, `fianu_gate`, `fianu_index`). Covers the shared `POST /entities/artifacts/deploy` endpoint, format parity, SHA256 content-hash idempotency, and how to choose between YAML and Terraform.
---

# Deploying Entities as Code

## Loads

- `deploying-entities-yaml`
- `deploying-entities-terraform`

## Overview

Fianu entities can be authored and deployed from a source repository in two
formats: on-disk YAML packages driven by `fianu console deploy`, or Terraform
HCL driven by the `fianulabs/fianu` provider. Both paths POST to the same
server endpoint (`/entities/artifacts/deploy`) and run through the same
`pkg/entities_files/control_deployer.go` code on the server, so they produce
identical `Control` / `Policy` / `Gate` rows and honour the same SHA256
content-hash idempotency gate.

Load this skill when an agent needs to author or apply entities from source.
For the read side and the platform-API draft+approval-ticket flow, load
`working-with-entities` instead.

## What "deploy from source" means

| Aspect | Source-deploy (this skill) | Platform-API write (`working-with-entities`) |
|---|---|---|
| Entrypoint | `POST /entities/artifacts/deploy` | `POST /create/control`, `POST /create/policy` |
| Author surface | YAML package or Terraform HCL in a repo | JSON body in a single HTTP call |
| Idempotency | SHA256 content hash; unchanged input → server returns `action: "skipped"` | None — every POST opens a new approval ticket |
| Approval flow | Draft → approval ticket → published (same as API path) | Draft → approval ticket → published |
| Typical caller | CI pipeline, Terraform apply | Agent reacting to a ticket or framework ingestion |

Both paths end up in the same `draft` state and the same approval-ticket
flow. The difference is only in how the bytes get to the server.

## Supported entities (current)

| Entity | YAML / CLI | Terraform | Notes |
|---|---|---|---|
| `control` | ✅ | ✅ `fianu_control` | Full parity. |
| `policy` | ✅ | ✅ `fianu_policy` | Full parity. |
| `policy_exception` | ✅ (exception template) | ✅ via `fianu_policy` with `type = "exception"` | Same wire shape; CLI and provider treat exception as a policy subtype. |
| `gate` | ⚠️ via CLI flags (`--gates`) | ✅ `fianu_gate` | Provider exposes the richer authoring surface (pods, env bindings, inline policy). |
| `index` | ❌ | ✅ `fianu_index` | Terraform-only at v0.1. |
| `environment` | ❌ | ⏳ v0.1.x `fianu_environment` | Neither path stable yet. |
| `target` | ❌ | ⏳ v0.1.x `fianu_target` | Neither path stable yet. |
| `collection` | ❌ | ⏳ v0.1.x `fianu_collection` | Neither path stable yet. |

When the matrix isn't at parity for an entity type, the format choice is
forced. Otherwise it's a workflow preference (see the picker below).

## Format-parity claim — what's actually identical

The CLI and the Terraform provider differ only in the wire format used to
upload an entity:

- **CLI:** tars the directory, multipart-POSTs `payload` (JSON metadata)
  plus `file` (binary archive). The server's `BuildControlFromFiles`
  extracts the archive and constructs the entity.
- **Provider:** builds an `*entities.Control` (or Policy/Gate/Index) in Go
  on the client, JSON-marshals it, base64-encodes the bytes into the
  `X-Fianu-Raw-Content` header, and POSTs.

After ingress, both flow into `control_deployer.go` and produce the same
entity row. A second deploy of an unchanged input — for either path —
returns `action: "skipped"` from the server and zero diff on the client
side (no Terraform plan, no CLI activity).

## Picking a format

```
Are you in a repo that already uses one format?
├─ yes → keep using it (don't mix formats per entity directory)
└─ no  → ask:
         ├─ Do you need a gate, index, environment, target, or collection?
         │   └─ yes → Terraform (only path that exposes them today)
         ├─ Is this a fresh entities-as-code repo with mostly controls + policies?
         │   └─ yes → YAML / CLI (closer to the official-controls layout, simpler authoring)
         └─ Are you already running Terraform for adjacent infra (Cognito, k8s, etc.)?
             └─ yes → Terraform (single apply pipeline, drift detection)
```

Heuristics:

- The on-disk YAML format is what the `official-controls` repo ships with;
  it stays closer to "edit a file, run a command".
- The Terraform provider gives plan-time validation, drift detection, and
  Resource Identity import — useful when entities sit alongside other
  Terraform-managed AWS/GCP/k8s resources.
- Don't mix formats inside one entity directory. Either the package is on
  disk (then deploy via CLI) or the entity is declared in HCL (then deploy
  via Terraform). Mixing breaks the SHA256 idempotency model for that
  entity because the two paths hash different normalisations of the input.

For format-specific details, see:

- YAML / CLI authoring → `deploying-entities-yaml`
- Terraform authoring → `deploying-entities-terraform`

## Common workflow (either format)

1. **Author or edit** the entity (YAML package or HCL block).
2. **Test locally**:
   - YAML: `fianu console test controls ./envs/dev/controls/` and
     `fianu console test policies ./envs/dev/policies/`.
   - Terraform: invoke the `fianu_control_test` action (or set a
     `lifecycle.action_trigger` on the resource).
3. **Plan**:
   - YAML: `fianu console plan ./envs/dev --project <P> --repository <R>`.
   - Terraform: `terraform plan`.
4. **Deploy**:
   - YAML: `fianu console deploy ./envs/dev --project <P> --repository <R>`.
   - Terraform: `terraform apply`.
5. **Approval ticket handling.** Deploy creates entities in `draft` state.
   The platform opens an approval ticket targeting each new/changed
   entity. See `working-with-entities` § Write endpoints (drafts + approval
   tickets) for the lifecycle, and `managing-ticket-approvals` for
   autonomous approval workflows.

## Idempotency — what "unchanged" means

The SHA256 gate is computed over the normalized server-side representation
of the entity, not the on-disk bytes. Things that look like a change but
hash identically and return `action: "skipped"`:

- Reordering keys inside a YAML map.
- Changing comments or blank lines in `spec.yaml`.
- Renaming a Terraform local variable that only affects HCL identifiers.

Things that always trigger a new version:

- Any byte change inside `rule.rego`, `detail.py`, `display.py`,
  `rule_test.rego`, or any `input/` / `data/` file.
- Any change to a field that flows into `entities.Control.detail` (the
  policy template, relations, assets, results, config).
- Renaming the entity path (this is a **replacement** in Terraform and a
  new entity in CLI — both treat path as immutable).

## Edge cases

### Approval ticket not yet closed

Deploy is asynchronous from approval. A second deploy of the same entity
before the first ticket has been approved will succeed (creates a new
draft) but produces a second approval ticket. To avoid ticket churn, wait
for the first ticket to close, or coordinate via `managing-ticket-approvals`.

### Path rename

Both formats treat the entity path as immutable. To rename, deploy a new
entity at the new path and (separately) archive the old one. Terraform
will mark the rename as a `forces replacement` plan; the CLI will create a
second draft without touching the old entity.

### Drift between formats

If a control was originally deployed via the CLI and someone subsequently
imports it into Terraform (`terraform import fianu_control.x control/<key>`),
the next `terraform apply` will rewrite the entity from HCL. Pick one
format per entity and stick with it.

### Cross-repo source-of-truth changes

This skill's accuracy depends on `../core/entities-as-code/` and
`../terraform-provider-fianu/` not drifting from the skill content. See
the **Maintenance** section in each sub-skill for the files to refresh
when updating.

## See also

- `working-with-entities` — read side and platform-API write path.
- `writing-rego-rules` — authoring `rule.rego` (referenced by both formats).
- `designing-policy-templates` — `policy_template.measures` syntax.
- `placing-entities-in-hierarchy` — domain/collection selection for `relations`.
- `working-with-evidence-plugins` — picking a plugin to subscribe to.
