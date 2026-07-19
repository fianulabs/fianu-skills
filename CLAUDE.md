# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`fianu-skills` is a multi-harness skill plugin distributed to customers building AI agents on the Fianu compliance platform. It ships skills for Claude Code, Codex CLI, Gemini CLI, and GitHub Copilot CLI. There is no application code — everything here is markdown skill files, JSON manifests, and shell scripts.

## Repo layout

- `skills/` — the canonical skill library (24 skills, 5 groups). See `docs/architecture.md` for the full inventory.
- `.claude-plugin/` / `.codex-plugin/` / `gemini-extension.json` / `plugin.json` (root, Copilot) — per-harness plugin manifests.
- `hooks/` — Claude Code SessionStart hook that bootstraps `using-fianu-skills`.
- `scripts/` — `bump-version.sh` (lockstep version updates) and `validate-skills.sh` (frontmatter + canary-string lint).
- `docs/architecture.md` and `docs/authoring-skills.md` — design docs for contributors.
- `docs/superpowers/specs/` and `docs/superpowers/plans/` — the restructure spec and plan that produced this layout.

## Working on skills

**Edit:** Use `Read` on the specific SKILL.md, `Edit` with enough surrounding context to keep `old_string` unique. Preserve the YAML frontmatter exactly — `validate-skills.sh` will reject changes to `name:` or unknown fields.

**Add a new skill:** Create `skills/<kebab-case-name>/SKILL.md` with frontmatter (`name:` matching the directory, `description:` tuned as a load trigger). Optional `references/*.md` for ancillary content. See `docs/authoring-skills.md`.

**Cross-skill dependencies:** Add a `## Loads` section at the top of the consumer skill's SKILL.md listing the skill names it depends on, in invocation order.

**Single canonical home rule:** every fact lives in one SKILL.md. Other skills reference it via `Loads:`. `validate-skills.sh` enforces this with canary strings — currently `config.resolved_approvers` → `working-with-tickets`, `bot|fianu-agent` → `working-with-tickets`, `GET /pods/entities` → `working-with-llm-context-rules`, `import rego.v1` → `writing-rego-rules`. Canary check runs on SKILL.md bodies only; frontmatter descriptions are load triggers and may legitimately reference canonical keywords.

## Versioning

`scripts/bump-version.sh <new-version>` is the only supported way to change the plugin version. It updates `package.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `gemini-extension.json`, and the root `plugin.json` (Copilot) in lockstep, and inserts a CHANGELOG.md heading. Editing manifests by hand will drift versions and break `/plugin install`.

## Validation

`scripts/validate-skills.sh` checks frontmatter (name matches directory, description present) and canary-string locations. Run it before every commit; CI will run it on every PR once configured.

## Cross-repo context

Skill content depends on contracts that originate in sibling repos (`~/Documents/fianulabs/core/`):

- **`../core/`** — Go backend. Every endpoint a skill references (`GET /tickets/:uuid`, `POST /create/control`, `GET /pods/entities/.../llm_context_rule/...`) has a handler here. Verify request/response shape against the handler before changing API tables.
- **`../fianu-plugins/`** — Plugin source. `skills/working-with-evidence-plugins/references/plugin-catalog.md` must match what's shipped here.
- **`../controllers/`** — Resource controllers for attestation/evaluation orchestration.
- **`../terraform-provider-fianu/`** — Entity-as-code surface. Out of scope for v0.1; lives in a future `fianu-iac` plugin.

There is no compile-time check that skills match sibling-repo state. Staleness compounds silently — when in doubt, grep the sibling repo.

## Things to avoid

- Don't introduce subjective language ("risky", "concerning", "warrants caution") into `analyzing-tickets`. That skill is fact-only by design.
- Don't add a confidence score to `analyzing-tickets`. Confidence belongs to `managing-ticket-approvals` (via `computing-decision-confidence`).
- Don't invent plugin names, control entity keys, or endpoint paths. If you can't ground it in `../core/` or `../fianu-plugins/`, leave it out.
- Don't bypass `bump-version.sh`. Editing a manifest version directly always introduces drift.
- Don't edit frontmatter `name:` after a skill ships. The directory name and the frontmatter name must always match, and changing it would break customer installs at the load-trigger level.
- Don't restate canonical facts in non-canonical skills. If you find yourself typing a canary string (`config.resolved_approvers`, `GET /pods/entities`, `import rego.v1`, etc.) outside its canonical owner, you're duplicating content — add a `Loads:` reference instead. `validate-skills.sh` will catch the duplicate.
