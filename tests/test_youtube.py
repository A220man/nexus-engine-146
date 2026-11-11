"""Tests for YouTube channel."""

from unittest.mock import MagicMock, patch

from nexus_engine.channels.youtube import (
    extract_video_id,
    get_transcript,
    get_video_info,
    parse_timestamp,
    parse_vtt,
    search_youtube,
)


class TestExtractVideoId:
    """Tests for extract_video_id function."""

    def test_standard_url(self):
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_short_url(self):
        assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_short_url_with_www(self):
        assert extract_video_id("https://www.youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_shorts_url(self):
        assert extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_embed_url(self):
        assert extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_mobile_url(self):
        assert extract_video_id("https://m.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_invalid_url(self):
        assert extract_video_id("https://example.com/video") is None

    def test_just_id(self):
        assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"


class TestParseTimestamp:
    """Tests for parse_timestamp function."""

    def test_hms_format(self):
        assert parse_timestamp("01:23:45.678") == 5025.678

    def test_ms_format(self):
        assert parse_timestamp("23:45.678") == 1425.678

    def test_seconds_only(self):
        assert parse_timestamp("45.678") == 45.678


class TestParseVTT:
    """Tests for parse_vtt function."""

    def test_simple_vtt(self):
        vtt = """WEBVTT

00:00:01.000 --> 00:00:04.000
Hello world

00:00:05.000 --> 00:00:08.000
This is a test
"""
        segments = parse_vtt(vtt)
        assert len(segments) == 2
        assert segments[0]["start"] == 1.0
        assert segments[0]["end"] == 4.0
        assert segments[0]["text"] == "Hello world"
        assert segments[1]["start"] == 5.0
        assert segments[1]["text"] == "This is a test"

    def test_vtt_with_formatting(self):
        vtt = """WEBVTT

00:00:01.000 --> 00:00:04.000
<c>Hello</c> <b>world</b>
"""
        segments = parse_vtt(vtt)
        assert len(segments) == 1
        assert segments[0]["text"] == "Hello world"

    def test_empty_vtt(self):
        assert parse_vtt("") == []
        assert parse_vtt("WEBVTT\n\n") == []


class TestSearchYoutube:
    """Tests for search_youtube function."""

    @patch("nexus_engine.channels.youtube.subprocess.run")
    def test_search_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"id": "abc123", "title": "Test Video", "channel": "Test Channel", "duration": 120, "view_count": 1000}\n'
        mock_run.return_value = mock_result

        results = search_youtube("test query", 5)
        assert len(results) == 1
        assert results[0]["id"] == "abc123"
        assert results[0]["title"] == "Test Video"

    @patch("nexus_engine.channels.youtube.subprocess.run")
    def test_search_failure(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error occurred"
        mock_run.return_value = mock_result

        results = search_youtube("test query", 5)
        assert results == []

    @patch("nexus_engine.channels.youtube.subprocess.run")
    def test_search_timeout(self, mock_run):
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("yt-dlp", 60)

        results = search_youtube("test query", 5)
        assert results == []

    @patch("nexus_engine.channels.youtube.subprocess.run")
    def test_search_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()

        results = search_youtube("test query", 5)
        assert results == []


class TestGetTranscript:
    """Tests for get_transcript function."""

    @patch("nexus_engine.channels.youtube.subprocess.run")
    @patch("nexus_engine.channels.youtube.urllib.request.urlopen")
    def test_get_transcript_success(self, mock_urlopen, mock_run):
        # Mock yt-dlp output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"subtitles": {"en": [{"ext": "vtt", "url": "http://example.com/sub.vtt"}]}}'
        mock_run.return_value = mock_result

        # Mock subtitle fetch
        mock_response = MagicMock()
        mock_response.read.return_value = b"WEBVTT\n\n00:00:01.000 --> 00:00:04.000\nHello world"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        mock_urlopen.return_value = mock_response

        result = get_transcript("test_id", "en")
        assert result is not None
        assert "segments" in result
        assert len(result["segments"]) == 1

    @patch("nexus_engine.channels.youtube.subprocess.run")
    def test_get_transcript_bot_challenge(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Sign in to confirm you're not a bot"
        mock_run.return_value = mock_result

        result = get_transcript("test_id", "en")
        assert result is None

    @patch("nexus_engine.channels.youtube.subprocess.run")
    def test_get_transcript_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()

        result = get_transcript("test_id", "en")
        assert result is None


class TestGetVideoInfo:
    """Tests for get_video_info function."""

    @patch("nexus_engine.channels.youtube.subprocess.run")
    def test_get_video_info_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"id": "abc123", "title": "Test Video", "channel": "Test Channel", "duration": 120, "view_count": 1000, "like_count": 100, "upload_date": "20240101", "tags": ["tag1"], "thumbnail": "http://example.com/thumb.jpg", "description": "Test description"}'
        mock_run.return_value = mock_result

        info = get_video_info("abc123")
        assert info is not None
        assert info["id"] == "abc123"
        assert info["title"] == "Test Video"

    @patch("nexus_engine.channels.youtube.subprocess.run")
    def test_get_video_info_failure(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        info = get_video_info("abc123")
        assert info is None


class TestFetchTranscriptGetYouTubeTranscript:
    """Tests for fetch_transcript_getyoutubetranscript function."""

    @patch("nexus_engine.channels.youtube.urllib.request.urlopen")
    def test_getyoutubetranscript_success(self, mock_urlopen):
        from nexus_engine.channels.youtube import fetch_transcript_getyoutubetranscript

        # Mock API response
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"segments": [{"start": 0.0, "duration": 5.0, "text": "Hello world"}, {"start": 5.0, "duration": 3.0, "text": "This is a test"}]}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        mock_urlopen.return_value = mock_response

        result = fetch_transcript_getyoutubetranscript("test_id", "en", "test_api_key")
        assert result is not None
        assert "segments" in result
        assert len(result["segments"]) == 2
        assert result["segments"][0]["start"] == 0.0
        assert result["segments"][0]["end"] == 5.0
        assert result["segments"][0]["text"] == "Hello world"
        assert result["segments"][1]["start"] == 5.0
        assert result["segments"][1]["text"] == "This is a test"
        assert "Hello world This is a test" in result["full_text"]

    @patch("nexus_engine.channels.youtube.urllib.request.urlopen")
    def test_getyoutubetranscript_no_api_key(self, mock_urlopen):
        from nexus_engine.channels.youtube import fetch_transcript_getyoutubetranscript

        result = fetch_transcript_getyoutubetranscript("test_id", "en", None)
        assert result is None
        mock_urlopen.assert_not_called()

    @patch("nexus_engine.channels.youtube.urllib.request.urlopen")
    def test_getyoutubetranscript_http_401(self, mock_urlopen):
        import urllib.error

        from nexus_engine.channels.youtube import fetch_transcript_getyoutubetranscript

        mock_urlopen.side_effect = urllib.error.HTTPError(
            "http://example.com", 401, "Unauthorized", {}, None
        )

        result = fetch_transcript_getyoutubetranscript("test_id", "en", "test_api_key")
        assert result is None

    @patch("nexus_engine.channels.youtube.urllib.request.urlopen")
    def test_getyoutubetranscript_http_404(self, mock_urlopen):
        import urllib.error

        from nexus_engine.channels.youtube import fetch_transcript_getyoutubetranscript

        mock_urlopen.side_effect = urllib.error.HTTPError(
            "http://example.com", 404, "Not Found", {}, None
        )

        result = fetch_transcript_getyoutubetranscript("test_id", "en", "test_api_key")
        assert result is None

    @patch("nexus_engine.channels.youtube.urllib.request.urlopen")
    def test_getyoutubetranscript_empty_segments(self, mock_urlopen):
        from nexus_engine.channels.youtube import fetch_transcript_getyoutubetranscript

        mock_response = MagicMock()
        mock_response.read.return_value = b'{"segments": []}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        mock_urlopen.return_value = mock_response

        result = fetch_transcript_getyoutubetranscript("test_id", "en", "test_api_key")
        assert result is None


class TestGetTranscriptWithBackend:
    """Tests for get_transcript function with backend parameter."""

    @patch("nexus_engine.channels.youtube.fetch_transcript_getyoutubetranscript")
    @patch("nexus_engine.config.get_channel_config")
    def test_get_transcript_getyoutubetranscript_backend(self, mock_get_config, mock_fetch):
        from nexus_engine.channels.youtube import get_transcript

        mock_get_config.return_value = {"backend": "getyoutubetranscript", "getyoutubetranscript_api_key": "test_key"}
        mock_fetch.return_value = {"segments": [{"start": 0.0, "end": 5.0, "duration": 5.0, "text": "Test"}], "full_text": "Test"}

        result = get_transcript("test_id", "en")
        assert result is not None
        assert result["full_text"] == "Test"
        mock_fetch.assert_called_once_with("test_id", "en", "test_key")

    @patch("nexus_engine.channels.youtube.fetch_transcript_getyoutubetranscript")
    @patch("nexus_engine.config.get_channel_config")
    def test_get_transcript_explicit_backend(self, mock_get_config, mock_fetch):
        from nexus_engine.channels.youtube import get_transcript

        mock_get_config.return_value = {"backend": "yt-dlp", "getyoutubetranscript_api_key": "config_key"}
        mock_fetch.return_value = {"segments": [{"start": 0.0, "end": 5.0, "duration": 5.0, "text": "Explicit"}], "full_text": "Explicit"}

        result = get_transcript("test_id", "en", backend="getyoutubetranscript", api_key="explicit_key")
        assert result is not None
        assert result["full_text"] == "Explicit"
        mock_fetch.assert_called_once_with("test_id", "en", "explicit_key")
