# Changelog

All notable changes to this repository will be documented in this file.

The format is based on Keep a Changelog and the project uses semantic versioning for schema releases.

## [0.3.0] - 2026-04-08

### Changed

- Require `schema_version` on every Decision Event instance.
- Update all bundled examples and validation fixtures to declare `0.3.0` explicitly.
- Align README, property reference, and citation metadata with the current schema contract.

### Added

- Add explicit regression tests for missing and malformed `schema_version` values.
- Add a minimal valid event example and migration guidance for v0.2.x consumers.
- Add a contribution guide and release checklist.

## [0.2.0] - 2026-04-08

### Changed

- Introduce four required top-level governance property groups.
- Add `logic_type`, `override_occurred`, `evidence_tier`, `hash_chain`, and conditional override validation.
- Add two-path human judgment design and boundary contract extensions.

## [0.1.0] - 2026-03-09

### Added

- Initial public release of the Decision Event Schema.
- Include schema definition, documentation, examples, and validation script.
