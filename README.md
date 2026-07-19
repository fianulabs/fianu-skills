# fianu-skills

Skills for building AI agents that operate on the [Fianu](https://fianu.io)
compliance platform — covering ticket workflows, entity management, evidence
summaries, and compliance-framework ingestion.

Installs as a plugin in Claude Code, Codex CLI, Gemini CLI, and GitHub Copilot CLI.

## Install

### Claude Code

```
/plugin marketplace add fianulabs/fianu-skills
/plugin install fianu-skills@fianu-skills
```

### Codex CLI

```
/plugins
```

Then search `fianu-skills` and select Install Plugin.

### Gemini CLI

```
gemini extensions install https://github.com/fianulabs/fianu-skills
```

### GitHub Copilot CLI

```
copilot plugin install fianulabs/fianu-skills
```

## What's inside

17 skills organized in four groups:

- **Meta** — `using-fianu-skills`, `using-fianu-best-practices`
- **Platform API** — `working-with-tickets`, `working-with-entities`, `working-with-llm-context-rules`, `working-with-evidence-plugins`
- **Logic primitives** — `diffing-policies`, `computing-decision-confidence`, `writing-rego-rules`, `designing-policy-templates`, `placing-entities-in-hierarchy`, `matching-existing-controls`, `parsing-framework-documents`
- **Entry-point orchestrators** — `analyzing-tickets`, `managing-ticket-approvals`, `converting-frameworks-to-controls`, `summarizing-evidence`

See `docs/architecture.md` for how they compose.

## Contributing

See `CLAUDE.md` (Claude Code) or `AGENTS.md` (other harnesses) and `docs/authoring-skills.md`.

## License

Apache-2.0. See `LICENSE`.
