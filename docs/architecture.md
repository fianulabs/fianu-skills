# Architecture

`fianu-skills` ships 17 skills in 4 groups. Orchestrator skills (Group D) are the entry points an agent typically loads first; they declare their dependencies via `## Loads:` and the agent loads each one in turn.

## Skill groups

### Group A — Meta (2)

| Skill | Purpose |
|---|---|
| `using-fianu-skills` | Bootstrap. Routes the agent to the right downstream skill based on user intent. Auto-loaded by the Claude Code SessionStart hook and Gemini CLI's `@`-import. |
| `using-fianu-best-practices` | Topical navigator over `references/FIANU.md` (the 905-line domain reference). Loaded whenever an agent needs to make a decision aligned with Fianu's domain model. |

### Group B — Platform API (4)

| Skill | Purpose |
|---|---|
| `working-with-tickets` | Canonical home for the Ticket/Condition/Activity data model, ticket endpoints, the bot identity convention, and the nested-approvers lookup gotcha. |
| `working-with-entities` | Read/write controls, policies, exceptions, gates. Draft + approval-ticket flow. |
| `working-with-llm-context-rules` | LLM context rule pods. Parent-walk pattern. The 0.70 confidence cap when no pod exists. |
| `working-with-evidence-plugins` | Plugin catalog + schema discovery. |

### Group C — Logic primitives (7)

| Skill | Purpose |
|---|---|
| `diffing-policies` | Compare two policy versions; classify changes; compute aggregate direction. |
| `computing-decision-confidence` | Confidence gate thresholds (0.50 / 0.75 / 0.90), 0.70 cap, ambiguity rule. |
| `writing-rego-rules` | OPA v1 patterns: threshold / score / presence / freshness / multi-metric. |
| `designing-policy-templates` | YAML template key syntax and readability conventions. |
| `placing-entities-in-hierarchy` | Domain + collection selection by framework keywords. |
| `matching-existing-controls` | Similarity scoring + thresholds for reuse vs. new-control. |
| `parsing-framework-documents` | Framework document → normalized requirements + classification. |

### Group D — Orchestrators (4)

| Skill | Loads |
|---|---|
| `analyzing-tickets` | `working-with-tickets`, `working-with-entities`, `diffing-policies`, `using-fianu-best-practices` |
| `managing-ticket-approvals` | All of the above + `working-with-llm-context-rules` + `computing-decision-confidence` |
| `converting-frameworks-to-controls` | `parsing-framework-documents`, `matching-existing-controls`, `working-with-evidence-plugins`, `writing-rego-rules`, `designing-policy-templates`, `placing-entities-in-hierarchy`, `working-with-entities`, `using-fianu-best-practices` |
| `summarizing-evidence` | (none — atomic one-shot skill) |

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

The canary check is scoped to SKILL.md *bodies* only — descriptions in frontmatter are load triggers and may legitimately mention canonical keywords. To add a new canary, edit the `CANARIES` variable in `scripts/validate-skills.sh`.

## How a typical session unfolds

1. Customer starts a Claude Code (or Codex / Gemini) session in a project where `fianu-skills` is installed.
2. The SessionStart hook (Claude Code) or `@`-import (Gemini) loads `using-fianu-skills`.
3. The customer mentions a Fianu concept ("analyze the open tickets", "ingest this framework", "summarize this finding").
4. The agent consults `using-fianu-skills`'s routing table and loads the appropriate orchestrator.
5. The orchestrator's `## Loads` section names its dependencies; the agent loads each in turn before executing the workflow.
6. The orchestrator runs its workflow, posting activities or rendering JSON as the workflow demands.

The same flow works across all three harnesses because the `skills/` tree is identical — only the per-harness manifests differ.
