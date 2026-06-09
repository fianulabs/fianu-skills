# `managing-ticket-approvals` output template

Posted to the ticket via `POST /tickets/:uuid/activities`.

## Analysis comment (always posted, regardless of confidence)

```markdown
## Agent Analysis

**Decision:** {Approve | Deny | Escalate | Advisory}
**Confidence:** {0.XX}

### Change Summary
{What changed — for policy tickets, the specific values that were modified}

### Reasoning
{2–5 sentences explaining the decision, citing specific LLM context rules and FIANU.md best practices}

### LLM Context Rules Applied
{List each rule from the entity's llm_context_rule pod that was relevant}
- "{quoted rule text}" -> {how it influenced the decision}

### Impact Assessment
- **Affected scope**: {asset type and index, or "all assets"}
- **Risk direction**: {Relaxing (higher risk) | Tightening (lower risk) | Neutral}
- **Control criticality**: {Critical | Standard | Non-critical}

---
*Fianu Agent v1.0 | Confidence: {0.XX}*
```

## Approval activity (when confidence triggers autonomous action)

Posted IN ADDITION to the analysis comment, never instead of it. `actor`
is set by the auth token — never in body.

```json
{
  "activityType": "approved",
  "conditionId": "<pending condition UUID>",
  "body": "Auto-approved by Fianu Agent (confidence: 0.94). See analysis comment above.",
  "metadata": {
    "agent_version": "1.0",
    "confidence": 0.94,
    "decision": "approve",
    "autonomous": true
  }
}
```

## Denial activity

```json
{
  "activityType": "denied",
  "conditionId": "<pending condition UUID>",
  "body": "Denied by Fianu Agent. See analysis comment above.",
  "metadata": {
    "agent_version": "1.0",
    "confidence": 0.91,
    "decision": "deny",
    "autonomous": true
  }
}
```
