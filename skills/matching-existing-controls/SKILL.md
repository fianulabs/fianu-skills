---
name: matching-existing-controls
description: Use when checking whether a new requirement is already satisfied by an existing Fianu control. Defines the similarity scoring (name 0.35 / description 0.30 / category 0.20 / plugin 0.15) and the 0.80 / 0.50 thresholds for reuse vs. flag-for-review vs. new-control.
---

# Matching Existing Controls

## Overview

Before creating a new control, check whether an existing one already
satisfies the requirement. This skill defines the similarity scoring
algorithm and the action thresholds.

## Search process

1. Fetch all active published controls:

   ```
   GET /controls?status=active&state=published
   ```

   (See `working-with-entities` for the endpoint contract.)

2. For each candidate control, compute a similarity score against the
   requirement on four axes.

3. Take the action determined by the score's threshold band.

## Scoring weights

| Factor | Weight | Score range |
|---|---|---|
| Name similarity | 0.35 | 0.0 – 1.0 |
| Description overlap | 0.30 | 0.0 – 1.0 |
| Category alignment | 0.20 | 0.0 – 1.0 |
| Plugin relevance | 0.15 | 0.0 – 1.0 |

Total similarity = Σ (factor × weight). Range: 0.0 – 1.0.

### Factor definitions

- **Name similarity**: lexical overlap between the control name and the
  requirement title. Token-set Jaccard works fine; weight stopwords low.
- **Description overlap**: shared key concepts between descriptions.
  Compute via keyword extraction + overlap, not character similarity.
- **Category alignment**: does the existing control's collection match
  the requirement's category? Binary or partial (0.5 if related,
  1.0 if exact).
- **Plugin relevance**: does the existing control subscribe to a plugin
  that could produce evidence for the requirement? Binary or 0.5/1.0.

## Thresholds

| Total similarity | Action |
|---|---|
| `≥ 0.80` | Recommend reuse — map the requirement to this existing control. |
| `0.50 – 0.79` | Possible match — flag for human review. Do not auto-reuse. |
| `< 0.50` | No match — proceed to new control design. |

## Worked example

Requirement: "CC-7.1: The organization manages changes to infrastructure
and software through a documented review process."

Candidate control: "Pull Request Review" in the "Change Management"
collection, subscribed to `github.pull_request`.

| Factor | Score | × Weight |
|---|---|---|
| Name similarity (Pull Request Review vs Change Management Controls) | 0.4 | 0.14 |
| Description overlap (review, change, approval) | 0.7 | 0.21 |
| Category alignment (Change Management) | 1.0 | 0.20 |
| Plugin relevance (github.pull_request) | 1.0 | 0.15 |
| **Total** | | **0.70** |

0.70 falls in `0.50 – 0.79` → flag for human review. The match is
plausible but not certain enough to silently reuse.

## See also

- `working-with-entities` — fetches the existing controls.
- `converting-frameworks-to-controls` — orchestrates this skill in
  Step 3 of the workflow.
- `placing-entities-in-hierarchy` — used when no existing control
  matches and a new one must be placed.
