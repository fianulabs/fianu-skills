# Fianu Framework-to-Rule Converter

Entry-point skill for ingesting compliance framework documents and autonomously mapping requirements to Fianu controls.

**Loads**: `fianu-shared.md`, `fianu-controls.md`, `fianu-policies.md`

---

## 1. Overview

This skill receives a compliance framework document (Excel, CSV, or structured text) and:
1. Parses each requirement into a structured format
2. Classifies each requirement by automation feasibility
3. Searches for existing Fianu controls that already satisfy the requirement
4. For unmatched requirements, designs new controls with Rego rules, policy templates, and hierarchy placement
5. Produces a mapping report for human review
6. Creates approved controls as drafts (opening approval tickets)

**Accuracy over speed**: Every mapping includes a confidence score. Low-confidence mappings are flagged for human review, not auto-created.

---

## 2. Framework Document Parsing

### Expected Input Formats

| Format | Parsing Approach |
|--------|-----------------|
| Excel (.xlsx) | Read rows from the primary sheet. Headers in row 1. |
| CSV | Standard CSV parsing with header row. |
| Structured text/PDF | Extract table-like structures. May require LLM-assisted extraction. |

### Expected Columns

The agent should identify these columns (names may vary by framework):

| Semantic | Common Column Names |
|----------|-------------------|
| **ID** | ID, Reference, Control ID, Ref #, Number |
| **Title** | Title, Name, Control Name, Requirement |
| **Description** | Description, Details, Full Text, Guidance |
| **Category** | Category, Domain, Family, Section, Group |
| **Evidence Type** | Evidence, Verification, Assessment, Test Method |

### Normalized Output

Each row becomes:
```json
{
  "id": "CC-7.1",
  "title": "Change Management Controls",
  "description": "The organization manages changes to infrastructure and software...",
  "category": "Change Management",
  "keywords": ["change", "infrastructure", "software", "approval", "testing"],
  "source": "SOC2-CC7",
  "rawRow": { ... }
}
```

### Keyword Extraction

Extract keywords from title and description for matching:
- Remove stop words (the, a, an, is, are, etc.)
- Extract technical terms (vulnerability, coverage, scan, SBOM, etc.)
- Extract compliance domain terms (access control, change management, etc.)

---

## 3. Requirement Classification

For each requirement, classify automation feasibility.

### Classification Categories

| Category | Description | Action |
|----------|-------------|--------|
| **Automated-evidence** | Can be fully evaluated by a plugin + Rego rule | Design control |
| **Manual-attestation** | Requires human-provided evidence | Create control with API event source |
| **Hybrid** | Automated check + manual sign-off | Design control + note manual component |
| **Informational** | Documentation-only, no evaluation needed | Skip -- note in report |

### Classification Signals

| Signal | Points To |
|--------|----------|
| Contains measurable metric (count, percentage, score, rating) | Automated |
| References specific tool output (scan results, test coverage) | Automated |
| Contains "shall", "must" with measurable criteria | Automated |
| References process or procedure (review, training, approval) | Manual or Hybrid |
| Requires human judgment (risk assessment, design review) | Manual |
| Documentation requirement (maintain a policy, document procedures) | Informational |
| "Verify that" + automated tool action | Automated |
| "Verify that" + human action | Hybrid |

### Confidence in Classification

Assign confidence to each classification:
- >= 0.80: High confidence, proceed with mapping
- 0.50-0.79: Medium confidence, flag for human confirmation
- < 0.50: Low confidence, skip automated mapping

---

## 4. Matching to Existing Controls

Before creating new controls, check if existing ones already satisfy the requirement.

### Search Process

1. Fetch all active published controls:
   ```
   GET /controls?status=active&state=published
   ```

2. For each requirement, compare against existing controls using:
   - **Name similarity**: Does the control name overlap with the requirement title?
   - **Description overlap**: Do the descriptions share key concepts?
   - **Category match**: Is the control in a relevant collection/domain?
   - **Subscription match**: Does the control subscribe to a relevant plugin?

3. Score each potential match:

| Factor | Weight | Score Range |
|--------|--------|-------------|
| Name similarity | 0.35 | 0.0 - 1.0 |
| Description overlap | 0.30 | 0.0 - 1.0 |
| Category alignment | 0.20 | 0.0 - 1.0 |
| Plugin relevance | 0.15 | 0.0 - 1.0 |

