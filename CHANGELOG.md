# Changelog

All notable changes to fianu-skills are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres
to [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
