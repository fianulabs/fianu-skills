# Design: Restructure `skills/` into the `fianu-skills` multi-harness plugin

**Date:** 2026-06-09
**Status:** Approved (sections walked through and confirmed)
**Distribution model:** public GitHub repo as a custom marketplace; primary target Claude Code; secondary targets Gemini CLI and Codex CLI.

---

## 1. Problem

The current `skills/` repo contains:

- `FIANU.md` (905 lines, domain reference)
- `CLAUDE.md` (contributor-facing notes)
- Four entry-point markdown files under `entry-points/` (`fianu-analysis.md`, `fianu-approval-manager.md`, `fianu-evidence-summarizer.md`, `fianu-framework-to-rule-converter.md`)

It has no plugin manifest, no install path, no harness compatibility, and three of the four entry-point files declare `**Loads**:` against shared files (`fianu-shared.md`, `fianu-policies.md`, `fianu-controls.md`, `fianu-default-analysis-guidance.md`) that have never been written. Same facts (Ticket data model, confidence framework, policy diffing methodology, the `config.resolved_approvers` gotcha, the `bot|fianu-agent` actor pattern) are duplicated across multiple entry-points and will drift.

Fianu plans to distribute this skill set to customers so they can build agents that operate on the Fianu compliance platform. Customers need a single, recognizable install path and a clean composable structure — not a folder of prose with broken cross-references.

## 2. Goals and non-goals

**Goals**
- Customers install with a single, well-known command per harness (Claude Code primary; Gemini CLI + Codex CLI secondary).
- One canonical home per fact — no content duplicated across skill files.
- The 4 current entry-point behaviors are reproducible end-to-end after migration.
- Layout matches the conventions of popular OSS skill plugins (specifically the structure used by `obra/superpowers` v5.1.0, which ships across the same harnesses).

**Non-goals (v0.1)**
- Cursor / OpenCode / Factory Droid / Copilot CLI manifests.
- Automated eval tests for skills.
- Deploy-from-source / Terraform-provider skills (lives in a future `fianu-iac` plugin).
- Publication to Anthropic's `claude-plugins-official` marketplace (consider for v0.2+ after iteration on descriptions).

## 3. Plugin identity

| Field | Value |
|---|---|
| Plugin name | `fianu-skills` |
| GitHub repo | `fianulabs/fianu-skills` |
| License | Apache-2.0 |
| Author | Fianu Labs (`support@fianu.io`) |
| Initial version | `0.1.0` |

The repo doubles as its own Claude Code marketplace so customers run:

```
/plugin marketplace add fianulabs/fianu-skills
/plugin install fianu-skills@fianu-skills
```

For Gemini CLI:

```
gemini extensions install https://github.com/fianulabs/fianu-skills
```

For Codex CLI:

```
/plugins         # then search "fianu-skills" → Install Plugin
```

## 4. Repo layout

```
fianu-skills/
├── README.md                              Per-harness install + "what's inside"
├── CLAUDE.md                              Contributor guide (rewritten in Phase 5)
├── GEMINI.md                              @-imports the using-fianu-skills SKILL
├── AGENTS.md                              Mirror of CLAUDE.md for Codex/generic agents
├── LICENSE                                Apache-2.0
├── package.json                           npm metadata (top-level version source of truth)
├── CHANGELOG.md
│
├── .claude-plugin/
│   ├── plugin.json                        Claude Code plugin manifest
│   └── marketplace.json                   Claude Code marketplace listing
├── .codex-plugin/
│   └── plugin.json                        Codex plugin manifest
├── gemini-extension.json                  Gemini CLI extension manifest
│
├── assets/
│   ├── fianu-skills-small.svg
│   └── app-icon.png
│
├── hooks/
│   ├── hooks.json                         Claude Code SessionStart hook
│   └── session-start                      Shell script that bootstraps using-fianu-skills
│
├── skills/                                Canonical skill library (see §5)
│   └── <skill-name>/
│       ├── SKILL.md                       YAML frontmatter (name, description) + body
│       └── references/                    Optional ancillary files loaded on demand
│
├── scripts/
│   ├── bump-version.sh                    Bumps version across all manifests + CHANGELOG
│   └── validate-skills.sh                 Lints SKILL.md frontmatter + cross-references
│
├── tests/
│   └── README.md                          Placeholder for v0.2 eval tests
│
└── docs/
    ├── architecture.md                    How skills compose (orchestrator → primitives → API → best-practices)
    ├── authoring-skills.md                Frontmatter rules, "Loads:" header convention, references/ usage
    └── superpowers/specs/                 Design docs (this file)
```