4. Thresholds:
   - >= 0.80: Recommend reuse (map requirement to existing control)
   - 0.50-0.79: Possible match (flag for human review)
   - < 0.50: No match (proceed to new control design)

---

## 5. Plugin Catalog

Available plugin categories for mapping requirements to evidence sources.

### Categories and Capabilities

| Category | Plugin Examples | Evidence Provided | Relevant For |
|----------|----------------|-------------------|-------------|
| **SAST** | Sonarqube, Checkmarx, Semgrep | Code quality metrics, vulnerability findings, coverage | Code quality, security vulnerabilities |
| **SCA** | Snyk, Sonatype, WhiteSource | Dependency vulnerabilities, license compliance | Dependency management, license compliance |
| **Container Scanning** | Prisma, Wiz, Trivy, Lacework | Container image vulnerabilities by severity | Container security, image hardening |
| **SBOM** | Syft, CycloneDX | Software bill of materials presence/completeness | Supply chain transparency |
| **Signature** | Sigstore, Cosign | Artifact/commit digital signature verification | Artifact integrity, code signing |
| **DAST** | ZAP, Burp Suite | Runtime vulnerability findings | Application security testing |
| **IaC Scanning** | Checkov, Terraform Sentinel | Infrastructure-as-code policy violations | Infrastructure compliance |
| **Testing** | Sonarqube, TestRail | Test results, code coverage percentages | Quality assurance |
| **Deployment** | Kubernetes, ArgoCD | Deployment records, environment promotion | Release management |
| **Pipeline** | GitHub Actions, GitLab CI | CI/CD execution records, build provenance | Build integrity |
| **Code Review** | GitHub, GitLab | Pull request review status, approvals | Peer review compliance |
| **Access Control** | GitHub, GitLab, Azure DevOps | Branch protection rules, permissions | Access management |

### Using Schema Discovery

For each candidate plugin, use schema discovery to understand the actual evidence fields:

```
GET /controls/:entity_key/schemas?producer={pluginPath}
```

This returns the field paths and types available in the plugin's evidence output. Use these to write the Rego rule.

---

## 6. New Control Design

When no existing control matches a requirement, design a new one using the fianu-controls skill.

### Design Process

For each unmatched automated/hybrid requirement:

1. **Select plugin**: Match requirement keywords to plugin capabilities (Section 5). If multiple candidates, prefer the plugin whose schema fields best cover the requirement.

2. **Discover schema**: Run schema discovery for the selected plugin to get field paths.

3. **Select Rego pattern**: Based on the requirement type:
   - Count/threshold requirement → Threshold check pattern
   - Minimum score requirement → Score comparison pattern
   - Existence requirement → Presence check pattern
   - Recency requirement → Freshness check pattern
   - Multiple metrics → Multi-metric pattern

4. **Generate Rego rule**: Map plugin schema fields to `input.detail.*` paths. Map policy thresholds to `data.*` paths.

5. **Generate policy template**: Create readable keys that map to the Rego rule's data references.

6. **Choose scope**: Based on the requirement (see fianu-controls.md Section 3).

7. **Assign confidence**: Score how well the generated control matches the original requirement.

### Output per Requirement

```json
{
  "requirementId": "CC-7.1",
  "classification": "automated",
  "existingMatch": null,
  "suggestedControl": {
    "name": "Change Management Approval",
    "path": "compliance.change_management.approval",
    "scope": "repository",
    "subscriptions": [
      { "type": "plugin", "source": "github.pull_request" }
    ],
    "regoRule": "package rule\nimport rego.v1\n...",
    "policyTemplate": {
      "approvals": { "minimum_reviewers": 2 }
    },
    "domain": "SOC2 Compliance",
    "collection": "Change Management"
  },
  "confidence": 0.82,
  "notes": "Mapped to GitHub PR review data. Verifies minimum reviewer count."
}
```

---

## 7. Hierarchy Placement

### Domain Selection

| Framework | Suggested Domain |
|-----------|-----------------|
| NIST 800-53 | "NIST Compliance" |
| SOC 2 | "SOC2 Compliance" |
| SOX | "SOX Compliance" |
| GDPR | "Data Privacy" |
| ISO 27001 | "ISO 27001" |
| Custom/Internal | Use the framework name or "Internal Standards" |

If no matching domain exists, recommend creating one. Follow FIANU.md guidance: large enterprises 3-6 domains, small companies 1-3.

