# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`fianu-skills` is a multi-harness skill plugin distributed to customers building AI agents on the Fianu compliance platform. It ships skills for Claude Code, Codex CLI, Gemini CLI, and GitHub Copilot CLI. There is no application code — everything here is markdown skill files, JSON manifests, and shell scripts.

## Repo layout

- `skills/` — the canonical skill library. See `docs/architecture.md` for the full inventory.
- `.claude-plugin/` / `.codex-plugin/` / `gemini-extension.json` / `plugin.json` (root, Copilot) — per-harness plugin manifests.
- `hooks/` — Claude Code SessionStart hook that bootstraps `using-fianu-skills`.
- `scripts/` — `bump-version.sh` (lockstep version updates), `validate-skills.sh` (frontmatter + canary-string + public-leak lint), `sync-provider-docs.sh`, `build-bundles.py` (agent prompt bundles), `render-facts.py` (generated facts regions), `check-code-blocks.py` (every code block runs).
- `facts/facts.json` — generated platform facts (enums, Rego builtins, plugin schemas).
- `manifests/agent-contexts.json` — which skills each Fianu agent entry point loads.
- `docs/architecture.md` and `docs/authoring-skills.md` — design docs for contributors.

## Working on skills

**Edit:** Use `Read` on the specific SKILL.md, `Edit` with enough surrounding context to keep `old_string` unique. Preserve the YAML frontmatter exactly — `validate-skills.sh` will reject changes to `name:` or unknown fields.

**Add a new skill:** Create `skills/<kebab-case-name>/SKILL.md` with frontmatter (`name:` matching the directory, `description:` tuned as a load trigger). Optional `references/*.md` for ancillary content. See `docs/authoring-skills.md`.

**Cross-skill dependencies:** Add a `## Loads` section at the top of the consumer skill's SKILL.md listing the skill names it depends on, in invocation order.

**Single canonical home rule:** every fact lives in one SKILL.md. Other skills reference it via `Loads:`. `validate-skills.sh` enforces this with canary strings — currently `config.resolved_approvers` → `working-with-tickets`, `bot|fianu-agent` → `working-with-tickets`, `GET /pods/entities` → `working-with-llm-context-rules`, `import rego.v1` → `writing-rego-rules`. Canary check runs on SKILL.md bodies only; frontmatter descriptions are load triggers and may legitimately reference canonical keywords.

## Versioning

`scripts/bump-version.sh <new-version>` is the only supported way to change the plugin version. It updates `package.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `gemini-extension.json`, and the root `plugin.json` (Copilot) in lockstep, and inserts a CHANGELOG.md heading. Editing manifests by hand will drift versions and break `/plugin install`.

## Validation

`.github/workflows/validate.yml` runs on every PR. Run the same checks locally before committing:

```bash
sh scripts/validate-skills.sh            # frontmatter, canaries, manifest, public-leak denylist
python3 scripts/build-bundles.py --check # every pointer resolves inside its bundle
python3 scripts/render-facts.py --check  # facts regions match facts/facts.json
python3 scripts/check-code-blocks.py     # every rego/json/yaml block parses (needs opa)
```

## Bundles

The in-cluster agent cannot open files, so `scripts/build-bundles.py` resolves every pointer ahead of time. A bundle is every SKILL.md body `manifests/agent-contexts.json` lists for an entry point, frontmatter stripped, in manifest order, then every file those bodies point at, inlined once each. Pointers it recognises:

```
references/<file>.md               a file in the same skill's references/
<skill>/references/<file>.md       a file in another skill's references/
`<skill>` -> <file>.md             the same, in prose (the arrow is -> or U+2192)
<file>.md §<A> > <B> / §<C>        every section named must be a heading in <file>
```

A pointer dangles when its file is missing, its skill is not in the same entry point, or a section it names is not a heading.

## This repo is public

Everything here ships to customers and is readable by anyone. `validate-skills.sh`
fails on references to Fianu-internal repos, cloud accounts,
cluster hostnames, or backend source paths. Maintainer-only grounding (which
backend file proves which claim) lives in the private `fianulabs/skills` repo's
`PROVENANCE.md` — never add a "Maintenance" or "source of truth" section here.

Fianu engineers work on this repo as the `public/` submodule of `fianulabs/skills`,
which pins it, runs control evals against it, and publishes it. Never hand-type a
value the platform can enumerate; it belongs in a `<!-- facts:... -->` region.

## Generated & vendored content

These are derived from other sources and must never be hand-edited:

| Path | Produced by | Source of truth |
|---|---|---|
| `skills/using-fianu-api/references/api-index.md` | Fianu-internal tooling (private repo) | The API gateway config |
| `facts/facts.json` | Fianu-internal tooling (private repo) | The platform source; render with `python3 scripts/render-facts.py` |
| `skills/deploying-entities-terraform/references/provider-docs/` | `scripts/sync-provider-docs.sh` | [`fianulabs/terraform-provider-fianu`](https://github.com/fianulabs/terraform-provider-fianu) at its **newest release tag** (the script fetches tags; it does not read the working tree) |

Run `./scripts/sync-provider-docs.sh` (or `--check` to detect drift) before
`bump-version.sh`. It needs the provider repo checked out next to this one, so it
is not part of `validate-skills.sh`.

## Things to avoid

- Don't introduce subjective language ("risky", "concerning", "warrants caution") into `analyzing-tickets`. That skill is fact-only by design.
- Don't add a confidence score to `analyzing-tickets`. Confidence belongs to `managing-ticket-approvals` (via `computing-decision-confidence`).
- Don't invent plugin names, control entity keys, or endpoint paths. If you can't ground it in `api-index.md`, the plugin catalog, or a live API response, leave it out.
- Don't bypass `bump-version.sh`. Editing a manifest version directly always introduces drift.
- Don't edit frontmatter `name:` after a skill ships. The directory name and the frontmatter name must always match, and changing it would break customer installs at the load-trigger level.
- Don't restate canonical facts in non-canonical skills. If you find yourself typing a canary string (`config.resolved_approvers`, `GET /pods/entities`, `import rego.v1`, etc.) outside its canonical owner, you're duplicating content — add a `Loads:` reference instead. `validate-skills.sh` will catch the duplicate.
