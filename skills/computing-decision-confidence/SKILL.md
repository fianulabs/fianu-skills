---
name: computing-decision-confidence
description: Use when an agent needs to produce a confidence score for an autonomous action on a Fianu ticket. Defines the 0.50 / 0.75 / 0.90 gate thresholds, the LLM-context-rule presence cap (0.70 without one), and the ambiguity-defaults-to-advisory rule.
---

# Computing Decision Confidence

## Overview

This skill defines the confidence framework Fianu agents use to gate
autonomous actions on tickets. Confidence is a scalar in `[0.0, 1.0]`
representing how strongly the agent believes its decision is correct. The
thresholds in `## The gate table` determine what action the agent is
allowed to take at each level.

Load this skill any time an agent is preparing to act autonomously on a
ticket. Fact-only workflows (e.g. `analyzing-tickets`) MUST NOT compute or
display confidence.

## The gate table

| Confidence | Action |
|---|---|
| `≥ 0.90` | Submit approval/denial activity on the appropriate condition. |
| `0.75 – 0.89` | Submit approval/denial + post notification. |
| `0.50 – 0.74` | Post comment with analysis only (human decides). |
| `< 0.50` | Post comment flagging for human review. |

The agent ALWAYS posts a comment with full reasoning, regardless of
threshold. Only the autonomous approve/deny step is gated.

## The 0.70 cap

**When no LLM context rule pod exists for the target entity or its parent,
the maximum confidence is 0.70 — advisory-only mode.**

This precondition is sourced by `working-with-llm-context-rules`. The cap
applies *after* whatever raw confidence the decision logic produces:
`final_confidence = min(raw_confidence, 0.70)` when no pod exists.

## The ambiguity rule

If the LLM context rule guidance is ambiguous, or the agent's analysis
produces mixed signals, default to advisory (comment-only). Do NOT take
autonomous action.

Be transparent about the ambiguity in the comment body — suggest what a
human reviewer should focus on. Examples of ambiguity:

- The pod guidance addresses a similar but not identical scenario.
- Multiple rules apply with conflicting conclusions.
- The diff (`diffing-policies`) shows mixed direction with no clear net.

## Inputs to consider when no guidance covers the scenario

When the LLM context rule does NOT cover the specific situation, the agent
must reason from the change itself. Raise scrutiny (lower confidence) when:

- **Risk direction** — the change is a relaxation (`diffing-policies`
  reports `net_relaxation`).
- **Blast radius** — the policy has no index, so it applies to all assets.
- **Exception duration** — exception expiration is far in the future.
- **Control criticality** — the parent control is tagged SOX-relevant or
  otherwise compliance-critical.

Each scrutiny signal nudges confidence down. The agent does not need a
formal weighted formula — these are intuitions encoded in the comment so
a human can verify.

## Worked example

A policy update relaxes `coverage.overall.minimum` from 0.8 to 0.5.

1. `diffing-policies` reports `net_relaxation`.
2. `working-with-llm-context-rules` returns a pod whose content says
   "Auto-deny any relaxation of `coverage.overall.minimum` below 0.7
   without sign-off from the engineering director."
3. The agent computes a raw confidence of 0.92 for "deny" — the rule is
   explicit and the change clearly violates it.
4. Pod exists, so no 0.70 cap.
5. Gate: 0.92 ≥ 0.90 → autonomous denial.

Submit a denial activity on the pending condition, with a comment quoting
the rule and the diff.

## See also

- `working-with-llm-context-rules` — source of the 0.70 cap precondition.
- `managing-ticket-approvals` — primary consumer.
- `analyzing-tickets` — explicitly does NOT consume this skill.
