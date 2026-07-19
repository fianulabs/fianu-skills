# GitHub Copilot CLI tool name mapping

Skills in fianu-skills reference Claude Code tool names. Copilot CLI uses
a different surface; here is the mapping.

| Claude Code | Copilot CLI |
|---|---|
| `Skill` | `skill` |
| `Bash` | `shell` |
| `Read` | `view` |
| `Edit` | `edit` |
| `Write` | `create` |
| `Grep` | `grep` |
| `WebFetch` | `web_fetch` |

When a skill says "invoke the X tool," substitute the Copilot equivalent.
Copilot auto-discovers skills from the plugin's `skills` path (declared in
`plugin.json`) and loads them by their frontmatter `description` when relevant —
no explicit `skill` call is required to bootstrap `using-fianu-skills`.
