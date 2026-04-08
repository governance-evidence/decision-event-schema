"""Validation tests for the Decision Event Schema v0.3.

Validates all example files against the schema, checks structural constraints,
and verifies that each example correctly demonstrates its intended governance
evidence gaps (structurally unfillable properties).

v0.1.0: initial schema with 6 property groups.
v0.2.0: 4 required property groups, logic_type, override_occurred,
evidence_tier, hash_chain, conditional override validation, two-path human
judgment design, crypto generation sequence, boundary contract extensions.
v0.3.0: schema_version is now required on every Decision Event instance.
"""

import json
import re
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
README_PATH = ROOT / "README.md"
CITATION_PATH = ROOT / "CITATION.cff"
PROPERTIES_DOC_PATH = ROOT / "docs" / "properties.md"
ADJACENT_DOC_PATH = ROOT / "docs" / "adjacent-specifications.md"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
SCHEMA_VERSION = "0.3.0"

PASSED = 0
FAILED = 0


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_text(path: Path) -> str:
    with open(path) as f:
        return f.read()


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
    """Event with schema_version and required property groups validates."""
    schema = load_json(SCHEMA_PATH)
    minimal = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {
            "decision_id": "550e8400-e29b-41d4-a716-446655440001",
            "decision_type": "automated_assessment",
        },
        "decision_logic": {
            "logic_type": "rule_based",
            "output": "approve",
        },
        "human_override_record": {
            "override_occurred": False,
        },
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {
                "previous_hash": None,
                "current_hash": "abc123",
                "algorithm": "SHA-256",
            },
            "evidence_tier": "lightweight",
        },
    }
    try:
        validate(instance=minimal, schema=schema)
        report("Minimal event (version + 4 required groups)", True)
    except ValidationError as e:
        report("Minimal event (version + 4 required groups)", False, str(e.message)[:120])


def test_missing_schema_version_rejected():
    """Event without schema_version is rejected."""
    schema = load_json(SCHEMA_PATH)
    invalid = {
        "decision_context": {
            "decision_id": "550e8400-e29b-41d4-a716-446655440001",
            "decision_type": "automated_assessment",
        },
        "decision_logic": {
            "logic_type": "rule_based",
            "output": "approve",
        },
        "human_override_record": {
            "override_occurred": False,
        },
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {
                "previous_hash": None,
                "current_hash": "abc123",
                "algorithm": "SHA-256",
            },
            "evidence_tier": "lightweight",
        },
    }
    try:
        validate(instance=invalid, schema=schema)
        report("Missing schema_version rejected", False, "Invalid event was not rejected")
    except ValidationError:
        report("Missing schema_version rejected", True)


def test_invalid_schema_version_format_rejected():
    """schema_version must follow semver."""
    schema = load_json(SCHEMA_PATH)
    invalid = {
        "schema_version": "v0.3",
        "decision_context": {
            "decision_id": "550e8400-e29b-41d4-a716-446655440001",
            "decision_type": "automated_assessment",
        },
        "decision_logic": {
            "logic_type": "rule_based",
            "output": "approve",
        },
        "human_override_record": {
            "override_occurred": False,
        },
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {
                "previous_hash": None,
                "current_hash": "abc123",
                "algorithm": "SHA-256",
            },
            "evidence_tier": "lightweight",
        },
    }
    try:
        validate(instance=invalid, schema=schema)
        report("Invalid schema_version format rejected", False, "Invalid event was not rejected")
    except ValidationError:
        report("Invalid schema_version format rejected", True)


def test_missing_required_groups_rejected():
    """Event missing required property groups is rejected."""
    schema = load_json(SCHEMA_PATH)
    # Missing decision_logic, human_override_record, temporal_metadata
    invalid = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {
            "decision_id": "test",
            "decision_type": "test",
        }
    }
    try:
        validate(instance=invalid, schema=schema)
        report("Missing required groups rejected", False, "Invalid event was not rejected")
    except ValidationError:
        report("Missing required groups rejected", True)


def test_missing_override_occurred_rejected():
    """human_override_record without override_occurred is rejected."""
    schema = load_json(SCHEMA_PATH)
    invalid = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "rule_based", "output": "deny"},
        "human_override_record": {"override_decision": "none"},
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "lightweight",
        },
    }
    try:
        validate(instance=invalid, schema=schema)
        report("Missing override_occurred rejected", False, "Was not rejected")
    except ValidationError:
        report("Missing override_occurred rejected", True)


