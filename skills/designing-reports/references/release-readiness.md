# Example: release readiness

Request: "Is Payments 2.3 ready to ship?"

## The story

- **Verdict.** Did the release's gates clear, and do the controls they check still fail anywhere.
- **Production Deploy controls.** Which of the gate's controls fail on which repositories.
- **Exceptions in play.** What is excused, and what expires soon.
- **Evidence detail.** Every control result.

The tension worth leading with: a gate can clear while the controls it reads still fail on some repositories. The verdict statement says both.

## Datasets

| id | source | scope | controls | window |
|---|---|---|---|---|
| `d1` | `gate_results` | release Payments 2.3 | none | `12m` |
| `d2` | `control_status` | application Payments | the Production Deploy gate's controls | none |
| `d3` | `exceptions` | application Payments | the same controls | none |

`d1` reads the longest window, a year: a release is not re-gated when its evidence changes, so a verdict read over the default 30 days would turn PENDING a month after the gates cleared.

## Sections

Opening section, no title. The release name is the user's words, so it may be typed; its counts may not.

```json
[
  {"name": "report-cover", "props": {
    "kind": "Release readiness",
    "title": "Payments 2.3 release readiness",
    "scope": "Gate verdicts for the release, the controls behind the Production Deploy gate, and exceptions in play",
    "metadata": [
      {"label": "Release", "value": "Payments 2.3"},
      {"label": "Gates", "value": "$data.d1.summary.total"},
      {"label": "Repositories", "value": "$data.d2.summary.assets"}
    ]}},
  {"name": "verdict-hero", "props": {
    "label": "Release gates",
    "verdict": "$data.d1.summary.verdict",
    "statement": {
      "template": "{cleared} of {total} gates cleared this release. {failing} of the {checked} results behind the Production Deploy gate fail.",
      "values": {
        "cleared": "$data.d1.summary.cleared", "total": "$data.d1.summary.total",
        "failing": "$data.d2.summary.failing", "checked": "$data.d2.summary.total"}},
    "facts": [
      {"label": "Gates cleared", "value": "$data.d1.summary.cleared", "of": "$data.d1.summary.total"},
      {"label": "Control results failing", "value": "$data.d2.summary.failing", "of": "$data.d2.summary.total", "warn": "$data.d2.summary.failing"},
      {"label": "Exceptions bound to Payments", "value": "$data.d3.summary.total"}]}},
  {"name": "data-table", "props": {
    "title": "Gate verdicts",
    "rows": "$data.d1.rows",
    "total": "$data.d1.total",
    "columns": [
      {"label": "Gate", "key": "gateName"},
      {"label": "Verdict", "key": "verdict", "format": "status"},
      {"label": "Evaluated", "key": "evaluatedAt", "format": "datetime"}]}}
]
```

A short table of gates belongs up front here: it is the verdict's own detail, a handful of rows, not the evidence dump.

"Production Deploy controls":

```json
[
  {"name": "kpi-row", "props": {"tiles": [
    {"label": "Pass rate", "value": "$data.d2.summary.passRate", "format": "%", "segments": [
      {"status": "pass", "value": "$data.d2.summary.passing"},
      {"status": "fail", "value": "$data.d2.summary.failing"},
      {"status": "warn", "value": "$data.d2.summary.other"},
      {"status": "missing", "value": "$data.d2.summary.missing"}]},
    {"label": "Failing", "value": "$data.d2.summary.failing", "of": "$data.d2.summary.total", "status": "fail"},
    {"label": "No evidence", "value": "$data.d2.summary.missing", "of": "$data.d2.summary.total", "status": "missing"}]}},
  {"name": "status-matrix", "props": {
    "title": "Controls by repository",
    "subtitle": "Failing first. No evidence means none was recorded or found for that commit.",
    "rows": "$data.d2.rows", "rowKey": "controlName", "colKey": "assetName", "valueKey": "result", "colSubKey": "commit"}},
  {"name": "callout", "props": {
    "when": "$data.d2.truncated", "tone": "info",
    "heading": "The matrix shows the first results only",
    "body": "Payments has more control results than a report reads at once. The matrix draws them failing first, so later results (warnings and passes) may be left out."}}
]
```

"Exceptions in play": the callout shows only when there are none, and the table's block `condition` (`$data.d3.rows`, the rows array itself) hides it when there are none, so the empty table never prints under the callout.

```json
[
  {"name": "callout", "props": {
    "when": {"_fn": "ifZero", "_args": ["$data.d3.summary.total", true, false]},
    "tone": "pass",
    "heading": "No exceptions bound to Payments",
    "body": "No live exception bound to Payments or its repositories covers these controls, so every failure above counts against the release. Exceptions scoped by an index or asset type are not listed here."}},
  {"name": "data-table", "condition": "$data.d3.rows", "props": {
    "rows": "$data.d3.rows",
    "total": "$data.d3.total",
    "columns": [
      {"label": "Exception", "key": "name"},
      {"label": "Control", "key": "control"},
      {"label": "Asset", "key": "assetName"},
      {"label": "Expires", "key": "expiresAt", "format": "date"}]}}
]
```

"Evidence detail" is the `data-table` from `references/application-health.md` with its `rows` bound to `$data.d2.rows` and its `total` to `$data.d2.total`.

## Why it is built this way

- `verdict-hero` because the question is yes or no. Its verdict binds `summary.verdict`, which is PENDING when no gate has a result, so a release with no gates never reads Cleared. Its statement holds both halves of the tension, each number a slot.
- The empty state says what the absence means for the reader, not just that a list is empty.
- The `kpi-row` has three tiles, not four: the passing count is already in the pass-rate segments.
