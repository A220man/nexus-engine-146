# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

youtube-transcript-api-backend

## Roadmap

### continue-implementation — Continue implementation and resolve known failures

Status: done

Acceptance:
- Run checks, fix failures, and implement the next planned feature

Implementation: `nexus_engine/channels/youtube.py`, `tests/test_youtube.py`

Tests: `tests/test_youtube.py::TestParseVTT::test_simple_vtt`, `tests/test_youtube.py::TestParseVTT::test_vtt_with_formatting`, `tests/test_youtube.py::TestGetTranscript::test_get_transcript_success`

### youtube-transcript-api-backend — YouTube optional hosted transcript API backend (getyoutubetranscript.com)

Status: done

Acceptance:
- Add getyoutubetranscript backend option to YouTube channel config
- Implement fetch_transcript_getyoutubetranscript function
- Update get_transcript to use configured backend
- Update doctor command to mention API route when key is configured
- Add tests for the new backend
- All tests pass
- Ruff linting passes
- Mypy passes for youtube.py

Implementation: `nexus_engine/channels/youtube.py`, `nexus_engine/cli.py`, `tests/test_youtube.py`

Tests: `tests/test_youtube.py::TestFetchTranscriptGetYouTubeTranscript::test_getyoutubetranscript_success`, `tests/test_youtube.py::TestFetchTranscriptGetYouTubeTranscript::test_getyoutubetranscript_no_api_key`, `tests/test_youtube.py::TestFetchTranscriptGetYouTubeTranscript::test_getyoutubetranscript_http_401`, `tests/test_youtube.py::TestFetchTranscriptGetYouTubeTranscript::test_getyoutubetranscript_http_404`, `tests/test_youtube.py::TestFetchTranscriptGetYouTubeTranscript::test_getyoutubetranscript_empty_segments`, `tests/test_youtube.py::TestGetTranscriptWithBackend::test_get_transcript_getyoutubetranscript_backend`, `tests/test_youtube.py::TestGetTranscriptWithBackend::test_get_transcript_explicit_backend`

