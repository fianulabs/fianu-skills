# fianu-skills Plugin Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the existing `skills/` repo (one FIANU.md + four entry-point markdown files) into the `fianu-skills` multi-harness plugin: 17 skills organized into 4 groups, manifests for Claude Code / Codex / Gemini CLI, a SessionStart hook that auto-loads the bootstrap skill, and lockstep versioning across all manifests.

**Architecture:** Single `skills/` tree referenced by all per-harness manifests (`.claude-plugin/`, `.codex-plugin/`, `gemini-extension.json`). One canonical home per fact — extraction phases (Phase 2/3) name a canonical owner per concept and delete duplicates elsewhere. Five sequential phases (scaffolding → meta → API skills → logic primitives → orchestrators → cleanup/release), each ending in a verifiable checkpoint.

**Tech Stack:** Markdown skill files with YAML frontmatter (Anthropic skill format), JSON manifests, POSIX shell scripts for version bumping and validation, `git` + `gh` CLI for release.

**Reference spec:** `docs/superpowers/specs/2026-06-09-fianu-skills-plugin-restructure-design.md`

---

## File Structure

Files that will exist at v0.1.0 (`*` marks files that already exist and get rewritten or relocated):

```
fianu-skills/
├── README.md                                  Per-harness install + skill inventory
├── CLAUDE.md*                                 Rewritten in Phase 5 to match new layout
├── GEMINI.md                                  Two-line @-import file
├── AGENTS.md                                  Mirror of CLAUDE.md for Codex/generic agents
├── LICENSE                                    Apache-2.0
├── CHANGELOG.md                               Versioned release notes
├── package.json                               Top-level version source of truth
├── .gitignore
├── .claude-plugin/plugin.json
├── .claude-plugin/marketplace.json
├── .codex-plugin/plugin.json
├── gemini-extension.json
├── assets/                                    (Empty at v0.1; icons added later)
│   └── .gitkeep
├── hooks/
│   ├── hooks.json                             Claude Code SessionStart hook config
│   └── session-start                          POSIX shell, bootstraps using-fianu-skills
├── scripts/
│   ├── bump-version.sh                        Updates version in all manifests in lockstep
│   └── validate-skills.sh                     Lints frontmatter + canary-string drift
├── tests/
│   └── README.md                              Placeholder; eval tests deferred to v0.2
├── docs/
│   ├── architecture.md                        How skills compose
│   ├── authoring-skills.md                    Conventions for adding new skills
│   └── superpowers/
│       ├── specs/2026-06-09-fianu-skills-plugin-restructure-design.md*
│       └── plans/2026-06-09-fianu-skills-plugin-restructure.md*  (this file)
└── skills/
    ├── using-fianu-skills/
    │   ├── SKILL.md
    │   └── references/
    │       ├── api-conventions.md             Common patterns (auth header, error codes)
    │       ├── codex-tools.md                 Tool name mapping for Codex
    │       └── gemini-tools.md                Tool name mapping for Gemini
    ├── using-fianu-best-practices/
    │   ├── SKILL.md                           Topical navigator over FIANU.md
    │   └── references/
    │       └── FIANU.md*                      Relocated from repo root (905 lines)
    ├── working-with-tickets/SKILL.md
    ├── working-with-entities/SKILL.md
    ├── working-with-llm-context-rules/SKILL.md
    ├── working-with-evidence-plugins/
    │   ├── SKILL.md
    │   └── references/
    │       └── plugin-catalog.md              Lifted from framework-to-rule-converter.md §5
    ├── diffing-policies/SKILL.md
    ├── computing-decision-confidence/SKILL.md
    ├── writing-rego-rules/
    │   ├── SKILL.md
    │   └── references/
    │       └── patterns.md                    Threshold/score/presence/freshness patterns
    ├── designing-policy-templates/SKILL.md
    ├── placing-entities-in-hierarchy/SKILL.md
    ├── matching-existing-controls/SKILL.md
    ├── parsing-framework-documents/SKILL.md
    ├── analyzing-tickets/
    │   ├── SKILL.md
    │   └── references/output-template.md
    ├── managing-ticket-approvals/
    │   ├── SKILL.md
    │   └── references/output-template.md
    ├── converting-frameworks-to-controls/
    │   ├── SKILL.md
    │   └── references/report-template.md
    └── summarizing-evidence/SKILL.md
```

Files to DELETE during Phase 5:
- `entry-points/fianu-analysis.md`
- `entry-points/fianu-approval-manager.md`
- `entry-points/fianu-evidence-summarizer.md`
- `entry-points/fianu-framework-to-rule-converter.md`
- `entry-points/` (directory itself)
- `FIANU.md` at repo root (already relocated into `using-fianu-best-practices/references/` in Phase 1)

---

## Conventions used throughout the plan

**SKILL.md frontmatter** — every SKILL.md must begin with:

```markdown
---
name: <directory-name>
description: <load trigger from the spec §5 table>
---
```

`name:` MUST match the directory name exactly (lowercased, hyphenated). `description:` is copied verbatim from the spec §5 table.

**`## Loads:` header** — every orchestrator skill (Group D) and any other skill that depends on another skill MUST declare its dependencies in a `## Loads:` section directly after the H1 title, before any other content:

```markdown
## Loads

- `working-with-tickets`
- `working-with-entities`
- `diffing-policies`
- `using-fianu-best-practices`
```

**Single canonical home rule** — every fact lives in exactly one SKILL.md. Other skills that need the fact `Loads:` the owner. The `validate-skills.sh` script greps for canary strings (defined in Phase 0 Task 0.9) and fails if they appear outside their canonical owner.

**Commit cadence** — commit at the end of every numbered task (every checklist sequence ending in a "Commit" step). Frequent commits = recoverable checkpoints if a later task goes wrong.

---

# Phase 0 — Scaffolding

Goal: produce the empty plugin shell. No content migrated yet. All 17 SKILL.md files exist with frontmatter only and `## Overview` stubs. All manifests are present and consistent. `validate-skills.sh` passes.

### Task 0.1: Initialize git and capture baseline

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Initialize git in the current directory**

Run:
```bash
cd /Users/noahkreiger/Documents/fianulabs/core/skills
git init -b main
```

Expected: `Initialized empty Git repository in /Users/noahkreiger/Documents/fianulabs/core/skills/.git/`

- [ ] **Step 2: Create `.gitignore`**

Write `.gitignore`:
```
.DS_Store
node_modules/
*.log
.env
.env.*
!.env.example
```

- [ ] **Step 3: Commit the baseline (current state including FIANU.md, entry-points/, CLAUDE.md, docs/)**

Run:
```bash
git add -A
git commit -m "chore: import existing skills repo as v0 baseline

Captures the pre-restructure state:
- FIANU.md (domain reference, 905 lines)
- entry-points/{fianu-analysis,fianu-approval-manager,fianu-evidence-summarizer,fianu-framework-to-rule-converter}.md
- CLAUDE.md (will be rewritten in Phase 5)
- docs/superpowers/specs/ and docs/superpowers/plans/

All subsequent commits restructure this into the fianu-skills plugin per
docs/superpowers/specs/2026-06-09-fianu-skills-plugin-restructure-design.md."
```

Expected: a single commit on `main`.

---

### Task 0.2: Create root-level package.json and LICENSE

**Files:**
- Create: `package.json`
- Create: `LICENSE`
- Create: `CHANGELOG.md`

- [ ] **Step 1: Write `package.json`**

```json
{
  "name": "fianu-skills",
  "version": "0.1.0",
  "description": "Skills for building AI agents that operate on the Fianu compliance platform.",
  "license": "Apache-2.0",
  "repository": { "type": "git", "url": "https://github.com/fianulabs/fianu-skills.git" }
}
```

- [ ] **Step 2: Write `LICENSE` — full Apache-2.0 text**

Fetch from `https://www.apache.org/licenses/LICENSE-2.0.txt` and save verbatim, then replace the bracketed copyright placeholder at the bottom of the file's "APPENDIX: How to apply the Apache License to your work" section with:
```
Copyright 2026 Fianu Labs

Licensed under the Apache License, Version 2.0 (the "License");
```

(The body of LICENSE is the unmodified Apache-2.0 text. The copyright notice goes at the very top, before the boilerplate text.)

- [ ] **Step 3: Write `CHANGELOG.md`**

```markdown
# Changelog

All notable changes to fianu-skills are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres
to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] — TBD

### Added
- Initial 17-skill release. See `docs/architecture.md` for the skill inventory.
- Multi-harness manifests: Claude Code, Codex CLI, Gemini CLI.
- SessionStart hook (Claude Code) that bootstraps `using-fianu-skills` automatically.
```

- [ ] **Step 4: Commit**

```bash
git add package.json LICENSE CHANGELOG.md
git commit -m "chore: add package.json, LICENSE (Apache-2.0), CHANGELOG"
```

---

### Task 0.3: Create the Claude Code manifests

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Write `.claude-plugin/plugin.json`**

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

- [ ] **Step 2: Write `.claude-plugin/marketplace.json`**

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

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/
git commit -m "feat(claude): add Claude Code plugin manifest and self-marketplace"
```

---

### Task 0.4: Create the Codex manifest

**Files:**
- Create: `.codex-plugin/plugin.json`

- [ ] **Step 1: Write `.codex-plugin/plugin.json`**

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

- [ ] **Step 2: Commit**

```bash
git add .codex-plugin/
git commit -m "feat(codex): add Codex CLI plugin manifest"
```

---

### Task 0.5: Create the Gemini manifest and root context file

**Files:**
- Create: `gemini-extension.json`
- Create: `GEMINI.md`

- [ ] **Step 1: Write `gemini-extension.json`**

```json
{
  "name": "fianu-skills",
  "description": "Skills for building AI agents that operate on the Fianu compliance platform.",
  "version": "0.1.0",
  "contextFileName": "GEMINI.md"
}
```

- [ ] **Step 2: Write `GEMINI.md`**

```
@./skills/using-fianu-skills/SKILL.md
@./skills/using-fianu-skills/references/gemini-tools.md
```

(Two lines, no trailing content. Gemini auto-loads any `@`-imported files at session start.)

- [ ] **Step 3: Commit**

```bash
git add gemini-extension.json GEMINI.md
git commit -m "feat(gemini): add Gemini CLI extension manifest and context file"
```

---

### Task 0.6: Create the Claude Code SessionStart hook

**Files:**
- Create: `hooks/hooks.json`
- Create: `hooks/session-start`

- [ ] **Step 1: Write `hooks/hooks.json`**

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

- [ ] **Step 2: Write `hooks/session-start` (POSIX shell)**

```sh
#!/usr/bin/env sh
# Claude Code SessionStart hook for fianu-skills.
# Emits a system-reminder telling the agent to load the bootstrap skill
# before responding to anything Fianu-related.