def test_invalid_logic_type_rejected():
    """Event with invalid logic_type (not core enum, not namespaced) is rejected."""
    schema = load_json(SCHEMA_PATH)
    invalid = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "INVALID", "output": "deny"},
        "human_override_record": {"override_occurred": False},
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "lightweight",
        },
    }
    try:
        validate(instance=invalid, schema=schema)
        report("Invalid logic_type rejected", False, "INVALID logic_type was not rejected")
    except ValidationError:
        report("Invalid logic_type rejected", True)


def test_namespaced_logic_type_accepted():
    """Namespaced logic_type (e.g., fintech:credit_scoring) is accepted."""
    schema = load_json(SCHEMA_PATH)
    event = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "fintech:credit_scoring", "output": "approve"},
        "human_override_record": {"override_occurred": False},
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "lightweight",
        },
    }
    try:
        validate(instance=event, schema=schema)
        report("Namespaced logic_type accepted", True)
    except ValidationError as e:
        report("Namespaced logic_type accepted", False, str(e.message)[:120])


def test_invalid_evidence_tier_rejected():
    """Event with invalid evidence_tier is rejected."""
    schema = load_json(SCHEMA_PATH)
    invalid = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "rule_based", "output": "deny"},
        "human_override_record": {"override_occurred": False},
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "invalid_tier",
        },
    }
    try:
        validate(instance=invalid, schema=schema)
        report("Invalid evidence_tier rejected", False, "invalid_tier was not rejected")
    except ValidationError:
        report("Invalid evidence_tier rejected", True)


def test_override_conditional_requires_fields():
    """When override_occurred=true, original_output/overridden_output/override_timestamp required."""
    schema = load_json(SCHEMA_PATH)
    # override_occurred=true but missing required override detail fields
    invalid = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "human_decision", "output": "approve"},
        "human_override_record": {
            "override_occurred": True,
            "override_rationale": "Better judgment",
        },
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "full",
        },
    }
    try:
        validate(instance=invalid, schema=schema)
        report("Override conditional (missing fields) rejected", False, "Was not rejected")
    except ValidationError:
        report("Override conditional (missing fields) rejected", True)


def test_override_conditional_with_fields_accepted():
    """When override_occurred=true with required fields, event validates."""
    schema = load_json(SCHEMA_PATH)
    event = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "ml_inference", "output": "deny"},
        "decision_quality_indicators": {"decision_risk_level": "high"},
        "human_override_record": {
            "override_occurred": True,
            "original_output": "deny",
            "overridden_output": "approve",
            "override_timestamp": "2026-01-01T01:00:00Z",
            "override_rationale": "Model confidence too low for this case",
            "override_actor": {"actor_id": "analyst-42", "actor_role": "senior_analyst"},
        },
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "full",
        },
    }
    try:
        validate(instance=event, schema=schema)
        report("Override conditional (with fields) accepted", True)
    except ValidationError as e:
        report("Override conditional (with fields) accepted", False, str(e.message)[:120])


# ─── Two-path human judgment tests ───────────────────────────────


def test_human_decision_requires_actor_rationale():
    """When logic_type=human_decision, override_actor and override_rationale are required."""
    schema = load_json(SCHEMA_PATH)
    # human_decision without override_actor/override_rationale should fail
    invalid = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "human_decision", "output": "approve"},
        "human_override_record": {
            "override_occurred": False,
        },
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "lightweight",
        },
    }
    try:
        validate(instance=invalid, schema=schema)
        report("human_decision without actor/rationale rejected", False, "Was not rejected")
    except ValidationError:
        report("human_decision without actor/rationale rejected", True)


def test_human_decision_with_actor_rationale_accepted():
    """human_decision with override_actor and override_rationale validates."""
    schema = load_json(SCHEMA_PATH)
    event = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "human_decision", "output": "approve"},
        "human_override_record": {
            "override_occurred": False,
            "override_actor": {"actor_id": "judge-1", "actor_role": "adjudicator"},
            "override_rationale": "Primary human judgment based on case review",
        },
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "lightweight",
        },
    }
    try:
        validate(instance=event, schema=schema)
        report("human_decision with actor/rationale accepted", True)
    except ValidationError as e:
        report("human_decision with actor/rationale accepted", False, str(e.message)[:120])


