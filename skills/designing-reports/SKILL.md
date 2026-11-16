---
name: designing-reports
description: Use when composing or editing a Fianu report document (datasets plus sections of blocks), deciding what it says first, which block shows which data (lede, verdict-hero, kpi-row, status-matrix, trend-chart, bar-list, timeline, data-table, callout), how every number binds to $data, status words, short commits and print layout. Not for writing a control's rule or for querying evidence.
---

# Designing Reports

## Overview

A Fianu report is read by an auditor or an executive, often as a printed PDF, and re-runs later on fresh data. Compose it like an editor. Say the answer first, show each fact in the form that makes it obvious, and keep the raw rows at the back as evidence. The blocks draw the scales, colours, legends and empty states. Your job is the story, the choice of block and the bindings.

## 1. Read the request as a story

1. Write the verdict sentence first: the one sentence the reader would repeat to their manager. It opens the report as a `lede`, or as a `verdict-hero` when the question has a yes or no answer (can this release ship, did the gate clear).
2. List the questions the reader asks next, in order, and give each its own section: where does it fail, is it getting better, what shipped, what is excused, what is the evidence.
3. One question per section. A section that needs two unrelated charts is two sections.
4. Order: verdict, current state, change over time, context (deployments, exceptions), evidence.
5. The cover names the scope: which assets, which commits, which window. A number without its scope is not evidence.

## 2. Pick the block for the data's job

| The data's job | Block | Rule |
|---|---|---|
| Cover | `report-cover` | `kind`, `title`, `scope`, `metadata` (each value bound) |
| Headline sentence | `lede` | One or two sentences; every number a `{slot}` |
| A yes or no answer | `verdict-hero` | The verdict, one bound statement, 2 to 4 `facts` with `of`; a fact that flags a problem binds `warn` to its own count (`true` paints a 0 in the fail colour) |
| 3 or 4 headline numbers | `kpi-row` | A count gets `of`; a rate gets `segments` (pass, fail, warn bound to `summary.other`, missing: every result, so the bar matches the rate); at most 4 tiles |
| Control by repository | `status-matrix` | Up to about 8 columns; for applications as columns set `aggregate: true` |
| Anything over time | `trend-chart` | `columns` for counts per bucket, `area` or `line` for a rate with `"format": "%"` (without it a 0 to 1 rate draws on a count axis); one scale per chart. `control_trend` buckets a window of 7 days or less by the hour, a longer one by the day: a "per day" chart needs a window over 7 days |
| Comparing a few things | `bar-list` | Ranked, one shared scale; `segments` split like a kpi-row rate (pass, fail, warn from `summary.other`, missing) |
| Deployments | `timeline` | Lanes are environments; `emphasis` on production |
| The rows behind the claims | `data-table` | Last, as evidence; `sortFailingFirst`; typed column `format`s; `maxRows`; when `rows` is `$data.<id>.rows`, bind `total` to `$data.<id>.total` so a capped dataset says how many rows it left out (a summary list such as `summary.byApplication` takes no `total`) |
| Nothing to show, or a caveat | `callout` | `when` so it shows only when true; say what it means and what to do |

Every block in this table takes `title` and `subtitle`, except `report-cover`, which takes `title` and no `subtitle` (its `scope` line does that job). Use the subtitle to say how to read the block ("Failing first. The commit under each repository is the one evaluated."), since a printed page has no hover.

## 3. Bind every number

- Numbers come only from datasets: `$data.<id>.summary.<field>`, `$data.<id>.rows`, and `$data.<id>.buckets[].<field>` for one column of values. `list_report_datasets` names each source's fields.
- Prose numbers go through slots. A `lede` (and a `verdict-hero` statement) is a `template` with `{name}` slots, `values` mapping each slot to a binding, and `formats` (`"%"` for a 0 to 1 fraction such as `passRate`, `"n"` for a count).
- Never type a count, rate or date into a title, subtitle, heading, body, metadata value or template. It is wrong on the next run. Words that stay true are fine ("Failing first", "One dot per deployment"). A title or subtitle may name the window the report defines ("30-day trend" over a dataset with window `30d`); `check_report` still lists it as an advisory `typed_number`, so say in a clause that it is the report's window. A `lede` template or `verdict-hero` statement may hold no digit outside a `{slot}`, the window included: the report refuses it, so write "the trend window" or leave the window to the title.
- Derive with a helper (`{"_fn": "<name>", "_args": [...]}`) instead of working a number out yourself. Use only these: `sum` (any number of values), `add`, `sub`, `divf` (a / b, 0 when b is 0), `percentOf` (value / total x 100), `ifZero` (n, then the value when n is 0, else the other), `default` (a fallback, then the value), `concat` (lists of rows into one), `distinctCount` (rows, field: how many distinct values), `countWhere` (rows, field, value: how many rows match, any case).
- A `status-matrix`, `timeline` or other block over `$data.<id>.rows` draws only the rows the dataset lists (control results failing first, deployments newest first), while every `summary` field counts every row. Put a `callout` in the same section with `when` `$data.<id>.truncated` saying the block may leave rows out (`truncated` also means a read stopped at its bound, so the callout promises no full count); `check_report` names any such block without one (`capped_rows`). A `data-table` says it itself through `total`.
- A matrix over several `control_status` datasets (`concat`) keys its rows by `controlLabel` (name and path): each dataset adds a path to a shared `controlName` only when its own rows hold both controls, so `controlName` can split one control or merge two across datasets.
- Row helpers (`distinctCount`, `countWhere`, and `concat` feeding them) see only the rows a dataset lists, at most 500 (or its `limit`), while every `summary` field counts every row. For a headline count, bind a `summary` field when one exists; use a row helper only when none does, and never mix the two in one claim (a capped count over an uncapped total).
- Pair a rate with its counts: "4 of 12 fail" beside "33%", never the percentage alone.
- Run `check_report` before you say the report is ready. It flags typed numbers and unbound datasets.

