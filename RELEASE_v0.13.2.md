# Hermes Agent v0.13.2 (v2026.5.17)

**Release Date:** May 17, 2026

> Tota Agent home-directory alignment: new fork installs now default to
> `~/.tota` while current `hermes2` deployments can keep using `~/.hermes2`
> through the legacy `HERMES_HOME` override.

## Highlights

- Added `TOTA_HOME` as the fork-native home-directory override.
- Changed the unset-env default from `~/.hermes` to `~/.tota` for new Tota
  installs, profile roots, setup scripts, and bundled Node bootstrap.
- Kept `HERMES_HOME` as a backward-compatible override so existing
  `~/.hermes2` runtimes continue to work without data migration.
- Updated focused home-directory tests and installer/help text.

## Validation

- `python -m pytest tests/test_hermes_constants.py tests/test_hermes_home_profile_warning.py tests/hermes_cli/test_config.py -q`
- `python -m ruff check hermes_constants.py hermes_cli/main.py hermes_cli/__init__.py tests/test_hermes_constants.py tests/test_hermes_home_profile_warning.py tests/hermes_cli/test_config.py scripts/build_model_catalog.py scripts/build_skills_index.py`