def test_human_decision_override_true_requires_output_fields():
    """human_decision + override_occurred=true requires both actor AND output fields."""
    schema = load_json(SCHEMA_PATH)
    # Has actor/rationale but missing original_output/overridden_output/override_timestamp
    invalid = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "human_decision", "output": "approve"},
        "human_override_record": {
            "override_occurred": True,
            "override_actor": {"actor_id": "judge-1", "actor_role": "adjudicator"},
            "override_rationale": "Overriding previous automated assessment",
        },
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "full",
        },
    }
    try:
        validate(instance=invalid, schema=schema)
        report("human_decision+override without output fields rejected", False, "Was not rejected")
    except ValidationError:
        report("human_decision+override without output fields rejected", True)


def test_algorithmic_override_requires_actor():
    """Non-human_decision + override_occurred=true requires override_actor and override_rationale."""
    schema = load_json(SCHEMA_PATH)
    # rule_based + override_occurred=true but missing override_actor
    invalid = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "rule_based", "output": "deny"},
        "human_override_record": {
            "override_occurred": True,
            "original_output": "deny",
            "overridden_output": "approve",
            "override_timestamp": "2026-01-01T01:00:00Z",
            "override_rationale": "Exception case",
        },
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "full",
        },
    }
    try:
        validate(instance=invalid, schema=schema)
        report("Algorithmic override without actor rejected", False, "Was not rejected")
    except ValidationError:
        report("Algorithmic override without actor rejected", True)


def test_non_human_no_override_minimal_accepted():
    """Non-human_decision + override_occurred=false: no actor/rationale required."""
    schema = load_json(SCHEMA_PATH)
    event = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "rule_based", "output": "approve"},
        "human_override_record": {
            "override_occurred": False,
        },
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "lightweight",
        },
    }
    try:
        validate(instance=event, schema=schema)
        report("Non-human + no override (minimal) accepted", True)
    except ValidationError as e:
        report("Non-human + no override (minimal) accepted", False, str(e.message)[:120])


# ─── Tier 2 decision_risk_level tests ────────────────────────────


def test_tier2_requires_decision_risk_level():
    """Tier 2 (sampled) requires decision_quality_indicators.decision_risk_level."""
    schema = load_json(SCHEMA_PATH)
    # sampled tier without decision_quality_indicators should fail
    invalid = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "rule_based", "output": "approve"},
        "human_override_record": {"override_occurred": False},
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "sampled",
        },
    }
    try:
        validate(instance=invalid, schema=schema)
        report("Tier 2 without decision_risk_level rejected", False, "Was not rejected")
    except ValidationError:
        report("Tier 2 without decision_risk_level rejected", True)


def test_tier2_with_decision_risk_level_accepted():
    """Tier 2 (sampled) with decision_risk_level validates."""
    schema = load_json(SCHEMA_PATH)
    event = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "rule_based", "output": "approve"},
        "decision_quality_indicators": {"decision_risk_level": "medium"},
        "human_override_record": {"override_occurred": False},
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "sampled",
        },
    }
    try:
        validate(instance=event, schema=schema)
        report("Tier 2 with decision_risk_level accepted", True)
    except ValidationError as e:
        report("Tier 2 with decision_risk_level accepted", False, str(e.message)[:120])


def test_tier1_without_decision_risk_level_accepted():
    """Tier 1 (lightweight) does NOT require decision_risk_level."""
    schema = load_json(SCHEMA_PATH)
    event = {
        "schema_version": SCHEMA_VERSION,
        "decision_context": {"decision_id": "test", "decision_type": "test"},
        "decision_logic": {"logic_type": "rule_based", "output": "approve"},
        "human_override_record": {"override_occurred": False},
        "temporal_metadata": {
            "event_timestamp": "2026-01-01T00:00:00Z",
            "sequence_number": 1,
            "hash_chain": {"previous_hash": None, "current_hash": "abc", "algorithm": "SHA-256"},
            "evidence_tier": "lightweight",
        },
    }
    try:
        validate(instance=event, schema=schema)
        report("Tier 1 without decision_risk_level accepted", True)
    except ValidationError as e:
        report("Tier 1 without decision_risk_level accepted", False, str(e.message)[:120])