cat <<'EOF'
<system-reminder>
fianu-skills is installed. If the user mentions the Fianu platform, controls,
policies, exceptions, gates, tickets, attestations, evidence, or compliance
frameworks, invoke the `using-fianu-skills` skill before responding so you
load the right downstream skill for the task.
</system-reminder>
EOF
```

- [ ] **Step 3: Make the script executable**

Run:
```bash
chmod +x hooks/session-start
```

- [ ] **Step 4: Verify the script runs**

Run:
```bash
hooks/session-start
```

Expected output:
```
<system-reminder>
fianu-skills is installed. If the user mentions the Fianu platform, controls,
policies, exceptions, gates, tickets, attestations, evidence, or compliance
frameworks, invoke the `using-fianu-skills` skill before responding so you
load the right downstream skill for the task.
</system-reminder>
```

- [ ] **Step 5: Commit**

```bash
git add hooks/
git commit -m "feat(hooks): add Claude Code SessionStart hook that bootstraps using-fianu-skills"
```

---

### Task 0.7: Create the version-bump script

**Files:**
- Create: `scripts/bump-version.sh`

- [ ] **Step 1: Write `scripts/bump-version.sh`**

```sh
#!/usr/bin/env sh
# Bumps the version in lockstep across all manifests.
# Usage: scripts/bump-version.sh <new-version>
# Example: scripts/bump-version.sh 0.2.0

set -eu

if [ "$#" -ne 1 ]; then
    echo "usage: $0 <new-version>" >&2
    exit 1
fi

NEW="$1"
REPO_ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"

# All six files that must be updated in lockstep:
FILES="
package.json
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
.codex-plugin/plugin.json
gemini-extension.json
"

cd "$REPO_ROOT"

for f in $FILES; do
    if [ ! -f "$f" ]; then
        echo "missing manifest: $f" >&2
        exit 1
    fi
    # Replace the first "version": "X.Y.Z" line. Works for top-level
    # and nested (marketplace.json plugins[].version) because we apply
    # a global substitution but every manifest's version values are
    # expected to match.
    tmp="$(mktemp)"
    sed -E 's/"version": "[^"]+"/"version": "'"$NEW"'"/g' "$f" > "$tmp"
    mv "$tmp" "$f"
    echo "updated $f → $NEW"
done

# Insert a new heading at the top of CHANGELOG.md if Unreleased exists.
if grep -q '^## \[Unreleased\]$' CHANGELOG.md; then
    today="$(date -u +%Y-%m-%d)"
    awk -v ver="$NEW" -v today="$today" '
        /^## \[Unreleased\]$/ {
            print
            print ""
            print "## [" ver "] — " today
            next
        }
        { print }
    ' CHANGELOG.md > CHANGELOG.md.tmp && mv CHANGELOG.md.tmp CHANGELOG.md
    echo "inserted [$NEW] heading in CHANGELOG.md"
fi

echo "done. Review with: git diff"
```

- [ ] **Step 2: Make the script executable**

Run:
```bash
chmod +x scripts/bump-version.sh
```

- [ ] **Step 3: Verify the script is idempotent against the current 0.1.0 state**

Run:
```bash
scripts/bump-version.sh 0.1.0
git diff --exit-code
```

Expected: `git diff` exits 0 (no changes — every file already at 0.1.0).

- [ ] **Step 4: Commit**

```bash
git add scripts/bump-version.sh
git commit -m "tooling: add bump-version.sh for lockstep version updates across manifests"
```

---

### Task 0.8: Create the skill-validation script

**Files:**
- Create: `scripts/validate-skills.sh`

- [ ] **Step 1: Write `scripts/validate-skills.sh`**

```sh
#!/usr/bin/env sh
# Validates SKILL.md files:
#   1. Every skills/<dir>/ contains a SKILL.md.
#   2. Every SKILL.md begins with YAML frontmatter containing `name:` and `description:`.
#   3. `name:` matches the directory name.
#   4. Canonical-home canaries: certain strings appear in exactly one SKILL.md.
#
# Exits non-zero on any violation.

set -eu

REPO_ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$REPO_ROOT"

EXIT=0

# Each canary line below is "<canary string>|<expected owner skill>". The script
# fails if the canary appears outside its expected owner. The owner is matched
# by directory name under skills/.
CANARIES="
config.resolved_approvers|working-with-tickets
bot|fianu-agent|working-with-tickets
GET /pods/entities|working-with-llm-context-rules
import rego.v1|writing-rego-rules
"

# --- Check 1+2+3: frontmatter ---
for dir in skills/*/; do
    name="$(basename "$dir")"
    skill="$dir/SKILL.md"

    if [ ! -f "$skill" ]; then
        echo "FAIL: missing $skill" >&2
        EXIT=1
        continue
    fi

    # Frontmatter must be the first non-empty line and start with ---.
    if ! head -n 1 "$skill" | grep -qx -- "---"; then
        echo "FAIL: $skill missing YAML frontmatter (must start with ---)" >&2
        EXIT=1
        continue
    fi

    # Extract the name: line from the frontmatter (top 10 lines should cover it).
    declared="$(head -n 10 "$skill" | sed -n 's/^name: *//p' | head -n 1)"
    if [ -z "$declared" ]; then
        echo "FAIL: $skill missing 'name:' in frontmatter" >&2
        EXIT=1
        continue
    fi
    if [ "$declared" != "$name" ]; then
        echo "FAIL: $skill declares name=$declared but directory is $name" >&2
        EXIT=1
    fi

    # description: must exist and be non-empty.
    desc="$(head -n 10 "$skill" | sed -n 's/^description: *//p' | head -n 1)"
    if [ -z "$desc" ]; then
        echo "FAIL: $skill missing or empty 'description:' in frontmatter" >&2
        EXIT=1
    fi
done

# --- Check 4: canary strings ---
echo "$CANARIES" | while IFS='|' read -r canary owner; do
    [ -z "$canary" ] && continue
    # Files where the canary appears, excluding references/ (which may include
    # quoted examples).
    hits="$(grep -rlF -- "$canary" skills/ 2>/dev/null | grep '/SKILL\.md$' || true)"
    if [ -z "$hits" ]; then
        echo "FAIL: canary '$canary' not found in any SKILL.md (expected in $owner)" >&2
        echo "_FAIL_" > /tmp/validate-skills.fail
        continue
    fi
    for h in $hits; do
        dir="$(basename "$(dirname "$h")")"
        if [ "$dir" != "$owner" ]; then
            echo "FAIL: canary '$canary' appears in skills/$dir/SKILL.md but canonical home is skills/$owner/SKILL.md" >&2
            echo "_FAIL_" > /tmp/validate-skills.fail
        fi
    done
done

if [ -f /tmp/validate-skills.fail ]; then
    rm -f /tmp/validate-skills.fail
    EXIT=1
fi

if [ "$EXIT" -eq 0 ]; then
    echo "validate-skills: OK"
fi
exit "$EXIT"
```

- [ ] **Step 2: Make the script executable**

Run:
```bash
chmod +x scripts/validate-skills.sh
```

- [ ] **Step 3: Verify the script runs (it will FAIL until skills are created in Task 0.9)**

Run:
```bash
scripts/validate-skills.sh; echo "exit=$?"
```

Expected: exits non-zero with "FAIL: missing skills/.../SKILL.md" errors. That's fine — Task 0.9 creates the skills.

- [ ] **Step 4: Commit**

```bash
git add scripts/validate-skills.sh
git commit -m "tooling: add validate-skills.sh to lint frontmatter and canary-string drift"
```

---

### Task 0.9: Create all 17 SKILL.md stubs with frontmatter

**Files:**
- Create: `skills/using-fianu-skills/SKILL.md`
- Create: `skills/using-fianu-best-practices/SKILL.md`
- Create: `skills/working-with-tickets/SKILL.md`
- Create: `skills/working-with-entities/SKILL.md`
- Create: `skills/working-with-llm-context-rules/SKILL.md`
- Create: `skills/working-with-evidence-plugins/SKILL.md`
- Create: `skills/diffing-policies/SKILL.md`
- Create: `skills/computing-decision-confidence/SKILL.md`
- Create: `skills/writing-rego-rules/SKILL.md`
- Create: `skills/designing-policy-templates/SKILL.md`
- Create: `skills/placing-entities-in-hierarchy/SKILL.md`
- Create: `skills/matching-existing-controls/SKILL.md`
- Create: `skills/parsing-framework-documents/SKILL.md`
- Create: `skills/analyzing-tickets/SKILL.md`
- Create: `skills/managing-ticket-approvals/SKILL.md`
- Create: `skills/converting-frameworks-to-controls/SKILL.md`
- Create: `skills/summarizing-evidence/SKILL.md`

- [ ] **Step 1: Write each stub using the template below**

Template (replace `<NAME>` and `<DESCRIPTION>`):

```markdown
---
name: <NAME>
description: <DESCRIPTION>
---

# <Title Case Name>

## Overview

