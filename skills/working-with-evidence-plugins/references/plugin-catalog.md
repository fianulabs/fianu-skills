# Plugin catalog

The categories below map evidence-providing plugins to the controls they
can satisfy. Maintained alongside `../../fianu-plugins` in the core
monorepo; update when new plugins ship.

## Categories and capabilities

| Category | Plugin examples | Evidence provided | Relevant for |
|---|---|---|---|
| **SAST** | Sonarqube, Checkmarx, Semgrep | Code quality metrics, vulnerability findings, coverage | Code quality, security vulnerabilities |
| **SCA** | Snyk, Sonatype, WhiteSource | Dependency vulnerabilities, license compliance | Dependency management, license compliance |
| **Container scanning** | Prisma, Wiz, Trivy, Lacework | Container image vulnerabilities by severity | Container security, image hardening |
| **SBOM** | Syft, CycloneDX | Software bill of materials presence/completeness | Supply chain transparency |
| **Signature** | Sigstore, Cosign | Artifact/commit digital signature verification | Artifact integrity, code signing |
| **DAST** | ZAP, Burp Suite | Runtime vulnerability findings | Application security testing |
| **IaC scanning** | Checkov, Terraform Sentinel | Infrastructure-as-code policy violations | Infrastructure compliance |
| **Testing** | Sonarqube, TestRail | Test results, code coverage percentages | Quality assurance |
| **Deployment** | Kubernetes, ArgoCD | Deployment records, environment promotion | Release management |
| **Pipeline** | GitHub Actions, GitLab CI | CI/CD execution records, build provenance | Build integrity |
| **Code review** | GitHub, GitLab | Pull request review status, approvals | Peer review compliance |
| **Access control** | GitHub, GitLab, Azure DevOps | Branch protection rules, permissions | Access management |
