"""Validation tests for the Decision Event Schema v0.1.

Validates all example files against the schema, checks structural constraints,
and verifies that each example correctly demonstrates its intended governance
evidence gaps (structurally unfillable properties).
"""

import json
import sys
from pathlib import Path

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema" / "decision-event.schema.json"
EXAMPLES_DIR = ROOT / "examples"

PASSED = 0
FAILED = 0


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def report(test_name: str, passed: bool, detail: str = ""):
    global PASSED, FAILED
    status = "PASS" if passed else "FAIL"
    if passed:
        PASSED += 1
    else:
        FAILED += 1
    msg = f"{status}: {test_name}"
    if detail:
        msg += f" -- {detail}"
    print(msg)
    return passed


# ─── Schema validation ────────────────────────────────────────────


def test_all_examples_valid():
    """Every JSON file in examples/ validates against the schema."""
    schema = load_json(SCHEMA_PATH)
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        try:
            validate(instance=example, schema=schema)
            report(f"Schema validation: {path.name}", True)
        except ValidationError as e:
            report(f"Schema validation: {path.name}", False, str(e.message)[:120])


def test_minimal_event_is_valid():
    """Event with only required fields validates."""
    schema = load_json(SCHEMA_PATH)
    minimal = {
        "decision_id": "550e8400-e29b-41d4-a716-446655440001",
        "timestamp": "2026-01-01T00:00:00Z",
        "decision_type": "human",
    }
    try:
        validate(instance=minimal, schema=schema)
        report("Minimal event (3 required fields)", True)
    except ValidationError as e:
        report("Minimal event (3 required fields)", False, str(e.message)[:120])


def test_missing_required_fields_rejected():
    """Event missing required fields is rejected."""
    schema = load_json(SCHEMA_PATH)
    invalid = {"decision_id": "550e8400-e29b-41d4-a716-446655440002"}
    try:
        validate(instance=invalid, schema=schema)
        report("Missing required fields rejected", False, "Invalid event was not rejected")
    except ValidationError:
        report("Missing required fields rejected", True)


def test_invalid_decision_type_rejected():
    """Event with invalid decision_type enum is rejected."""
    schema = load_json(SCHEMA_PATH)
    invalid = {
        "decision_id": "550e8400-e29b-41d4-a716-446655440003",
        "timestamp": "2026-01-01T00:00:00Z",
        "decision_type": "unknown",
    }
    try:
        validate(instance=invalid, schema=schema)
        report("Invalid decision_type rejected", False, "Invalid decision_type was not rejected")
    except ValidationError:
        report("Invalid decision_type rejected", True)


# ─── Schema version ───────────────────────────────────────────────


def test_schema_version_present():
    """All examples include schema_version field."""
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        has_version = "schema_version" in example
        report(f"schema_version present: {path.name}", has_version)


def test_schema_version_format():
    """schema_version follows semver pattern."""
    import re
    semver = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        version = example.get("schema_version", "")
        report(f"schema_version semver: {path.name}", bool(semver.match(version)), version)


# ─── Structural property tests ────────────────────────────────────


GOVERNANCE_PROPERTIES = [
    "decision_context",
    "decision_logic",
    "decision_boundary",
    "decision_quality_indicators",
    "human_override_record",
    "temporal_metadata",
]


def test_all_governance_properties_present():
    """All examples populate all 6 governance evidence properties."""
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        missing = [p for p in GOVERNANCE_PROPERTIES if p not in example]
        report(
            f"All governance properties: {path.name}",
            len(missing) == 0,
            f"missing: {missing}" if missing else "",
        )


def test_recoverability_notes():
    """All examples include _recoverability_note in each governance property."""
    case_studies = [
        "knight-capital-2012.json",
        "robodebt-2015.json",
        "crowdstrike-2024.json",
        "uber-atg-2018.json",
        "cloudflare-2025.json",
    ]
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        if path.name not in case_studies:
            continue
        example = load_json(path)
        missing_notes = []
        for prop in GOVERNANCE_PROPERTIES:
            obj = example.get(prop, {})
            if isinstance(obj, dict) and "_recoverability_note" not in obj:
                missing_notes.append(prop)
        report(
            f"Recoverability notes: {path.name}",
            len(missing_notes) == 0,
            f"missing in: {missing_notes}" if missing_notes else "",
        )


