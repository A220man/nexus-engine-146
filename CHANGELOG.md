# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
