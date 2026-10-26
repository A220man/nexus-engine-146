# Nexus Engine 146

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.


Give your AI agent eyes to see the entire internet. Read & search Twitter, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu — one CLI, zero API fees.

## Installation

```bash
pip install nexus-engine-146
```

Or install with optional dependencies:

```bash
# Browser automation support
pip install nexus-engine-146[browser]

# Cookie extraction support
pip install nexus-engine-146[cookies]

# All optional dependencies
pip install nexus-engine-146[all]
```

## Quick Start

```bash
# Check environment and configuration
nexus-engine doctor

# Configure API keys
nexus-engine configure groq_api_key "your-key-here"
nexus-engine configure youtube_transcript_api_key "your-key-here"

# List configured keys
nexus-engine configure --list

# Search (placeholder)
nexus-engine search "query"

# Read content from URL (placeholder)
nexus-engine read "https://example.com"
```

## Configuration

Configuration is stored in `~/.config/nexus-engine/config.yaml`:

```yaml
api_keys:
  groq_api_key: "your-groq-key"
  youtube_transcript_api_key: "your-youtube-transcript-key"

channels:
  youtube:
    backend: "yt-dlp"  # or "getyoutubetranscript"
    getyoutubetranscript_api_key: null

browser:
  enabled: false
```

Environment variables can override config file values:
- `NEXUS_ENGINE_GROQ_API_KEY`
- `NEXUS_ENGINE_YOUTUBE_TRANSCRIPT_API_KEY`
- `NEXUS_ENGINE_CONFIG_DIR` - Custom config directory
- `NEXUS_ENGINE_CONFIG_FILE` - Custom config file path

## Commands

### `nexus-engine doctor`
Check environment, configuration, and optional dependencies.

### `nexus-engine configure`
Manage API keys and settings.

```bash
# Set a key
nexus-engine configure KEY VALUE

# List all keys (masked)
nexus-engine configure --list
```

### `nexus-engine search` (placeholder)
Search across enabled channels.

### `nexus-engine read` (placeholder)
Read content from a URL.

## Development

```bash
# Install in development mode
pip install -e .[dev]

# Run tests
pytest tests/

# Lint
ruff check .
```

## License

MIT License - see LICENSE file for details.

Maintainer: Ryan Vo <ryandtvo@gmail.com>
