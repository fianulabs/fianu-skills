---
name: using-fianu-skills
description: Use when starting any conversation involving the Fianu platform — bootstraps the rest of the library, explains the API conventions, the bot|fianu-agent auth pattern, and which skill to load for which task.
---

# Using fianu-skills

## Overview

This skill bootstraps `fianu-skills`. When the user mentions the Fianu platform
or any of its concepts (controls, policies, exceptions, gates, tickets,
attestations, evidence, frameworks), load this skill first to route to the
right downstream skill.

## API conventions

All skills in this plugin call the Fianu HTTP API. The conventions are
documented once in `references/api-conventions.md`. Read it before making any
API calls.

Key gotchas (load the canonical skill before acting on any of these):

- Ticket activity writes: the `actor` is set by the auth token, **never** the
  request body. → see `working-with-tickets`.
- Approvers are nested inside the condition's config, not at the top level.
  → see `working-with-tickets`.
- LLM context rule absence caps confidence at 0.70. → see
  `working-with-llm-context-rules`.
- OPA Rego rules use v1 syntax. → see `writing-rego-rules`.

## Routing — load the skill that matches the user's intent

| User intent | Load this skill |
|---|---|
| "Analyze this ticket" / fact-only ticket commentary | `analyzing-tickets` |
| "Approve / deny this ticket" / autonomous workflow | `managing-ticket-approvals` |
| Querying evidence at a commit / digest / release — picking the right series | `working-with-asset-series` |
| A control is missing from results (SBOM / signature / artifact version absent at a commit) | `working-with-asset-series` |
| "Why did this control fail?" — the measured value, threshold, or failed items | `working-with-attestations` |
| List violations / findings / vulnerabilities for an asset or note | `working-with-findings-and-violations` |
| Produce a JSON summary of a finding/violation/attestation (output schema) | `summarizing-evidence` |
| "Ingest this compliance framework" / map to controls | `converting-frameworks-to-controls` |
| "Deploy entities from source" / `fianu console deploy` / Terraform `fianu_*` | `deploying-entities-as-code` |
| Authoring on-disk YAML control packages | `deploying-entities-yaml` |
| Authoring Fianu entities in Terraform HCL | `deploying-entities-terraform` |
| Reading/writing tickets without a full workflow | `working-with-tickets` |
| Reading/writing controls/policies/gates/exceptions | `working-with-entities` |
| Reading attestation results / history / submitting a manual attestation | `working-with-attestations` |
| Evaluating gates / release status / why a release is blocked | `working-with-release-gating` |
| Reading/writing indexes (reusable asset scopes) | `working-with-indexes` |
| Reading LLM-context-rule pods | `working-with-llm-context-rules` |
| Picking a plugin / discovering evidence schemas | `working-with-evidence-plugins` |
| Comparing two policy versions | `diffing-policies` |
| Producing a confidence score for an autonomous action | `computing-decision-confidence` |
| Writing an OPA Rego rule | `writing-rego-rules` |
| Writing a CEL scope expression (policy criteria / index) | `writing-cel-expressions` |
| Designing a YAML policy template | `designing-policy-templates` |
| Deciding domain/collection placement | `placing-entities-in-hierarchy` |
| Checking if an existing control covers a requirement | `matching-existing-controls` |
| Parsing a framework document (Excel/CSV/PDF) | `parsing-framework-documents` |
| Reasoning about Fianu semantics in general | `using-fianu-best-practices` |

## Cross-harness tool names

Skills in this plugin reference tool names in the Claude Code dialect (`Skill`,
`Bash`, `Read`, `Edit`, `Write`, `TaskCreate`, `WebFetch`). When invoking
fianu-skills from a different harness:

- **Codex CLI:** see `references/codex-tools.md`
- **Gemini CLI:** see `references/gemini-tools.md`
- **GitHub Copilot CLI:** see `references/copilot-tools.md`
- **Claude Code:** no mapping needed; tool names are native.
