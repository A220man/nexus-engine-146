"""YouTube channel implementation using yt-dlp."""

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs

from rich.console import Console

from ..config import get_channel_config

console = Console()


def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats."""
    # Handle bare video ID (11 chars, alphanumeric + hyphen/underscore)
    if re.match(r"^[A-Za-z0-9_-]{11}$", url):
        return url

    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/")
    if parsed.hostname in ("youtube.com", "www.youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/shorts/")[1].split("/")[0]
        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/embed/")[1].split("/")[0]
    return None


def search_youtube(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search YouTube videos using yt-dlp flat playlist extraction."""
    try:
        # Use yt-dlp's flat playlist to search without downloading
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--dump-json",
            f"ytsearch{limit}:{query}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            console.print(f"[red]yt-dlp search failed: {result.stderr}[/red]")
            return []

        videos = []
        for line in result.stdout.strip().split("\n"):
            if line:
                try:
                    data = json.loads(line)
                    videos.append({
                        "id": data.get("id"),
                        "title": data.get("title"),
                        "url": f"https://www.youtube.com/watch?v={data.get('id')}",
                        "channel": data.get("channel"),
                        "duration": data.get("duration"),
                        "view_count": data.get("view_count"),
                    })
                except json.JSONDecodeError:
                    continue
        return videos[:limit]
    except subprocess.TimeoutExpired:
        console.print("[red]Search timed out[/red]")
        return []
    except FileNotFoundError:
        console.print("[red]yt-dlp not found. Install with: pip install yt-dlp[/red]")
        return []


def get_transcript(video_id: str, language: str = "en") -> Optional[Dict[str, Any]]:
    """Extract transcript/subtitles from a YouTube video using yt-dlp."""
    try:
        cmd = [
            "yt-dlp",
            "--write-sub",
            "--write-auto-sub",
            "--sub-lang",
            language,
            "--skip-download",
            "--dump-json",
            f"https://www.youtube.com/watch?v={video_id}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            stderr = result.stderr.lower()
            if "sign in to confirm you're not a bot" in stderr:
                console.print("[red]YouTube bot challenge detected. Try using --cookies-from-browser or configure GetYouTubeTranscript API key.[/red]")
            else:
                console.print(f"[red]yt-dlp failed: {result.stderr}[/red]")
            return None

        # Parse the video info to get subtitle info
        data = json.loads(result.stdout)
        subtitles = data.get("subtitles", {})
        auto_subtitles = data.get("automatic_captions", {})

        # Try requested language first, then fall back to any available
        for subs in [subtitles, auto_subtitles]:
            if language in subs:
                sub_formats = subs[language]
                # Prefer vtt or srt format
                for fmt in sub_formats:
                    if fmt.get("ext") in ("vtt", "srt", "json3"):
                        sub_url = fmt.get("url")
                        if sub_url:
                            return fetch_subtitle_content(sub_url)
            # Fall back to first available language
            for lang, sub_formats in subs.items():
                for fmt in sub_formats:
                    if fmt.get("ext") in ("vtt", "srt", "json3"):
                        sub_url = fmt.get("url")
                        if sub_url:
                            console.print(f"[yellow]Using {lang} subtitles (requested: {language})[/yellow]")
                            return fetch_subtitle_content(sub_url)

        console.print("[yellow]No subtitles found for this video[/yellow]")
        return None
    except subprocess.TimeoutExpired:
        console.print("[red]Transcript extraction timed out[/red]")
        return None
    except FileNotFoundError:
        console.print("[red]yt-dlp not found. Install with: pip install yt-dlp[/red]")
        return None
    except json.JSONDecodeError:
        console.print("[red]Failed to parse yt-dlp output[/red]")
        return None


def fetch_subtitle_content(url: str) -> Optional[Dict[str, Any]]:
    """Fetch and parse subtitle content from URL."""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode("utf-8")

        # Parse VTT format
        segments = parse_vtt(content)
        return {
            "segments": segments,
            "full_text": " ".join(s["text"] for s in segments),
        }
    except Exception as e:
        console.print(f"[red]Failed to fetch subtitles: {e}[/red]")
        return None


def parse_vtt(content: str) -> List[Dict[str, Any]]:
    """Parse WebVTT subtitle content."""
    segments = []
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Skip WEBVTT header and empty lines
        if not line or line == "WEBVTT" or line.startswith("NOTE"):
            i += 1
            continue
        # Check if line is a timestamp
        if "-->" in line:
            parts = line.split("-->")
            start_str = parts[0].strip()
            end_str = parts[1].split(" ")[0].strip()

            start = parse_timestamp(start_str)
            end = parse_timestamp(end_str)

            # Collect text lines until empty line
            i += 1
            text_lines = []
            while i < len(lines) and lines[i].strip():
                text_lines.append(lines[i].strip())
                i += 1

            text = " ".join(text_lines)
            # Remove VTT formatting tags
            import re
            text = re.sub(r"<[^>]+>", "", text)

            if text:
                segments.append({
                    "start": start,
                    "end": end,
                    "duration": end - start,
                    "text": text,
                })
        else:
            i += 1
    return segments


def parse_timestamp(ts: str) -> float:
    """Parse VTT timestamp (HH:MM:SS.mmm, MM:SS.mmm, or SS.mmm) to seconds."""
    parts = ts.split(":")
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h = 0
        m, s = parts
    elif len(parts) == 1:
        h = 0
        m = 0
        s = parts[0]
    else:
        return 0.0
    return round(int(h) * 3600 + int(m) * 60 + float(s), 3)


def get_video_info(video_id: str) -> Optional[Dict[str, Any]]:
    """Get video metadata using yt-dlp."""
    try:
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-playlist",
            f"https://www.youtube.com/watch?v={video_id}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        return {
            "id": data.get("id"),
            "title": data.get("title"),
            "description": data.get("description"),
            "channel": data.get("channel"),
            "channel_id": data.get("channel_id"),
            "duration": data.get("duration"),
            "view_count": data.get("view_count"),
            "like_count": data.get("like_count"),
            "upload_date": data.get("upload_date"),
            "tags": data.get("tags", []),
            "thumbnail": data.get("thumbnail"),
        }
    except Exception:
        return None