# ─── Schema version ───────────────────────────────────────────────


def test_schema_version_present():
    """All examples include schema_version field."""
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        has_version = "schema_version" in example
        report(f"schema_version present: {path.name}", has_version)


def test_schema_version_format():
    """schema_version follows semver pattern."""
    semver = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        version = example.get("schema_version", "")
        report(f"schema_version semver: {path.name}", bool(semver.match(version)), version)


def test_schema_version_matches_current_release():
    """All examples reference the current schema version."""
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        report(
            f"schema_version={SCHEMA_VERSION}: {path.name}",
            example.get("schema_version") == SCHEMA_VERSION,
            example.get("schema_version", ""),
        )


def test_schema_metadata_version_matches_current_release():
    """Schema metadata advertises the current schema version."""
    schema = load_json(SCHEMA_PATH)
    version_examples = schema.get("properties", {}).get("schema_version", {}).get("examples", [])
    report(
        "schema metadata version example matches current release",
        version_examples == [SCHEMA_VERSION],
        str(version_examples),
    )
    report(
        "schema description mentions current release",
        f"Version {SCHEMA_VERSION}" in schema.get("description", ""),
        schema.get("description", "")[:80],
    )


def test_release_docs_version_consistency():
    """README, docs, citation, and changelog stay aligned with the schema version."""
    readme = load_text(README_PATH)
    citation = load_text(CITATION_PATH)
    properties_doc = load_text(PROPERTIES_DOC_PATH)
    adjacent_doc = load_text(ADJACENT_DOC_PATH)
    changelog = load_text(CHANGELOG_PATH)

    checks = [
        (
            "README badge version matches current release",
            f"![Version: v{SCHEMA_VERSION}]" in readme,
            f"v{SCHEMA_VERSION}",
        ),
        (
            "README schema properties heading matches current release",
            f"## Schema Properties (v{SCHEMA_VERSION})" in readme,
            f"v{SCHEMA_VERSION}",
        ),
        (
            "README minimal event uses current schema version",
            f'"schema_version": "{SCHEMA_VERSION}"' in readme,
            SCHEMA_VERSION,
        ),
        (
            "README version section matches current release",
            f"**v{SCHEMA_VERSION}**" in readme,
            f"v{SCHEMA_VERSION}",
        ),
        (
            "README citation block matches current release",
            f"version = {{{SCHEMA_VERSION}}}" in readme,
            SCHEMA_VERSION,
        ),
        (
            "CITATION version matches current release",
            f"version: {SCHEMA_VERSION}" in citation,
            SCHEMA_VERSION,
        ),
        (
            "properties doc version matches current release",
            f"Version {SCHEMA_VERSION}" in properties_doc,
            SCHEMA_VERSION,
        ),
        (
            "adjacent specifications doc version matches current release",
            f"Version {SCHEMA_VERSION}" in adjacent_doc,
            SCHEMA_VERSION,
        ),
        (
            "changelog contains current release heading",
            f"## [{SCHEMA_VERSION}]" in changelog,
            SCHEMA_VERSION,
        ),
    ]

    for test_name, passed, detail in checks:
        report(test_name, passed, detail)


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


# ─── Contract field tests ─────────────────────────────────────────


VALID_LOGIC_TYPES = {"rule_based", "ml_inference", "hybrid", "policy_evaluation", "human_decision"}
NAMESPACED_PATTERN = re.compile(r"^[a-z][a-z0-9_]*:[a-z][a-z0-9_]*$")


def test_logic_type_valid():
    """All examples use valid logic_type (core enum or namespaced)."""
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        lt = example.get("decision_logic", {}).get("logic_type", "")
        valid = lt in VALID_LOGIC_TYPES or bool(NAMESPACED_PATTERN.match(lt))
        report(f"Valid logic_type: {path.name}", valid, lt)


def test_override_occurred_present():
    """All examples include override_occurred boolean."""
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        hor = example.get("human_override_record", {})
        present = "override_occurred" in hor and isinstance(hor["override_occurred"], bool)
        report(f"override_occurred present: {path.name}", present)