The same `skills/` tree is referenced by every manifest. Only the per-harness JSON wrappers differ.

## 5. Skill inventory (17 skills, 4 groups)

Names use the gerund convention. The `description:` is tuned as a load trigger, not a marketing blurb — agents read it to decide whether to load the skill, so it must name the concrete situations in which the skill applies.

### Group A — Meta (2)

| Skill | Description (frontmatter) |
|---|---|
| `using-fianu-skills` | Use when starting any conversation involving the Fianu platform — bootstraps the rest of the library, explains the API conventions, the `bot\|fianu-agent` auth pattern, and which skill to load for which task. |
| `using-fianu-best-practices` | Use when reasoning about Fianu entities, assets, hierarchy, or compliance semantics (controls, policies, exceptions, gates, attestations, releases, policy layering). Loads the FIANU.md source of truth and the per-entity best-practices guidance. |

### Group B — Platform API (4) — *the contract with `../core/`*

| Skill | Description |
|---|---|
| `working-with-tickets` | Use when fetching ticket data (tickets, conditions, activities) or posting activities (comment, approved, denied). Establishes the auth-token actor pattern (never `actor` in body), the `config.resolved_approvers` lookup gotcha, and queue iteration. |
| `working-with-entities` | Use when fetching or creating Fianu entities — controls, policies, policy exceptions, gates — or reading their version history. Covers `GET /controls/:key`, `/policies/:key`, `/gates/:key`, `/exceptions/:key`, history endpoints, and `POST /create/control` / `/create/policy` (which create drafts + open approval tickets). |
| `working-with-llm-context-rules` | Use when fetching the markdown guidance pods entity owners attach to controls/policies (`GET /pods/entities/{id}?type=llm_context_rule` and `/llm_context_rule/{key}`). Includes the parent-walk pattern (policy → control). Without a pod, downstream confidence is capped at 0.70. |
| `working-with-evidence-plugins` | Use when picking a plugin to source evidence from or discovering its evidence schema. Covers the plugin catalog (SAST, SCA, container scanning, SBOM, signature, DAST, IaC, testing, deployment, pipeline, code review, access control) and `GET /controls/:key/schemas?producer={pluginPath}`. |

### Group C — Logic primitives (7)

| Skill | Description |
|---|---|
| `diffing-policies` | Use when comparing two versions of a policy or exception to classify changes (threshold relaxed/tightened, key added/removed) and compute aggregate direction. Used by analysis, approval, and any change-review workflow. |
| `computing-decision-confidence` | Use when an agent needs to produce a confidence score for an autonomous action on a Fianu ticket. Defines the 0.50 / 0.75 / 0.90 gate thresholds, the LLM-context-rule presence cap (0.70 without one), and the ambiguity-defaults-to-advisory rule. |
| `writing-rego-rules` | Use when authoring OPA Rego rules for Fianu controls. Covers v1 syntax (`import rego.v1`, `if` keyword), the `input.detail.*` ↔ `data.*` mapping, and the canonical patterns: threshold check, score comparison, presence check, freshness check, multi-metric. |
| `designing-policy-templates` | Use when designing a YAML policy template for a control. Enforces key-naming syntax (alphanumeric + underscore, no leading digit, case-sensitive), readability conventions, and alignment with the Rego rule's `data.*` paths. |
| `placing-entities-in-hierarchy` | Use when deciding which domain and collection a new control or policy belongs to. Maps framework/category keywords to recommended domains (NIST/SOC2/SOX/GDPR/ISO 27001) and collections (Security/QA/Access Control/Change Management/Data Protection/Observability/Infrastructure/Governance). |
| `matching-existing-controls` | Use when checking whether a new requirement is already satisfied by an existing Fianu control. Defines the similarity scoring (name 0.35 / description 0.30 / category 0.20 / plugin 0.15) and the 0.80 / 0.50 thresholds for reuse vs. flag-for-review vs. new-control. |
| `parsing-framework-documents` | Use when ingesting a compliance framework document (Excel, CSV, structured text/PDF) to extract requirements. Covers expected columns, keyword extraction, and classification (automated / manual-attestation / hybrid / informational) with confidence scoring. |

