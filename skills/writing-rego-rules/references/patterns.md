# OPA v1 Rego patterns for Fianu controls

All Fianu Rego rules use OPA v1 syntax. Always begin with:

```rego
package rule
import rego.v1
```

`input.detail.*` paths are the evidence shape (provided by the subscribed
plugin). `data.*` paths are the policy values.

## Threshold check (count vs maximum)

Use when policy declares a maximum count of something in evidence.

```rego
pass if {
    policy := data.vulnerabilities
    vulns := input.detail.vulnerabilities
    critical := count([v | v := vulns[_]; v.rating == "CRITICAL"])
    critical <= policy.critical.maximum
}
```

## Score comparison (>= minimum / <= maximum)

Use when policy declares a minimum score.

```rego
pass if {
    policy := data.scores
    input.detail.measures.reliability >= policy.reliability.minimum
    input.detail.measures.maintainability >= policy.maintainability.minimum
}
```

## Presence check (must exist)

Use for "the artifact must have an SBOM" controls.

```rego
pass if {
    input.detail.sbom != null
    count(input.detail.sbom.components) > 0
}
```

## Freshness check (must be recent)

Use for controls requiring evidence within a time window.

```rego
pass if {
    policy := data.freshness
    age_seconds := time.now_ns()/1e9 - input.detail.generated_at_unix
    age_seconds <= policy.maximum_age_seconds
}
```

## Multi-metric (all sub-checks must pass)

Use when one control evaluates multiple measurements. Container Scan is the
canonical example — critical/high/medium/low vulnerability counts must all
be at or below policy maxima.

```rego
pass if {
    policy := data.vulnerabilities
    vulns  := input.detail.vulnerabilities

    critical := count([v | v := vulns[_]; v.rating == "CRITICAL"])
    high     := count([v | v := vulns[_]; v.rating == "HIGH"])
    medium   := count([v | v := vulns[_]; v.rating == "MEDIUM"])
    low      := count([v | v := vulns[_]; v.rating == "LOW"])

    critical <= policy.critical.maximum
    high     <= policy.high.maximum
    medium   <= policy.medium.maximum
    low      <= policy.low.maximum
}
```

## List (ban / allow)

Use when the policy names items that must not appear (a ban list) or the
only items that may appear (an allow list): banned models, allowed licenses,
approved base images.

- The policy holds item names as `array.string` under `<section>.banned` or
  `<section>.allowed`, and nothing else: no reasons, owners or dates (see
  `designing-policy-templates`).
- The rule reads only the evidence items of the listed kind and builds each
  item's name the way the user writes it in the list (`group/name`, not an
  internal id).
- Each failing item records one violation: the item, the version the
  evidence reports, and a one-line message.
- Evidence that lists no items of the listed kind is `notFound`, not `fail`.
- `pass` counts the failing items themselves, not the recorded violations.

CycloneDX AI-BOM example, failing on any banned model:

```rego
package rule
import rego.v1
default pass := false
models contains {"name": model_name(c), "version": object.get(c, "version", "")} if {
  some c in input.detail.components
  c.type == "machine-learning-model"
}
# CycloneDX makes group and version optional: a model missing either still counts.
model_name(c) := sprintf("%s/%s", [c.group, c.name]) if c.group
model_name(c) := c.name if not c.group
prohibited contains m if {
  some m in models
  m.name in data.models.banned
  not m.name in data.exceptions.models
}
violations contains m.name if {
  some m in prohibited
  fianu.record_violation(false, {"model": m.name, "version": m.version, "message": sprintf("%s %s is a prohibited model", [m.name, m.version])})
}
notFound if count(models) == 0
pass if { count(models) > 0; count(prohibited) == 0 }
```

For an allow list, swap the membership test in `prohibited` to
`not m.name in data.models.allowed`.

Policy template, in the control's `spec.yaml`:

```yaml
policyTemplate:
  measures:
    - name: models
      type: section
      children:
        - name: banned
          type: metric
          value: array.string
    - name: exceptions
      type: section
      children:
        - name: models
          type: metric
          value: array.string
```

Policy values:

```yaml
models:
  banned:
    - deepseek-ai/DeepSeek-R1
    - meta-llama/Llama-2-7b-hf
exceptions:
  models: []
```

## Exceptions

A control that judges items (commits, models, packages, findings) SHOULD
support exceptions by default. Add an `exceptions.<items>` metric of
`array.string` to the template and subtract it in the rule, as `prohibited`
does above. The official Code Review History control does the same with
`exceptions.commits` and `exceptions.authors`.

The base policy leaves the list empty. A Fianu exception is a layered,
temporary policy: it fills `exceptions.<items>` for only the assets its index
covers, until it expires. The rule needs no date logic. See
`using-fianu-best-practices` → FIANU.md §Policies & Exceptions.

When the evidence items carry an `id`, the `withoutExceptions(items,
exceptions)` builtin is the alternative. It returns the items not excepted;
each exception is an object with `id` and `expiration`, and an expired one no
longer applies. The exceptions list is then `array.object`.

```rego
open_findings := withoutExceptions(input.detail.findings, data.exceptions.findings)
```

Add a `required` bool (`notRequired if { not pass; data.required == false }`)
only when a user asks to waive the whole control, never to except items.
