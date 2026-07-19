# Changelog

All notable changes to fianu-skills are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres
to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- GitHub Copilot CLI support: root `plugin.json` manifest (`skills: ./skills/`) and `using-fianu-skills/references/copilot-tools.md` tool-name mapping. Install with `copilot plugin install fianulabs/fianu-skills`.

## [v0.2,1] - 2026-06-15

## [0.2.0] - 2026-06-13

## [0.1.0] — 2026-06-09

### Added
- Initial 17-skill release. See `docs/architecture.md` for the skill inventory.
- Multi-harness manifests: Claude Code, Codex CLI, Gemini CLI.
- SessionStart hook (Claude Code) that bootstraps `using-fianu-skills` automatically.