### Group D — Entry-point orchestrators (4)

| Skill | Description |
|---|---|
| `analyzing-tickets` | Use when posting a factual analysis comment on a Fianu approval ticket. Fact-only: no decisions, no confidence scores, no LLM context rules, no opinions. Loads: working-with-tickets, working-with-entities, diffing-policies, using-fianu-best-practices. |
| `managing-ticket-approvals` | Use when autonomously approving or denying a Fianu approval ticket. Loads the confidence framework, LLM context rules, diffing, and submits decisions guarded by the confidence gate. |
| `converting-frameworks-to-controls` | Use when ingesting a compliance framework and mapping requirements to Fianu controls (existing or new). Loads parsing, matching, plugin selection, Rego authoring, policy templates, hierarchy placement, and produces a mapping report for human review before creating any drafts. |
| `summarizing-evidence` | Use when producing a JSON summary of a Fianu finding, violation, or attestation for the in-product evidence panel. Strict schema, no markdown fences, no editorializing. |

### Design rules that apply to every skill

1. **Frontmatter:** `name` (matches directory name) and `description` (load trigger) only. No other fields at v0.1.
2. **`## Loads:` header** appears near the top of any orchestrator and lists the skills it depends on, in the order they're invoked.
3. **References** (extended content, catalogs, templates) live in `references/` next to the SKILL.md and are loaded on demand by the skill body.
4. **No fact lives in two skills.** If two skills need the same fact, the canonical home is whichever skill is most concept-aligned, and the other skill loads it via `Loads:`.

## 6. Multi-harness manifests

The same `skills/` tree is referenced by every manifest. Only the per-harness JSON wrappers differ.

### `.claude-plugin/plugin.json`

```json
{
  "name": "fianu-skills",
  "description": "Skills for building AI agents that operate on the Fianu compliance platform.",
  "version": "0.1.0",
  "author": { "name": "Fianu Labs", "email": "support@fianu.io" },
  "homepage": "https://github.com/fianulabs/fianu-skills",
  "repository": "https://github.com/fianulabs/fianu-skills",
  "license": "Apache-2.0",
  "keywords": ["fianu", "compliance", "controls", "policies", "governance", "skills"]
}
```

### `.claude-plugin/marketplace.json`

```json
{
  "name": "fianu-skills",
  "description": "Fianu Labs skill plugins",
  "owner": { "name": "Fianu Labs", "email": "support@fianu.io" },
  "plugins": [
    {
      "name": "fianu-skills",
      "description": "Skills for building AI agents that operate on the Fianu compliance platform.",
      "version": "0.1.0",
      "source": "./",
      "author": { "name": "Fianu Labs", "email": "support@fianu.io" }
    }
  ]
}
```

