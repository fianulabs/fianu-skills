# Fianu Data Model

- [Assets](#assets) (done)
- [Entities](#entities) (in progress)
- [Notes](#notes) (not started)




## Assets

The Fianu platform defines an asset as anything that an attestation can be attributed to. Another way to say say this would be, an asset is anything that could comply or fail to comply with defined controls or policies.

Assets form the foundation of Fianu’s governance model. Every control, policy, exception, and gate is evaluated against one or more assets within this framework.

Fianu classifies assets into three primary categories:

- Fixed Assets
- Logical Assets
- Releases (specialized assets)

### Fixed Assets

Fixed assets (FA) are software assets that have a concrete, uniquely identifiable form and can be directly referenced, versioned, and managed within technical systems. They represent tangible components in the software lifecycle and typically exist as files, directories, or generated outputs.

Fianu currently supports three fixed assets:

- **Source code repository**: A centralized version-controlled location (such as Git) where a software project’s source code, configuration, and change history are stored and collaboratively maintained.
- **Module**: A logically grouped subdirectory within a larger repository that contains related source code and resources, typically built, tested, and versioned as a distinct component of the overall system.
- **Artifact**: A generated, distributable output of the software lifecycle such as a package, binary, container image, or SBOM that is published, deployed, or used as part of a running system. Artifacts are immutable. Any change results in a new artifact with a distinct identity.

---

### Logical Assets

Logical assets (LA), formerly called abstract assets, are organizational groupings used to structure, manage, and govern fixed assets at business, architectural, and operational levels.

They do not correspond to a single physical or digital object. Instead, they represent ownership models, deployment boundaries, and policy scopes composed of fixed assets and other logical assets.

Logical assets enable consistent governance, reporting, and policy application across complex enterprise environments.

#### Hierarchy Requirements

Logical assets must maintain a hierarchical structure to ensure accurate ownership assignment, control inheritance, and policy enforcement. Fianu requires organizations to define at least one logical asset layer and supports up to four configurable levels.

Examples of logical assets include:

- *Line of Business: A collection of portfolios and systems that support a common business function or organizational unit.*
- *Portfolio: A collection of related software products that are integrated, coordinated, or operate within a shared domain.*
- *Product: A collection of applications and services that together deliver a cohesive customer-facing or internal capability.*
- *Application: A deployable system composed of multiple software components that operate together to provide a defined function.*

**Note**: The default logical asset 1 is "Application." This can be changed only by Fianu system administrators.

---

### Asset Hierarchy

Fianu enforces a structured hierarchy to ensure consistent governance and traceability across all assets. Organizations may configure the logical asset layers, but fixed asset positions are immutable.

| Order (Descending) | Category / Code                 | Type    | Name            | Configurable    |
| ------------------ | ------------------------------- | ------- | --------------- | --------------- |
| 7                  | IT Catalog / `4000`             | Logical | Logical Asset 4 | Name & Position |
| 6                  | IT Catalog / `3000`             | Logical | Logical Asset 3 | Name & Position |
| 5                  | IT Catalog / `2000`             | Logical | Logical Asset 2 | Name & Position |
| 4                  | IT Catalog / `1000`             | Logical | Logical Asset 1 | Name & Position |
| 3                  | Software Inventory / `3000`     | Fixed   | Repository      | Name            |
| 2                  | Software Inventory / `2000`     | Fixed   | Module          | Name            |
| 1                  | Software Inventory / `1000`     | Fixed   | Artifact        | N/A             |

#### Parent-Child Model

Each asset belongs to a single parent in the hierarchy.

An asset functions both as:

- A compliance subject
- A container for subordinate assets

As a result, compliance posture and control status can be aggregated upward.

Artifacts are leaf nodes and do not contain child assets.

#### Module Exception

Modules may optionally belong to a different Logical Asset 1 than their parent repository. This configuration is supported for edge cases but is strongly discouraged, as it weakens ownership clarity and governance alignment.

---


### Releases

Releases represent a specialized asset type designed to govern the transition of software from development to production.

They function as staging and governance container for multiple assets prior to deployment.

#### Background

In enterprise environments, the term “release” is interpreted differently across disciplines:

- <u>Engineering</u>: Deployment of new code to production
- <u>Risk and Change Management</u>: A coordinated set of approved changes
- <u>Business</u>: Introduction of new customer-facing functionality

These interpretations often diverge, leading to misalignment between technical execution, governance oversight, and business communication.

Fianu releases are designed to unify these perspectives into a single, auditable construct.

#### Definition

To understand releases, it is helpful to contrast them with other asset types.

To understand how releases function within the Fianu platform, it is helpful to first contrast their behavior with that of other asset types.

- Logical assets, such as applications or products, function primarily as structural containers. They define organizational and governance boundaries but do not produce technical outputs. Over time, their internal composition may change, but their identity remains stable.

- Repositories (or modules) share some of this persistence but introduce versioning and production. A repository evolves through commits, branches, and merges while retaining a consistent identity. At the same time, repositories generate artifacts, which represent concrete outputs of the development process.

- Artifacts differ fundamentally from both logical assets and repositories. They are immutable by design. An artifact represents a specific build output at a specific point in time. If its contents change, it becomes a new artifact with a new identity. This immutability is enforced in Fianu through digital signing and provenance controls.

Releases combine elements of all three of these asset types.

Similar to a logical asset, a release acts as a container. It groups together repositories, modules, artifacts, documentation, and governance records into a single unit of delivery.

However, like a repository, a release evolves over time. While it is open, assets may be added, removed, or replaced. Documentation may be updated. Approvals may be granted or revoked. Compliance status may change. Throughout this process, the release maintains a continuous identity.

Lastly, a release acts like an artifact in that it ultimately becomes immutable. Once it is closed, its contents and compliance posture are fixed and preserved as an auditable record.

#### Lifecycle and Change History

A release may be created long before any software reaches production. During its lifecycle, it can change form many times as assets are incorporated, updated, or removed.

These changes do not create a new release. Instead, Fianu records each modification in a comprehensive change history. This history enables auditors and governance teams to reconstruct how a release reached its final state, including which assets were included at each stage, when controls were satisfied, and when exceptions were granted.

Unlike source control systems, this historical record is not intended for technical rollback. Its purpose is governance transparency and accountability. It explains why a release looks the way it does, rather than providing a mechanism to revert it.

The release history also captures changes in the compliance status of contained assets. If an artifact fails a security control, if a policy exception is approved, or if a gate is overridden, those events become part of the permanent record of the release.

#### Governance and Control Application

In many enterprise environments, certain controls cannot be evaluated meaningfully at the level of individual components. They require system-level validation across multiple repositories, services, or deployment units.

Fianu enables such controls to be assigned directly to releases.

For example, a control governing user acceptance testing may apply to a coordinated group of services that must be validated together. In this case, the corresponding attestation is recorded at the release level rather than against any single artifact. This approach allows organizations to express governance requirements that span technical boundaries and to document compliance for integrated systems rather than isolated components.

Releases may also be subject to approval gates, policy enforcement rules, and exception workflows. These mechanisms operate in parallel with asset-level controls and provide an additional layer of oversight for production changes.

#### Closure and Immutability

When a release reaches its final stage and is approved for completion, it is formally closed.

At this point, the release becomes immutable. Its contents, documentation, approvals, and compliance status are locked and cannot be modified. The closed release serves as a permanent audit artifact representing what was delivered, how it was governed, and under what conditions it was approved.

Any subsequent changes to release or its underlying components require the creation of a new release. This preserves historical integrity and prevents retroactive modification of compliance records.

In this closed state, a release functions similarly to an artifact. It represents a finalized output of the delivery and governance process and provides durable evidence for regulatory, internal audit, and risk management purposes.



## Entities

The Fianu platform defines an entity as a global configuration item that contributes to the creation, result, or enforcement of an attestation.

Entities are:

- Versioned: Fianu ensures complete reproducibility by versioning every change to an entity.
- Access controlled: Each entity can assign owners, managers, and approvers, as well as inherit access from its parent entity.
- Configurable through dashboard or GUI

Entities are ordered by either a one-to-one or one-to-many child-to-parent relationship and maintain a hierarchical structure that's segmeneted by the following areas of interest:

- [Compliance](#compliance)
- [Enforcement](#enforcement)
- [Integration](#integration)
- [Deployment](#deployment)

---

### Compliance
```txt
┌──────────────┐
│    Domains   │
└──────────────┘
       ↓        
┌──────────────┐
│ Collections  │
└──────────────┘
       ↓        
┌──────────────┐
│   Controls   │
└──────────────┘
       ↓        
┌──────────────┐
│   Policies   │
└──────────────┘
       ↓        
┌──────────────┐
│   Indexes    │
└──────────────┘
```

#### Domains

Domains are groups of collections based on broad areas of governance. This is the highest level of organizing governance and is intended for broad categorization.

##### Best Practices

Organizations must have at least one domain, but domains should be used sparingly and users should take a broach approach when creating them. Large enterprises may have anywhere from 3-6 domains, but are advised against creating more than 10. Whereas smaller companies should aim for 1-3 domains.

##### Example Use Cases

- Domains can be used to represent control frameworks, such as SOX, NIST, or GDPR
- Domains can be used to segment controls based on the type of software, such as an “application compliance” domain or an “infrastructure compliance” domain

##### Relationship

> **Parent**: None
>
> **Child**: One or many collections

##### Permissions

- Owner
  - Can make changes to the domain
  - Can add or remove collections from the domain
  - Can approve requests to make changes to the domain
  - Can approve requests to add or remove collections from the domain
- Manager
  - Can make changes to the domain
  - Can approve requests to make changes to the domain
  - Can approve requests to add or remove collections from the domain
- Approver
  - Can approve requests to add or remove collections from the domain



---

#### Collections

Collections are groups controls that fall under a similar area of interest. In other words, collections are grouped based on either the stage in the SDLC, the category of control (Security, QA, etc.), or stakeholder ownership.

##### Best Practices

Every control must belong to at least one collection. Unlike domains, we recommend creating anywhere from 5-20 collections, depending on the following

- The number of controls implemented in the organization
- The range of SDLC phases covered by controls
- The division of stakeholder ownership
- The number of domains

A corner case arises from the restriction that collections can only belong to one domain, so in situations where a similar group of controls should exist in two domains, there may be two collections that share the same name. For example, Code Review and Commit Signature would likely existin in both a "IaC Compliance" domain and an "Application Compliance" domain. The reason why this is a suggested practice is that it does not require duplication of controls because a single control can serve two different contexts (i.e. domains).

##### Example Use Cases

- A collection called "Security," containing application security controls, and where the director of AppSec is the collection owner and can approve changes to any control or any policy in the Security collection
- Two collections called "Source Code," each having the same two controls "code review" and "commit signature" ─ fairly standard controls for anything stored in source code ─ but one collection belongs to the "Application Compliance" domain and one collection belongs to the "IaC Compliance" domain

##### Relationship

> **Parent**: One domain
>
> **Child**: One or many controls

##### Permissions

- Owner
  - Can make changes to the collection
  - Can add or remove controls from the collection
  - Can request the collection move to a different domain
  - Can approve requests to make changes to the collection
  - Can approve requests to add or remove controls from the collection

- Manager
  - Can make changes to the collection
  - Can approve requests to make changes to the collection
  - Can approve requests to add or remove controls from the collection

- Approver
  - Can approve requests to add or remove controls from the collection




---

#### Controls

Controls are configurable units of code that measure compliance. Each control consumes evidence and evaluates it against policy. The output of each evaluation is an immutable attestation. Essentially, they're applets that subscribe to event sources and execute OPA Rego rules to determine pass, fail, warn, etc.

##### Best Practices

###### Designing a Control

It is important to be deliberate when deciding the evaluations that a control will perform. In some cases, it makes sense to perform multiple evaluations in a single control, but that may not always be the case. When deciding whether to create one control with multiple evaluations or break out each evaluation into its own control, consider whether or not it's appropriate for a software asset to pass one evaluation and fail another, or if it's better to fail the entire control when just one evaluation fails.

> When a single policy is sufficient for managing the control requirements, grouping multiple evaluations into a single control is likely the best approach. However, you expect that a subset of policy will change frequently compared to the rest of the policy, it's recommended that you break out into separate controls.

For example, a control called "Container Scan" may evaluate the number of critical, high, medium, and low vulnerabilities in a container image. This *could* be broken up into four separate controls, one for each vulnerability rating, but Fianu believes that performing all four evaluations in the same control offers the best user experience in this scenario. First, the definition of passing a container scan can be succintly expressed in an OPA rule by measuring whether the count of of vulnerabilities in a container scan exceed the maximum allowed by the control policy. Second, using line items that measure the count of vulnerabilities by their severity rating is trivial and the user (in this case a developer) would likely understand that in order to pass the control, no vulnerabilty counts may exceet the maximum set for each rating.

*Example policy and OPA rule (i.e. evaluation) for Container Scan:*

**Policy**

```yaml
vulnerabilities:
	critical:
		maximum: 0
	high:
		maximum: 0
	medium:
		maximum: 0
	low:
		maximum: 0
```

**Evaluation**

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

On the other hand, separating measurements may be appropriate. For example, let's say an organization would like to create controls that leverage SonarQube's static code analysis capability. SonarQube has dozens of metrics that could be included and the effort for remediating one failed metric could differ greatly from the effort required to remediate another. So to group all of the metrics under a  "Static Code Analysis" control would not be appropriate. Instead, the measurements should be broken apart into separate controls. Perhaps separate code coverage into two controls, one control called "Overall Code Coverage" and another control called "New Code Coverage," while grouping reliability and maintainability scores into a single control called "Code Quality." The result would be three distinct controls with presumably different policy lifecycles. But ultimately, the user has a more clear understand of each requirement and why one control may be failing. 

*Example policy and OPA rule (i.e. evaluation) for Code Quality:*

**Policy**

```yaml
scores:
	reliability:
		minimum: A
	maintainability:
		minimum: B
```

**Evaluation**

```rego
pass if {
	policy := data.scores
	
	input.detail.measures.reliability     >= policy.reliability
	input.detail.measures.maintainability >= policy.maintainability
}
```



###### Creating a Policy Template

Policy templates define the format in which policies values will be set. Templates have four main functions:

1. Creating a schema whereby the control's OPA rule can reference the policy via dot-separated path
2. Defining the GUI-based form for users that prefer to use the Fianu dashboard to create or change policies
3. Defining the YAML schema for users that prefer to use a policy-as-code approach to creating or changing policies
4. Enforcing accuracy of data types when values are set by a user

Essentially, a policy defines the "keys" as well as they data type of the "value" that will be set later. Although policies can be represented as a GUI form, they also can be represented as YAML (when stored in source code) and JSON (when stored in an attestation). Therefore Fianu requires that each policy template key conform to the following syntax rules:

- Cannot start with a number
- Accepts alphanumeric characters
- Keys are case sensitive
- No spaces or special characters, except for `_`
- Words should be separated with an underscore (e.g. `vulnerability_count`)

When creating a policy template, consider readability first and foremost. Although a control creator can add comments to each line of the policy template to provide context for policy creators, the most user-friendly policy templates read as closely to a real sentence as possible and provide the user with enough verbage to convey *what* the control is evaluating and *how*.



Below are three examples of the same policy in different templates.

**Example 1**

This policy is the most user-friendly template. It's self-evident to users that the control is evaluating whether the count of critical and high vulnerabilities exceed the maximum allowed by the policy. This template provides clarity for users while not being overly verbose.

```yaml
vulnerabilities:
	critical:
		maximum: 0
	high:
		maximum: 0
```

**Example 2**

This policy template is slightly less user friendly. It is terse and does communicate that the control will be evaluating whether the count of critical and high exceed the maximum allowed by the policy. However, it does not describe what critical and high are counting (in this case, vulnerabilities). This template has the potential to confuse users.

```yaml
critical:
	max: 0
high
	max: 0
```

**Example 3**

This policy template is the least user friendly. It shows simply a number for critical and high. The user does not know what critical and high are measuring nor whether the control is looking for less than, greater than, or equal to the value set. This will likely confuse users.

```yaml
critical: 0
high: 0
```



###### Naming a Control

Control names should be indicate the activity being performed. Typically, the name of the control indicates the thing that's being evaluated to measure compliance, such as "Code Coverage." This is an effective control name because it describes the metric (percent value of lines of code covered by unit tests) that will be compared against policy minimum to determine pass to fail.

Most controls are performing some sort of measurement, but there are plenty of situations in which a control simply validates the existence of something, such as "Artifact Signature" or "SBOM," where there is no measurement, per-se, but rather a simple check to see that the required item exists in the proper state. For controls of this nature, the name should simply reflect the item that must exist, and not the existence itself. So a control named "SBOM Existence," while descriptive of the thing that's being measured, is not appropriate in this scenario. Instead, simply naming the control "SBOM" would be the preferred approach.

It is recommended that controls not be named after the platform or tool iteslf. For example, a control measuring the results of software composition analysis (SCA) originating from Sonatype should not be called "Sonatype Scan." Instead it should be called "Software Composition Analysis," or something similarly generic. The reason for this is that it is common for enterprises to change point solution platforms in their DevSecOps toolchain, so its important that the control requirment remains independent of the name of the vendor, tool, or platform used to meet that requirement.

On occasion, the control name and the type of platform or tool that performs the activity are the same. One example of this is SAST,  where the control name and the type of platform generating the evidence are the same. However this is uncommon and should not be common practice.

###### Choosing Sources

Sources (sometimes referred to as "event sources") are the data feeds the supply Fianu with evidence that controls can use to evaluate against policy. Sources are designed to be event-driven, so from an architecture standpoint the data is queued in an event broker. Each event that reaches the broker is assigned an identified based on the source from which it originated. One-by-one events are pulled off of the queue and executed by each control that subscribes to that event's source. Essentially, by subscribing to an event source, a user has determined the type of evidence that the control will use to evaluate compliance. Controls must subscribe to at least one source, but there is no limit for how many sources a control can subscribe to. A challenge

There are three types of event sources:

| Type    | Description                                                  |
| ------- | ------------------------------------------------------------ |
| Plugin  | A plugin source produces Fianu note occurrences that originate from a third-party integration (i.e. plugin), created either by Fianu or an end user. Fianu has over 60 plugins that cover the most popular DevSecOps and QA platforms. If a user wishes to subscribe to a plugin source, they must choose which plugin to subscribe to. |
| API     | An API source produces Fianu note occurrences originating from an API endpoint. This event source is used when the control must evaluate data produced by a custom-built tool where simply pushing data to Fianu via API is easier for the customer than building a full Fianu plugin. The URL for API endpoint will be derived from the control path and the endpoint will be active once the control has been created. |
| Control | A control source produces signed attestations, as Fianu note attestations, from an existing control. This is the least common choice for an event source but can be useful if the control that you are building is predicated on the attestation result of a different control. If a user wishes to subscribe to a control source, they must choose which control to subscribe to. |

*A Caution for Users*

Although Fianu notes are structured payloads, the `detail` block ─ the dedicated section a Fianu note that does not guarantee JSON structure ─ is where the evidence that will be evaluated by a control most likely exists. To solve this problem, each event source maintains its own structure for data in the `detail` section of the Fianu note. While this simplifies the control building process, users are encouraged to limit the number of sources that a control subscribes to, as each additional event source requires more control evaluation logic to account for the different JSON formats.

###### Control Scope

Controls also have a niche configuration that can may be confusing to some users. It's called "scope." The scope of a control declares which asset type is performing the control activity, and thus which type of asset will see the attestation.

There are four default options for control scope but up to eight options may be available for the user to select depending on how many abstract assets are configured in the organization. So if an organization only creates 2 abstract asset types (e.g. "Application" and "Line of Business") then the user will see 6 options, not 4. Similarly, if they leverage all four abstract asset levels, they will see 8 options.

1. Abstract asset (levels 1-4)
2. Repository
3. Module
4. Artifact
5. Release

The most common control scopes are repository and artifact because the majority of SLDC activity can be attributed to one of those two asset types. For example, controls such as Code Review, Branching Strategy, or Code Coverage would be scoped to the repository. In some cases, however, a user may add modules as second scope, because modules are simply subdirectories of a repository, and in large "monorepo" structures, subdirectories act like individual repositories. Artifact-scoped controls are used for controls such as Container Scan, Artifact Version, and Artifact Signature, because the attestation will attest to the compliance of the artifact itself and not the repository that it originiated from.

Controls may be scoped to a release if the control activity involves more than one particular software asset, but still pertain to specific versions of each software asset. Examples of this are Regression Tests and Accessibility Tests, as these are controls that could encompass a broader surface area than a particular repository or artifact, but whos results are still relevant only to the exact versions of each software asset in the release.

Abstract asset controls are less-defined because series options for these assets are almost entirely limited to time-based series. This is because abstract assets are essentially arbitrary groupings of other assets, and have no inherent method for creating discrete versions. Examples of controls that would most likely be scoped to an abstract asset would be annual Failover Validation for an Application or Risk Review for a Line of Business.

##### Relationship

> **Parent**: One or many collections
>
> **Child**: One or many policies

##### Permissions

- Owner
  - Can make changes to the control
  - Can approve changes to the control
  - Can add and remove managers and approvers to the control
  - Can approve requests to create new policies and exceptions
  - Can approve requests to change policies and exceptions
- Manager
  - Can make changes to the control
  - Can approve changes to the control
  - Can approve requests to create new policies and exceptions
  - Can approve requests to change policies and exceptions
- Approver
  - Can approve requests to create new policies and exceptions
  - Can approve requests to change policies and exceptions



---

#### Policies & Exceptions

Policies define the expected values or thresholds that must be met in order to be considered compliant for a given control. Exceptions are a temporary policy that either eases a policy's requirements or removes the policy requirement altogether. Given their similarity, Fianu's documentation will refer to both policies and exceptions as simply "policies."

##### Assigning Policies

Policies derive their format (aka "template") from the control. A control's OPA rule uses the policy values when evaluating evidence to measure compliance and determine if the attestation result shows pass, fail, warn, etc. Therefore, one control can have many policies but one policy can only belong to one control.

Policies use asset indexes (formerly called "criteria") to refine the population of assets that a given policy is applied to. Indexes are not a requirement for a policy, but when no index is defined the policy will apply to all assets in the organization.

##### Policy Layering

Indexes are a powerful tool for tailoring policy to a subset of the asset population. However, if the need arises for different requirements to apply to an even smaller subset, users need a way to override the original policy.

To solve this challenge, Fianu allows policies to be layered based on their position in a hierarchy. Policy hierarchy is the order in which the policies are applied to an asset. Policy hierarchy is derived from asset hierarchy so the order in which policies are applied is determined by the asset level that the policy is assigned to. To avoid policy collisions, Fianu allows only one policy at each asset level.

Policies take precedent in ascending order (i.e. the lowest level policy overrides all higher level policies). This pattern continues, bottom-up, for every layered policy that exists for a given control. The final policy that is used to measure compliance is called the "computed policy."

A policy is not required to define all values in the policy template. When a value is not defined, it is inherited from the policy next in precedent.

###### Policy Layering Defined in Set Notation

To better understand the behaviors of policy layering, consider the following construction.

> **Definitions**
>
> Let \( P \) be a **policy**.
>
> Let \( P_1, P_2, \ldots, P_n \) be an **ordered sequence of policies**.
> The ordering is significant: a policy appearing later in the sequence has higher precedence and overrides earlier sets where they overlap.
>
> Define a binary **override operator** \( \triangleleft \) on sets as follows:
>
> $$
> P_{x} \triangleleft P_y \;:=\; (P_{x} \setminus P_y) \cup P_y
> $$
> This operation removes from policy \( P_{x} \) all elements that also appear in policy \( P_y \), and then adds all elements of policy \( P_y \). As a result, elements of policy \( P_y \) take precedence wherever the two sets overlap.
>
> 
>
> **Cumulative Override of Sequence**
>
> The cumulative override of the ordered sequence
> $$
> (P_1, P_2, \ldots, P_n)
> $$
> is defined by repeated application of the override operator:
>
> $$
> P_1 \triangleleft P_2 \triangleleft \ldots \triangleleft P_n
> $$
>
> Evaluation proceeds from left to right, so that each successive set overrides the result of all preceding sets.
>
> 
>
> **Expanded SetNotation**
>
> The expression above expands purely in standard set notation as:
>
> $$
> ((((P_1 \setminus P_2) \cup P_2) \setminus P_3) \cup P_3 \;\cdots\;) \cup P_n
> $$
>
> **Semantics**
>
> Under this definition:
>
> - All elements of \( P_n \) have the highest precedence.
> - For any \( k < n \), elements of policy \( P_k \) are included **only if** they do not appear in any \( P_j \) for \( j > k \).
> - In the case of overlap between sets, the element from the set with the greatest index is retained.
>



##### Example - Part 2

Consider the following example that uses policies for a control called "Code Coverage" that measures both the overall coverage of a codebase as well as the coverage of new code added since the last production release. Because the Code Coverage control is scoped to the repository asset level, all policies for this control are applied to repositories.

**Policy A**  is set at the "Application" level, which in this organization, is the term for abstract asset level 1. It has no index so it applies to every repository (determined by the control scope) in every application. The policy sets a threshold of at least 50% coverage for the overall codebase and 85% coverage for new code that has been added since the last release.

```yaml
coverage:
	overall:
		minimum: 0.5
	new:
		minimum: 0.85
```

**Policy B** is set at the "Repository" level, a fixed asset that is one degree lower on the asset hierarchy than abstract asset level 1. It creates higher threshold for overall coverage, requiring that at least 80% of the codebase must be covered by unit tests. Without an index to refine the population of assets that must comply with this policy, Policy B would *also* apply to every codebase in the organization.

```yaml
coverage:
	overall:
		minimum: 0.8
```

**Computed Policy**

```yaml
coverage:
	overall:
		minimum: 0.8
	new:
		minimum: 0.85
```

The final policy applied to each repository would reflect that Policy B overrides Policy A, wherever Policy B is defined. So Policy B takes precedent over Policy A for overall coverage minimum (80%) but because Policy B does not define a new coverage minimum, the computed policy uses Policy A's new coverage of 85%.

##### Policy Variations

A natural constraint emerges when one policy cannot cover the diversity of requirements at a given asset level. For example, a single code coverage policy at the repository level may not suffice all repositories. An index can be used to isolate this repository-level policy to a subset of the population, but that precludes the user from creating another repository-level policy for different subset of the asset population. Fianu's solution for this constraint is called a variation.

Policy variations behave largely as they sound. They are variations of a single policy that can exist at the same hierarchy level, and use indexes to isolate the appropriate asset populations to ensure that each variation covers the asset populations that the variation should apply to.

Fianu uses two logical operators, AND and OR, to ensure that when policy variations collide (multiple variations at the same hierarchy apply to the same asset) there is a clear resolution.



##### Example - Part 2

Building upon part 1 of this example, let's incorporate asset indexes and variations to create a more realistic enterprise scenario.

**Policy A**  is still set at the "Application" level (abstract asset level 1). Now it has an index that applies to all repositories that belong to applications with the Fianu property `asset.cmdb.custom` which signifies an application with custom-developed software components as opposed to commercial off-the-shelf software (COTS).

```yaml
index: 'asset.cmdb.custom == true'

coverage:
	overall:
		minimum: 0.5
	new:
		minimum: 0.85
```

**Policy B** is still set at the "Repository" level, one degree lower on the asset hierarchy, and therefore the dominant policy. Hower, policy B has two variations. *Variation 1* uses the index `asset.cmdb.internet_facing`, which signifies that the repository deploys to a production environment with exposure to the public-facing internet. Assets that are considered internet facing typically pose a greater risk to the organization, therefore the IT Risk Management team would like to elevate the requirements for code coverage. *Variation 2* uses an index on `asset.framework` and looks for repositories that use `angular` or`react`. These are web UI frameworks and IT Risk Management has strict UI functional test requirements, so they would like to lower the unit test code coverage threshold for UI repositories because they believe it's redundant.

```yaml
- variation: 1
  index: 'asset.cmdb.internet_facing == true'
  coverage:
    overall:
      minimum: 0.9
- operator: 'OR'
- variation: 2
  index: 'asset.framework == \"angular\" || asset.framework == \"react\"' 
  coverage:
    overall:
      minimum: 0.25
    new:
      minimum: 0.1
```

The combined total population of assets subject to the Code Coverage control is determined by the combined indexes. We can express this in set notation as follows
$$
A \cap (B_1 \cup B_2)
$$
Where:

- \( A \) represents the set of items that conform to the index on Policy  **A**
- \(B_1\) represents the set of items that to the index on Policy **B**, Variation **1**
- \( B_2 \) represents the set of items that to the index on Policy **B**, Variation **2**

This represents the populations that conform to **A** and also conform to **either** **B1** or **B2**.

Let's now represent this using a sample population of four repositories. First, we'll start by using boolean values to express each assets conformity with the indexes.

| Repository     | Custom  | Internet Facing | Angular | React   |
| -------------- | ------- | --------------- | ------- | ------- |
| `repository_w` | `false` | `false`         | `true`  | `false` |
| `repository_x` | `true`  | `true`          | `false` | `false` |
| `repository_y` | `true`  | `false`         | `true`  | `false` |
| `repository_z` | `true`  | `true`          | `false` | `true`  |

Using the above table, we can now express which combination of policies will be layered for each asset. 

| Repository     | Policy \( A \) | Policy \(B_1\) | Policy \( B_2 \) |
| -------------- | -------------- | -------------- | ---------------- |
| `repository_w` | `false`        | `false`        | `true`           |
| `repository_x` | `true`         | `true`         | `false`          |
| `repository_y` | `true`         | `false`        | `true`           |
| `repository_z` | `true`         | `true`         | `true`           |

- Although`repository_w` does not conform with Policy\( A \) index, it conforms with the \( B_2 \) index, therefore the computed policy will simply be \( B_2 \)
- Both `repository_x` and `repository_y` conform to Policy \( A \), but each conforms to only one variation of Policy \(B\), so the policy layering is straightforward, \(B_1 \triangleleft A\)  and \(B_2 \triangleleft A\) respectively
- Because `repository_z` conforms to both \(B_1\) and \( B_2 \) and the variations are separated with an "OR" operator, the repository only needs to only pass one of the two computed policies to be considered passing


---

### Enforcement
```txt
┌──────────────┐
│    Gates     │
└──────────────┘
       ↓        
┌──────────────┐
│   Controls   │
└──────────────┘
       ↓        
┌──────────────┐
│   Indexes    │
└──────────────┘
```

#### Gates

[description]

##### Relationship

> **Parent**: [description]
>
> **Child**: [description]

##### Permissions

- Owner
  - [description]
- Manager
  - [description]
- Approver
  - [description]

---

### Integration

Fianu, like many SaaS platforms, offers integration capability with third-party systems. The primary purpose of these integrations is the extraction of evidence that must be evaluated to comply with controls and policies.

Because of Fianu's emphasis on audibility, it treats integrations with greater rigor than most other DevSecOps platforms.

In order to fully understand the structure and hierarchy of Fianu integrations, it's important to understand the core design principles for

```txt
         ┌──────────────┐
         │    Vendors   │
         └──────────────┘
           ↓          ↓
┌──────────────┐ ┌──────────────┐
│  Platforms   │ │   Tools      │
└──────────────┘ └──────────────┘
       ↓              │
┌──────────────┐      │
│   Instances  │      │
└──────────────┘      │
           ↓          ↓
       ┌─────────────────┐
       │   Plugins       │
       └─────────────────┘      
```

---

#### Vendors

[description]

##### Relationship

> **Parent**: [description]
>
> **Child**: [description]

##### Permissions

- Owner
  - [description]
- Manager
  - [description]
- Approver
  - [description]

---

#### Platforms

[description]

##### Relationship

> **Parent**: [description]
>
> **Child**: [description]

##### Permissions

- Owner
  - [description]
- Manager
  - [description]
- Approver
  - [description]

---

#### Instances

[description]

##### Relationship

> **Parent**: [description]
>
> **Child**: [description]

##### Permissions

- Owner
  - [description]
- Manager
  - [description]
- Approver
  - [description]

---

#### Tools

[description]

##### Relationship

> **Parent**: [description]
>
> **Child**: [description]

##### Permissions

- Owner
  - [description]
- Manager
  - [description]
- Approver
  - [description]

---

#### Plugins

[description]

##### Relationship

> **Parent**: [description]
>
> **Child**: [description]

##### Permissions

- Owner
  - [description]
- Manager
  - [description]
- Approver
  - [description]

---

### Deployments

[description]

```txt
┌──────────────┐
│ Environments │
└──────────────┘
       ↓        
┌──────────────┐
│   Targets    │
└──────────────┘
```

---

#### Environments

[description]

##### Relationship

> **Parent**: [description]
>
> **Child**: [description]

##### Permissions

- Owner
  - [description]
- Manager
  - [description]
- Approver
  - [description]

---

#### Targets

[description]

##### Relationship

> **Parent**: [description]
>
> **Child**: [description]

##### Permissions

- Owner
  - [description]
- Manager
  - [description]
- Approver
  - [description]
