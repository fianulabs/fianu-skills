---
name: working-with-evidence-plugins
description: Use when picking a plugin to source evidence from or discovering its evidence schema. Covers the plugin catalog (SAST, SCA, container scanning, SBOM, signature, DAST, IaC, testing, deployment, pipeline, code review, access control) and GET /controls/:key/schemas.
---

# Working with Evidence Plugins

## Overview

Fianu plugins are evidence sources — they emit notes with structured
payloads that controls evaluate against policy. When designing a new
control or routing an existing control's evidence, an agent needs to (a)
pick the right plugin and (b) understand the shape of that plugin's
evidence so the Rego rule can reference it correctly.

This skill is the canonical home for plugin selection and schema discovery.

## The plugin catalog

The catalog of supported plugins by category lives in
`references/plugin-catalog.md`. Load that file when picking a plugin for a
new control.

## Schema discovery

Once a candidate plugin is chosen, discover its evidence schema:

```
GET /controls/:entity_key/schemas?producer={pluginPath}
```

The response lists the field paths and types available in the plugin's
evidence output (the `input.detail.*` shape that Rego rules reference). Use
these field paths to write the Rego rule via `writing-rego-rules`.

## Selecting a plugin

Decision procedure:

1. Identify the requirement's evidence type — code quality, dependency
   vulnerabilities, container image scan, SBOM presence, signature, runtime
   vulnerabilities, IaC, test results, deployment records, CI/CD execution,
   pull-request review, branch protection, etc.
2. Map evidence type to a plugin category via `references/plugin-catalog.md`.
3. If multiple plugins satisfy the category, prefer the plugin whose schema
   fields best cover the requirement (fewest gaps). Run schema discovery
   for each candidate and compare.
4. If no plugin in the catalog covers the evidence, recommend an
   **API-sourced control** (custom integration). The control subscribes to
   an `api` event source rather than a `plugin` source. See
   `using-fianu-best-practices` → FIANU.md §Controls > Choosing Sources.

## Edge cases

### Plugin in catalog but not deployed in target environment

The catalog reflects what fianu-plugins ships; whether a specific tenant
has the plugin enabled is a deployment question. Schema discovery against
a non-enabled plugin will return an empty/404 response. In that case,
escalate to a human or recommend enabling the plugin.

### Multiple plugins satisfying the same category

Prefer the plugin already configured for the target organization (visible
via the platform admin UI). Do not silently pick a plugin the tenant has
not opted into.

## See also

- `references/plugin-catalog.md` — full plugin catalog by category.
- `writing-rego-rules` — for mapping discovered schema fields onto Rego.
- `using-fianu-best-practices` → FIANU.md §Choosing Sources — when an
  API-sourced control is more appropriate than a plugin-sourced one.