### `hooks/hooks.json`

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/session-start\"", "async": false }
        ]
      }
    ]
  }
}
```

`hooks/session-start` is a small shell script that prints a system-reminder telling the agent to invoke `using-fianu-skills` before anything else.

### `gemini-extension.json`

```json
{
  "name": "fianu-skills",
  "description": "Skills for building AI agents that operate on the Fianu compliance platform.",
  "version": "0.1.0",
  "contextFileName": "GEMINI.md"
}
```

### `GEMINI.md`

```
@./skills/using-fianu-skills/SKILL.md
@./skills/using-fianu-skills/references/gemini-tools.md
```

### `.codex-plugin/plugin.json`

```json
{
  "name": "fianu-skills",
  "version": "0.1.0",
  "description": "Skills for building AI agents that operate on the Fianu compliance platform.",
  "author": { "name": "Fianu Labs", "email": "support@fianu.io" },
  "homepage": "https://github.com/fianulabs/fianu-skills",
  "repository": "https://github.com/fianulabs/fianu-skills",
  "license": "Apache-2.0",
  "skills": "./skills/",
  "interface": {
    "displayName": "Fianu Skills",
    "shortDescription": "Build AI agents on the Fianu compliance platform.",
    "developerName": "Fianu Labs",
    "category": "Compliance",
    "capabilities": ["Interactive", "Read", "Write"],
    "defaultPrompt": [
      "Analyze the open Fianu approval tickets and post analysis comments.",
      "Ingest this compliance framework and map requirements to Fianu controls."
    ],
    "websiteURL": "https://fianu.io",
    "brandColor": "#0A2540",
    "logo": "./assets/app-icon.png"
  }
}
```

### `package.json`

```json
{
  "name": "fianu-skills",
  "version": "0.1.0",
  "description": "Skills for building AI agents that operate on the Fianu compliance platform.",
  "license": "Apache-2.0",
  "repository": { "type": "git", "url": "https://github.com/fianulabs/fianu-skills.git" }
}
```

### Lockstep versioning

`scripts/bump-version.sh` updates the version in **all six** manifest files (`package.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `gemini-extension.json`, plus a CHANGELOG.md heading) in lockstep. Manifest drift breaks `/plugin install` silently, so this script (or equivalent CI gate) is mandatory.

## 7. Migration plan

Five phases, each ending in a verifiable state. Each phase produces a clean git checkpoint.

### Phase 0 — Scaffolding

- Create all six manifests with `0.1.0` version.
- Create `hooks/hooks.json`, `hooks/session-start`, `scripts/bump-version.sh`, `scripts/validate-skills.sh`.
- Create `skills/<name>/SKILL.md` for all 17 skills with frontmatter only — bodies are stubs.
- **Exit:** `scripts/validate-skills.sh` passes; `/plugin install` against the local path succeeds in Claude Code; the SessionStart hook fires and lists the 17 skills.

### Phase 1 — Domain & meta skills

- Move `FIANU.md` → `skills/using-fianu-best-practices/references/FIANU.md`. Write a SKILL.md that acts as a topical navigator over that file (e.g. "for policy layering semantics, see §Policies & Exceptions").
- Write `skills/using-fianu-skills/SKILL.md` — explains the platform API conventions, the `bot|fianu-agent` actor identity, and routes by-intent to the right next skill.
- **Exit:** root `FIANU.md` deleted; an agent that loads `using-fianu-skills` can route to the right next skill based on intent.

### Phase 2 — Platform API skills

Extract canonical content from the existing entry-points:

