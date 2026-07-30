# Architecture

`fianu-skills` ships 26 skills in 5 groups. Orchestrator skills (Group D) are the entry points an agent typically loads first; they declare their dependencies via `## Loads:` and the agent loads each one in turn.

## Skill groups

### Group A — Meta (2)

| Skill | Purpose |
|---|---|
| `using-fianu-skills` | Bootstrap. Routes the agent to the right downstream skill based on user intent. Auto-loaded by the Claude Code SessionStart hook and Gemini CLI's `@`-import; Codex and Copilot CLIs discover it by frontmatter `description`. |
| `using-fianu-best-practices` | Topical navigator over `references/FIANU.md` (the 905-line domain reference). Loaded whenever an agent needs to make a decision aligned with Fianu's domain model. |

### Group B — Platform API (9)

| Skill | Purpose |
|---|---|
| `working-with-tickets` | Canonical home for the Ticket/Condition/Activity data model, ticket endpoints, the bot identity convention, and the nested-approvers lookup gotcha. |
| `working-with-entities` | Read/write controls, policies, exceptions, gates. Draft + approval-ticket flow. |
| `working-with-attestations` | Read attestation results / history, the six-value result vocabulary, manual upload, and **reading a failing control's measured value / threshold / failed items off the raw note**. Owns the warning that `/meta` is policy-provenance only. |
| `working-with-release-gating` | Runtime gate evaluation against assets/releases + the release lifecycle (gate *config* reads stay in `working-with-entities`). |
| `working-with-indexes` | The `/entities/indexes` HTTP surface + compute lifecycle for materialized CEL asset scopes. |
| `working-with-llm-context-rules` | LLM context rule pods. Parent-walk pattern. The 0.70 confidence cap when no pod exists. |
| `working-with-evidence-plugins` | Plugin catalog + schema discovery. |
| `working-with-asset-series` | **Foundation for every evidence query.** The series catalog (`digest`/`uri`/`commit`/`tag`/`release`/`timestamp`/`period_*` + codes), the four series axes, the snapshot + `export` endpoints, cross-series `associations`, and series discovery. Canonical home for "a control is missing from my results". |
| `working-with-findings-and-violations` | Read violations/findings/vulnerabilities off an asset or note (`/evidence/assets/:asset/violations`, `/notes/:uuid/findings`, raw note) + the normalized `Finding` schema. Owns the violations-vs-findings pipeline distinction. Loads `working-with-asset-series`. |

### Group C — Logic primitives (8)

| Skill | Purpose |
|---|---|
| `diffing-policies` | Compare two policy versions; classify changes; compute aggregate direction. |
| `computing-decision-confidence` | Confidence gate thresholds (0.50 / 0.75 / 0.90), 0.70 cap, ambiguity rule. |
| `writing-rego-rules` | OPA v1 patterns: threshold / score / presence / freshness / multi-metric. |
| `designing-policy-templates` | YAML template key syntax and readability conventions. |
| `placing-entities-in-hierarchy` | Domain + collection selection by framework keywords. |
| `matching-existing-controls` | Similarity scoring + thresholds for reuse vs. new-control. |
| `parsing-framework-documents` | Framework document → normalized requirements + classification. |
| `writing-cel-expressions` | The Fianu CEL dialect for policy criteria + index scopes: the `$asset.field.(cast)` grammar and operator vocabulary. |

### Group D — Orchestrators (4)

| Skill | Loads |
|---|---|
| `analyzing-tickets` | `working-with-tickets`, `working-with-entities`, `working-with-attestations`, `diffing-policies`, `using-fianu-best-practices` |
| `managing-ticket-approvals` | All of the above + `working-with-llm-context-rules` + `computing-decision-confidence` |
| `converting-frameworks-to-controls` | `parsing-framework-documents`, `matching-existing-controls`, `working-with-evidence-plugins`, `writing-rego-rules`, `designing-policy-templates`, `placing-entities-in-hierarchy`, `working-with-entities`, `using-fianu-best-practices` |
| `summarizing-evidence` | (none — atomic one-shot skill) |
| `deploying-entities-as-code` | `deploying-entities-yaml`, `deploying-entities-terraform` |

### Group E — Entities-as-code (2)

| Skill | Purpose |
|---|---|
| `deploying-entities-yaml` | On-disk YAML packages and the `fianu console plan/test/deploy` CLI. Canonical home for the controls/ + policies/ directory layout, `spec.yaml` / `contents.yaml` / `rule.rego` file matrix, and the multipart upload contract. |
| `deploying-entities-terraform` | The `fianulabs/fianu` Terraform provider. Canonical home for `fianu_control` / `fianu_policy` / `fianu_gate` / `fianu_index` resource shapes, the `fianu_control_test` action, OIDC vs static-bearer auth, and the X-Fianu-Raw-Content wire format. |

## Composition model

```
orchestrator skill (Group D)
  └─ Loads: → API skills (Group B) + logic primitives (Group C)
                                      └─ See also: → using-fianu-best-practices (Group A)
                                                       └─ references/FIANU.md
```

The bootstrap (`using-fianu-skills`) is loaded by the harness at session start (via the Claude Code SessionStart hook or Gemini's `@`-import); it routes the agent to the right orchestrator based on user intent.

## Single canonical home rule

Every fact lives in exactly one SKILL.md. Consumers reference via `Loads:` and prose pointers like `See <owner-skill>`. `scripts/validate-skills.sh` enforces this with canary strings — if `config.resolved_approvers` appears in any SKILL.md body outside `working-with-tickets`, validation fails.

Current canaries and their owners:

| Canary string | Canonical owner |
|---|---|
| `config.resolved_approvers` | `working-with-tickets` |
| `bot\|fianu-agent` | `working-with-tickets` |
| `GET /pods/entities` | `working-with-llm-context-rules` |
| `import rego.v1` | `writing-rego-rules` |
| `/internal/upload` | `working-with-attestations` |
| `/assets/releases/` | `working-with-release-gating` |
| `recomputeStatus` | `working-with-indexes` |
| `.(list_string)` | `writing-cel-expressions` |
| `/notes/:uuid/findings` | `working-with-findings-and-violations` |
| `record_violation` | `working-with-findings-and-violations` |
| `/evidence/assets/by-series` | `working-with-asset-series` |
| `series_catalog` | `working-with-asset-series` |
| `attestations/export` | `working-with-asset-series` |
| `attestations/snapshot` | `working-with-asset-series` |
| `policy.evaluation.logs` | `working-with-attestations` |

The canary check is scoped to SKILL.md *bodies* only — descriptions in frontmatter are load triggers and may legitimately mention canonical keywords. To add a new canary, edit the `CANARIES` variable in `scripts/validate-skills.sh`.

## How a typical session unfolds

1. Customer starts a Claude Code (or Codex / Gemini) session in a project where `fianu-skills` is installed.
2. The SessionStart hook (Claude Code) or `@`-import (Gemini) loads `using-fianu-skills`.
3. The customer mentions a Fianu concept ("analyze the open tickets", "ingest this framework", "summarize this finding").
4. The agent consults `using-fianu-skills`'s routing table and loads the appropriate orchestrator.
5. The orchestrator's `## Loads` section names its dependencies; the agent loads each in turn before executing the workflow.
6. The orchestrator runs its workflow, posting activities or rendering JSON as the workflow demands.

The same flow works across all four harnesses (Claude Code, Codex CLI, Gemini CLI, GitHub Copilot CLI) because the `skills/` tree is identical — only the per-harness manifests differ.