Stub — body content arrives in Phase 1/2/3/4 per
`docs/superpowers/plans/2026-06-09-fianu-skills-plugin-restructure.md`.
```

The `name:` value matches the directory name. The `description:` values come from the spec (`docs/superpowers/specs/2026-06-09-fianu-skills-plugin-restructure-design.md` §5). Copy them verbatim. They are:

| name | description |
|---|---|
| `using-fianu-skills` | `Use when starting any conversation involving the Fianu platform — bootstraps the rest of the library, explains the API conventions, the bot\|fianu-agent auth pattern, and which skill to load for which task.` |
| `using-fianu-best-practices` | `Use when reasoning about Fianu entities, assets, hierarchy, or compliance semantics (controls, policies, exceptions, gates, attestations, releases, policy layering). Loads the FIANU.md source of truth and the per-entity best-practices guidance.` |
| `working-with-tickets` | `Use when fetching ticket data (tickets, conditions, activities) or posting activities (comment, approved, denied). Establishes the auth-token actor pattern (never actor in body), the config.resolved_approvers lookup gotcha, and queue iteration.` |
| `working-with-entities` | `Use when fetching or creating Fianu entities — controls, policies, policy exceptions, gates — or reading their version history. Covers GET /controls/:key, /policies/:key, /gates/:key, /exceptions/:key, history endpoints, and POST /create/control / /create/policy.` |
| `working-with-llm-context-rules` | `Use when fetching the markdown guidance pods entity owners attach to controls/policies. Includes the parent-walk pattern (policy → control). Without a pod, downstream confidence is capped at 0.70.` |
| `working-with-evidence-plugins` | `Use when picking a plugin to source evidence from or discovering its evidence schema. Covers the plugin catalog (SAST, SCA, container scanning, SBOM, signature, DAST, IaC, testing, deployment, pipeline, code review, access control) and GET /controls/:key/schemas.` |
| `diffing-policies` | `Use when comparing two versions of a policy or exception to classify changes (threshold relaxed/tightened, key added/removed) and compute aggregate direction. Used by analysis, approval, and any change-review workflow.` |
| `computing-decision-confidence` | `Use when an agent needs to produce a confidence score for an autonomous action on a Fianu ticket. Defines the 0.50 / 0.75 / 0.90 gate thresholds, the LLM-context-rule presence cap (0.70 without one), and the ambiguity-defaults-to-advisory rule.` |
| `writing-rego-rules` | `Use when authoring OPA Rego rules for Fianu controls. Covers v1 syntax (import rego.v1, if keyword), the input.detail.* ↔ data.* mapping, and the canonical patterns: threshold check, score comparison, presence check, freshness check, multi-metric.` |
| `designing-policy-templates` | `Use when designing a YAML policy template for a control. Enforces key-naming syntax (alphanumeric + underscore, no leading digit, case-sensitive), readability conventions, and alignment with the Rego rule's data.* paths.` |
| `placing-entities-in-hierarchy` | `Use when deciding which domain and collection a new control or policy belongs to. Maps framework/category keywords to recommended domains (NIST/SOC2/SOX/GDPR/ISO 27001) and collections (Security/QA/Access Control/Change Management/Data Protection/Observability/Infrastructure/Governance).` |
| `matching-existing-controls` | `Use when checking whether a new requirement is already satisfied by an existing Fianu control. Defines the similarity scoring (name 0.35 / description 0.30 / category 0.20 / plugin 0.15) and the 0.80 / 0.50 thresholds for reuse vs. flag-for-review vs. new-control.` |
| `parsing-framework-documents` | `Use when ingesting a compliance framework document (Excel, CSV, structured text/PDF) to extract requirements. Covers expected columns, keyword extraction, and classification (automated / manual-attestation / hybrid / informational) with confidence scoring.` |
| `analyzing-tickets` | `Use when posting a factual analysis comment on a Fianu approval ticket. Fact-only: no decisions, no confidence scores, no LLM context rules, no opinions. Loads: working-with-tickets, working-with-entities, diffing-policies, using-fianu-best-practices.` |
| `managing-ticket-approvals` | `Use when autonomously approving or denying a Fianu approval ticket. Loads the confidence framework, LLM context rules, diffing, and submits decisions guarded by the confidence gate.` |
| `converting-frameworks-to-controls` | `Use when ingesting a compliance framework and mapping requirements to Fianu controls (existing or new). Loads parsing, matching, plugin selection, Rego authoring, policy templates, hierarchy placement, and produces a mapping report for human review before creating any drafts.` |
| `summarizing-evidence` | `Use when producing a JSON summary of a Fianu finding, violation, or attestation for the in-product evidence panel. Strict schema, no markdown fences, no editorializing.` |

(Pipe characters in descriptions — e.g. `bot|fianu-agent` — are intentional. YAML treats them as plain scalars in this context. If a parser objects, wrap that single description in double quotes.)

- [ ] **Step 2: Note that `validate-skills.sh` will still FAIL the canary check at this stage**

At Step 1 completion, the canary check fails because no SKILL.md body content exists yet — none of the canary strings (`config.resolved_approvers`, `bot|fianu-agent`, `GET /pods/entities`, `import rego.v1`) appears in any SKILL.md body. That's expected; the canaries are populated in Phases 2/3.

Suppress the canary check for now by temporarily commenting out the canary loop in `scripts/validate-skills.sh` (lines starting with `echo "$CANARIES"` through `done`) and confirm the frontmatter checks pass:

```bash
scripts/validate-skills.sh; echo "exit=$?"
```

Expected output:
```
validate-skills: OK
exit=0
```

Then **un-comment** the canary loop and commit both changes together. (The canary check will start passing once Phase 2/3 lands the bodies.)

- [ ] **Step 3: Commit**

```bash
git add skills/
git commit -m "feat(skills): scaffold 17 SKILL.md stubs with frontmatter

Each stub contains only YAML frontmatter (name, description from spec §5)
and a placeholder '## Overview' section. Bodies arrive in Phases 1-4."
```

---

### Task 0.10: Create root context files (AGENTS.md, README.md, .gitkeeps, docs placeholders)

**Files:**
- Create: `AGENTS.md`
- Create: `README.md`
- Create: `assets/.gitkeep`
- Create: `tests/README.md`
- Create: `docs/architecture.md` (placeholder)
- Create: `docs/authoring-skills.md` (placeholder)

- [ ] **Step 1: Write `AGENTS.md`** — placeholder pointing at CLAUDE.md

```markdown
# fianu-skills — Contributor Notes

This file is the entry point for Codex CLI and other generic agents. The full
contributor guide lives in `CLAUDE.md`; everything in CLAUDE.md applies to
agents working in this repo regardless of harness.

See `docs/authoring-skills.md` for conventions when adding new skills.
```

- [ ] **Step 2: Write `README.md`**

```markdown
# fianu-skills

Skills for building AI agents that operate on the [Fianu](https://fianu.io)
compliance platform — covering ticket workflows, entity management, evidence
summaries, and compliance-framework ingestion.

Installs as a plugin in Claude Code, Codex CLI, and Gemini CLI.

## Install

### Claude Code

```
/plugin marketplace add fianulabs/fianu-skills
/plugin install fianu-skills@fianu-skills
```

### Codex CLI

```
/plugins
```

Then search `fianu-skills` and select Install Plugin.

### Gemini CLI

```
gemini extensions install https://github.com/fianulabs/fianu-skills
```

## What's inside

17 skills organized in four groups:

- **Meta** — `using-fianu-skills`, `using-fianu-best-practices`
- **Platform API** — `working-with-tickets`, `working-with-entities`, `working-with-llm-context-rules`, `working-with-evidence-plugins`
- **Logic primitives** — `diffing-policies`, `computing-decision-confidence`, `writing-rego-rules`, `designing-policy-templates`, `placing-entities-in-hierarchy`, `matching-existing-controls`, `parsing-framework-documents`
- **Entry-point orchestrators** — `analyzing-tickets`, `managing-ticket-approvals`, `converting-frameworks-to-controls`, `summarizing-evidence`

See `docs/architecture.md` for how they compose.

## Contributing

See `CLAUDE.md` (Claude Code) or `AGENTS.md` (other harnesses) and `docs/authoring-skills.md`.

## License

Apache-2.0. See `LICENSE`.
```

- [ ] **Step 3: Write `assets/.gitkeep`** (empty file so the directory is tracked)

```bash
touch assets/.gitkeep
```

- [ ] **Step 4: Write `tests/README.md`** (placeholder)

```markdown
# tests/

Eval tests for individual skills are planned for v0.2. v0.1 ships with manual
parity tests against the staging Fianu API (see Phase 5 of the implementation
plan at `docs/superpowers/plans/2026-06-09-fianu-skills-plugin-restructure.md`).
```

- [ ] **Step 5: Write `docs/architecture.md`** (placeholder — full content lands in Phase 5)

```markdown
# Architecture

This file is a placeholder. Full content lands in Phase 5 of the restructure plan
(`docs/superpowers/plans/2026-06-09-fianu-skills-plugin-restructure.md`).
```

- [ ] **Step 6: Write `docs/authoring-skills.md`** (placeholder — full content lands in Phase 5)

```markdown
# Authoring Skills

This file is a placeholder. Full content lands in Phase 5 of the restructure plan
(`docs/superpowers/plans/2026-06-09-fianu-skills-plugin-restructure.md`).
```

- [ ] **Step 7: Commit**

```bash
git add AGENTS.md README.md assets/.gitkeep tests/README.md docs/architecture.md docs/authoring-skills.md
git commit -m "docs: add README, AGENTS, placeholders for architecture and authoring guides"
```

---

### Task 0.11: Phase 0 exit verification

- [ ] **Step 1: Run validation**

```bash
scripts/validate-skills.sh; echo "exit=$?"
```

Expected:
```
validate-skills: OK
exit=0
```

If FAIL, fix the offending SKILL.md and re-run.

- [ ] **Step 2: Confirm the directory tree matches the File Structure section**

```bash
find . -type f -not -path './.git/*' | sort
```

Compare against the File Structure section at the top of this plan. All files except the four `entry-points/*.md` files and the root `FIANU.md` should be present.

- [ ] **Step 3: Tag the Phase 0 exit point**

```bash
git tag -a phase-0-exit -m "Phase 0 (scaffolding) complete; all manifests and stubs in place"
```

---

# Phase 1 — Domain & meta skills

Goal: relocate FIANU.md into `using-fianu-best-practices`, write the bootstrap `using-fianu-skills`, and write the per-harness tool-mapping references.

### Task 1.1: Relocate FIANU.md into `using-fianu-best-practices`

**Files:**
- Move: `FIANU.md` → `skills/using-fianu-best-practices/references/FIANU.md`
- Modify: `skills/using-fianu-best-practices/SKILL.md`

- [ ] **Step 1: Create the references directory and move the file**

```bash
mkdir -p skills/using-fianu-best-practices/references
git mv FIANU.md skills/using-fianu-best-practices/references/FIANU.md
```

Expected: `git status` shows the rename, no content change.

- [ ] **Step 2: Rewrite `skills/using-fianu-best-practices/SKILL.md` as a topical navigator**

Open the stub from Task 0.9 and replace its body (everything after the `---` frontmatter close) with:

```markdown
# Using Fianu Best Practices

## Overview

This skill loads the authoritative Fianu domain reference (`references/FIANU.md`,
905 lines) and acts as a topical navigator. When another skill needs to make
a decision aligned with Fianu's domain model — entity hierarchy, asset taxonomy,
policy layering semantics, control design rules, naming conventions — load this
skill and jump to the relevant section of `references/FIANU.md`.

## When to load

- Designing a new control, policy, exception, or gate
- Picking a scope (repository / module / artifact / release / logical asset)
- Naming a control (do not name after a vendor)
- Writing a policy template (key syntax, readability)
- Reasoning about policy layering when multiple policies apply
- Placing entities under domains and collections
- Understanding release lifecycle, immutability, closure

## Section index

`references/FIANU.md` is organized as follows. Jump directly to the section
you need:

| Topic | Section in FIANU.md |
|---|---|
| Asset taxonomy (fixed / logical / releases) | `## Assets` |
| Asset hierarchy table and parent-child model | `### Asset Hierarchy` |
| Release lifecycle and immutability | `### Releases` |
| Compliance flow (Domains → Collections → Controls → Policies → Indexes) | `### Compliance` |
| Domain best practices (3–6 for large enterprises; 1–3 for small) | `#### Domains > Best Practices` |
| Collection best practices (5–20 collections) | `#### Collections > Best Practices` |
| Designing a control (one-vs-many evaluations) | `#### Controls > Designing a Control` |
| Creating a policy template (key syntax + readability examples) | `#### Controls > Creating a Policy Template` |
| Naming a control (do not name after vendors) | `#### Controls > Naming a Control` |
| Choosing event sources (Plugin / API / Control) | `#### Controls > Choosing Sources` |
| Control scope (repository / module / artifact / release / abstract) | `#### Controls > Control Scope` |
| Policy layering semantics + override operator | `##### Policy Layering` |
| Policy variations and the AND/OR resolution | `##### Policy Variations` |
| Gates, integrations (vendors/platforms/instances/tools/plugins), deployments | `### Enforcement`, `### Integration`, `### Deployments` |

