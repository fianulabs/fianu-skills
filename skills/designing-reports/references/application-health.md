# Example: one application's health

Request: "How is DBX doing?"

## The story

- **Verdict.** How many of DBX's control results fail now, and how the last 30 days went.
- **Current status.** Which controls fail on which repositories.
- **30-day trend.** Is it getting better.
- **Evidence detail.** Every result behind the matrix.

## Datasets

| id | source | scope | window |
|---|---|---|---|
| `d1` | `control_status` | application DBX | none |
| `d2` | `control_trend` | application DBX | `30d` |

## Sections

The cover and the lede open the report, in a first section with no title.

```json
[
  {"name": "report-cover", "props": {
    "kind": "Application health",
    "title": "DBX health",
    "scope": "Every control on the newest default-branch commit of each DBX repository",
    "metadata": [
      {"label": "Repositories", "value": "$data.d1.summary.assets"},
      {"label": "Controls", "value": "$data.d1.summary.controls"}
    ]}},
  {"name": "lede", "props": {
    "template": "{failing} of {total} control results fail across DBX's repositories, a pass rate of {rate}. Over the trend window, {evalFailed} evaluations failed and {evalPassed} passed.",
    "values": {
      "failing": "$data.d1.summary.failing", "total": "$data.d1.summary.total", "rate": "$data.d1.summary.passRate",
      "evalFailed": "$data.d2.summary.failed", "evalPassed": "$data.d2.summary.passed"},
    "formats": {"rate": "%", "failing": "n", "total": "n", "evalFailed": "n", "evalPassed": "n"}}}
]
```

"Current status": the headline numbers, then where they fall.

```json
[
  {"name": "kpi-row", "props": {"tiles": [
    {"label": "Pass rate", "value": "$data.d1.summary.passRate", "format": "%", "segments": [
      {"status": "pass", "value": "$data.d1.summary.passing"},
      {"status": "fail", "value": "$data.d1.summary.failing"},
      {"status": "warn", "value": "$data.d1.summary.other"},
      {"status": "missing", "value": "$data.d1.summary.missing"}]},
    {"label": "Passing", "value": "$data.d1.summary.passing", "of": "$data.d1.summary.total", "status": "pass"},
    {"label": "Failing", "value": "$data.d1.summary.failing", "of": "$data.d1.summary.total", "status": "fail"},
    {"label": "No evidence", "value": "$data.d1.summary.missing", "of": "$data.d1.summary.total", "status": "missing"}]}},
  {"name": "status-matrix", "props": {
    "title": "Controls by repository",
    "subtitle": "Failing controls first. The commit under each repository is the one evaluated.",
    "rows": "$data.d1.rows", "rowKey": "controlName", "colKey": "assetName", "valueKey": "result", "colSubKey": "commit"}},
  {"name": "callout", "props": {
    "when": "$data.d1.truncated", "tone": "info",
    "heading": "The matrix shows the first results only",
    "body": "DBX has more control results than a report reads at once. The matrix draws them failing first, so later results (warnings and passes) may be left out."}}
]
```

"30-day trend": counts per day are columns. The window is the report's own, so the section title may name it (`check_report` still lists it as an advisory `typed_number`; say so in a clause). The lede may not: a template holds no digit outside a `{slot}`, so it says "the trend window".

```json
[
  {"name": "trend-chart", "props": {
    "title": "Evaluations per day",
    "subtitle": "Passed and failed control evaluations by evaluation date.",
    "kind": "columns",
    "x": "$data.d2.buckets[].date",
    "series": [
      {"label": "Passed", "status": "pass", "values": "$data.d2.buckets[].passed"},
      {"label": "Failed", "status": "fail", "values": "$data.d2.buckets[].failed"}]}},
  {"name": "trend-chart", "props": {
    "title": "Pass rate per day",
    "subtitle": "Passed and not required evaluations as a share of the day's evaluations; a day with none leaves a gap.",
    "kind": "line",
    "format": "%",
    "x": "$data.d2.buckets[].date",
    "series": [
      {"label": "Pass rate", "status": "pass", "values": "$data.d2.buckets[].passRate"}]}}
]
```

"Evidence detail", last.

```json
[
  {"name": "data-table", "props": {
    "subtitle": "Every result behind the matrix, failing first.",
    "rows": "$data.d1.rows",
    "total": "$data.d1.total",
    "sortFailingFirst": true,
    "columns": [
      {"label": "Repository", "key": "assetName"},
      {"label": "Control", "key": "controlName"},
      {"label": "Result", "key": "result", "format": "status"},
      {"label": "Commit", "key": "commit", "format": "sha"},
      {"label": "Evaluated", "key": "evaluatedAt", "format": "datetime"}]}}
]
```

## Why it is built this way

- The lede carries the answer, and each of its numbers is a slot, so a re-run rewrites it.
- "Is it getting better" is the rate, so it gets its own `line` chart with `"format": "%"`: on the counts chart's axis a 0 to 1 rate would draw flat at the bottom.
- The second `kpi-row` a first draft often adds for the trend (evaluations, passed, failed, rate) repeats the lede. It was cut.
- The matrix answers "where". The table repeats it row by row, so it goes last as evidence.
