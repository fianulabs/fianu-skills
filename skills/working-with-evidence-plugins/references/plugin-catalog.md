# Plugin catalog

The categories below map evidence-providing plugins to the controls they
can satisfy. Updated when new plugins ship.

## Producer catalog

<!-- facts:producer-catalog -->
| Plugin | Relation path | Detail fields |
| --- | --- | --- |
| `42crunch-dast` | `42crunch.dast.scan.result` | `apis`, `collection`, `scan_summary` |
| `42crunch-oas` | `42crunch.oas.scan.result` | `apis`, `collection`, `summary` |
| `aquasecurity-trivy` | `trivy.containerscan` | `ArtifactID`, `ArtifactName`, `ArtifactType`, `CreatedAt`, `Metadata`, `ReportID`, `Results`, `SchemaVersion`, `Trivy` |
| `aquasecurity-trivy` | `trivy.iacscan` | `ArtifactID`, `ArtifactName`, `ArtifactType`, `CreatedAt`, `Metadata`, `ReportID`, `Results`, `SchemaVersion`, `Trivy` |
| `bandit-sast` | `bandit.sast` | `errors`, `generated_at`, `metrics`, `results` |
| `bandit-sast` | `bandit.sast.sarif` | `$schema`, `inlineExternalProperties`, `properties`, `runs`, `version` |
| `bitbucket` | `ci.bitbucket.commit` | `ahead_by`, `base`, `behind_by`, `commits`, `head`, `status`, `total_commits`, `url` |
| `blackduck` | `blackduck.sca` | `scan` |
| `checkmarx` | `checkmarx.one.scan.details` | `branch`, `commitHash`, `completedScans`, `correlationId`, `format`, `initiator`, `projectId`, `projectName`, `repoUrl`, `scanId`, `scanReports` |
| `checkmarx` | `checkmarx.sast` | `additionalDetails`, `files`, `link`, `loc`, `project`, `projectId`, `scanType`, `team`, `xissues` |
| `checkmarx` | `checkmarx.sast.scan_report.details` | `originalUrl`, `projectId`, `scanDetails`, `scanId` |
| `checkmarx` | `checkmarx.sca.scan_report.details` | `originalUrl`, `projectId`, `reportUuid`, `scanReport` |
| `cobertura` | `cobertura.testing.coverage` | `branch_rate`, `branches_covered`, `branches_valid`, `complexity`, `line_rate`, `lines_covered`, `lines_valid`, `packages`, `sources`, `timestamp`, `version` |
| `cycode` | `cycode.vulnerabilities` | `check_run`, `pipelineRun`, `project`, `push_event`, `repositoryName`, `repositoryNodeID`, `scan_metadata`, `scmInfo`, `summary`, `vulnerabilities`, `workflow_run` |
| `env-comparison` | `env.comparison.sonarqube.sca` | `benchmark`, `current` |
| `fianu-deployments` | `cd.deployment.asset` | `artifact`, `commit`, `commitTag`, `deployment`, `digest`, `evidence`, `message`, `registry`, `repositories`, `signature`, `tags`, `type`, `uris`, `uuid` |
| `flake8` | `flake8.sast` |  |
| `flake8` | `flake8.sast.junit` | `testsuites` |
| `github` | `ci.commit` | `ahead_by`, `base`, `behind_by`, `commits`, `head`, `status`, `total_commits`, `url` |
| `github` | `ci.commithistory` | `ahead_by`, `base`, `behind_by`, `commits`, `head`, `status`, `total_commits`, `url` |
| `github-actions` | `ci.github.app.build.artifacts` | `artifacts`, `jobs`, `runs`, `suites`, `summary` |
| `github-actions` | `ci.github.app` | `artifacts`, `jobs`, `runs`, `suites`, `summary` |
| `github-actions` | `ci.pipeline` | `branch`, `pipeline`, `runs`, `snapshot`, `summary` |
| `github-actions` | `f.event.github.log.platform.checkmarx.sast.scan_report` |  |
| `github-actions` | `f.event.github.log.platform.checkmarx.sca.scan_report` |  |
| `github-attestations` | `ci.github.attestations` | `artifact`, `attestedCommit`, `class`, `commitDetermined`, `commitMatch`, `createdAt`, `eventCommit`, `evidenceCount`, `evidenceName`, `evidenceUrl`, `predicate`, `predicateBytes`, `predicateTruncated`, `predicateType`, `providerId`, `signer`, `source`, `verificationError`, `verificationMethod`, `verifiedByFianu`, `verifiedByJfrog` |
| `github-attestations` | `ci.github.attestations_https___cyclonedx.org_bom` | `mediaType`, `signature`, `statement`, `verifiedIdentity`, `verifiedTimestamps` |
| `github-attestations` | `ci.github.attestations_https___slsa.dev_provenance_v1` | `mediaType`, `signature`, `statement`, `verifiedIdentity`, `verifiedTimestamps` |
| `github-codeql` | `sast.codeql` | `alerts`, `analyses`, `repository` |
| `github-dependabot` | `ci.dependabot` | `alerts`, `enabled`, `repository` |
| `github-dependency-review` | `ci.dependency.review` | `repository`, `results` |
| `github-file-evidence` | `ci.github.file.evidence` | `files`, `metadata` |
| `github-fileanalyzer` | `ci.github.repository_files` | `tree`, `workflows` |
| `github-rulesets` | `ci.github.repository_rulesets` | `ruleSets`, `ruleSetsComplete`, `ruleSetsError`, `secrets`, `secretsComplete`, `secretsError` |
| `github-secret-scanning` | `ci.github.secret_scanning` | `alerts`, `enabled`, `repository` |
| `gitlab` | `ci.gitlab.commit` | `commit`, `commitDiff`, `mergeRequests`, `signature` |
| `gitlab` | `ci.gitlab.pipeline.build.artifacts` | `asset`, `digest`, `id`, `name`, `properties`, `source`, `tags`, `type`, `version` |
| `gitlab` | `ci.gitlab.pipeline` | `artifacts`, `branch`, `detailedStatus`, `duration`, `jobs`, `pipeline`, `snapshot`, `source`, `status`, `summary` |
| `gitlab` | `f.event.gitlab.log.platform.checkmarx.sast.scan_report` | `filterCategory`, `filterKey`, `instanceKey`, `instanceName`, `integrationPath`, `integrationType`, `matchedPattern`, `original`, `path`, `platformName`, `queryParameters`, `scheme`, `snippet`, `tags`, `url` |
| `gitlab` | `f.event.gitlab.log.platform.checkmarx.sca.scan_report` | `filterCategory`, `filterKey`, `instanceKey`, `instanceName`, `integrationPath`, `integrationType`, `matchedPattern`, `original`, `path`, `platformName`, `queryParameters`, `scheme`, `snippet`, `tags`, `url` |
| `gitlab` | `f.gitlab.clusterimagescan` | `scan`, `version`, `vulnerabilities` |
| `gitlab` | `f.gitlab.containerscan` | `remediations`, `scan`, `version`, `vulnerabilities` |
| `gitlab` | `f.gitlab.dast` | `scan`, `version`, `vulnerabilities` |
| `gitlab` | `f.gitlab.dependencyscan` | `dependency_files`, `scan`, `version`, `vulnerabilities` |
| `gitlab` | `f.gitlab.sast` | `remediations`, `scan`, `version`, `vulnerabilities` |
| `gitlab` | `f.gitlab.secretdetection` | `scan`, `version`, `vulnerabilities` |
| `gitlab` | `f.gitlab.testing.coverage.cobertura` | `branch_rate`, `branches_covered`, `branches_valid`, `complexity`, `line_rate`, `lines_covered`, `lines_valid`, `packages`, `sources`, `timestamp`, `version` |
| `gitlab` | `f.gitlab.testing.coverage.jacoco` | `report` |
| `gitlab` | `f.gitlab.testing.junit` | `testsuites` |
| `gitlab-file-evidence` | `ci.gitlab.file.evidence` | `files`, `metadata` |
| `gitlab-security` | `f.gitlab.containerscan.trivy` | `artifact`, `remediations`, `scan`, `schema`, `version`, `vulnerabilities` |
| `gitlab-security` | `f.gitlab.sast.checkov` | `remediations`, `scan`, `schema`, `version`, `vulnerabilities` |
| `gitlab-security` | `f.gitlab.sast.kics` | `remediations`, `scan`, `schema`, `version`, `vulnerabilities` |
| `gitlab-security` | `f.gitlab.sast.semgrep` | `remediations`, `scan`, `schema`, `version`, `vulnerabilities` |
| `gitlab-security` | `f.gitlab.secretdetection.gitleaks` | `remediations`, `scan`, `schema`, `version`, `vulnerabilities` |
| `gitlab-security` | `f.gitlab.security.clusterimagescan` | `artifact`, `remediations`, `scan`, `schema`, `version`, `vulnerabilities` |
| `gitlab-security` | `f.gitlab.security.containerscan` | `artifact`, `remediations`, `scan`, `schema`, `version`, `vulnerabilities` |
| `gitlab-security` | `f.gitlab.security.dast` | `remediations`, `scan`, `schema`, `version`, `vulnerabilities` |
| `gitlab-security` | `f.gitlab.security.dependencyscan` | `remediations`, `scan`, `schema`, `version`, `vulnerabilities` |
| `gitlab-security` | `f.gitlab.security.sast` | `remediations`, `scan`, `schema`, `version`, `vulnerabilities` |
| `gitlab-security` | `f.gitlab.security.secretdetection` | `remediations`, `scan`, `schema`, `version`, `vulnerabilities` |
| `gitlab-security` | `f.gitlab.security.vulnerabilities` | `project_id`, `summary`, `vulnerabilities` |
| `gitlab-workflow-config` | `ci.gitlab.workflow_config` | `commitSha`, `errorMessage`, `fileContent`, `fileContentRaw`, `fileExists`, `fileName`, `projectId` |
| `helm` | `helm.sign` | `packagedDeployableArtifacts`, `rekor`, `verification` |
| `jacoco` | `jacoco.testing.coverage` | `report` |
| `jenkins` | `ci.jenkins.pipeline.build.artifacts` | `artifacts`, `buildNumber`, `event`, `images`, `jobName`, `scmInfo`, `state`, `system`, `url`, `workflow` |
| `jenkins` | `ci.jenkins.pipeline.in_progress` | `artifacts`, `buildNumber`, `event`, `images`, `jobName`, `scmInfo`, `state`, `system`, `url`, `workflow` |
| `jenkins` | `ci.jenkins.pipeline` | `artifacts`, `buildNumber`, `event`, `images`, `jobName`, `scmInfo`, `state`, `system`, `url`, `workflow` |
| `jenkins` | `f.event.jenkins.log.platform.checkmarx.sast.scan_report` |  |
| `jenkins` | `f.event.jenkins.log.platform.checkmarx.sca.scan_report` |  |
| `jfrog-signatures` | `(default)` | `artifact`, `attestedCommit`, `class`, `commitDetermined`, `commitMatch`, `createdAt`, `createdBy`, `downloadPath`, `eventCommit`, `evidenceCount`, `evidenceName`, `evidenceUrl`, `platformUrl`, `predicate`, `predicateBytes`, `predicateCategory`, `predicateSlug`, `predicateTruncated`, `predicateType`, `providerId`, `signer`, `source`, `verificationError`, `verificationMethod`, `verifiedByFianu`, `verifiedByJfrog` |
| `jfrog-xray` | `jfrog.xray.artifact_summary` | `general`, `issues`, `licenses`, `operational_risks`, `policyViolations` |
| `jira-batch` | `jira.no_response` |  |
| `jira-events` | `jira.issue.created` | `changelog`, `issue`, `issue_event_type_name`, `timestamp`, `user`, `webhookEvent` |
| `jira-events` | `jira.issue.deleted` | `changelog`, `issue`, `issue_event_type_name`, `timestamp`, `user`, `webhookEvent` |
| `jira-events` | `jira.issue.updated` | `changelog`, `issue`, `issue_event_type_name`, `timestamp`, `user`, `webhookEvent` |
| `jira-events` | `jira.project.archived` | `project`, `timestamp`, `user`, `webhookEvent` |
| `jira-events` | `jira.project.created` | `project`, `timestamp`, `user`, `webhookEvent` |
| `jira-events` | `jira.project.deleted` | `project`, `timestamp`, `user`, `webhookEvent` |
| `jira-events` | `jira.project.restore_archived` | `project`, `timestamp`, `user`, `webhookEvent` |
| `jira-events` | `jira.project.restore_soft_deleted` | `project`, `timestamp`, `user`, `webhookEvent` |
| `jira-events` | `jira.project.soft_deleted` | `project`, `timestamp`, `user`, `webhookEvent` |
| `jira-events` | `jira.project.updated` | `project`, `timestamp`, `user`, `webhookEvent` |
| `jira-events` | `jira.version.created` | `timestamp`, `version`, `webhookEvent` |
| `jira-events` | `jira.version.deleted` | `timestamp`, `version`, `webhookEvent` |
| `jira-events` | `jira.version.released` | `timestamp`, `version`, `webhookEvent` |
| `jira-events` | `jira.version.unreleased` | `timestamp`, `version`, `webhookEvent` |
| `jira-events` | `jira.version.updated` | `timestamp`, `version`, `webhookEvent` |
| `jira-pullrequest` | `ci.commithistory.jira` | `ahead_by`, `base`, `behind_by`, `commits`, `head`, `status`, `total_commits`, `url` |
| `jira-pullrequest` | `ci.commithistory.module.jira` | `ahead_by`, `base`, `behind_by`, `commits`, `head`, `status`, `total_commits`, `url` |
| `jira-pullrequest` | `jira.github.pull_request.event` | `commits`, `issue`, `pullRequest` |
| `junit` | `testing.cd.functional.junit` | `testsuites` |
| `junit` | `testing.cd.unit.junit` | `testsuites` |
| `junit` | `testing.ci.functional.junit` | `testsuites` |
| `junit` | `testing.ci.unit.junit` | `testsuites` |
| `junit` | `testing.unit.junit` | `testsuites` |
| `kyverno-linting` | `testing.kyverno.helm.linting` | `apiVersion`, `kind`, `metadata`, `results`, `scope`, `scopeSelector`, `summary` |
| `lacework` | `lacework.containerscan` | `cve`, `policy` |
| `manifest-cyber-sbom` | `manifest_cyber.sbom` | `bundle`, `verification` |
| `multimodule-commit-history` | `ci.commithistory.module` | `ahead_by`, `base`, `behind_by`, `commits`, `head`, `status`, `total_commits`, `url` |
| `mypy` | `mypy.sast` | `results` |
| `mypy` | `mypy.sast.junit` | `testsuites` |
| `pipaudit` | `pipaudit.sca.cyclonedx` | `$schema`, `annotations`, `bomFormat`, `components`, `compositions`, `declarations`, `definitions`, `dependencies`, `externalReferences`, `formulation`, `metadata`, `properties`, `serialNumber`, `services`, `signature`, `specVersion`, `version`, `vulnerabilities` |
| `pipaudit` | `pipaudit.sca` | `dependencies`, `fixes` |
| `prismacloud` | `prismacloud.containerscan` | `image`, `scan_result` |
| `pytest` | `pytest.testing.coverage.cobertura` | `coverage` |
| `pytest` | `pytest.testing.coverage` | `files`, `meta`, `totals` |
| `pytest` | `pytest.testing` | `collectors`, `created`, `duration`, `environment`, `exitcode`, `root`, `summary`, `tests` |
| `pytest` | `pytest.testing.junit` | `testsuites` |
| `sigstore-tools` | `blob.sign.file` | `bundle`, `certificate`, `uri`, `verification` |
| `sigstore-tools` | `blob.sign.sbom` | `bundle`, `certificate`, `verification` |
| `sigstore-tools` | `cosign.sign.asset.attestations` | `attestations` |
| `sigstore-tools` | `cosign.sign.asset.attestations.sbom` | `attestations` |
| `sigstore-tools` | `cosign.sign.asset.helm` | `bundles`, `signature`, `verification` |
| `sigstore-tools` | `cosign.sign.asset.sbom` | `bundles`, `signature`, `verification` |
| `sigstore-tools` | `cosign.sign` | `bundles`, `signature`, `verification` |
| `snyk-sast` | `snyk.sast` | `error`, `scan` |
| `snyk-sca` | `snyk.sca` | `scan`, `schemaFormat` |
| `sonarqube` | `sonarqube.sca` | `measures`, `properties`, `qualityGate`, `task` |
| `sonarqube` | `testing.sonarqube.cov.execution` |  |
| `sonarqube` | `testing.sonarqube.cov.generic` | `-version`, `file` |
| `synopsys-coverity` | `sast.coverity` | `desktopAnalysisSettings`, `error`, `formatVersion`, `issues`, `suppressedIssueCount`, `type`, `warnings` |
| `tekton` | `ci.tekton.pipelinerun.build.artifacts` | `asset`, `digest`, `id`, `name`, `properties`, `source`, `tags`, `type`, `version` |
| `tekton` | `ci.tekton.pipelinerun` | `artifacts`, `parameters`, `pipelineRun`, `scmInfo`, `tasks`, `tektonHost` |
| `tekton` | `f.event.tekton.log.platform.checkmarx.sast.scan_report` |  |
| `tekton` | `f.event.tekton.log.platform.checkmarx.sca.scan_report` |  |
| `tenable-containerscan` | `tenable.containerscan` | `Digest`, `EndTime`, `ImageId`, `Link`, `OperatingSystem`, `Repository`, `ScanTime`, `Success`, `Tag`, `Version`, `Vulnerabilities`, `VulnerabilitySeverities` |
| `testrail-runs` | `testrail.run_results` | `plan`, `results`, `run`, `webhook` |
| `wiz-containerscan` | `wiz.containerscan` | `createdAt`, `createdBy`, `extraInfo`, `id`, `outdatedPolicies`, `policies`, `projects`, `result`, `scanOriginResource`, `startedAt`, `status`, `tags` |
| `wiz-iac` | `wiz.iacscan` | `createdAt`, `createdBy`, `extraInfo`, `id`, `outdatedPolicies`, `policies`, `projects`, `reportUrl`, `result`, `scanOriginResource`, `startedAt`, `status`, `taggedResource`, `tags` |
<!-- /facts:producer-catalog -->