## 4. Status, commits, time

- Status is a closed set: `pass`, `fail`, `warn`, `missing`, `na`. The blocks draw each with its colour, a glyph and a word (Pass, Fail, Warning, No evidence, Not required). Supply the status, never a colour.
- `missing` means no evidence was recorded. It is neither a pass nor a fail. When it is a large share, say so in a subtitle.
- A not required result passes, as it does at a gate: `summary.passing`, every `passRate` and the "N of M pass" counts of the `status-matrix` and `statusBars` all count it, though the blocks draw it as Not required.
- Commits use `format: sha` (7 characters). Event times use `datetime`, expiries `date`.
- Names stay as the tenant spells them.

## 5. Never

- A table first. Tables are evidence and come last.
- A long SHA column, or a table whose only varying column is a commit.
- A 30-row table of zeros or of identical passes. Summarise it in a `kpi-row` or `status-matrix` and cap the table with `maxRows`.
- A chart for one number (use a tile), or a trend over a single bucket (use a `callout`).
- More than 4 KPI tiles, or a count without its denominator.
- Two blocks in one section answering the same question.
- Decoration that carries no fact: dividers, badges, images, numbered markers on content that is not a sequence.
- An empty section. Show a `callout` with `when` instead, worded as what it means and no wider than its dataset reads ("No exceptions bound to Payments").
- Illustrative or sample data in a saved report.

## 6. Before you say it is ready

- The verdict answers the question asked. For "is X ready", cleared gates with failing required controls (or a pending release) is not ready. Never show a green verdict that your reply contradicts.
- The report and your reply say the same thing. Never state a grouping, count or name in chat that the report does not show.
- A field you group or label by must be filled. If `check_report` or the data shows it empty (an exception with no application), say so in a `callout` instead of "across 0 applications".
- A `callout` for the empty case shows with `when`, and the table it replaces gets the block `condition` `$data.<id>.rows` (the rows array itself, not a field inside it), so the empty table never prints under it. `data-table` has no `when`.
- Every series the lede counts is on the chart, or the chart's total and the lede disagree.
- A per-day table lists only days with activity, or is capped with `maxRows`.
- This skill is already loaded on every report path. Don't call `load_skill` for it.

## 7. Print

- Pages are US Letter. A block never splits across pages, so keep each section to about a page: a `kpi-row` and one chart, or one matrix.
- Long tables repeat their header on every page. Cap them in the body and put the full rows in a last section ("Evidence detail" or "Appendix: raw data").
- Keep a `status-matrix` to about 8 columns. With more, aggregate by application, or show the failing columns and leave the rest to the table.
- Nothing is interactive. Every chart must read on paper from its title, subtitle and labels alone.

## 8. Restraint

- Spend boldness in one place, the verdict, and keep everything else quiet.
- Visual structure is information. A label, border or number earns its place by telling the reader something.
- Write in the reader's words: "No evidence", not "missing attestation". Use sentence case and plain verbs.
- Before you finish, remove one block. If the report reads as well without it, leave it out.

## Worked examples

- `references/application-health.md`: "How is DBX doing?" One application's current status, its 30-day trend and the evidence.
- `references/release-readiness.md`: "Is Payments 2.3 ready to ship?" A verdict, the gate's controls and an empty exceptions state.
- `references/executive-summary.md`: three applications compared, then one application's deployments.

## See also

- `working-with-attestations` for what each result means.
- `working-with-release-gating` for gate verdicts and release status.

Section 8 and the empty-state rule in section 5 are adapted from Anthropic's `frontend-design` skill, licensed under the Apache License 2.0 (https://www.apache.org/licenses/LICENSE-2.0). Fianu changed them for printed compliance reports.