def test_evidence_tier_valid():
    """All examples use valid evidence_tier."""
    valid_tiers = {"lightweight", "sampled", "full"}
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        tier = example.get("temporal_metadata", {}).get("evidence_tier", "")
        report(f"Valid evidence_tier: {path.name}", tier in valid_tiers, tier)


def test_hash_chain_present():
    """All examples include hash_chain with required fields."""
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        hc = example.get("temporal_metadata", {}).get("hash_chain", {})
        has_required = "current_hash" in hc and "algorithm" in hc
        report(f"hash_chain present: {path.name}", has_required)


def test_event_timestamp_iso8601():
    """All examples have ISO 8601 event_timestamp."""
    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        ts = example.get("temporal_metadata", {}).get("event_timestamp", "")
        report(f"ISO 8601 event_timestamp: {path.name}", bool(iso_pattern.match(ts)), ts[:25])


def test_decision_id_in_context():
    """All examples have decision_id inside decision_context (not top-level)."""
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        ctx = example.get("decision_context", {})
        has_id = "decision_id" in ctx
        no_top_level = "decision_id" not in example
        report(f"decision_id in context: {path.name}", has_id and no_top_level)


def test_output_present():
    """All examples have output field in decision_logic."""
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        example = load_json(path)
        dl = example.get("decision_logic", {})
        report(f"output present: {path.name}", "output" in dl)


# ─── Knight Capital specific ──────────────────────────────────────


