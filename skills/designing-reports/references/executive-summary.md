# Example: executive summary across applications

Request: "Give me an executive summary of DBX, CRM and Payments, and how Payments has been shipping."

## The story

- **Verdict.** Each application's pass rate, how many results fail or have no evidence across the three, and how many deployments Payments shipped.
- **Posture by application.** Which application is worst, and which controls fail everywhere.
- **Payments deployments.** What shipped where, and what the gates stopped.

## Datasets

| id | source | scope | window |
|---|---|---|---|
| `d1` | `control_status` | application DBX | none |
| `d2` | `control_status` | application CRM | none |
| `d3` | `control_status` | application Payments | none |
| `d4` | `deployments` | application Payments | `14d` |

## Sections

Opening section, no title. Even the count of applications is bound: typed, it goes stale the day the scope changes.

```json
[
  {"name": "report-cover", "props": {
    "kind": "Executive summary",
    "title": "Compliance posture: DBX, CRM and Payments",
    "scope": "Control results on the newest default-branch commit of every repository, and Payments deployments over 14 days",
    "metadata": [
      {"label": "Repositories", "value": {"_fn": "sum", "_args": ["$data.d1.summary.assets", "$data.d2.summary.assets", "$data.d3.summary.assets"]}},
      {"label": "Control results", "value": {"_fn": "sum", "_args": ["$data.d1.summary.total", "$data.d2.summary.total", "$data.d3.summary.total"]}}
    ]}},
  {"name": "lede", "props": {
    "template": "Payments passes {pay} of its control results, CRM {crm} and DBX {dbx}. Across the three, {failing} of {total} results fail and {missing} have no evidence. Payments recorded {deploys} deployments in the window, and its gates approved {approved} of them.",
    "values": {
      "pay": "$data.d3.summary.passRate", "crm": "$data.d2.summary.passRate", "dbx": "$data.d1.summary.passRate",
      "failing": {"_fn": "sum", "_args": ["$data.d1.summary.failing", "$data.d2.summary.failing", "$data.d3.summary.failing"]},
      "missing": {"_fn": "sum", "_args": ["$data.d1.summary.missing", "$data.d2.summary.missing", "$data.d3.summary.missing"]},
      "total": {"_fn": "sum", "_args": ["$data.d1.summary.total", "$data.d2.summary.total", "$data.d3.summary.total"]},
      "deploys": "$data.d4.summary.total", "approved": "$data.d4.summary.approved"},
    "formats": {"pay": "%", "crm": "%", "dbx": "%"}}}
]
```

"Posture by application": one bar per application on a shared scale, then where the failures cluster. With applications as columns the matrix aggregates, so a cell reads "2 of 3 fail".

```json
[
  {"name": "bar-list", "props": {
    "title": "Control results by application",
    "subtitle": "Each bar is one application's results on its newest commits.",
    "items": [
      {"label": "DBX", "value": "$data.d1.summary.failing", "valueLabel": "failing", "segments": [
        {"status": "pass", "value": "$data.d1.summary.passing"},
        {"status": "fail", "value": "$data.d1.summary.failing"},
        {"status": "warn", "value": "$data.d1.summary.other"},
        {"status": "missing", "value": "$data.d1.summary.missing"}]},
      {"label": "CRM", "value": "$data.d2.summary.failing", "valueLabel": "failing", "segments": [
        {"status": "pass", "value": "$data.d2.summary.passing"},
        {"status": "fail", "value": "$data.d2.summary.failing"},
        {"status": "warn", "value": "$data.d2.summary.other"},
        {"status": "missing", "value": "$data.d2.summary.missing"}]},
      {"label": "Payments", "value": "$data.d3.summary.failing", "valueLabel": "failing", "segments": [
        {"status": "pass", "value": "$data.d3.summary.passing"},
        {"status": "fail", "value": "$data.d3.summary.failing"},
        {"status": "warn", "value": "$data.d3.summary.other"},
        {"status": "missing", "value": "$data.d3.summary.missing"}]}]}},
  {"name": "status-matrix", "props": {
    "title": "Where failures cluster",
    "subtitle": "Failing repositories per control and application. Controls with the most failing results come first.",
    "aggregate": true,
    "rows": {"_fn": "concat", "_args": ["$data.d1.rows", "$data.d2.rows", "$data.d3.rows"]},
    "rowKey": "controlLabel", "colKey": "application", "valueKey": "result"}},
  {"name": "callout", "props": {
    "when": "$data.d1.truncated", "tone": "info",
    "heading": "DBX shows its first results only",
    "body": "DBX has more control results than a report lists, so its column counts the first of them, failing first."}},
  {"name": "callout", "props": {
    "when": "$data.d2.truncated", "tone": "info",
    "heading": "CRM shows its first results only",
    "body": "CRM has more control results than a report lists, so its column counts the first of them, failing first."}},
  {"name": "callout", "props": {
    "when": "$data.d3.truncated", "tone": "info",
    "heading": "Payments shows its first results only",
    "body": "Payments has more control results than a report lists, so its column counts the first of them, failing first."}}
]
```

"Payments deployments": a timeline, then a capped table.

```json
[
  {"name": "timeline", "props": {
    "title": "Deployment timeline",
    "subtitle": "One dot per deployment. Prod is highlighted; a cross marks a deployment the gate rejected or could not judge.",
    "events": "$data.d4.rows",
    "timeKey": "deployedAt", "laneKey": "environment", "rowKey": "assetName", "statusKey": "result",
    "emphasis": "Prod", "days": 14}},
  {"name": "callout", "props": {
    "when": "$data.d4.truncated", "tone": "info",
    "heading": "The timeline shows the newest deployments only",
    "body": "Payments deployed more often than a report reads at once, so the earliest days may look quieter than they were."}},
  {"name": "data-table", "props": {
    "title": "Deployments",
    "rows": "$data.d4.rows",
    "total": "$data.d4.total",
    "maxRows": 10,
    "columns": [
      {"label": "When", "key": "deployedAt", "format": "datetime"},
      {"label": "Deployed asset", "key": "assetName"},
      {"label": "Environment", "key": "environment"},
      {"label": "Commit", "key": "commit", "format": "sha"},
      {"label": "Gate result", "key": "result", "format": "status"}]}}
]
```

## Why it is built this way

- Three applications are a comparison, so `bar-list`, not three separate matrices.
- The per-repository matrix would run past 8 columns, so the matrix aggregates by application and the per-repository detail stays in each application's own report.
- The deployment table is capped; the timeline shows every event the dataset lists (the newest first, with a callout when there were more), and the table's job is the commits.
- The matrix keys rows by `controlLabel` (name and path): each application's dataset adds a path to `controlName` only when its own rows hold two controls of that name, so `controlName` could split one control or merge two across the applications.
- Each grid over a dataset's rows has a callout on that dataset's `truncated`: the grid draws only the rows the dataset lists. The callout claims no full count, since `truncated` also means a read stopped at its bound.
- The timeline lists no `lanes`, so an environment the application starts deploying to gets its own lane; `emphasis` names the tenant's own production environment, read from the data, never guessed.
- The lede sets `summary.approved` against `summary.total`: both count every deployment in the window, where `countWhere` over the capped rows would set a capped count against an uncapped total.
- The cover's repository count sums each application's `summary.assets`: a repository belongs to one application, so none is counted twice, and the sum stays exact past the row cap, where `distinctCount` over the concatenated rows would undercount.
