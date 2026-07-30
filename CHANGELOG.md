# Changelog

All notable changes to fianu-skills are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres
to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [v0.3.0] - 2026-07-29

### Added
- `working-with-asset-series` (Group B) — the foundation under every evidence query: the series catalog (`digest` 2110 / `uri` 2111 / `commit` 2112 / `tag` 2113 / `release` 2116 / `timestamp` 2117 / `period_*` 2118–2122), the four series axes (`seriesName` / `seriesCode` / `seriesId` / `seriesType`), how an attestation lands on exactly one series (lowest code the occurrence carries), the snapshot and `export` endpoints, cross-series `associations`, and series discovery. Canonical home for "a control is missing from my results at this commit".
- `working-with-findings-and-violations` (Group B) — reading violations / findings / vulnerabilities off an asset or note (`GET /evidence/assets/:asset/violations`, `GET /notes/:uuid/findings`, `GET /notes/:uuid?format=raw`), the normalized `Finding` schema, and the violations-vs-findings pipeline distinction. Loads `working-with-asset-series`.
- `working-with-attestations` — new section on reading a failing control's **measured value**, threshold, and failed items off `GET /notes/:uuid?format=raw` (`$.detail.*`, `$.policy.data.*`, `$.policy.evaluation.logs[]`, `$.display.violations.rows`), plus the threshold-vs-item-based failure-shape distinction.
- GitHub Copilot CLI support: root `plugin.json` manifest (`skills: ./skills/`) and `using-fianu-skills/references/copilot-tools.md` tool-name mapping. Install with `copilot plugin install fianulabs/fianu-skills`.

### Fixed
- **`working-with-attestations`: removed "Prefer this over the per-policy fan-out" from `GET /notes/attestations/:uuid/meta`.** That endpoint returns policy provenance only — no `result`, no `detail`, no `display` — so the guidance sent agents to the one endpoint that cannot answer "what was the measured value", producing false "Fianu doesn't persist the measurement" conclusions. Now labelled explicitly, with the raw-note path documented alongside.
- **Corrected the series catalog.** Prior values came from `../core` `external/db/series/constants.go`, which is dead code (only importer is a test) and disagrees with the seeded catalog. `tag` is a real series (2113, not absent); `release` is 2116 (not 2115); `timestamp` 2117 and `period_*` 2118–2122; `jira_issue` / `jira_fix_version` are not seeded at all.
- **Removed the invented `Unknown` / "not resolvable" result value** from `working-with-asset-series`, `working-with-attestations`, `working-with-findings-and-violations`, and the routing table. The real vocabulary is six values: `pass` / `warn` / `fail` / `in progress` / `not required` / `not found`.
- **Corrected the "keyed on digest" model.** An attestation lands on exactly one series — the lowest-coded declared series the occurrence actually carries — and the evidence query matches on series *value*, never name or code. Declaring `[digest, uri, commit]` does not mean the attestation exists on all three. 19 prod controls share that binding, not 3.
- **Corrected `associations` semantics.** A non-empty array widens the query; each entry then applies a conjunctive filter that *narrows*. Adding a second association shrinks results rather than unioning them.
- **Fixed `POST /evidence/assets/by-series`:** `associations` is a JSON **string** (`"true"`), not a boolean. The previous example would 400.
- **Removed the `branch` parameter** from `GET /evidence/assets/:asset/violations` — the route never extracts it. It was copied from the web client, which sends it uselessly.
- **Corrected the batch-snapshot ceiling.** `seriesType` is validated to `branch`/`commit` but passes `seriesId` through verbatim, so batch *can* reach digest-keyed evidence. Its real limitation is that it never populates `associations` and so cannot expand one series into another.
- **Dropped "every violation is a finding."** Violations and findings come from independent pipelines (Rego `record_violation` at evaluation vs. plugin schema extraction at read time), joined only by an opt-in `matchKey` correlation. Findings require `x-findings-*` schema annotations and return empty for plugins that lack them, including SonarQube.
- `Finding` schema: added `matchKey`; documented that `isViolation` is `omitempty` (absent, never `false`) and only populated for attestation UUIDs; corrected the `source` example, which showed a shape the API cannot emit; downgraded `severity` from an enumerated set to an unvalidated lowercased pass-through (adds `info`).
- Documented that `GET /evidence/assets/:asset/violations` excludes gate attestations, and that the snapshot endpoint silently defaults an omitted `seriesId` to the asset's latest commit while violations 400s.
- Re-grounded every Maintenance table at the Go handlers, `fior` constants, and the seeded DB rather than `ui-fianu/src/functions/api.js`, which was the source of several of the errors above.
- **`GET /assets/:asset/attestations/export` takes `?commit=`, not `?seriesId=`** — the wrong param is silently ignored and returns an empty `attestations` array. Response is an object (`{summary, attestations[]}`), so paths are `$.attestations[].raw.*`. Documented that raw-snapshot reporting is commit-series only.
- **Unknown series names *are* rejected at entity-deploy time** with `series[N]: unknown series name '<x>' - cannot resolve code` (400), on the path every prod spec uses. An earlier draft claimed nothing validates them.
- **Series selection sorts on exact asset-type match first**, with `seriesCode` as the tiebreak — not code alone. Also noted that an occurrence carrying none of the declared series leaves the version unreduced.
- Corrected `matchKey` mechanics: match keys are derived and stamped **at read time** from schema mappings, not emitted by the rule author during evaluation, and correlation uses `matchKey` exclusively with no `id` fallback.
- Execution `status` is `complete` / `initiated` / `error` (not `in_progress`); removed the unsupported `not_run` spelling.
- Attestation history route is `GET /entities/:entity_id/attestations` (exposed through the proxy as `/api/controls/:entity_id/attestations`) — the previously documented `/controls/:entity_key/attestations` does not exist. Manual upload path params are `:control_entity_key` / `:action`; agent summary param is `:finding_id`.
- Narrowed "the evidence query never filters on series name or code" — true of the primary predicate, but association entries do filter on `seriesName` / `seriesCode`.
- Corrected the JFrog Xray control count (five, not three) and softened "empty by design" on threshold controls to an authoring convention, which is what the code supports.

## [v0.2.2] - 2026-06-26

### Added
- `working-with-attestations` (Group B) — attestation reads, computed-policy meta, manual attestation upload, and the pass/fail/notRequired/notFound result vocabulary.
- `working-with-release-gating` (Group B) — runtime gate evaluation against assets/releases and the release lifecycle.
- `working-with-indexes` (Group B) — the `/entities/indexes` HTTP surface and the index compute lifecycle.
- `writing-cel-expressions` (Group C) — the Fianu CEL dialect (`$asset.field.(cast)`) for policy criteria and index scopes.

### Changed
- Wired the existing orchestrators and authoring skills to the new canonical homes (`analyzing-tickets`, `managing-ticket-approvals`, `summarizing-evidence`, `parsing-framework-documents`, `working-with-entities`, `deploying-entities-yaml`, `deploying-entities-terraform`, `writing-rego-rules`, `using-fianu-skills`).
- Registered four canary strings in `validate-skills.sh` (`/internal/upload`, `/assets/releases/`, `recomputeStatus`, `.(list_string)`).

## [v0.2,1] - 2026-06-15

## [0.2.0] - 2026-06-13

## [0.1.0] — 2026-06-09

### Added
- Initial 17-skill release. See `docs/architecture.md` for the skill inventory.
- Multi-harness manifests: Claude Code, Codex CLI, Gemini CLI.
- SessionStart hook (Claude Code) that bootstraps `using-fianu-skills` automatically.
