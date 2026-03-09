# Decision Event Schema: Property Reference

Version 0.1.0

## Required Properties

| Property | Type | Description |
|----------|------|-------------|
| `decision_id` | `string` (uuid) | Unique identifier for this decision event. |
| `timestamp` | `string` (date-time) | ISO 8601 timestamp of when the decision was executed. |
| `decision_type` | `enum` | Whether the decision was made by a `human`, `automated` system, or `hybrid` combination. |

## Governance Evidence Properties

Each optional property captures a dimension of governance evidence that resists a specific degradation type identified in the analytical framework.

| Property | Resists Degradation Type | Definition | Example |
|----------|--------------------------|------------|---------|
| `decision_context` | Content Staleness | Records the inputs, alternatives, and constraints available at the time of decision. Without this, reconstructors rely on current-state documentation that may not reflect conditions at decision time. | Available market data feeds, regulatory constraints, alternative routing options |
| `decision_logic` | Schema Drift | Records the rule version, parameters, and thresholds governing the decision. Without this, the logic applied at decision time becomes irrecoverable as systems update. | SMARS v4.0 routing rules, position limit of $2M, no rate limit configured |
| `decision_boundary` | Coverage Erosion | Records contributing subsystems and external dependencies. Without this, the scope of system involvement in a decision narrows over time as components are decommissioned or restructured. | Order routing engine, legacy Power Peg module, NYSE matching engine |
| `decision_quality_indicators` | Metric Erosion | Records confidence scores, uncertainty flags, and ground truth availability. Without this, assessment of decision quality at the time becomes impossible as metrics definitions evolve. | No confidence score available, 4 uncertainty flags raised, ground truth not available |
| `human_override_record` | Override Accumulation | Records override decisions, independence assessments, and deviation rationale. Without this, the pattern of human interventions (or absence thereof) cannot be reconstructed. | Manual intervention attempted 45 min after market open, operators lacked halt authority |
| `temporal_metadata` | Content Staleness (via Ground Truth Delay) | Records the gap between decision execution, evidence availability, and ground truth arrival. Without this, the temporal structure of accountability -- who could have known what, when -- is lost. | Decision at 09:30, evidence available at 10:15, ground truth (SEC ruling) on 2012-10-16 |

## Degradation Type Definitions

From the governance artifact degradation taxonomy (Paper 12, Section 5). The taxonomy is mixed-level by design (4+1): four types describe artifact degradation; override accumulation describes governance-process decoupling, requiring process redesign rather than artifact repair.

- **Content Staleness**: Decision context documentation becomes outdated as operational conditions change, making retrospective reconstruction unreliable. Includes temporal evidence decay (Ground Truth Delay): the gap between decision execution and ground truth arrival makes real-time accountability structurally impossible.
- **Schema Drift**: Rule definitions and model parameters evolve without preserving the version active at decision time.
- **Coverage Erosion**: The boundary of systems contributing to a decision narrows in the record as components are replaced or decommissioned.
- **Metric Erosion**: Quality indicators lose their meaning as measurement definitions and baselines shift.
- **Override Accumulation**: The record of human interventions (or their absence) degrades as override patterns are normalized or forgotten. Operates at the process level rather than the artifact level and can compound any of the four artifact types.

## Design Principles

1. **Diagnostic, not prescriptive**: The schema defines what governance evidence should capture, not how systems must implement it.
2. **Minimal viable structure**: v0.1 uses simple object types. Deeply nested or domain-specific subschemas are deferred to future versions.
3. **Extensible**: All object properties allow `additionalProperties: true` to support domain-specific extensions.
