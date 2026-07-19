# Authoring skills

## Skill file layout

```
skills/<kebab-case-name>/
├── SKILL.md                  Required. Frontmatter + body.
└── references/               Optional. Ancillary content loaded on demand.
    └── *.md
```

`SKILL.md` MUST exist. Anything else under the skill directory is optional and loaded by the skill body via explicit reference.

## Frontmatter

```yaml
---
name: <directory-name>
description: <load trigger>
---
```

- `name:` MUST equal the directory name (lowercase, hyphenated).
- `description:` is what the agent reads to decide whether to load the skill. Tune it as a load trigger ("Use when …"), not a marketing blurb. Concrete situations beat abstractions.
- No other fields at v0.1.

Descriptions can contain canary strings (like `config.resolved_approvers`) — the validate script only checks bodies. But avoid burying your skill's actual identity in a description that doesn't trigger; descriptions are the load trigger and the most important field.

## Body structure

Every SKILL.md body should include:

1. `# <Title Case Name>` — H1 title.
2. `## Loads` (orchestrators only) — list of dependent skill names, one per line under a bullet.
3. `## Overview` — 1–2 paragraphs: when to load, what it does, what it doesn't do.
4. The body content — endpoints, tables, patterns, workflow steps, edge cases. Use headers, tables, and code blocks aggressively. Avoid prose paragraphs longer than 4 lines.
5. `## See also` — cross-references to related skills.

## Single canonical home rule

Every fact lives in exactly one SKILL.md. Other skills that need the fact `Loads:` the owner. The canary list in `scripts/validate-skills.sh` enforces this for the most-duplicated facts.

To add a new canary: edit the `CANARIES` variable in `scripts/validate-skills.sh` and add a `printf '%s\t%s\n' '<canary string>' '<owner skill directory>'` line.

## Adding a new skill

1. Create `skills/<name>/SKILL.md` with frontmatter and an `## Overview` stub.
2. Run `scripts/validate-skills.sh` — confirm it passes.
3. Fill in the body. If you find yourself re-stating a fact that already lives in another skill, stop and add a `## Loads:` reference (for orchestrators) or a `See <owner-skill>` pointer (for primitives) instead.
4. If the skill needs ancillary content (catalogs, templates, full code listings), add `references/<name>.md` and link to it from the SKILL.md body.
5. Update `docs/architecture.md` to list the new skill.
6. Run `scripts/validate-skills.sh` again, then `scripts/bump-version.sh <next-version>`.

## Description-tuning tips

The description is the load trigger. Bad descriptions cause skills not to load when needed (or to load when not needed).

- **Specific situations beat generic categories.** "Use when posting a comment activity on a ticket" beats "Tickets."
- **Name the concrete things.** "Confidence gate thresholds (0.50 / 0.75 / 0.90)" beats "Confidence scoring."
- **Constraint-mention is a load signal.** Mentioning what the skill enforces ("never actor in body") makes the agent more likely to load when it's about to do that wrong.
- **Cite by name what the skill does NOT do.** "No decisions, no confidence scores, no LLM context rules" in `analyzing-tickets` prevents misuse as much as positive triggers.

## Versioning

`scripts/bump-version.sh <new-version>` is the only supported way to change the plugin version. It updates the six manifest files plus the CHANGELOG.md heading in lockstep. Never edit a manifest version by hand.

## Cross-harness considerations

Skills are loaded by Claude Code, Codex CLI, Gemini CLI, and GitHub Copilot CLI from the same `skills/` tree. When writing a skill:

- Use Claude Code tool names (`Skill`, `Bash`, `Read`, `Edit`, etc.). Tool-name mapping for other harnesses lives in `skills/using-fianu-skills/references/codex-tools.md`, `gemini-tools.md`, and `copilot-tools.md`.
- Don't write skills that depend on a specific harness's exotic feature. Stick to the lowest common denominator (markdown + plain shell where needed).
- The SessionStart hook (`hooks/session-start`) is a Claude Code feature. Gemini's equivalent is the `@`-import in `GEMINI.md`. Codex (`.codex-plugin/plugin.json`) and Copilot (root `plugin.json`) auto-discover skills from their `skills` field — no bootstrap nudge; the `using-fianu-skills` description is the load trigger.
