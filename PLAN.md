# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

core-cli

## Roadmap

### core-cli — Core CLI skeleton with configuration and basic commands

Status: done

Acceptance:
- CLI entrypoint 'nexus-engine' runs and shows help
- Configuration file at ~/.config/nexus-engine/config.yaml
- Basic 'configure' command to set API keys
- Basic 'doctor' command to check environment

Implementation: `nexus_engine/cli.py`, `nexus_engine/config.py`, `pyproject.toml`

Tests: `tests/test_cli.py`, `tests/test_config.py`

### channels-youtube — YouTube channel with yt-dlp transcript extraction

Status: planned

Acceptance:
- Search YouTube videos
- Extract transcripts via yt-dlp
- Handle bot challenges gracefully

### channels-social — Social media channels (Twitter, Reddit, Instagram, TikTok, Xiaohongshu, Bilibili)

Status: planned

Acceptance:
- Search posts/profiles on each platform
- Read post content and metadata
- Support authenticated access where applicable

### channels-github — GitHub channel for code search and repo info

Status: planned

Acceptance:
- Search repositories
- Read repository metadata
- List issues/PRs

### integrations-mcp — MCP server integration

Status: planned

Acceptance:
- Run as MCP server
- Expose search/read tools to AI agents

### youtube-transcript-api — Optional GetYouTubeTranscript API backend

Status: planned

Acceptance:
- Config option for API key
- Fallback to API when yt-dlp fails with bot challenge
- Doctor reports API availability

