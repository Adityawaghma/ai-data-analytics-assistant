# Changelog

All notable changes to this project will be documented in this file.

## [v1.0-rc] - 2026-08-28

### Added
- CSV/Excel data loading via `loader.py`
- Data cleaning and preprocessing via `cleaner.py`
- SQLite-backed storage and querying via `db.py`
- Chart generation and visualization via `charts.py`
- Machine learning pipeline via `ml_pipeline.py`
- PyQt5 desktop dashboard UI
- PDF report generation via `reporter.py`
- AI-assisted result summaries via `ai_assistant.py`
- End-to-end pytest test suite (`tests/`) with coverage reporting
- CI pipeline via GitHub Actions (`.github/workflows/ci.yml`), including
  headless UI tests via Xvfb and a separate SQL test job
- Developer documentation (`docs/ARCHITECTURE.md`, `docs/SCHEMA.md`,
  `docs/UI_COMPONENTS.md`) with Mermaid architecture and data-flow diagrams
- Performance profiling workflow (cProfile + snakeviz)

### Changed
- N/A (first release candidate)

### Fixed
- High-priority bugs resolved via test-driven bug-fix workflow
  (see closed GitHub Issues labeled `high-priority`)

### Known Issues
- <!-- list any open bugs, partially implemented features, or
      limitations that should ship with this RC -->

### Database
- Schema version: <!-- fill in current DB schema version -->
- A backup of the production database was taken prior to tagging this
  release candidate.

---

## [Unreleased]
- <!-- track work in progress for the next release here -->