# ─── Knight Capital specific ──────────────────────────────────────


def test_knight_capital_velocity_collapse():
    """Knight Capital demonstrates velocity-driven collapse patterns."""
    path = EXAMPLES_DIR / "knight-capital-2012.json"
    if not path.exists():
        report("Knight Capital file exists", False)
        return
    ex = load_json(path)

    # decision_type must be automated
    report("Knight: decision_type=automated", ex.get("decision_type") == "automated")

    # quality_indicators must show structural unfillability (null confidence, empty flags)
    qi = ex.get("decision_quality_indicators", {})
    report(
        "Knight: quality_indicators unfillable",
        qi.get("confidence_score") is None and qi.get("ground_truth_available") is False,
    )

    # human_override must be null (velocity prevents intervention)
    hor = ex.get("human_override_record", {})
    report(
        "Knight: override architecturally absent",
        hor.get("override_decision") is None,
    )

    # temporal_metadata should be recoverable (SEC timestamps)
    tm = ex.get("temporal_metadata", {})
    report(
        "Knight: temporal_metadata recoverable",
        tm.get("decision_timestamp") is not None
        and tm.get("ground_truth_arrival_timestamp") is not None,
    )


# ─── Robodebt specific ────────────────────────────────────────────


def test_robodebt_scale_collapse():
    """Robodebt demonstrates scale-driven collapse with procedural closure."""
    path = EXAMPLES_DIR / "robodebt-2015.json"
    if not path.exists():
        report("Robodebt file exists", False)
        return
    ex = load_json(path)

    report("Robodebt: decision_type=automated", ex.get("decision_type") == "automated")

    # decision_logic should be present but reveal structural flaw
    dl = ex.get("decision_logic", {})
    params = dl.get("parameters", {})
    report(
        "Robodebt: logic reveals structural flaw",
        "structural_flaw" in params,
    )

    # quality_indicators must show structural unfillability
    qi = ex.get("decision_quality_indicators", {})
    report(
        "Robodebt: quality_indicators unfillable",
        qi.get("confidence_score") is None and qi.get("ground_truth_available") is False,
    )

    # human_override formally present but epistemically void
    hor = ex.get("human_override_record", {})
    report(
        "Robodebt: override formally present",
        hor.get("override_decision") is not None,
        hor.get("override_decision", "")[:60] if hor.get("override_decision") else "",
    )

    # temporal_metadata: massive ground truth delay (8 years)
    tm = ex.get("temporal_metadata", {})
    report(
        "Robodebt: ground truth delay to 2023",
        "2023" in str(tm.get("ground_truth_arrival_timestamp", "")),
    )


# ─── CrowdStrike specific ─────────────────────────────────────────


def test_crowdstrike_scale_velocity_collapse():
    """CrowdStrike demonstrates scale+velocity collapse with dual-pipeline gap."""
    path = EXAMPLES_DIR / "crowdstrike-2024.json"
    if not path.exists():
        report("CrowdStrike file exists", False)
        return
    ex = load_json(path)

    report("CrowdStrike: decision_type=automated", ex.get("decision_type") == "automated")

    # decision_logic should be fully recoverable (non-null rule_version)
    dl = ex.get("decision_logic", {})
    report(
        "CrowdStrike: logic fully recoverable",
        dl.get("rule_version") is not None and "Channel File 291" in dl.get("rule_version", ""),
    )

    # decision_boundary should be fully recoverable (Congressional testimony)
    db = ex.get("decision_boundary", {})
    report(
        "CrowdStrike: boundary well-documented",
        len(db.get("contributing_subsystems", [])) >= 4,
    )

    # quality_indicators unfillable for Rapid Response pathway
    qi = ex.get("decision_quality_indicators", {})
    report(
        "CrowdStrike: quality_indicators unfillable",
        qi.get("confidence_score") is None,
    )

    # human_override absent by design (no human in loop)
    hor = ex.get("human_override_record", {})
    report(
        "CrowdStrike: override absent by design",
        hor.get("override_decision") is None,
    )

    # temporal_metadata fully recoverable (same-day ground truth)
    tm = ex.get("temporal_metadata", {})
    report(
        "CrowdStrike: same-day ground truth",
        "2024-07-19" in str(tm.get("ground_truth_arrival_timestamp", "")),
    )


