# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

continue-implementation

## Roadmap

### continue-implementation — Continue implementation and resolve known failures

Status: in_progress

Acceptance:
- Run checks, fix failures, and implement the next planned feature

### fix-youtube-transcript-parsing — Fix YouTube transcript VTT parsing and urllib import

Status: done

Acceptance:
- parse_vtt correctly handles VTT format with empty lines between cues
- parse_timestamp handles empty string input without ValueError
- urllib.request imported at module level for proper mocking in tests
- All 33 tests pass
- Ruff linting passes
- Mypy passes for youtube.py

Implementation: `nexus_engine/channels/youtube.py`

Tests: `tests/test_youtube.py::TestParseVTT::test_simple_vtt`, `tests/test_youtube.py::TestParseVTT::test_vtt_with_formatting`, `tests/test_youtube.py::TestGetTranscript::test_get_transcript_success`