### Collection Selection

Map requirement categories to collections:

| Category Keywords | Suggested Collection |
|------------------|---------------------|
| vulnerability, scan, security, SAST, SCA, DAST | "Security" |
| code quality, coverage, testing, QA | "Quality Assurance" |
| access, authentication, authorization, identity | "Access Control" |
| change, deployment, release, pipeline | "Change Management" |
| data, encryption, privacy, PII | "Data Protection" |
| logging, monitoring, alerting, incident | "Observability" |
| configuration, infrastructure, IaC | "Infrastructure" |
| documentation, policy, procedure | "Governance" |

Prefer existing collections over creating new ones. One control can belong to multiple collections.

---

## 8. Batch Processing Workflow

### Step 1: Parse Document

Parse the input document into normalized requirements (Section 2).
Validate: reject if fewer than 1 requirement parsed, warn if column mapping is uncertain.

### Step 2: Classify All Requirements

Run classification (Section 3) for each requirement. Report the distribution:
- X automated, Y manual, Z hybrid, W informational

### Step 3: Match Against Existing Controls

Search for existing matches (Section 4) for all automated/hybrid requirements.
Report: X direct matches, Y possible matches, Z unmatched.

### Step 4: Design New Controls

For each unmatched automated/hybrid requirement, run the design workflow (Section 6).
Only proceed for requirements with classification confidence >= 0.80.

### Step 5: Generate Mapping Report

Output a comprehensive report:

```markdown
# Framework Mapping Report: {Framework Name}

## Summary
- Total requirements: {N}
- Automated: {N} | Manual: {N} | Hybrid: {N} | Informational: {N}
- Matched to existing controls: {N}
- New controls designed: {N}
- Requires human review: {N}
- Gap (no automated path): {N}

## Existing Control Matches
| Requirement | Existing Control | Confidence |
|------------|-----------------|------------|
| CC-7.1 | Change Management (entity_key: ...) | 0.92 |

## New Controls to Create
| Requirement | Suggested Name | Scope | Plugin | Confidence |
|------------|---------------|-------|--------|------------|
| CC-8.1 | Container Image Scan | artifact | prisma | 0.85 |

## Requires Human Review
| Requirement | Reason |
|------------|--------|
| CC-9.1 | Low classification confidence (0.55) |
| CC-9.2 | Possible match but uncertain (0.62) |

## No Automated Path (Manual/Informational)
| Requirement | Classification | Recommendation |
|------------|---------------|----------------|
| CC-10.1 | manual-attestation | Create API-sourced control for manual upload |
| CC-10.2 | informational | Document in governance collection |
```

### Step 6: Human Review

Present the report. The human reviews and approves/modifies/rejects each mapping.

### Step 7: Create Approved Controls

For each approved design:
```
POST /create/control
```

This creates the control in **draft mode** and automatically opens an approval ticket. The control is NOT published until a human approves the ticket.

For each control that needs a default policy:
```
POST /create/policy
```

---

## 9. Quality Checks

Before producing the final report, verify:

1. **No duplicate controls**: If two requirements map to the same control, consolidate them
2. **Rego rule validity**: Each generated rule should follow OPA v1 syntax (import rego.v1, if keywords)
3. **Policy template consistency**: Keys follow naming conventions (alphanumeric + underscores)
4. **Scope appropriateness**: Scope matches the evidence type (source-level → repository, build → artifact)
5. **Plugin existence**: Every referenced plugin actually exists and is queryable
6. **Hierarchy validity**: Domain and collection suggestions are reasonable (not duplicating existing)

---

## 10. Edge Cases

### Framework with Non-Standard Format
If the document doesn't have clear columns, use LLM-assisted extraction:
- Identify the document structure (one requirement per row, per paragraph, per section)
- Extract fields based on context clues
- Flag low-confidence extractions in the report

### Requirement Too Vague
If a requirement is too vague to classify or map:
- Classify as "manual-attestation" with low confidence
- Flag for human review with note: "Requirement too vague for automated mapping"

### No Matching Plugin
If a requirement is classified as automated but no plugin can provide the evidence:
- Suggest creating an API-sourced control (custom integration)
- Flag the gap in the report

### Overlapping Requirements
If multiple framework requirements describe the same control:
- Group them under a single control
- Note all requirement IDs in the mapping
- Example: "NIST AC-2" and "SOC2 CC-6.1" may both map to the same "Access Control" control
