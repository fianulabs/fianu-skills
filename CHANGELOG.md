# Changelog

All notable changes to fianu-skills are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres
to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [v0.3.0] - 2026-07-29

### Added
- `working-with-asset-series` (Group B) — the foundation under every evidence query: the series catalog (`digest` / `uri` / `commit` / `release` / `jira_*` / `period_*` with their codes), the `seriesName` / `seriesCode` / `seriesId` / `seriesType` axes, which series a control binds to, the snapshot endpoints, cross-series queries via `associations`, and series discovery. Canonical home for the build-info "Unknown" fix: Artifact Signature / Version and SBOM attest on the `digest` series, not the git commit.
- `working-with-findings-and-violations` (Group B) — reading violations / findings / vulnerabilities off an asset or note (`GET /evidence/assets/:asset/violations`, `GET /notes/:uuid/findings`, `GET /notes/:uuid?format=raw`) and the normalized `Finding` schema. Loads `working-with-asset-series`.
- GitHub Copilot CLI support: root `plugin.json` manifest (`skills: ./skills/`) and `using-fianu-skills/references/copilot-tools.md` tool-name mapping. Install with `copilot plugin install fianulabs/fianu-skills`.

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
