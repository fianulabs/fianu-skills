---
name: managing-ticket-approvals
description: Use when autonomously approving or denying a Fianu approval ticket. Loads the confidence framework, LLM context rules, diffing, and submits decisions guarded by the confidence gate.
---

# Managing Ticket Approvals

## Loads

- `working-with-tickets`
- `working-with-entities`
- `working-with-attestations`
- `working-with-llm-context-rules`
- `diffing-policies`
- `computing-decision-confidence`
- `using-fianu-best-practices`

## Overview

`managing-ticket-approvals` produces autonomous approve/deny decisions on
Fianu approval tickets, gated by the confidence framework. Every action
posts a full reasoning comment for audit. When confidence is below the
autonomous threshold, the agent posts the comment as advisory only — a
human makes the call.

If the goal is fact-only analysis (no decision), load `analyzing-tickets`
instead.

## Workflow

### 1. Fetch ticket context

Via `working-with-tickets`. If `state == "closed"`, do not act — log
and skip.

### 2. Fetch target entity

Via `working-with-entities`, branching on `targetEntityType`. Same
branching as `analyzing-tickets` step 2.

### 3. Fetch LLM context rules

Via `working-with-llm-context-rules`. Walk the parent chain (policy →
control). If no pod exists for the target or its parent, the confidence
cap of 0.70 applies (see step 7).

### 4. Fetch change history

Via `working-with-entities` (for policies). Used to detect patterns
(repeated relaxations, recent reversals) that feed the decision reasoning.

### 5. Diff analysis

Via `diffing-policies`. The aggregate direction (`net_relaxation` /
`net_tightening` / `neutral`) feeds the decision logic.

### 6. Produce decision

Synthesize the inputs into a structured analysis:

- **Decision**: `approve` | `deny` | `escalate` | `comment`
- **Confidence**: 0.0 – 1.0
- **Justification**: 2–5 sentences
- **Rules applied**: which LLM context rules influenced the decision and how
- **Impact summary**: affected scope, risk direction, control criticality, recent attestation trend (via `working-with-attestations`)

Decision logic:

1. Read the LLM context rule content carefully. It is the entity owner's
   explicit guidance.
2. If the guidance says to **deny** this type of change → deny (cite the
   specific rule).
3. If the guidance says to **escalate** → escalate (cite the rule).
4. If the guidance **approves** this type of change → approve (cite the
   rule).
5. If no guidance covers the scenario, fall back to the inputs in
   `computing-decision-confidence` § Inputs to consider — risk direction,
   blast radius, exception duration, control criticality. Use these to
   produce a raw confidence; never invent a rule.

### 7. Apply the confidence gate

Via `computing-decision-confidence`. Apply the 0.70 cap if no LLM context
rule pod was found in step 3.

| Confidence | Action |
|---|---|
| `≥ 0.90` | Submit approval/denial activity on the appropriate condition. |
| `0.75 – 0.89` | Submit approval/denial + post notification. |
| `0.50 – 0.74` | Post comment with analysis only (human decides). |
| `< 0.50` | Post comment flagging for human review. |

### 8. Submit activity

ALWAYS post the analysis comment (regardless of confidence). See
`references/output-template.md`.

If confidence ≥ threshold for autonomous action, ALSO post an
`approved` / `denied` activity on the appropriate pending condition.
See `working-with-tickets` for the submission contract (especially: the
`actor` is set by the auth token, never the body).

## Activity submission

See `references/output-template.md` for:
- The analysis comment template (Markdown body).
- The approval activity JSON body.
- The denial activity JSON body.

## Edge cases

### Ticket already closed

See `working-with-tickets`. Do not act.

### Multiple pending conditions

A ticket may have multiple pending conditions. Act only on conditions
where the agent's actor identity appears in the condition's resolved
approver list, or where the agent has system-level authorization. See
`working-with-tickets` for the exact lookup path and gotchas.

### Conflicting signals

If the LLM context rule guidance is ambiguous or the analysis produces
mixed signals, default to advisory (comment-only). See
`computing-decision-confidence` § The ambiguity rule. Be transparent
about the ambiguity in the comment and suggest what a human reviewer
should focus on.

### No target entity found

If `working-with-entities` returns 404 for the target, post a comment
noting the issue. Do NOT submit any approve/deny.