## How other skills cite this skill

When another skill needs a fact from FIANU.md, the convention is:

```
See `using-fianu-best-practices` → FIANU.md §<Section Title>.
```

Do not re-state the fact in the consuming skill. Single canonical home.
```

- [ ] **Step 3: Verify validate-skills still passes**

```bash
scripts/validate-skills.sh; echo "exit=$?"
```

Expected: `validate-skills: OK / exit=0`.

- [ ] **Step 4: Commit**

```bash
git add skills/using-fianu-best-practices/ FIANU.md 2>/dev/null || true
git add -A
git commit -m "feat(skills): write using-fianu-best-practices as topical navigator over FIANU.md"
```

---

### Task 1.2: Write `using-fianu-skills` bootstrap

**Files:**
- Modify: `skills/using-fianu-skills/SKILL.md`
- Create: `skills/using-fianu-skills/references/api-conventions.md`
- Create: `skills/using-fianu-skills/references/codex-tools.md`
- Create: `skills/using-fianu-skills/references/gemini-tools.md`

- [ ] **Step 1: Rewrite `skills/using-fianu-skills/SKILL.md`**

Replace the stub body with:

```markdown
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

Key points (loaded eagerly because they trip up every new agent):

- The `actor` on a ticket activity is set by the auth token, **never** in the
  request body. Posting `{"actor": "..."}` is a bug.
- The agent identity is `bot|fianu-agent` and must be set in the auth token.
- Approvers live in `condition.config.resolved_approvers`, **not** at the top
  level of the condition.
- All OPA Rego rules use v1 syntax (`import rego.v1`, `if` keyword).

## Routing — load the skill that matches the user's intent

| User intent | Load this skill |
|---|---|
| "Analyze this ticket" / fact-only ticket commentary | `analyzing-tickets` |
| "Approve / deny this ticket" / autonomous workflow | `managing-ticket-approvals` |
| "Summarize this finding/violation/attestation" | `summarizing-evidence` |
| "Ingest this compliance framework" / map to controls | `converting-frameworks-to-controls` |
| Reading/writing tickets without a full workflow | `working-with-tickets` |
| Reading/writing controls/policies/gates/exceptions | `working-with-entities` |
| Reading LLM-context-rule pods | `working-with-llm-context-rules` |
| Picking a plugin / discovering evidence schemas | `working-with-evidence-plugins` |
| Comparing two policy versions | `diffing-policies` |
| Producing a confidence score for an autonomous action | `computing-decision-confidence` |
| Writing an OPA Rego rule | `writing-rego-rules` |
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
- **Claude Code:** no mapping needed; tool names are native.
```

- [ ] **Step 2: Write `references/api-conventions.md`**

```markdown
# Fianu API conventions

All Fianu API calls in this plugin share these conventions.

## Base URL

The base URL is configured per environment by the harness and provided to the
agent via the `FIANU_API_BASE` environment variable. Skills MUST read it from
the environment, never hardcode it.

## Authentication

All requests carry a bearer token in the `Authorization` header:

```
Authorization: Bearer <token>
```

The token is provided to the agent at session start. The token's subject
determines the `actor` recorded on any write operation — **the agent does
not set `actor` in the request body.** For agents acting as the platform
agent, the token's subject is `bot|fianu-agent`.

## Common write operations: actor is NOT in the body

When posting a ticket activity:

```http
POST /tickets/:uuid/activities
Authorization: Bearer <token>
Content-Type: application/json

{
  "activityType": "comment",
  "body": "..."
}
```

The server extracts `actor` from the token via `h.User()`. Skills MUST NOT
include `"actor": "..."` in the request body.

## Error response shape

Errors follow:

```json
{ "error": { "code": "NOT_FOUND", "message": "ticket not found" } }
```

Common codes:

- `400 BAD_REQUEST` — schema validation failed
- `401 UNAUTHORIZED` — token missing or expired
- `403 FORBIDDEN` — actor lacks permission
- `404 NOT_FOUND` — referenced entity does not exist
- `409 CONFLICT` — version conflict on entity update
- `422 UNPROCESSABLE_ENTITY` — semantic validation failed (e.g. policy fails template schema)

## Pagination

List endpoints use cursor pagination:

```
GET /tickets?limit=50&cursor=<opaque>
```

Response includes `nextCursor` if more results exist. Skills MUST follow
pagination when iterating (e.g. the `analyzing-tickets` queue loop).
```

- [ ] **Step 3: Write `references/codex-tools.md`**

```markdown
# Codex CLI tool name mapping

Skills in fianu-skills reference Claude Code tool names. Codex CLI uses
the same `Skill` tool (renamed `skill`) for skill invocation, and provides
equivalents for shell and file operations.

| Claude Code | Codex CLI |
|---|---|
| `Skill` | `skill` |
| `Bash` | `shell` |
| `Read` | `read_file` |
| `Edit` | `apply_patch` |
| `Write` | `apply_patch` (new-file mode) |
| `Grep` | `shell` with `rg` |
| `WebFetch` | `web_fetch` |

When a skill says "invoke the X tool," substitute the Codex equivalent.
```

- [ ] **Step 4: Write `references/gemini-tools.md`**

```markdown
# Gemini CLI tool name mapping

Skills in fianu-skills reference Claude Code tool names. Gemini CLI uses
a different surface; here is the mapping.

| Claude Code | Gemini CLI |
|---|---|
| `Skill` | `activate_skill` |
| `Bash` | `run_shell_command` |
| `Read` | `read_file` |
| `Edit` | `replace` |
| `Write` | `write_file` |
| `Grep` | `search_file_content` |
| `WebFetch` | `web_fetch` |

