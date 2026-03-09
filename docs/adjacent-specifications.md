# Adjacent Specifications: Positioning the Decision Event Schema

Version 0.1.0

## Overview

The Decision Event Schema is not the first attempt to standardize event-level recording for complex systems. Multiple specifications exist for logging, observability, and provenance. The critical distinction is not between specifications that record "what happened" and those that do not, but between specifications that preserve sufficient evidence for an independent third party to reconstruct whether the decision-making process was adequate and those that optimize for other concerns.

## Comparison Summary

| Specification | Primary concern | Captures decision context | Captures decision quality | Maps to degradation types | Governance adequacy |
|---------------|----------------|:---:|:---:|:---:|:---:|
| CloudEvents (CNCF, 2018) | Event transport envelope | No | No | No | No |
| OpenTelemetry (CNCF, 2019) | System observability | Partial (trace context) | No | No | No |
| W3C PROV-DM (2013) | Data provenance | Partial (Entity-Activity-Agent) | No | No | No |
| NIST SP 800-53 AU (2020) | Audit event requirements | Prescribed (AU-3) | No | No | No |
| IEEE P7001 (2021) | Transparency for autonomous systems | Process-level | Process-level | No | No |
| Decision Event Schema (this paper) | Governance evidence | Yes (`decision_context`) | Yes (`quality_indicators`) | Yes (by design) | Yes |

## Detailed Analysis

### CloudEvents (CNCF, 2018)

