# Decision Event Schema

JSON Schema specification for decision events as governance evidence units.

## Academic Context

This schema operationalizes the governance-compliance evidence distinction proposed in:

> Solozobov, O. (2026). Distinguishing Governance Evidence from Compliance Evidence in Automated Decision Systems: A Diagnostic Framework for Post-Incident Reconstruction (forthcoming).

Traditional accountability mechanisms produce **compliance evidence** -- documentation that a process exists and was followed. Post-incident reconstruction requires **governance evidence** -- records that enable independent third-party reconstruction of *why* decisions were made and whether the decision-making process was adequate.

The Decision Event Schema defines the minimal unit of governance evidence. Each property captures a dimension of evidence that resists a specific type of governance artifact degradation.

## Quick Start

Validate an example against the schema:

```bash
pip install jsonschema
python tests/validate.py
```

Or validate programmatically:

```python
import json
from jsonschema import validate

with open("schema/decision-event.schema.json") as f:
    schema = json.load(f)

with open("examples/cloudflare-2025.json") as f:
    event = json.load(f)

validate(instance=event, schema=schema)
```

## Schema Properties

| Property | Required | Resists Degradation Type |
|----------|----------|--------------------------|
| `decision_id` | yes | -- |
| `timestamp` | yes | -- |
| `decision_type` | yes | -- |
| `decision_context` | no | Content Staleness |
| `decision_logic` | no | Schema Drift |
| `decision_boundary` | no | Coverage Erosion |
| `decision_quality_indicators` | no | Metric Erosion |
| `human_override_record` | no | Override Accumulation |
| `temporal_metadata` | no | Content Staleness (via Ground Truth Delay) |

See [docs/properties.md](docs/properties.md) for detailed definitions and examples.

## Repository Structure

```
schema/
  decision-event.schema.json   # v0.1 JSON Schema (draft 2020-12)
examples/
  cloudflare-2025.json         # Cloudflare outage November 2025 (scale: abstraction boundaries)
  crowdstrike-2024.json        # CrowdStrike Falcon sensor outage (scale + velocity)
  knight-capital-2012.json     # Knight Capital trading loss (velocity)
  robodebt-2015.json           # Australian Robodebt scheme 2015-2019 (scale)
  uber-atg-2018.json           # Uber ATG autonomous vehicle fatality (opacity)
docs/
  properties.md                # Property reference and degradation mapping
  adjacent-specifications.md   # Comparison with CloudEvents, OpenTelemetry, W3C PROV, NIST, IEEE
tests/
  validate.py                  # Schema validation script
```

## Governance Evidence Feasibility Matrix

Diagnostic application of DES to the four paradigmatic cases (Paper 12, Table 19). Each cell indicates whether the governance evidence property was captured, partially available, structurally unfillable, or opaque at the time of the incident. The Cloudflare case (illustrative) is included in the examples directory but excluded from this matrix.

| Property | Knight Capital 2012 (velocity) | Robodebt 2015-2019 (scale) | Uber ATG 2018 (opacity) | CrowdStrike 2024 (scale+vel.) |
|----------|:---:|:---:|:---:|:---:|
| `decision_context` | **Unfillable** | Partial (no alternatives) | Recoverable | **Unfillable** (no alternatives) |
| `decision_logic` | Recoverable | Recoverable (but wrong) | **Opaque** (irreducible) | Fully recoverable |
| `decision_boundary` | **Unfillable** | Recoverable | **Unfillable** (handoff unmonitored) | **Unfillable** (bypassed governance) |
| `decision_quality_indicators` | **Unfillable** | **Unfillable** | **Unfillable** | **Unfillable** |
| `human_override_record` | **Unfillable** (velocity) | Epistemically void | Captured (safety driver) | **Absent by design** |
| `temporal_metadata` | Recoverable | Partial (8-year GTD) | Recoverable | Fully recoverable |

**Key findings:**

- **`decision_quality_indicators`** is structurally unfillable across all four paradigmatic cases -- the hardest property to satisfy regardless of collapse modality.
- **`human_override_record`** fails for structurally different reasons in each case: *too fast* (Knight Capital), *epistemically void* (Robodebt), *captured but insufficient* (Uber ATG), and *absent by design* (CrowdStrike).
- **`decision_logic`** ranges from fully recoverable (CrowdStrike) to opaque (Uber ATG) to "recoverable but wrong" (Robodebt) -- demonstrating that logic recoverability does not imply logic adequacy, and that opacity creates a qualitatively distinct failure mode.
- Only **`temporal_metadata`** approaches consistent recoverability, largely because timestamp requirements are mandated by regulatory compliance regimes (SEC, NTSB, audit trails).

## Version

**v0.1.0** -- Minimal viable schema demonstrating the concept is formalizable. Full specification with domain-specific extensions will accompany the JOSS submission.

## Contributing

This is a research artifact under active development. Issues and pull requests are welcome. Please reference the academic framework when proposing schema changes.

## Citation

If you use this schema in your research, please cite:

```bibtex
@software{solozobov2026decision,
  author = {Solozobov, Oleg},
  title = {Decision Event Schema},
  version = {0.1.0},
  year = {2026},
  url = {https://github.com/governance-evidence/decision-event-schema}
}
```

See [CITATION.cff](CITATION.cff) for machine-readable citation metadata.

## License

[MIT](LICENSE)

---

Part of the [governance-evidence](https://github.com/governance-evidence) research initiative.