When a skill says "invoke the X tool," substitute the Gemini equivalent.
Skills loaded via `@./skills/.../SKILL.md` from `GEMINI.md` are auto-loaded
at session start (no `activate_skill` call required for those).
```

- [ ] **Step 5: Verify**

```bash
scripts/validate-skills.sh; echo "exit=$?"
```

Expected: `validate-skills: OK / exit=0`.

- [ ] **Step 6: Commit**

```bash
git add skills/using-fianu-skills/
git commit -m "feat(skills): write using-fianu-skills bootstrap + api-conventions + tool mappings"
```

---

### Task 1.3: Phase 1 exit verification

- [ ] **Step 1: Confirm FIANU.md is no longer at the repo root**

```bash
[ ! -f FIANU.md ] && echo "OK: root FIANU.md removed" || echo "FAIL: root FIANU.md still exists"
```

Expected: `OK: root FIANU.md removed`.

- [ ] **Step 2: Confirm `using-fianu-best-practices/references/FIANU.md` exists and is the original 905-line file**

```bash
wc -l skills/using-fianu-best-practices/references/FIANU.md
```

Expected: `905` (matches the line count from the spec).

- [ ] **Step 3: Tag**

```bash
git tag -a phase-1-exit -m "Phase 1 (domain + meta skills) complete"
```

---

# Phase 2 — Platform API skills

Goal: extract canonical API content into four skills. After Phase 2, the Ticket/Condition/Activity data model exists exactly once.

For each skill, the workflow is:
1. Read the named source sections from `entry-points/*.md`.
2. Write a SKILL.md body that includes (a) endpoint reference tables, (b) data model tables, (c) canonical patterns and gotchas, (d) a worked example.
3. Run validate-skills.sh.
4. Commit.

### Task 2.1: `working-with-tickets`

**Source content** (these are the lines you extract from):
- `entry-points/fianu-analysis.md` §2 (Ticket Data Model, lines 27–82)
- `entry-points/fianu-analysis.md` §3 (API Reference, lines 84–119)
- `entry-points/fianu-analysis.md` §7 (Queue Processing, lines 317–333)
- `entry-points/fianu-approval-manager.md` §2 (same data model — confirm it matches; the version in approval-manager is canonical for this task)
- `entry-points/fianu-approval-manager.md` §3 (API Reference, with write-operation details)

**Files:**
- Modify: `skills/working-with-tickets/SKILL.md`

- [ ] **Step 1: Replace the body of `skills/working-with-tickets/SKILL.md`**

The body MUST contain, in this order:

1. `## Overview` — 2 paragraphs explaining when to load this skill.
2. `## Data Model` — three tables: TicketReport, ConditionReport, ActivityReport. Copy the column definitions from `entry-points/fianu-analysis.md` lines 29–82 verbatim into Markdown tables. Include the **bold-text note** "Approvers are inside `config.resolved_approvers`, not a top-level field." (this is the canary string for the validate script).
3. `## API Reference` — Read Operations and Write Operations subsections. Endpoints come from `entry-points/fianu-approval-manager.md` lines 83–117 (canonical because it includes write operations).
4. `## The actor convention` — section that documents the `bot|fianu-agent` actor pattern. MUST include the literal string `bot|fianu-agent` (this is the canary string for the validate script).
5. `## Queue iteration` — extracted from `entry-points/fianu-analysis.md` lines 317–333. Rate limit: max 10 tickets per batch, 2-second pause between tickets.
6. `## Edge Cases` — combine the relevant subsections from both source files (Ticket Already Closed, Multiple Pending Conditions, No Target Entity Found).

Use the frontmatter from Task 0.9 verbatim; do NOT modify it.

- [ ] **Step 2: Verify the canary strings appear in this SKILL.md and nowhere else**

```bash
grep -rln 'config.resolved_approvers' skills/ | tee /tmp/canary1.txt
grep -rln 'bot|fianu-agent' skills/ | tee /tmp/canary2.txt
```

Expected output of each grep (one line each):
```
skills/working-with-tickets/SKILL.md
```

If either canary appears in another skill, delete the duplicate.

- [ ] **Step 3: Re-enable the canary check in validate-skills.sh if it was disabled in Task 0.9, and run**

```bash
scripts/validate-skills.sh; echo "exit=$?"
```

Expected: `validate-skills: OK / exit=0`.

- [ ] **Step 4: Commit**

```bash
git add skills/working-with-tickets/SKILL.md scripts/validate-skills.sh
git commit -m "feat(skills): extract canonical ticket data model + API into working-with-tickets"
```

---

### Task 2.2: `working-with-entities`

**Source content:**
- `entry-points/fianu-analysis.md` §4 Step 2 (entity-type branching, lines 130–143)
- `entry-points/fianu-analysis.md` §4 Step 3 (change history, lines 144–151)
- `entry-points/fianu-framework-to-rule-converter.md` §8 Step 7 (POST /create/control + draft+ticket flow, lines 322–336)
- `skills/using-fianu-best-practices/references/FIANU.md` "Compliance" section (for entity-type reference)

**Files:**
- Modify: `skills/working-with-entities/SKILL.md`

- [ ] **Step 1: Replace body with:**

1. `## Overview` — when to load (any time an agent reads or writes control/policy/exception/gate state).
2. `## Entity types` — table listing the four types with: parent entity, lifecycle states (draft/active/published), version semantics. Cross-reference: "See `using-fianu-best-practices` → FIANU.md §Controls / §Policies & Exceptions / §Gates for design rules."
3. `## Read endpoints` — the table from `fianu-analysis.md` §4 Step 2.

   ```
   GET /controls/:entity_key
   GET /policies/:entity_key
   GET /exceptions/:entity_key
   GET /gates/:entity_key
   GET /controls/:entity_key/policies/history
   GET /controls/:entity_key/schemas?producer={pluginPath}
   ```
4. `## Write endpoints (drafts + approval tickets)` — extracted from `framework-to-rule-converter.md` §8 Step 7:

   ```
   POST /create/control      → creates draft + opens approval ticket
   POST /create/policy       → creates draft + opens approval ticket
   ```

   Document the draft-then-ticket flow: every create/update goes through an approval ticket. Skills MUST NOT expect the entity to be `published` immediately after a POST.
5. `## Version semantics` — entities are immutable per version; updates produce new versions. Reference the change-history endpoint.
6. `## Edge Cases` — entity 404, version conflict (409), draft not yet approved.

- [ ] **Step 2: Verify**

```bash
scripts/validate-skills.sh; echo "exit=$?"
```

- [ ] **Step 3: Commit**

```bash
git add skills/working-with-entities/SKILL.md
git commit -m "feat(skills): write working-with-entities (controls/policies/exceptions/gates + draft flow)"
```

---

### Task 2.3: `working-with-llm-context-rules`

**Source content:**
- `entry-points/fianu-approval-manager.md` §4 Step 3 (LLM Context Rules, lines 141–151)

**Files:**
- Modify: `skills/working-with-llm-context-rules/SKILL.md`

- [ ] **Step 1: Replace body with:**

1. `## Overview` — when to load (autonomous decision skills only; `analyzing-tickets` MUST NOT load this — see edge case below).
2. `## Endpoints` — MUST include the literal string `GET /pods/entities` (canary):

   ```
   GET /pods/entities/{targetEntityId}?type=llm_context_rule
   GET /pods/entities/{targetEntityId}/llm_context_rule/{key}
   ```
3. `## The parent walk` — if the target is a policy or exception, also fetch the parent control's LLM context rule pod. Document the order: target → parent.
4. `## The 0.70 cap` — when no pod exists for either the target or its parent, downstream confidence MUST be capped at 0.70. This rule lives here because the cap is sourced from the absence of a pod.
5. `## Content shape` — pods contain raw markdown in a `content` field. They are entity-owner-authored guidance, not structured rules. Skills MUST treat the content as natural-language guidance, not a formal schema.
6. `## Edge cases` — no pod found, pod fetch fails, ambiguous guidance.

- [ ] **Step 2: Verify canary string is only in this file**

```bash
grep -rln 'GET /pods/entities' skills/
```

Expected: only `skills/working-with-llm-context-rules/SKILL.md`.

- [ ] **Step 3: Verify**

```bash
scripts/validate-skills.sh; echo "exit=$?"
```

- [ ] **Step 4: Commit**

```bash
git add skills/working-with-llm-context-rules/SKILL.md
git commit -m "feat(skills): write working-with-llm-context-rules (pod fetch + parent walk + 0.70 cap)"
```

---

### Task 2.4: `working-with-evidence-plugins`

**Source content:**
- `entry-points/fianu-framework-to-rule-converter.md` §5 (Plugin Catalog, lines 137–167)

**Files:**
- Modify: `skills/working-with-evidence-plugins/SKILL.md`
- Create: `skills/working-with-evidence-plugins/references/plugin-catalog.md`

- [ ] **Step 1: Move the plugin catalog table into `references/plugin-catalog.md`**

Create `skills/working-with-evidence-plugins/references/plugin-catalog.md` containing the table from `framework-to-rule-converter.md` lines 143–157 verbatim (Categories and Capabilities). Prepend a one-line header:

```markdown
# Plugin catalog

The categories below map evidence-providing plugins to the controls they
can satisfy. Maintained alongside `../../fianu-plugins` in the core monorepo;
update when new plugins ship.
```

- [ ] **Step 2: Replace body of `SKILL.md` with:**

1. `## Overview` — when to load (picking a plugin to source evidence; discovering its schema).
2. `## Schema discovery` — endpoint:

   ```
   GET /controls/:entity_key/schemas?producer={pluginPath}
   ```

   Returns field paths and types available in the plugin's evidence output. Used to write Rego rules that reference `input.detail.<path>`.
3. `## Selecting a plugin` — short decision procedure: match requirement keywords against the plugin catalog in `references/plugin-catalog.md`; if multiple candidates, prefer the plugin whose schema fields best cover the requirement (i.e., fewest gaps).
4. `## See also` — link to `references/plugin-catalog.md` for the full table.

- [ ] **Step 3: Verify**

```bash
scripts/validate-skills.sh; echo "exit=$?"
```

- [ ] **Step 4: Commit**

```bash
git add skills/working-with-evidence-plugins/
git commit -m "feat(skills): write working-with-evidence-plugins + plugin-catalog reference"
```

---

### Task 2.5: Phase 2 exit verification

- [ ] **Step 1: Confirm no entry-point file contains the canonical strings anymore**

```bash
grep -l 'config.resolved_approvers' entry-points/*.md
grep -l 'GET /pods/entities' entry-points/*.md
```

Expected: both grep commands return non-zero (the strings still exist in entry-points/ because we have NOT deleted those files yet — Phase 5 does that). This is fine; the canary check only enforces canonical home within `skills/`, not yet within `entry-points/`. Phase 4 rewrites the entry-points; Phase 5 deletes them.

- [ ] **Step 2: Confirm validate-skills passes**

```bash
scripts/validate-skills.sh; echo "exit=$?"
```

Expected: `validate-skills: OK / exit=0`.

- [ ] **Step 3: Tag**

```bash
git tag -a phase-2-exit -m "Phase 2 (platform API skills) complete"
```

---

# Phase 3 — Logic primitives

Goal: extract seven reusable algorithms into their own skills. Each replaces "the X methodology" cross-references that today exist as broken `Loads: fianu-policies.md` declarations.

### Task 3.1: `diffing-policies`

**Source content:**
- `entry-points/fianu-analysis.md` §4 Step 4 (Diff Analysis, lines 152–158)
- `entry-points/fianu-approval-manager.md` §5 (Diff Analysis, lines 161–166)
- `skills/using-fianu-best-practices/references/FIANU.md` "Policy Layering" section (override operator semantics)

**Files:**
- Modify: `skills/diffing-policies/SKILL.md`

- [ ] **Step 1: Replace body with:**

1. `## Overview` — what a policy diff means in Fianu (compare two versions of a policy or exception; classify each change).
2. `## Methodology` — three steps:
   - Compare current vs. proposed values at each key path.
   - Classify each change: `threshold_relaxed`, `threshold_tightened`, `key_added`, `key_removed`, `value_changed_neutral`.
   - Compute aggregate direction: `net_relaxation` / `net_tightening` / `neutral`.
3. `## Output format` — a structured object the consumer can iterate over (see Section 5 of `fianu-analysis.md` for the field-level diff table format).
4. `## Worked example` — show before/after policies and the resulting classified diff, drawn from FIANU.md's Code Coverage example.
5. `## See also` — link to `using-fianu-best-practices` → FIANU.md §Policy Layering for the override operator.

- [ ] **Step 2: Verify and commit**

```bash
scripts/validate-skills.sh
git add skills/diffing-policies/SKILL.md
git commit -m "feat(skills): extract diffing-policies methodology"
```

---

### Task 3.2: `computing-decision-confidence`

**Source content:**
- `entry-points/fianu-approval-manager.md` §7 (Confidence Gate, lines 191–206)
- `entry-points/fianu-approval-manager.md` §1 (overall framing, lines 11–21)
- Cross-skill rule: load this only with `working-with-llm-context-rules`

**Files:**
- Modify: `skills/computing-decision-confidence/SKILL.md`

- [ ] **Step 1: Replace body with:**

1. `## Overview` — produces a confidence score for an autonomous action on a Fianu ticket.
2. `## The gate table` — the action thresholds:

   | Confidence | Action |
   |---|---|
   | `≥ 0.90` | Submit approval/denial activity on the appropriate condition. |
   | `0.75 – 0.89` | Submit approval/denial + post notification. |
   | `0.50 – 0.74` | Post comment with analysis only (human decides). |
   | `< 0.50` | Post comment flagging for human review. |
3. `## The 0.70 cap` — when no LLM context rule pod exists for the target entity or its parent, the maximum confidence is 0.70 (advisory-only mode). Cross-reference to `working-with-llm-context-rules`.
4. `## Ambiguity rule` — if the LLM context rule guidance is ambiguous or analysis produces mixed signals, default to advisory comment (do not take autonomous action). Be transparent about the ambiguity in the comment.
5. `## Inputs to consider when no guidance covers the scenario`:
   - Risk direction (relaxing = higher scrutiny)
   - Blast radius (all assets = higher scrutiny)
   - Exception duration (long = higher scrutiny)
   - Control criticality (SOX/compliance-critical = higher scrutiny)
6. `## See also` — `working-with-llm-context-rules`, `analyzing-tickets` (which deliberately does NOT use confidence), `managing-ticket-approvals`.

- [ ] **Step 2: Verify and commit**

```bash
scripts/validate-skills.sh
git add skills/computing-decision-confidence/SKILL.md
git commit -m "feat(skills): extract computing-decision-confidence (gate thresholds + caps)"
```

---

### Task 3.3: `writing-rego-rules`

**Source content:**
- `entry-points/fianu-framework-to-rule-converter.md` §6 (New Control Design, lines 169–222)
- `skills/using-fianu-best-practices/references/FIANU.md` Container Scan example (lines 302–335)
- `skills/using-fianu-best-practices/references/FIANU.md` Code Quality example (lines 339–360)

**Files:**
- Modify: `skills/writing-rego-rules/SKILL.md`
- Create: `skills/writing-rego-rules/references/patterns.md`

- [ ] **Step 1: Write `references/patterns.md`** — five canonical patterns

```markdown
# OPA v1 Rego patterns for Fianu controls

All Fianu Rego rules use OPA v1 syntax. Always begin with:

```rego
package rule
import rego.v1
```

`input.detail.*` paths are the evidence shape (provided by the subscribed
plugin). `data.*` paths are the policy values.

## Threshold check (count vs maximum)

Use when policy declares a maximum count of something in evidence.

```rego
pass if {
    policy := data.vulnerabilities
    vulns := input.detail.vulnerabilities
    critical := count([v | v := vulns[_]; v.rating == "CRITICAL"])
    critical <= policy.critical.maximum
}
```

## Score comparison (>= minimum / <= maximum)

Use when policy declares a minimum score.

```rego
pass if {
    policy := data.scores
    input.detail.measures.reliability >= policy.reliability.minimum
    input.detail.measures.maintainability >= policy.maintainability.minimum
}
```

## Presence check (must exist)

Use for "the artifact must have an SBOM" controls.

```rego
pass if {
    input.detail.sbom != null
    count(input.detail.sbom.components) > 0
}
```

## Freshness check (must be recent)

Use for controls requiring evidence within a time window.

```rego
pass if {
    policy := data.freshness
    age_seconds := time.now_ns()/1e9 - input.detail.generated_at_unix
    age_seconds <= policy.maximum_age_seconds
}
```

## Multi-metric (all sub-checks must pass)

Use when one control evaluates multiple measurements.

```rego
pass if {
    every check in checks {
        check
    }
}

checks contains result if {
    policy := data.vulnerabilities
    vulns := input.detail.vulnerabilities
    counts := {sev: count([v | v := vulns[_]; v.rating == sev]) |
               sev := {"CRITICAL", "HIGH", "MEDIUM", "LOW"}[_]}
    counts.CRITICAL <= policy.critical.maximum
    result := true
}
```
```

- [ ] **Step 2: Replace body of `SKILL.md` with:**

1. `## Overview` — when to load (authoring a Rego rule for a new control).
2. `## v1 syntax requirement` — MUST include the literal string `import rego.v1` (canary). Every rule begins:

   ```rego
   package rule
   import rego.v1
   ```

   Use `if` keyword for every rule body. Avoid v0 syntax.
3. `## input ↔ data mapping` — `input.detail.*` is evidence (from the subscribed plugin's note shape); `data.*` is policy values.
4. `## Patterns` — short list of the five patterns with a one-line description each; link to `references/patterns.md` for full code.
5. `## See also` — `designing-policy-templates` (must match `data.*` paths in the rule).

- [ ] **Step 3: Verify canary appears only here**

```bash
grep -rln 'import rego.v1' skills/ | grep -v references
```

Expected: only `skills/writing-rego-rules/SKILL.md`. (The patterns.md file is allowed to contain it because canary check only matches SKILL.md.)

- [ ] **Step 4: Verify and commit**

```bash
scripts/validate-skills.sh
git add skills/writing-rego-rules/
git commit -m "feat(skills): write writing-rego-rules + patterns reference"
```

---

### Task 3.4: `designing-policy-templates`

**Source content:**
- `skills/using-fianu-best-practices/references/FIANU.md` "Creating a Policy Template" section (lines 364–418)

**Files:**
- Modify: `skills/designing-policy-templates/SKILL.md`

- [ ] **Step 1: Replace body with:**

1. `## Overview` — when to load (designing a new policy YAML template alongside a new control).
2. `## Key syntax rules` (extract verbatim from FIANU.md lines 373–379):
   - Cannot start with a number
   - Alphanumeric characters only
   - Case-sensitive
   - No spaces or special characters, except `_`
   - Words separated with underscore (e.g. `vulnerability_count`)
3. `## Readability conventions` — extracted from FIANU.md lines 381–417. Three worked examples (most-friendly → least-friendly).
4. `## Schema alignment with Rego` — every key in the template MUST correspond to a `data.<path>` reference in the control's Rego rule. Mismatches silently fail at evaluation time. Cross-reference `writing-rego-rules`.
5. `## See also` — `writing-rego-rules`, `using-fianu-best-practices` → FIANU.md §Controls.

- [ ] **Step 2: Verify and commit**

```bash
scripts/validate-skills.sh
git add skills/designing-policy-templates/SKILL.md
git commit -m "feat(skills): extract designing-policy-templates (key syntax + readability + Rego alignment)"
```

---

### Task 3.5: `placing-entities-in-hierarchy`

**Source content:**
- `entry-points/fianu-framework-to-rule-converter.md` §7 (Hierarchy Placement, lines 225–256)
- `skills/using-fianu-best-practices/references/FIANU.md` "Domains" and "Collections" sections

**Files:**
- Modify: `skills/placing-entities-in-hierarchy/SKILL.md`

- [ ] **Step 1: Replace body with:**

1. `## Overview` — when to load (placing a new control under a domain/collection).
2. `## Domain selection` — table from `framework-to-rule-converter.md` lines 230–238 (NIST → "NIST Compliance", SOC2 → "SOC2 Compliance", SOX → "SOX Compliance", GDPR → "Data Privacy", ISO 27001 → "ISO 27001", custom → framework name or "Internal Standards"). Cross-reference `using-fianu-best-practices` → FIANU.md §Domains for sizing guidance (3-6 for large enterprises, 1-3 for small).
3. `## Collection selection` — table from `framework-to-rule-converter.md` lines 244–254 (vulnerability/scan → Security, code quality → Quality Assurance, etc.). Prefer existing collections.
4. `## Cross-domain controls` — note the corner case from FIANU.md §Collections: one control can belong to collections in two different domains (e.g. Code Review in both "Application Compliance" and "IaC Compliance"). Do not duplicate the control.
5. `## See also` — `using-fianu-best-practices` → FIANU.md §Domains, §Collections.

- [ ] **Step 2: Verify and commit**

```bash
scripts/validate-skills.sh
git add skills/placing-entities-in-hierarchy/SKILL.md
git commit -m "feat(skills): extract placing-entities-in-hierarchy (domain/collection selection)"
```

---

### Task 3.6: `matching-existing-controls`

**Source content:**
- `entry-points/fianu-framework-to-rule-converter.md` §4 (Matching to Existing Controls, lines 105–135)

**Files:**
- Modify: `skills/matching-existing-controls/SKILL.md`

- [ ] **Step 1: Replace body with:**

1. `## Overview` — when to load (before creating a new control, check if an existing one satisfies the requirement).
2. `## Search process` — fetch active published controls via `GET /controls?status=active&state=published`. Compare each candidate against the requirement on four axes.
3. `## Scoring weights` (verbatim from lines 120–127):

   | Factor | Weight | Score range |
   |---|---|---|
   | Name similarity | 0.35 | 0.0 – 1.0 |
   | Description overlap | 0.30 | 0.0 – 1.0 |
   | Category alignment | 0.20 | 0.0 – 1.0 |
   | Plugin relevance | 0.15 | 0.0 – 1.0 |
4. `## Thresholds` (verbatim from lines 130–133):
   - `≥ 0.80` — recommend reuse (map requirement to existing control)
   - `0.50 – 0.79` — possible match (flag for human review)
   - `< 0.50` — no match (proceed to new control design)
5. `## See also` — `working-with-entities` (for fetching controls), `converting-frameworks-to-controls` (which orchestrates this).

- [ ] **Step 2: Verify and commit**

```bash
scripts/validate-skills.sh
git add skills/matching-existing-controls/SKILL.md
git commit -m "feat(skills): extract matching-existing-controls (similarity scoring + thresholds)"
```

---

### Task 3.7: `parsing-framework-documents`

**Source content:**
- `entry-points/fianu-framework-to-rule-converter.md` §2 (Framework Document Parsing, lines 22–67)
- `entry-points/fianu-framework-to-rule-converter.md` §3 (Requirement Classification, lines 69–102)

**Files:**
- Modify: `skills/parsing-framework-documents/SKILL.md`

- [ ] **Step 1: Replace body with:**

1. `## Overview` — when to load (ingesting a compliance framework document).
2. `## Input formats` — table from `framework-to-rule-converter.md` lines 28–32 (Excel/CSV/structured text+PDF).
3. `## Expected columns` — table from lines 36–42 (ID / Title / Description / Category / Evidence Type — names may vary).
4. `## Normalized output shape` — JSON shape from lines 49–58.
5. `## Keyword extraction` — short rules from lines 62–66.
6. `## Requirement classification` — table from lines 76–82 (automated-evidence / manual-attestation / hybrid / informational) + signals table from lines 86–95.
7. `## Classification confidence` — thresholds from lines 99–102 (≥0.80 high / 0.50-0.79 medium flag / <0.50 skip).
8. `## Edge cases` — non-standard format, vague requirement, no matching plugin, overlapping requirements (extracted from `framework-to-rule-converter.md` §10).

- [ ] **Step 2: Verify and commit**

```bash
scripts/validate-skills.sh
git add skills/parsing-framework-documents/SKILL.md
git commit -m "feat(skills): extract parsing-framework-documents (formats, columns, classification)"
```

---

### Task 3.8: Phase 3 exit verification

- [ ] **Step 1: Confirm all 7 logic primitives have bodies**

```bash
for s in diffing-policies computing-decision-confidence writing-rego-rules \
         designing-policy-templates placing-entities-in-hierarchy \
         matching-existing-controls parsing-framework-documents; do
    if [ "$(wc -l < skills/$s/SKILL.md)" -lt 20 ]; then
        echo "FAIL: skills/$s/SKILL.md is too short (still a stub)" >&2
    else
        echo "OK: $s"
    fi
done
```

Expected: 7 "OK" lines.

- [ ] **Step 2: Validate**

```bash
scripts/validate-skills.sh; echo "exit=$?"
```

Expected: `validate-skills: OK / exit=0`.

- [ ] **Step 3: Tag**

```bash
git tag -a phase-3-exit -m "Phase 3 (logic primitives) complete"
```

---

# Phase 4 — Orchestrator skills

Goal: rewrite the four entry-point behaviors as thin coordinators that `Loads:` their dependencies and walk through the workflow. Bodies shrink dramatically because most content moved to Phases 2/3.

### Task 4.1: `analyzing-tickets`

**Source content:**
- `entry-points/fianu-analysis.md` (entire file, especially §1 Purpose, §4 Analysis Workflow, §5 Output Format, §6 Presentation Rules)

**Files:**
- Modify: `skills/analyzing-tickets/SKILL.md`
- Create: `skills/analyzing-tickets/references/output-template.md`

- [ ] **Step 1: Write `references/output-template.md`** — lift `fianu-analysis.md` §5 verbatim (the Markdown template starting at line 183 through line 297). Save it under that filename.

- [ ] **Step 2: Replace body of `SKILL.md` with:**

1. `## Loads`:
   - `working-with-tickets`
   - `working-with-entities`
   - `diffing-policies`
   - `using-fianu-best-practices`
2. `## Overview` — fact-only ticket analysis. Posts a structured comment activity. Makes NO decisions, references NO LLM context rules, has NO confidence score, expresses NO opinions.
3. `## Workflow` — six steps (from `fianu-analysis.md` §4):
   1. Fetch ticket context (via `working-with-tickets`).
   2. Fetch target entity (via `working-with-entities`, branching on `targetEntityType`).
   3. Fetch change history for policies (via `working-with-entities`).
   4. Diff analysis for policy/exception changes (via `diffing-policies`).
   5. Fetch attestation history.
   6. Post analysis comment (via `working-with-tickets`).
4. `## Output format` — point at `references/output-template.md`.
5. `## Presentation rules` — verbatim from `fianu-analysis.md` §6 (the 9 non-negotiable rules). MUST include explicit guards:
   - No confidence scores.
   - No references to LLM context rule pods.
   - No opinions, subjective language ("risky", "concerning", "warrants caution").
6. `## Queue processing` — point at `working-with-tickets` §Queue iteration; same rate limits.
7. `## Edge cases` — point at `working-with-tickets` § Edge cases; this skill adds: "New entity (no prior version)" → present configuration as-is without a diff table.

- [ ] **Step 3: Verify and commit**

```bash
scripts/validate-skills.sh
git add skills/analyzing-tickets/
git commit -m "feat(skills): rewrite analyzing-tickets as orchestrator over working-with-tickets/entities/diffing"
```

---

### Task 4.2: `managing-ticket-approvals`

**Source content:**
- `entry-points/fianu-approval-manager.md` (entire file)

**Files:**
- Modify: `skills/managing-ticket-approvals/SKILL.md`
- Create: `skills/managing-ticket-approvals/references/output-template.md`

- [ ] **Step 1: Write `references/output-template.md`** — lift `fianu-approval-manager.md` §5 verbatim (activity comment template lines 213–270).

- [ ] **Step 2: Replace body of `SKILL.md` with:**

1. `## Loads`:
   - `working-with-tickets`
   - `working-with-entities`
   - `working-with-llm-context-rules`
   - `diffing-policies`
   - `computing-decision-confidence`
   - `using-fianu-best-practices`
2. `## Overview` — autonomous approve/deny of workflow tickets. Confidence-gated. Every action posts a full reasoning comment. Auditable.
3. `## Workflow` — eight steps (from `fianu-approval-manager.md` §4):
   1. Fetch ticket context (`working-with-tickets`).
   2. Fetch target entity (`working-with-entities`).
   3. Fetch LLM context rules (`working-with-llm-context-rules`); cap confidence at 0.70 if none.
   4. Fetch change history (`working-with-entities`).
   5. Diff analysis (`diffing-policies`).
   6. Produce decision (decision + confidence + justification + rules applied + impact summary). Decision logic from `fianu-approval-manager.md` §4 Step 6 (read LLM context rule first; if guidance says deny/escalate/approve, cite the rule).
   7. Apply confidence gate (`computing-decision-confidence`).
   8. Submit activity (always post comment; if confidence ≥ threshold, also post approved/denied activity on the pending condition).
4. `## Activity comment format` — point at `references/output-template.md`.
5. `## Submission rules` — explicit JSON bodies for approved/denied; reinforce that `actor` is set by auth token (see `working-with-tickets`).
6. `## Edge cases` — ticket already closed, multiple pending conditions, conflicting signals (default to advisory), no target entity.

- [ ] **Step 3: Verify and commit**

```bash
scripts/validate-skills.sh
git add skills/managing-ticket-approvals/
git commit -m "feat(skills): rewrite managing-ticket-approvals as orchestrator over confidence-gated workflow"
```

---

### Task 4.3: `converting-frameworks-to-controls`

**Source content:**
- `entry-points/fianu-framework-to-rule-converter.md` §1 (Overview), §8 (Batch Processing Workflow), §9 (Quality Checks)

**Files:**
- Modify: `skills/converting-frameworks-to-controls/SKILL.md`
- Create: `skills/converting-frameworks-to-controls/references/report-template.md`

- [ ] **Step 1: Write `references/report-template.md`** — lift the Mapping Report markdown template from `framework-to-rule-converter.md` §8 Step 5 (lines 285–317) verbatim.

- [ ] **Step 2: Replace body of `SKILL.md` with:**

1. `## Loads`:
   - `parsing-framework-documents`
   - `matching-existing-controls`
   - `working-with-evidence-plugins`
   - `writing-rego-rules`
   - `designing-policy-templates`
   - `placing-entities-in-hierarchy`
   - `working-with-entities`
   - `using-fianu-best-practices`
2. `## Overview` — ingests a compliance framework document and produces a mapping report for human review BEFORE creating any drafts. Accuracy over speed.
3. `## Workflow` — seven steps (from `framework-to-rule-converter.md` §8):
   1. Parse document (`parsing-framework-documents`).
   2. Classify all requirements (`parsing-framework-documents`).
   3. Match against existing controls (`matching-existing-controls`).
   4. For each unmatched automated/hybrid requirement with classification confidence ≥ 0.80, design a new control: pick a plugin (`working-with-evidence-plugins`), generate the Rego rule (`writing-rego-rules`), generate the policy template (`designing-policy-templates`), pick a scope (`using-fianu-best-practices`), place it under a domain/collection (`placing-entities-in-hierarchy`).
   5. Generate mapping report (`references/report-template.md`).
   6. Human review — STOP. Do not proceed until a human approves the report.
   7. For each approved design, `POST /create/control` and `/create/policy` (via `working-with-entities`) — creates drafts and opens approval tickets. Drafts are NOT published until tickets are approved.
4. `## Quality checks` — six checks before producing the final report (from `framework-to-rule-converter.md` §9): no duplicate controls, Rego rule validity (v1 syntax), policy template consistency, scope appropriateness, plugin existence, hierarchy validity.
5. `## Edge cases` — non-standard format, vague requirement, no matching plugin, overlapping requirements (from `framework-to-rule-converter.md` §10).

- [ ] **Step 3: Verify and commit**

```bash
scripts/validate-skills.sh
git add skills/converting-frameworks-to-controls/
git commit -m "feat(skills): rewrite converting-frameworks-to-controls as orchestrator"
```

---

### Task 4.4: `summarizing-evidence`

**Source content:**
- `entry-points/fianu-evidence-summarizer.md` (entire 59-line file)

**Files:**
- Modify: `skills/summarizing-evidence/SKILL.md`

- [ ] **Step 1: Lift the entire body of `entry-points/fianu-evidence-summarizer.md`** (from `## Output format` through the end) into `skills/summarizing-evidence/SKILL.md`, preserving the existing frontmatter from Task 0.9.

The body sections (verbatim):
- `## Output format` (the JSON schema)
- `## Summary content rules`
- `## nextSteps rules`
- `## Subject-specific framing`
- `## What never goes in the output`

Add a short `## When to load` section at the top of the body (before `## Output format`) explaining: load when the user is producing a one-shot evidence summary for the Fianu console; this skill is atomic — it does not load other skills.

- [ ] **Step 2: Verify and commit**

```bash
scripts/validate-skills.sh
git add skills/summarizing-evidence/SKILL.md
git commit -m "feat(skills): lift summarizing-evidence body from fianu-evidence-summarizer.md"
```

---

### Task 4.5: Phase 4 exit verification — parity test

The 4 entry-point behaviors must be reproducible via the new skills.

- [ ] **Step 1: Manually walk through each orchestrator skill in this checklist:**

For each of `analyzing-tickets`, `managing-ticket-approvals`, `converting-frameworks-to-controls`, `summarizing-evidence`:

1. Open `skills/<orchestrator>/SKILL.md`.
2. Open the corresponding `entry-points/<file>.md`.
3. Confirm every numbered workflow step in the entry-point has a corresponding bullet in the orchestrator's `## Workflow` section.
4. Confirm every "Edge case" subsection in the entry-point is either covered by the orchestrator's `## Edge cases` or delegated explicitly to a skill the orchestrator loads.
5. Confirm any output templates from the entry-point are present in the orchestrator's `references/`.

- [ ] **Step 2: Validate**

```bash
scripts/validate-skills.sh; echo "exit=$?"
```

- [ ] **Step 3: Tag**

```bash
git tag -a phase-4-exit -m "Phase 4 (orchestrators) complete; entry-point parity verified"
```

---

# Phase 5 — Cleanup and release

Goal: delete the old `entry-points/` directory, rewrite `CLAUDE.md`, finish `docs/`, tag v0.1.0, push to GitHub.

### Task 5.1: Delete the old entry-points directory

**Files:**
- Delete: `entry-points/fianu-analysis.md`
- Delete: `entry-points/fianu-approval-manager.md`
- Delete: `entry-points/fianu-evidence-summarizer.md`
- Delete: `entry-points/fianu-framework-to-rule-converter.md`
- Delete: `entry-points/` (directory)

- [ ] **Step 1: Confirm the orchestrator skills are complete before deleting source**

```bash
for s in analyzing-tickets managing-ticket-approvals converting-frameworks-to-controls summarizing-evidence; do
    body_lines=$(wc -l < skills/$s/SKILL.md)
    echo "$s: $body_lines lines"
    if [ "$body_lines" -lt 20 ]; then
        echo "ABORT: skills/$s/SKILL.md still looks like a stub" >&2
        exit 1
    fi
done
```

Expected: 4 lines reporting reasonable line counts (>20).

- [ ] **Step 2: Delete the entry-points directory**

```bash
git rm -r entry-points/
```

- [ ] **Step 3: Commit**

```bash
git commit -m "chore: delete entry-points/ now that content has migrated into skills/

All four entry-point behaviors are reproducible via the new orchestrator
skills under skills/. See Phase 4 of the restructure plan for the mapping."
```

---

### Task 5.2: Rewrite root CLAUDE.md to match the new structure

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Read the current `CLAUDE.md`**

It references `entry-points/`, the `Loads: fianu-shared.md` declarations, and the four entry-point files — all stale after Phase 5 Task 5.1.

- [ ] **Step 2: Replace its body with the structure below**

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`fianu-skills` is a multi-harness skill plugin distributed to customers building AI agents on the Fianu compliance platform. It ships skills for Claude Code, Codex CLI, and Gemini CLI. There is no application code — everything here is markdown skill files, JSON manifests, and shell scripts.

## Repo layout

- `skills/` — the canonical skill library (17 skills, 4 groups). See `docs/architecture.md` for the full inventory.
- `.claude-plugin/` / `.codex-plugin/` / `gemini-extension.json` — per-harness plugin manifests.
- `hooks/` — Claude Code SessionStart hook that bootstraps `using-fianu-skills`.
- `scripts/` — `bump-version.sh` (lockstep version updates) and `validate-skills.sh` (frontmatter + canary-string lint).
- `docs/architecture.md` and `docs/authoring-skills.md` — design docs for contributors.
- `docs/superpowers/specs/` and `docs/superpowers/plans/` — the restructure spec and plan that produced this layout.

## Working on skills

**Edit:** Use `Read` on the specific SKILL.md, `Edit` with enough surrounding context to keep `old_string` unique. Preserve the YAML frontmatter exactly — `validate-skills.sh` will reject changes to `name:` or unknown fields.

**Add a new skill:** Create `skills/<kebab-case-name>/SKILL.md` with frontmatter (`name:` matching the directory, `description:` tuned as a load trigger). Optional `references/*.md` for ancillary content. See `docs/authoring-skills.md`.

**Cross-skill dependencies:** Add a `## Loads` section at the top of the consumer skill's SKILL.md listing the skill names it depends on, in invocation order.

**Single canonical home rule:** every fact lives in one SKILL.md. Other skills reference it via `Loads:`. `validate-skills.sh` enforces this with canary strings (`config.resolved_approvers` → `working-with-tickets`, `GET /pods/entities` → `working-with-llm-context-rules`, `import rego.v1` → `writing-rego-rules`, `bot|fianu-agent` → `working-with-tickets`).

## Versioning

`scripts/bump-version.sh <new-version>` is the only supported way to change the plugin version. It updates `package.json`, all four `*-plugin/plugin.json` and `marketplace.json` files, and `gemini-extension.json` in lockstep, and inserts a CHANGELOG.md heading. Editing manifests by hand will drift versions and break `/plugin install`.

## Validation

`scripts/validate-skills.sh` checks frontmatter (name matches directory, description present) and canary-string locations. Run it before every commit; CI runs it on every PR.

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
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: rewrite CLAUDE.md to match post-restructure layout"
```

---

### Task 5.3: Write `docs/architecture.md`

**Files:**
- Modify: `docs/architecture.md`

- [ ] **Step 1: Replace placeholder with:**

```markdown
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
| `working-with-tickets` | Canonical home for the Ticket/Condition/Activity data model, ticket endpoints, the `bot\|fianu-agent` actor pattern, and the `config.resolved_approvers` gotcha. |
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

The bootstrap (`using-fianu-skills`) is loaded by the harness at session start; it routes the agent to the right orchestrator based on user intent.

## Single canonical home rule

Every fact lives in exactly one SKILL.md. Consumers reference via `Loads:`. `scripts/validate-skills.sh` enforces this with canary strings — if `config.resolved_approvers` appears outside `working-with-tickets`, validation fails.
```

- [ ] **Step 2: Commit**

```bash
git add docs/architecture.md
git commit -m "docs: write architecture.md (skill inventory, composition model, canonical home rule)"
```

---

### Task 5.4: Write `docs/authoring-skills.md`

**Files:**
- Modify: `docs/authoring-skills.md`

- [ ] **Step 1: Replace placeholder with:**

```markdown
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

## Body structure

Every SKILL.md body should include:

1. `# <Title Case Name>` — H1 title.
2. `## Loads` (orchestrators only) — list of dependent skill names, one per line under a bullet.
3. `## Overview` — 1–2 paragraphs: when to load, what it does, what it doesn't do.
4. The body content — endpoints, tables, patterns, workflow steps, edge cases. Use headers, tables, and code blocks aggressively. Avoid prose paragraphs longer than 4 lines.
5. `## See also` — cross-references to related skills.

## Single canonical home rule

Every fact lives in exactly one SKILL.md. Other skills that need the fact `Loads:` the owner. The canary list in `scripts/validate-skills.sh` enforces this for the most-duplicated facts.

To add a new canary: edit the `CANARIES` variable in `scripts/validate-skills.sh` with `<canary-string>|<owner-skill-directory>`.

## Adding a new skill

1. Create `skills/<name>/SKILL.md` with frontmatter and an `## Overview` stub.
2. Run `scripts/validate-skills.sh` — confirm it passes.
3. Fill in the body. If you find yourself re-stating a fact that already lives in another skill, stop and add a `## Loads:` reference instead.
4. If the skill needs ancillary content (catalogs, templates, full code listings), add `references/<name>.md` and link to it from the SKILL.md body.
5. Update `docs/architecture.md` to list the new skill.
6. Run `scripts/validate-skills.sh` again, then `scripts/bump-version.sh <next-version>`.

## Description-tuning tips

The description is the load trigger. Bad descriptions cause skills not to load when needed (or to load when not needed).

- **Specific situations beat generic categories.** "Use when posting a comment activity on a ticket" beats "Tickets."
- **Name the concrete things.** "Confidence gate thresholds (0.50 / 0.75 / 0.90)" beats "Confidence scoring."
- **Constraint-mention is a load signal.** "MUST NOT include actor in body" makes the agent more likely to load when it's about to do that wrong.
- **Cite by name what the skill does NOT do.** "No decisions, no confidence scores, no LLM context rules" in `analyzing-tickets` prevents misuse as much as positive triggers.
```

- [ ] **Step 2: Commit**

```bash
git add docs/authoring-skills.md
git commit -m "docs: write authoring-skills.md (frontmatter, body structure, single canonical home rule)"
```

---

### Task 5.5: Final validation, bump CHANGELOG entry, tag v0.1.0

- [ ] **Step 1: Run validation one last time**

```bash
scripts/validate-skills.sh; echo "exit=$?"
```

Expected: `validate-skills: OK / exit=0`.

- [ ] **Step 2: Confirm all manifests still report 0.1.0**

```bash
grep -H '"version"' package.json .claude-plugin/plugin.json .claude-plugin/marketplace.json .codex-plugin/plugin.json gemini-extension.json
```

Expected: every line shows `"version": "0.1.0"`.

- [ ] **Step 3: Update CHANGELOG.md to replace `TBD` with today's date**

Edit `CHANGELOG.md`: change the line `## [0.1.0] — TBD` to `## [0.1.0] — <today's date in YYYY-MM-DD>`.

- [ ] **Step 4: Commit and tag**

```bash
git add CHANGELOG.md
git commit -m "release: stamp v0.1.0 in CHANGELOG"
git tag -a v0.1.0 -m "fianu-skills v0.1.0 — initial multi-harness plugin release"
```

---

### Task 5.6: Push to GitHub and verify install

- [ ] **Step 1: Create the GitHub repo (if it does not already exist)**

```bash
gh repo create fianulabs/fianu-skills --public \
    --description "Skills for building AI agents that operate on the Fianu compliance platform." \
    --source=. --remote=origin
```

Expected: prints the URL of the new repo.

If the repo already exists, instead:
```bash
git remote add origin https://github.com/fianulabs/fianu-skills.git
```

- [ ] **Step 2: Push main and tags**

```bash
git push -u origin main
git push origin --tags
```

Expected: push succeeds, including the v0.1.0 tag and all phase-N-exit tags.

- [ ] **Step 3: Install verification (Claude Code)**

In a clean Claude Code session on a separate machine or directory:

```
/plugin marketplace add fianulabs/fianu-skills
/plugin install fianu-skills@fianu-skills
```

Expected:
- Marketplace add succeeds.
- Install succeeds; `/plugin` shows fianu-skills as installed at v0.1.0.
- Starting a new conversation triggers the SessionStart hook; the system-reminder text from `hooks/session-start` appears in the conversation.
- Calling `Skill` with `fianu-skills:using-fianu-skills` loads the bootstrap skill body successfully.

- [ ] **Step 4: Install verification (Gemini CLI)**

```bash
gemini extensions install https://github.com/fianulabs/fianu-skills
gemini extensions list
```

Expected: extension is listed at v0.1.0.

- [ ] **Step 5: Install verification (Codex CLI)**

In Codex CLI, run `/plugins`, search for `fianu-skills`. Confirm it's listed and installable.

- [ ] **Step 6: Parity smoke test against staging Fianu API**

For each orchestrator, run a smoke test against staging:

1. `analyzing-tickets` — invoke against a known open ticket on staging; confirm it posts a fact-only comment in the expected format.
2. `managing-ticket-approvals` — invoke against a synthetic test ticket that has an LLM context rule pod; confirm it produces a decision + confidence and either submits or stays advisory per the gate.
3. `converting-frameworks-to-controls` — invoke against a small CSV (5–10 rows); confirm it produces a mapping report and DOES NOT create any drafts without explicit human approval.
4. `summarizing-evidence` — invoke with a sample finding; confirm valid JSON output with no markdown fences.

If any smoke test fails, **do not proceed** — file an issue against the affected skill and fix in a follow-up commit/version bump.

- [ ] **Step 7: Mark release complete**

```bash
echo "fianu-skills v0.1.0 released and verified."
```

---

# Self-review

(For the author: looked at the spec with fresh eyes.)

**Spec coverage check:** every section of the spec maps to a phase in this plan.
- Spec §3 (plugin identity) → Phase 0 manifests (Tasks 0.2–0.5).
- Spec §4 (repo layout) → Phase 0 in full.
- Spec §5 (skill inventory, all 17 skills) → Phases 1/2/3/4 each cover their group.
- Spec §6 (multi-harness manifests) → Phase 0 Tasks 0.3–0.5 + 0.7.
- Spec §7 (migration plan, 5 phases) → exactly the 5 phases of this plan.
- Spec §8 (risks/mitigations) → canary-check script (Task 0.8) addresses content drift; lockstep script (Task 0.7) addresses version drift; Phase 5 explicitly rewrites CLAUDE.md.
- Spec §9 (out of scope) → confirmed no Cursor/OpenCode/Factory Droid/Copilot manifests, no tests/, no Terraform-provider skills.

**Placeholder scan:** no "TBD", no "TODO", no "implement later" in the plan body. Every task names exact files, exact JSON, exact commands. Where SKILL.md body content is described structurally (Phase 2/3/4), the source lines in the existing `entry-points/*.md` files are cited so an implementer can extract precisely.

**Type/name consistency:** skill names are stable across all phases (`working-with-tickets`, `using-fianu-best-practices`, etc.). The `Loads:` declarations in Phase 4 orchestrators reference the exact directory names created in Phase 0 Task 0.9. Canary strings in Task 0.8 match the canonical-home assignments in Phase 2 Tasks 2.1, 2.3 and Phase 3 Task 3.3.
