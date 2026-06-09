---
name: placing-entities-in-hierarchy
description: Use when deciding which domain and collection a new control or policy belongs to. Maps framework/category keywords to recommended domains (NIST/SOC2/SOX/GDPR/ISO 27001) and collections (Security/QA/Access Control/Change Management/Data Protection/Observability/Infrastructure/Governance).
---

# Placing Entities in Hierarchy

## Overview

When creating a new control, an agent must place it under a domain and
one or more collections (see `using-fianu-best-practices` →
FIANU.md §Compliance for the Domain → Collection → Control hierarchy).

This skill is the canonical home for the keyword-based recommendation
tables.

## Domain selection

| Framework | Suggested domain |
|---|---|
| NIST 800-53 | "NIST Compliance" |
| SOC 2 | "SOC2 Compliance" |
| SOX | "SOX Compliance" |
| GDPR | "Data Privacy" |
| ISO 27001 | "ISO 27001" |
| Custom / internal | Use the framework name or "Internal Standards" |

If no matching domain exists, recommend creating one. Domain sizing
guidance lives in `using-fianu-best-practices` → FIANU.md §Domains
(large enterprises 3–6 domains, smaller orgs 1–3).

## Collection selection

| Category keywords | Suggested collection |
|---|---|
| vulnerability, scan, security, SAST, SCA, DAST | "Security" |
| code quality, coverage, testing, QA | "Quality Assurance" |
| access, authentication, authorization, identity | "Access Control" |
| change, deployment, release, pipeline | "Change Management" |
| data, encryption, privacy, PII | "Data Protection" |
| logging, monitoring, alerting, incident | "Observability" |
| configuration, infrastructure, IaC | "Infrastructure" |
| documentation, policy, procedure | "Governance" |

Prefer existing collections over creating new ones. One control can
belong to multiple collections.

## Cross-domain controls

A single control can — and often should — belong to collections in two
different domains. Example: a "Code Review" control may be in both an
"Application Compliance" domain (under a Source Code collection) and an
"IaC Compliance" domain (under a Source Code collection). The control
itself exists once; it's referenced from collections in both domains.

Do NOT duplicate the control. Add the control to a second collection in
the other domain.

## Workflow

1. Identify the framework (or "internal") the requirement came from.
2. Map framework → domain. If no match, suggest a new domain and confirm
   with a human.
3. Extract category keywords from the requirement title/description.
4. Map keywords → collection. Prefer existing collections.
5. If the control logically fits in two domains, add it to a collection
   in each. Do not duplicate.

## See also

- `using-fianu-best-practices` → FIANU.md §Domains — domain sizing,
  permissions, best practices.
- `using-fianu-best-practices` → FIANU.md §Collections — collection
  sizing, the same-name-different-domain pattern.
- `matching-existing-controls` — run this first, before recommending a
  new control + placement.