def test_knight_capital_velocity_collapse():
    """Knight Capital demonstrates velocity-driven collapse patterns."""
    path = EXAMPLES_DIR / "knight-capital-2012.json"
    if not path.exists():
        report("Knight Capital file exists", False)
        return
    ex = load_json(path)

    ctx = ex.get("decision_context", {})
    report("Knight: decision_type=transaction_execution",
           ctx.get("decision_type") == "transaction_execution")

    dl = ex.get("decision_logic", {})
    report("Knight: logic_type=rule_based", dl.get("logic_type") == "rule_based")

    qi = ex.get("decision_quality_indicators", {})
    report(
        "Knight: quality_indicators unfillable",
        qi.get("confidence_score") is None and qi.get("ground_truth_available") is False,
    )

    hor = ex.get("human_override_record", {})
    report("Knight: override_occurred=false", hor.get("override_occurred") is False)
    report("Knight: override architecturally absent", hor.get("override_decision") is None)

    tm = ex.get("temporal_metadata", {})
    report(
        "Knight: temporal_metadata recoverable",
        tm.get("event_timestamp") is not None
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

    ctx = ex.get("decision_context", {})
    report("Robodebt: decision_type=welfare_assessment",
           ctx.get("decision_type") == "welfare_assessment")

    dl = ex.get("decision_logic", {})
    report("Robodebt: logic_type=rule_based", dl.get("logic_type") == "rule_based")

    params = dl.get("parameters", {})
    report("Robodebt: logic reveals structural flaw", "structural_flaw" in params)

    qi = ex.get("decision_quality_indicators", {})
    report(
        "Robodebt: quality_indicators unfillable",
        qi.get("confidence_score") is None and qi.get("ground_truth_available") is False,
    )

    hor = ex.get("human_override_record", {})
    report("Robodebt: override_occurred=false", hor.get("override_occurred") is False)
    report(
        "Robodebt: override formally present",
        hor.get("override_decision") is not None,
        hor.get("override_decision", "")[:60] if hor.get("override_decision") else "",
    )

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

    ctx = ex.get("decision_context", {})
    report("CrowdStrike: decision_type=software_deployment",
           ctx.get("decision_type") == "software_deployment")

    dl = ex.get("decision_logic", {})
    report("CrowdStrike: logic_type=rule_based", dl.get("logic_type") == "rule_based")
    report(
        "CrowdStrike: logic fully recoverable",
        dl.get("rule_version") is not None and "Channel File 291" in dl.get("rule_version", ""),
    )

    db = ex.get("decision_boundary", {})
    report(
        "CrowdStrike: boundary well-documented",
        len(db.get("contributing_subsystems", [])) >= 4,
    )

    qi = ex.get("decision_quality_indicators", {})
    report("CrowdStrike: quality_indicators unfillable", qi.get("confidence_score") is None)

    hor = ex.get("human_override_record", {})
    report("CrowdStrike: override_occurred=false", hor.get("override_occurred") is False)
    report("CrowdStrike: override absent by design", hor.get("override_decision") is None)

    tm = ex.get("temporal_metadata", {})
    report(
        "CrowdStrike: same-day ground truth",
        "2024-07-19" in str(tm.get("ground_truth_arrival_timestamp", "")),
    )


# ─── Cloudflare specific ──────────────────────────────────────────


def test_cloudflare_scale_collapse():
    """Cloudflare demonstrates scale collapse via abstraction boundary failure."""
    path = EXAMPLES_DIR / "cloudflare-2025.json"
    if not path.exists():
        report("Cloudflare file exists", False)
        return
    ex = load_json(path)

    ctx = ex.get("decision_context", {})
    report("Cloudflare: decision_type=infrastructure_change",
           ctx.get("decision_type") == "infrastructure_change")

    dl = ex.get("decision_logic", {})
    report("Cloudflare: logic_type=rule_based", dl.get("logic_type") == "rule_based")

    hor = ex.get("human_override_record", {})
    report("Cloudflare: override_occurred=false", hor.get("override_occurred") is False)

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

    ctx = ex.get("decision_context", {})
    report("Uber ATG: decision_type=autonomous_operation",
           ctx.get("decision_type") == "autonomous_operation")

    dl = ex.get("decision_logic", {})
    report("Uber ATG: logic_type=ml_inference", dl.get("logic_type") == "ml_inference")

    params = dl.get("parameters", {})
    report(
        "Uber ATG: logic opaque (classification oscillation)",
        "reclassified" in params.get("classification_behavior", "").lower()
        or "reclassif" in params.get("classification_behavior", "").lower(),
    )

    qi = ex.get("decision_quality_indicators", {})
    report(
        "Uber ATG: quality_indicators unfillable",
        qi.get("confidence_score") is None and qi.get("ground_truth_available") is False,
    )

    hor = ex.get("human_override_record", {})
    report("Uber ATG: override_occurred=false", hor.get("override_occurred") is False)
    report(
        "Uber ATG: override captured (no intervention)",
        hor.get("override_decision") is not None
        and "no override" in hor.get("override_decision", "").lower(),
    )

    tm = ex.get("temporal_metadata", {})
    report(
        "Uber ATG: NTSB ground truth 2019",
        "2019" in str(tm.get("ground_truth_arrival_timestamp", "")),
    )


# ─── Runner ────────────────────────────────────────────────────────


if __name__ == "__main__":
    print(f"Schema: {SCHEMA_PATH}")
    print(f"Examples: {EXAMPLES_DIR}")
    print(f"Example files: {[p.name for p in sorted(EXAMPLES_DIR.glob('*.json'))]}")
    print()

    test_all_examples_valid()
    print()
    test_minimal_event_is_valid()
    test_missing_schema_version_rejected()
    test_invalid_schema_version_format_rejected()
    test_missing_required_groups_rejected()
    test_missing_override_occurred_rejected()
    test_invalid_logic_type_rejected()
    test_namespaced_logic_type_accepted()
    test_invalid_evidence_tier_rejected()
    test_override_conditional_requires_fields()
    test_override_conditional_with_fields_accepted()
    print()
    test_human_decision_requires_actor_rationale()
    test_human_decision_with_actor_rationale_accepted()
    test_human_decision_override_true_requires_output_fields()
    test_algorithmic_override_requires_actor()
    test_non_human_no_override_minimal_accepted()
    print()
    test_tier2_requires_decision_risk_level()
    test_tier2_with_decision_risk_level_accepted()
    test_tier1_without_decision_risk_level_accepted()
    print()
    test_schema_version_present()
    test_schema_version_format()
    test_schema_version_matches_current_release()
    test_schema_metadata_version_matches_current_release()
    test_release_docs_version_consistency()
    print()
    test_all_governance_properties_present()
    test_recoverability_notes()
    print()
    test_logic_type_valid()
    test_override_occurred_present()
    test_evidence_tier_valid()
    test_hash_chain_present()
    test_event_timestamp_iso8601()
    test_decision_id_in_context()
    test_output_present()
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
    print(f"Results: {PASSED} passed, {FAILED} failed")
    if FAILED > 0:
        sys.exit(1)
    else:
        print("All checks passed.")
