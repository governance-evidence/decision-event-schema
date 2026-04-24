# Decision Event Schema

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18923177.svg)](https://doi.org/10.5281/zenodo.18923177)
[![arXiv](https://img.shields.io/badge/arXiv-2604.09296-b31b1b.svg)](https://arxiv.org/abs/2604.09296)
[![GitHub release](https://img.shields.io/github/v/release/governance-evidence/decision-event-schema)](https://github.com/governance-evidence/decision-event-schema/releases/latest)
![Version: v0.3.0](https://img.shields.io/badge/version-v0.3.0-blue)
![JSON Schema: draft 2020-12](https://img.shields.io/badge/json%20schema-draft%202020--12-0f766e)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

JSON Schema specification for decision events as governance evidence units.

## Academic Context

This schema is the primary artifact of:

> Solozobov, O. (2026). *Decision Trace Schema for Governance Evidence in Real-Time Risk Systems*. arXiv:2604.09296. <https://arxiv.org/abs/2604.09296>

It also operationalizes the governance-compliance evidence distinction proposed in:

> Solozobov, O. (2026). *Distinguishing Governance Evidence from Compliance Evidence in Automated Decision Systems: A Diagnostic Framework for Post-Incident Reconstruction*. SSRN preprint. <https://doi.org/10.2139/ssrn.6457861>

Synthesis context — this schema is one of the four artifacts whose transferability is assessed in:

> Solozobov, O. (2026). *Governed Auditable Decisioning Under Uncertainty: Synthesis and Agentic Extension*. arXiv:2604.19112. <https://arxiv.org/abs/2604.19112>

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

## Schema Properties (v0.3.0)

`schema_version` plus four top-level property groups are **required**. Each group contains its own required sub-fields.

| Property Group | Required | Key Sub-fields | Resists Degradation Type |
| -------------- | -------- | -------------- | ------------------------ |
| `schema_version` | **yes** | semver string (`0.3.0`) | Contract clarity |
| `decision_context` | **yes** | `decision_id`, `decision_type` | Content Staleness |
| `decision_logic` | **yes** | `logic_type`, `output` | Schema Drift |
| `human_override_record` | **yes** | `override_occurred` (+ conditional fields when true) | Override Accumulation |
| `temporal_metadata` | **yes** | `event_timestamp`, `sequence_number`, `hash_chain`, `evidence_tier` | Content Staleness (via Ground Truth Delay) |
| `decision_boundary` | no | `contributing_subsystems`, `upstream_decisions`, `downstream_consumers` | Coverage Erosion |
| `decision_quality_indicators` | no | `confidence_score`, `ground_truth_available` | Metric Erosion |

See [docs/properties.md](docs/properties.md) for detailed definitions and examples.

## Minimal Valid Event

```json
{
  "schema_version": "0.3.0",
  "decision_context": {
    "decision_id": "550e8400-e29b-41d4-a716-446655440001",
    "decision_type": "automated_assessment"
  },
  "decision_logic": {
    "logic_type": "rule_based",
    "output": "approve"
  },
  "human_override_record": {
    "override_occurred": false
  },
  "temporal_metadata": {
    "event_timestamp": "2026-01-01T00:00:00Z",
    "sequence_number": 1,
    "hash_chain": {
      "previous_hash": null,
      "current_hash": "abc123",
      "algorithm": "SHA-256"
    },
    "evidence_tier": "lightweight"
  }
}
```

## Upgrading from v0.2.x

- Add `schema_version` to every Decision Event instance.
- Set `schema_version` to `0.3.0` for payloads targeting this release.
- Re-run validation for stored examples and producer fixtures before publishing or ingesting events.

## Repository Structure

```text
schema/
  decision-event.schema.json   # v0.3 JSON Schema (draft 2020-12)
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
| -------- | :---: | :---: | :---: | :---: |
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

**v0.3.0** -- Breaking change from v0.2.0. Requires explicit `schema_version` on every Decision Event instance while preserving the v0.2 top-level property group structure and validation rules. All five case study examples and validation fixtures now declare the schema version they conform to.

## Contributing

This is a research artifact under active development. Issues and pull requests are welcome. Please reference the academic framework when proposing schema changes.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution workflow and release checklist, and [CHANGELOG.md](CHANGELOG.md) for version history.

Local quality checks:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install pre-commit jsonschema
pre-commit install
pre-commit run --all-files
python tests/validate.py
```

## Citation

If you use this schema in your research, please cite both the paper and the software artifact.

**Paper (primary):**

```bibtex
@misc{solozobov2026decisiontrace,
  author = {Solozobov, Oleg},
  title  = {Decision Trace Schema for Governance Evidence in Real-Time Risk Systems},
  year   = {2026},
  eprint = {2604.09296},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CY},
  doi    = {10.48550/arXiv.2604.09296},
  url    = {https://arxiv.org/abs/2604.09296}
}
```

**Software (this repository):**

```bibtex
@software{solozobov2026decisioneventschema,
  author  = {Solozobov, Oleg},
  title   = {Decision Event Schema},
  version = {0.3.0},
  year    = {2026},
  url     = {https://github.com/governance-evidence/decision-event-schema},
  doi     = {10.5281/zenodo.18923177}
}
```

The software `doi` above is the **concept DOI** (always resolves to the latest Zenodo release). The current v0.3.0 version DOI is [10.5281/zenodo.19471740](https://doi.org/10.5281/zenodo.19471740).

See [CITATION.cff](CITATION.cff) for machine-readable citation metadata.

## Related Projects

This schema is part of the [governance-evidence](https://github.com/governance-evidence) toolkit:

| Repository | Role | Concept DOI |
| ---------- | ---- | ----------- |
| [evidence-collector-sdk](https://github.com/governance-evidence/evidence-collector-sdk) | Produces events conforming to this schema from raw telemetry | [10.5281/zenodo.19245404](https://doi.org/10.5281/zenodo.19245404) |
| [evidence-sufficiency-calc](https://github.com/governance-evidence/evidence-sufficiency-calc) | Scores sufficiency of event streams validated against this schema | [10.5281/zenodo.19233930](https://doi.org/10.5281/zenodo.19233930) |
| [governance-drift-toolkit](https://github.com/governance-evidence/governance-drift-toolkit) | Monitors degradation of event streams conforming to this schema | [10.5281/zenodo.19236417](https://doi.org/10.5281/zenodo.19236417) |
| [governance-benchmark-dataset](https://github.com/governance-evidence/governance-benchmark-dataset) | Benchmark scoring each schema property across four decision architectures | [10.5281/zenodo.19248722](https://doi.org/10.5281/zenodo.19248722) |

All DOIs above are **concept DOIs** -- each resolves to the latest Zenodo release of that artifact.

## License

[MIT](LICENSE)

---

Part of the [governance-evidence](https://github.com/governance-evidence) research initiative.
