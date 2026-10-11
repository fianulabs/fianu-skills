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

27 skills organized in five groups:

- **Meta** — `using-fianu-skills`, `using-fianu-best-practices`, `using-fianu-api`
- **Platform API** — `working-with-tickets`, `working-with-entities`, `working-with-llm-context-rules`, `working-with-evidence-plugins`, `working-with-asset-series`, `working-with-attestations`, `working-with-findings-and-violations`, `working-with-indexes`, `working-with-release-gating`
- **Logic primitives** — `diffing-policies`, `computing-decision-confidence`, `writing-rego-rules`, `writing-cel-expressions`, `designing-policy-templates`, `placing-entities-in-hierarchy`, `matching-existing-controls`, `parsing-framework-documents`
- **Entities as code** — `deploying-entities-as-code`, `deploying-entities-yaml`, `deploying-entities-terraform`
- **Entry-point orchestrators** — `analyzing-tickets`, `managing-ticket-approvals`, `converting-frameworks-to-controls`, `summarizing-evidence`

See `docs/architecture.md` for how they compose.

## Contributing

See `CLAUDE.md` (Claude Code) or `AGENTS.md` (other harnesses) and `docs/authoring-skills.md`.

## License

Apache-2.0. See `LICENSE`. 
