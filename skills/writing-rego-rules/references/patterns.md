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