# ─── Cloudflare specific ──────────────────────────────────────────


def test_cloudflare_scale_collapse():
    """Cloudflare demonstrates scale collapse via abstraction boundary failure (illustrative)."""
    path = EXAMPLES_DIR / "cloudflare-2025.json"
    if not path.exists():
        report("Cloudflare file exists", False)
        return
    ex = load_json(path)

    report("Cloudflare: decision_type=automated", ex.get("decision_type") == "automated")

    # All 6 governance properties present
    for prop in GOVERNANCE_PROPERTIES:
        report(f"Cloudflare: {prop} present", prop in ex)


# ─── Uber ATG specific ───────────────────────────────────────────


def test_uber_atg_opacity_collapse():
    """Uber ATG demonstrates opacity-driven collapse with irreducible inference."""
    path = EXAMPLES_DIR / "uber-atg-2018.json"
    if not path.exists():
        report("Uber ATG file exists", False)
        return
    ex = load_json(path)

    report("Uber ATG: decision_type=automated", ex.get("decision_type") == "automated")

    # decision_logic present but opaque (classification oscillation)
    dl = ex.get("decision_logic", {})
    params = dl.get("parameters", {})
    report(
        "Uber ATG: logic opaque (classification oscillation)",
        "reclassified" in params.get("classification_behavior", "").lower()
        or "reclassif" in params.get("classification_behavior", "").lower(),
    )

    # quality_indicators structurally unfillable (no confidence threshold)
    qi = ex.get("decision_quality_indicators", {})
    report(
        "Uber ATG: quality_indicators unfillable",
        qi.get("confidence_score") is None and qi.get("ground_truth_available") is False,
    )

    # human_override captured (safety driver present but did not intervene)
    hor = ex.get("human_override_record", {})
    report(
        "Uber ATG: override captured (no intervention)",
        hor.get("override_decision") is not None
        and "no override" in hor.get("override_decision", "").lower(),
    )

    # temporal_metadata recoverable (NTSB investigation)
    tm = ex.get("temporal_metadata", {})
    report(
        "Uber ATG: NTSB ground truth 2019",
        "2019" in str(tm.get("ground_truth_arrival_timestamp", "")),
    )


# ─── Cross-example consistency ─────────────────────────────────────


def test_all_decision_types_valid():
    """All examples use valid decision_type enum values."""
    valid_types = {"human", "automated", "hybrid"}
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        dt = example.get("decision_type")
        report(f"Valid decision_type: {path.name}", dt in valid_types, dt)


def test_timestamps_iso8601():
    """All top-level timestamps are ISO 8601 format."""
    import re
    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        ts = example.get("timestamp", "")
        report(f"ISO 8601 timestamp: {path.name}", bool(iso_pattern.match(ts)), ts[:25])


# ─── Runner ────────────────────────────────────────────────────────


if __name__ == "__main__":
    print(f"Schema: {SCHEMA_PATH}")
    print(f"Examples: {EXAMPLES_DIR}")
    print(f"Example files: {[p.name for p in sorted(EXAMPLES_DIR.glob('*.json'))]}")
    print()

    test_all_examples_valid()
    print()
    test_minimal_event_is_valid()
    test_missing_required_fields_rejected()
    test_invalid_decision_type_rejected()
    print()
    test_schema_version_present()
    test_schema_version_format()
    print()
    test_all_governance_properties_present()
    test_recoverability_notes()
    print()
    test_knight_capital_velocity_collapse()
    print()
    test_robodebt_scale_collapse()
    print()
    test_crowdstrike_scale_velocity_collapse()
    print()
    test_uber_atg_opacity_collapse()
    print()
    test_cloudflare_scale_collapse()
    print()
    test_all_decision_types_valid()
    test_timestamps_iso8601()

    print()
    print(f"Results: {PASSED} passed, {FAILED} failed")
    if FAILED > 0:
        sys.exit(1)
    else:
        print("All checks passed.")
