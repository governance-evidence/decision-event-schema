# Contributing

Thanks for contributing to the Decision Event Schema.

## Scope

This repository publishes a versioned JSON Schema for decision events as governance evidence units. Changes should preserve internal consistency across:

- `schema/decision-event.schema.json`
- `examples/*.json`
- `docs/*.md`
- `README.md`
- `CITATION.cff`
- `CHANGELOG.md`

## Local Checks

Run the full local validation flow before opening a pull request:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install pre-commit jsonschema
pre-commit install
pre-commit run --all-files
python tests/validate.py
```

## Change Expectations

- Update example files whenever the schema contract changes.
- Update README and docs when required fields, terminology, or versioning behavior changes.
- Keep citation metadata aligned with the current release version.
- Add or update regression coverage in `tests/validate.py` for every contract change.

## Release Checklist

Before cutting a release:

1. Bump schema version references across schema, examples, README, docs, and `CITATION.cff`.
2. Add a new entry to `CHANGELOG.md` with breaking, changed, and added items.
3. Run `pre-commit run --all-files` and `python tests/validate.py`.
4. Verify the README badge, citation block, and migration notes reference the new release.
5. Create the Git tag and publish the GitHub release notes from the changelog entry.
