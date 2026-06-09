# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is the **central hub for Fianu agent skills** — markdown skill files consumed by LLM agents that act on the Fianu platform (compliance/governance for software delivery). There is no build step, no test runner, no application code: every file here is prose that an agent loads at runtime. Edits are validated by reading, not compiling.

Skills here are referenced/loaded by agents running against the platform; they encode workflow logic, API contracts, output schemas, and decision rules. Treat each skill file as a contract between the agent runtime and the Fianu HTTP API — getting the field names, endpoints, and decision thresholds wrong silently breaks production behavior.

## Repo layout

```
FIANU.md                          ← Domain source of truth (905 lines). Entity hierarchy, asset model,
                                    policy layering semantics, control design rules. Cited by every skill.
entry-points/                     ← Top-level skills an agent is dispatched into directly.
  fianu-analysis.md               ← Posts factual analysis comments on approval tickets. No decisions.
  fianu-approval-manager.md       ← Autonomous approve/deny on tickets, gated by confidence + LLM context rules.
  fianu-evidence-summarizer.md    ← Summarizes findings/violations/attestations as strict JSON.
  fianu-framework-to-rule-converter.md  ← Ingests compliance frameworks, maps requirements to controls/Rego.
```

Note: entry-point skills declare `**Loads**: fianu-shared.md, fianu-policies.md, fianu-controls.md, fianu-default-analysis-guidance.md` — **those shared files do not yet exist in this repo**. When extracting shared logic out of entry-points, create those files at the repo root (or in a `shared/` directory) and keep the `Loads` declarations honest.

## Conventions that span every skill

1. **FIANU.md is the source of truth.** Entity hierarchy, asset definitions, policy layering with the override operator `P_x ◁ P_y := (P_x \ P_y) ∪ P_y`, control scope rules, and naming conventions all live there. When a skill's behavior contradicts FIANU.md, FIANU.md wins — fix the skill.
2. **Two-skill split for ticket work.** `fianu-analysis.md` is fact-only (no confidence scores, no opinions, no LLM context rules). `fianu-approval-manager.md` is decision-making (confidence-gated autonomous actions). Don't bleed analysis-only language into approval-manager or vice versa.
3. **Actor identity is set by the auth token, not the request body.** Every `POST /tickets/:uuid/activities` example must omit `actor` — the Fianu API extracts it from `h.User()`. The agent's bot identity is `bot|fianu-agent`. Skills that show `"actor": "..."` in a request body are wrong.
4. **Confidence gate thresholds** (defined in `fianu-approval-manager.md` §7): `≥0.90` autonomous, `0.75–0.89` autonomous + notify, `0.50–0.74` advisory only, `<0.50` human review. No LLM context rule pod → cap confidence at 0.70.
5. **Approver lookup gotcha.** Approvers live in `condition.config.resolved_approvers`, not a top-level condition field. Easy to get wrong.
6. **OPA Rego is v1.** All generated rules use `import rego.v1` and `if` keyword syntax. Map plugin evidence to `input.detail.*`, policy values to `data.*`.
7. **Output format is part of the contract.** `fianu-evidence-summarizer.md` requires raw JSON with no markdown fences. Ticket activity comments use the exact `## Agent Analysis` / `## Analysis:` headers shown in their respective entry-points. Changing the template silently breaks downstream UI rendering.

## Cross-repo context

This repo is a sibling of the Fianu monorepo and lives under `~/Documents/fianulabs/core/`. Skills frequently encode contracts that originate in those sibling repos — verify against the code, not just memory:

- **`../core/`** — Go backend. Entity handlers/deployers, ticket API, controls/policies/gates services, attestation pipeline. When a skill references an endpoint (`GET /tickets/:uuid`, `POST /create/control`, `GET /pods/entities/{id}/llm_context_rule/{key}`), the handler lives here. Verify request/response shape before changing a skill's API section.
- **`../fianu-plugins/`** — Plugin source. The plugin catalog in `fianu-framework-to-rule-converter.md` §5 (Sonarqube, Snyk, Prisma, Sigstore, GitHub Actions, …) and the `producer` field in `GET /controls/:entity_key/schemas?producer=...` must match what's actually shipped here.
- **`../controllers/`** — Resource controllers; relevant when skills touch attestation or evaluation orchestration.
- **`../terraform-provider-fianu/`** — Entity-as-code surface. If a skill describes how a control or policy is deployed from source, the provider's resource schema is the ground truth.
- **`../entities-as-code/` / `../core/pkg/entities_files/`** — Entity file formats referenced by deploy-from-source skills.

When updating a skill, the workflow is: read FIANU.md → read the relevant sibling-repo code → update the skill → verify by grep'ing the skill back against the code. There is no compile-time check; staleness compounds silently.

## Working on skills

**Editing an existing skill.** Skills are long and structured. Use `Read` on the specific section, `Edit` with enough surrounding context to keep `old_string` unique, and preserve section numbering (§1, §2, …) — entry-points cross-reference each other by section number.

**Adding a new entry-point skill.** Follow the existing pattern: top-of-file `Loads: ...` declaration, then numbered sections (Purpose/Overview → Data Model → API Reference → Workflow → Output Format → Edge Cases). Cite FIANU.md as the domain source of truth in the Purpose section.

**Extracting shared logic.** When two entry-points repeat the same content (the Ticket/Condition/Activity data model, the diff methodology, the confidence framework), promote it to a `fianu-shared.md` / `fianu-policies.md` / `fianu-controls.md` file and replace the duplicated section with a reference. The entry-points already declare these files in `**Loads**:` — match those names.

**Verifying changes.** No automated checks exist. Manually:
- Re-read the skill end-to-end after edits to confirm section numbering and cross-references still resolve.
- Grep sibling repos for any endpoint, field name, or constant you added/changed (`rg "/tickets/:uuid/activities" ../core/`).
- Check that any JSON examples are valid JSON (the `fianu-evidence-summarizer.md` contract is strict — no trailing commas, no markdown fences).

## Things to avoid

- Don't introduce subjective language ("risky", "concerning", "warrants caution") into `fianu-analysis.md`. That skill is fact-only by design — see its §6 "Presentation Rules".
- Don't add a confidence score to `fianu-analysis.md` output. Confidence belongs to `fianu-approval-manager.md` only.
- Don't invent plugin names, control entity keys, or endpoint paths. If you can't ground it in `../core/` or `../fianu-plugins/`, leave it out.
- Don't change the `*Fianu Agent v1.0 | …*` footer format in activity comments — the UI parses it.
