# Codex CLI tool name mapping

Skills in fianu-skills reference Claude Code tool names. Codex CLI uses
the same `Skill` tool (renamed `skill`) for skill invocation, and provides
equivalents for shell and file operations.

| Claude Code | Codex CLI |
|---|---|
| `Skill` | `skill` |
| `Bash` | `shell` |
| `Read` | `read_file` |
| `Edit` | `apply_patch` |
| `Write` | `apply_patch` (new-file mode) |
| `Grep` | `shell` with `rg` |
| `WebFetch` | `web_fetch` |

When a skill says "invoke the X tool," substitute the Codex equivalent.