- **Specification:** [cloudevents.io](https://cloudevents.io/)
- **Primary concern:** Event transport envelope for interoperability across distributed systems
- **What it provides:** Source, type, time, and data content attributes for event delivery
- **Governance gap:** Semantically neutral -- carries any payload without imposing governance semantics. A CloudEvents envelope could transport a decision event record, but provides no governance structure: it specifies *how events are delivered*, not *what they must contain for accountability purposes*.
- **Overlap with DES:** None at the semantic level; CloudEvents could serve as a transport layer for Decision Event Schema payloads.

### OpenTelemetry (CNCF, 2019)

- **Specification:** [opentelemetry.io](https://opentelemetry.io/)
- **Primary concern:** System observability through distributed traces, metrics, and logs
- **What it provides:** Distributed trace propagation, metric collection, structured logging. Building on Sigelman et al. (2010), "Dapper, a Large-Scale Distributed Systems Tracing Infrastructure."
- **Governance gap:** Answers "what happened in the system" (observability) but not "was the decision-making process adequate" (accountability). Trace context provides temporal ordering and causal propagation across service boundaries -- capabilities that overlap with `temporal_metadata` and `decision_boundary` -- but does not capture decision rationale, alternatives considered, or quality assessment.
- **Overlap with DES:** Partial overlap with `temporal_metadata` (timestamps, causal ordering) and `decision_boundary` (service dependency mapping). OpenTelemetry traces could provide infrastructure for populating these two DES properties.

### W3C PROV-DM (2013)

- **Specification:** [W3C PROV Data Model](https://www.w3.org/TR/prov-dm/)
- **Primary concern:** Data provenance -- recording the origin and history of data artifacts
- **What it provides:** Entity-Activity-Agent provenance graphs capturing "who did what to what"
- **Governance gap:** The closest existing specification to the Decision Event Schema. PROV-DM provides lineage documentation that overlaps with the traceability construct. However, it includes no degradation-aware properties, no decision quality indicators, and no human override record. It answers "what is the origin of this data artifact" rather than "can an independent third party reconstruct whether the decision process was adequate."
- **Structural example:** A PROV-compliant provenance graph for the Knight Capital incident would document the sequence of trade executions without capturing that no mechanism existed for operator intervention at the velocity at which decisions were executing.
- **Overlap with DES:** Significant overlap with `decision_boundary` (entity-activity relationships map to subsystem contributions) and partial overlap with `decision_context` (PROV activities can record inputs). PROV-DM could serve as a foundation for a governance-extended provenance model.

### NIST SP 800-53 AU Controls (2020)

- **Specification:** [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final), Audit and Accountability family
- **Primary concern:** Audit event requirements for federal information systems
- **What it provides:** Prescriptive controls specifying what events to log (AU-2), what content to record (AU-3), how to store records (AU-4), and how to review them (AU-6). AU-3 specifies that audit records should contain sufficient information to establish: event type, time, location, source, outcome, and identity of associated subjects.
- **Governance gap:** Provides no data model -- only categories of information that should be present. Organizations can satisfy AU-3 requirements while producing only compliance evidence: the controls prescribe categories without specifying the structural properties that distinguish governance evidence from compliance documentation.
- **Overlap with DES:** AU-3 content requirements map broadly to DES required fields (`timestamp`, `decision_type`, `decision_id`) and partially to `decision_context`. The gap is in optional governance properties that AU controls do not require.

### IEEE P7001 (2021)

- **Specification:** [IEEE 7001-2021](https://standards.ieee.org/ieee/7001/6929/), Transparency of Autonomous Systems
- **Primary concern:** Graduated transparency requirements for autonomous system stakeholders (developers, users, affected parties)
- **What it provides:** Process-level transparency definitions and assessment criteria across five levels. Establishes that different stakeholders require different transparency guarantees.
- **Governance gap:** Defines transparency at the process level, not the event level. Does not specify event-level data structures, does not connect transparency requirements to empirically observable degradation patterns, and does not distinguish between compliance-adequate and governance-adequate evidence.
- **Overlap with DES:** Conceptual alignment with the governance-compliance distinction, but at a different level of abstraction. IEEE P7001 could reference DES as an event-level operationalization of its transparency principles.

## The Governance Gap

The gap revealed by this comparison is not in the capability to log events -- contemporary systems generate enormous volumes of operational data -- but in *what the log is designed to preserve*:

| Specification | Optimizes for |
|---------------|---------------|
| CloudEvents | Transport interoperability |
| OpenTelemetry | System observability |
| W3C PROV-DM | Data lineage |
| NIST SP 800-53 AU | Compliance audit |
| IEEE P7001 | Stakeholder transparency |
| **Decision Event Schema** | **Governance reconstruction adequacy** |

None of the existing specifications optimize for governance reconstruction adequacy -- the capacity of recorded evidence to support independent third-party determination of whether the decision-making process was adequate to the risks it addressed.

## Design Principle: Degradation-Aware Schema Design

The Decision Event Schema's distinguishing design principle is that each property is explicitly mapped to a governance artifact degradation type identified through the empirical taxonomy of governance artifact degradation:

| DES Property | Resists Degradation Type | Adjacent Spec Coverage |
|-------------|--------------------------|------------------------|
| `decision_context` | Content Staleness | PROV-DM (partial), NIST AU-3 (prescribed) |
| `decision_logic` | Schema Drift | None |
| `decision_boundary` | Coverage Erosion | OpenTelemetry (partial), PROV-DM (partial) |
| `decision_quality_indicators` | Metric Erosion | None |
| `human_override_record` | Override Accumulation | None |
| `temporal_metadata` | Content Staleness (via Ground Truth Delay) | OpenTelemetry (partial) |

Three DES properties -- `decision_logic`, `decision_quality_indicators`, and `human_override_record` -- have no coverage in any adjacent specification. These represent the governance-specific evidence dimensions that existing standards do not address.

## Interoperability Opportunities

Rather than replacing existing specifications, the Decision Event Schema is designed to complement them:

1. **CloudEvents as transport:** DES payloads can be delivered via CloudEvents envelopes, leveraging existing event routing infrastructure.
2. **OpenTelemetry as infrastructure:** Distributed traces can provide the temporal ordering and boundary mapping that populate `temporal_metadata` and `decision_boundary` properties.
3. **PROV-DM as foundation:** PROV provenance graphs can be extended with governance-specific properties to create governance-adequate provenance records.
4. **NIST AU as compliance baseline:** DES extends AU-3 content requirements with governance-specific properties that enable reconstruction beyond compliance verification.
5. **IEEE P7001 as process framework:** DES provides event-level operationalization of the transparency principles that P7001 defines at the process level.
