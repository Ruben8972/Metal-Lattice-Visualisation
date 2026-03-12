# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.2.3] - 2026-03-12

### Added
- MIT license.
- README screenshot for the main viewer.

### Changed
- Switched public-facing project naming to English.
- Updated package, script, and Windows executable naming to match the repository name.
- Refined the README and supporting project documentation for the current release state.

## [0.2.2] - 2026-03-01

### Added
- Local Windows release check script for validating the release-style build before tagging.

### Changed
- Refined interactive controls and improved the in-viewer status overlay layout.
- Stabilized overlay anchoring and text placement for release builds and window resizing.

## [0.2.1] - 2026-02-28

### Added
- Adaptive sphere resolution based on atom count.
- Tests for the interactive viewer resolution logic.

### Changed
- Improved interactive viewer controls and plotting behavior.

## [0.2.0] - 2026-02-28

### Added
- Interactive PyVista viewer entrypoint via `main.py` and `vis.main`.
- Module runner support (`python -m vis`).
- Windows `.exe` release workflow for GitHub tags (`v*`).

### Changed
- Package metadata and executable entry points in `setup.py`.

### Removed
- Legacy `run_vis.py`.
- Legacy `src/vis/gui.py`.
