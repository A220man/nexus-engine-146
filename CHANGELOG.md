# Changelog

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## [0.2.0] - 2026-11-01

### Added
- YouTube channel implementation with yt-dlp integration
- `nexus-engine youtube search` command for video search
- `nexus-engine youtube transcript` command for subtitle extraction
- `nexus-engine youtube info` command for video metadata
- `youtube` optional dependency extra (yt-dlp)
- YouTube channel tests (unit tests with mocks)
- Video ID extraction from multiple URL formats
- VTT subtitle parsing with timestamp support
- Bot challenge detection and graceful error messaging

### Changed
- Updated README with YouTube commands and installation instructions
- Added youtube optional dependency to pyproject.toml
- Updated PLAN.md and feature-plan.json for channels-youtube in_progress
## [0.1.0] - 2026-10-26

### Added
- Core CLI skeleton with Click framework
- Configuration management with YAML file (`~/.config/nexus-engine/config.yaml`)
- `nexus-engine doctor` command for environment diagnostics
- `nexus-engine configure` command for API key management
- `nexus-engine search` and `nexus-engine read` placeholder commands
- Comprehensive test suite (10 tests passing)
- Support for environment variable overrides
- Optional dependency detection (playwright, browser-cookie3, yt-dlp)

### Configuration
- API keys stored in config file with environment variable override
- Channel-specific configuration (YouTube backend selection)
- Cross-platform config directory support (XDG compliant)

### Dependencies
- Core: click, pyyaml, requests, rich
- Optional: playwright (browser), browser-cookie3 (cookies), yt-dlp (YouTube)
