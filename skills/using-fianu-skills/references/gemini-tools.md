# Gemini CLI tool name mapping

Skills in fianu-skills reference Claude Code tool names. Gemini CLI uses
a different surface; here is the mapping.

| Claude Code | Gemini CLI |
|---|---|
| `Skill` | `activate_skill` |
| `Bash` | `run_shell_command` |
| `Read` | `read_file` |
| `Edit` | `replace` |
| `Write` | `write_file` |
| `Grep` | `search_file_content` |
| `WebFetch` | `web_fetch` |

When a skill says "invoke the X tool," substitute the Gemini equivalent.
Skills loaded via `@./skills/.../SKILL.md` from `GEMINI.md` are auto-loaded
at session start (no `activate_skill` call required for those).