1. `working-with-tickets` — single Ticket/Condition/Activity data model (currently duplicated across `fianu-analysis.md` and `fianu-approval-manager.md`). Endpoints, auth-token actor pattern, `config.resolved_approvers` gotcha, queue iteration.
2. `working-with-entities` — control/policy/exception/gate fetching + version history. `POST /create/control` and `/create/policy` (draft + approval-ticket flow).
3. `working-with-llm-context-rules` — pod endpoints, parent-walk pattern.
4. `working-with-evidence-plugins` — plugin catalog (today's §5 of framework-to-rule-converter) + schema discovery via `GET /controls/:key/schemas?producer={pluginPath}`.

**Exit:** the data model, API tables, and field gotchas exist exactly once in the repo.

### Phase 3 — Logic primitives

Extract in this order (each used by ≥2 orchestrators):

1. `diffing-policies` (used by analysis + approval).
2. `computing-decision-confidence` (gate table from `fianu-approval-manager.md` §7; LLM-context-rule cap; ambiguity-defaults-to-advisory).
3. `writing-rego-rules` (OPA v1 patterns from framework-to-rule-converter §6 + FIANU.md examples).
4. `designing-policy-templates` (from FIANU.md "Creating a Policy Template").
5. `placing-entities-in-hierarchy` (framework-to-rule-converter §7).
6. `matching-existing-controls` (framework-to-rule-converter §4).
7. `parsing-framework-documents` (framework-to-rule-converter §2–3).

**Exit:** every reusable algorithm exists in exactly one SKILL.md. Each orchestrator references the primitive by name.

### Phase 4 — Orchestrator skills

Rewrite each entry-point as a thin coordinator that loads its dependencies, walks workflow steps, renders output template:

- `analyzing-tickets` (from `fianu-analysis.md`) — fact-only constraints preserved.
- `managing-ticket-approvals` (from `fianu-approval-manager.md`) — confidence-gated autonomy preserved.
- `converting-frameworks-to-controls` (from `fianu-framework-to-rule-converter.md`).
- `summarizing-evidence` (from `fianu-evidence-summarizer.md`) — lift-and-shift; minimal extraction.

**Exit:** the 4 original entry-point behaviors are reproducible end-to-end via the new skill set.

### Phase 5 — Cleanup, validation, first release

- Delete `entry-points/` directory.
- Rewrite root `CLAUDE.md` to describe the new structure (the current one references `entry-points/` and the never-existed shared files).
- Write `docs/architecture.md` and `docs/authoring-skills.md`.
- `scripts/bump-version.sh 0.1.0`; `scripts/validate-skills.sh` clean.
- `gh repo create fianulabs/fianu-skills`, push, tag `v0.1.0`.
- End-to-end install on a clean machine: `/plugin marketplace add fianulabs/fianu-skills && /plugin install fianu-skills@fianu-skills`. Run each orchestrator against the staging Fianu API to confirm behavior parity.

**Exit:** v0.1.0 tagged and installable from GitHub on Claude Code, Gemini CLI, and Codex CLI.

## 8. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Content drift during extraction — same fact in multiple skills. | Each Phase 2/3 extraction names one canonical home and deletes from others. `scripts/validate-skills.sh` greps for known canary strings (e.g. `config.resolved_approvers`) and fails if they appear outside `working-with-tickets`. |
| Skill descriptions are load triggers — wrong wording means agents don't auto-load the right skill. | v0.1 ships best-guess descriptions; v0.2 iterates based on real agent behavior. Eval tests planned in v0.2. |
| Today's `CLAUDE.md` becomes obsolete on Phase 5. | Phase 5 explicitly includes a full rewrite of `CLAUDE.md`. |
| No automated tests at v0.1. | Accepted. Phase 5 includes a manual parity test against the staging Fianu API for all 4 orchestrators. Eval tests are a v0.2 deliverable. |
| Manifest version drift across the six files. | `scripts/bump-version.sh` is the single supported way to change version. CI gate (in v0.2) will reject PRs where manifest versions disagree. |
| `bot|fianu-agent` auth-token contract is enforced server-side in `../core/` but is easy to mis-state in skills. | Documented in exactly one place (`working-with-tickets` SKILL.md). All other skills that reference posting activities load `working-with-tickets`. |

## 9. Things explicitly out of scope for v0.1

- Cursor `.cursor-plugin/plugin.json`, OpenCode `.opencode/`, Factory Droid, Copilot CLI marketplace.
- Eval tests in `tests/`.
- Terraform-provider / deploy-from-source skills.
- Publication to `claude-plugins-official` marketplace.
- Skill descriptions tuned via real-traffic telemetry (best-guess at v0.1).
- The `using-superpowers` bootstrap pattern from `obra/superpowers` — referenced as a structural model only; we don't depend on or repackage it.
