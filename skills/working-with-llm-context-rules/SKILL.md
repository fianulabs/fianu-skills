---
name: working-with-llm-context-rules
description: Use when fetching the markdown guidance pods entity owners attach to controls/policies. Includes the parent-walk pattern (policy → control). Without a pod, downstream confidence is capped at 0.70.
---

# Working with LLM Context Rules

## Overview

Entity owners attach "LLM context rule" pods to controls and policies. A
pod is a markdown document containing the owner's explicit decision
guidance — under what conditions an autonomous agent may approve, deny, or
escalate changes to that entity. This skill is the canonical home for the
pod fetch contract and the parent-walk pattern.

**Important:** This skill is loaded ONLY by autonomous decision workflows
(e.g. `managing-ticket-approvals`). Fact-only workflows like
`analyzing-tickets` MUST NOT load this skill — referencing LLM context
rules during fact-only analysis violates that skill's contract.

## Endpoints

```
GET /pods/entities/{targetEntityId}?type=llm_context_rule    # List all LLM rules for entity
GET /pods/entities/{targetEntityId}/llm_context_rule/{key}   # Get specific rule by key
```

The list endpoint returns metadata for all `llm_context_rule` pods attached
to the entity. The single-key endpoint returns the full pod including its
markdown `content` field.

## The parent walk

If the target entity is a `policy` or `policy_exception`, also fetch the
parent control's LLM context rule pod. Guidance can exist at either level:
the policy's pod takes precedence for policy-specific rules; the control's
pod provides general guidance that applies to all policies under it.

Order:

1. Fetch pods for the target entity.
2. If the target is a `policy` or `policy_exception`, also fetch pods for
   the parent control (via `working-with-entities`).
3. Aggregate: when both exist, prefer policy-level for policy-specific
   decisions; consult control-level for broader guidance.

If neither the target nor its parent has a pod, the agent operates without
explicit owner guidance.

## The 0.70 confidence cap

**When no LLM context rule pod exists for either the target entity or its
parent, the maximum decision confidence is 0.70 — advisory-only mode.**

This cap is sourced from the absence of explicit owner guidance: without
guidance, the agent cannot confidently take autonomous action and must
fall back to posting a comment for human review. The cap is enforced by
`computing-decision-confidence`; this skill is the source of the
precondition that triggers the cap.

## Content shape

Pods contain a `content` field holding raw markdown. The content is
entity-owner-authored, free-form natural language. Skills MUST treat the
content as guidance, not a formal schema — do not attempt to parse it as
structured rules.

Typical content patterns:

- "Approve relaxations of `coverage.new.minimum` below 0.5 only with sign-off from the SRE on-call."
- "Auto-deny any policy that removes the `internet_facing` index."
- "Escalate to legal if the eased values change `data.encryption.at_rest`."

## Edge cases

### No pod found

Cap confidence at 0.70 (see above) and note "operating in advisory-only
mode" in the decision comment.

### Pod fetch fails (5xx)

Treat as "no pod found" for confidence purposes, but log the failure
distinctly so a human reviewer can investigate whether the pod was supposed
to exist.

### Ambiguous guidance

If the pod content covers a scenario but the guidance is ambiguous,
default to advisory (comment-only) and quote the relevant pod text in the
comment so a human can interpret.
