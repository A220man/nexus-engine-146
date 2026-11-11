"""Main CLI entrypoint for Nexus Engine."""

import sys

import click
from rich.console import Console
from rich.table import Table

from .channels.youtube import (
    extract_video_id,
    get_transcript,
    get_video_info,
    search_youtube,
)
from .config import (
    DEFAULT_CONFIG_DIR,
    get_config_file,
    load_config,
    set_api_key,
)

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(version="0.1.0", prog_name="nexus-engine")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Nexus Engine - Give your AI agent eyes to see the entire internet.

    Read & search Twitter, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu
    — one CLI, zero API fees.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
def doctor() -> None:
    """Check environment and configuration status."""
    console.print("[bold]Nexus Engine Doctor[/bold]")
    console.print()

    # Check config file
    config_file = get_config_file()
    console.print(f"Config file: [cyan]{config_file}[/cyan]")
    if config_file.exists():
        console.print("  Status: [green]Found[/green]")
    else:
        console.print("  Status: [yellow]Not found (using defaults)[/yellow]")

    # Check config directory
    console.print(f"Config dir: [cyan]{DEFAULT_CONFIG_DIR}[/cyan]")
    if DEFAULT_CONFIG_DIR.exists():
        console.print("  Status: [green]Exists[/green]")
    else:
        console.print("  Status: [yellow]Not created yet[/yellow]")

    # Load and show config
    config = load_config()
    console.print()
    console.print("[bold]Configuration:[/bold]")

    # API keys (masked)
    api_keys = config.get("api_keys", {})
    if api_keys:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Key")
        table.add_column("Status")
        for key in api_keys:
            masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "****"
            table.add_row(key, f"[green]Set[/green] ({masked})")
        console.print(table)
    else:
        console.print("  API keys: [yellow]None configured[/yellow]")

    # Channel configs
    channels = config.get("channels", {})
    if channels:
        console.print()
        console.print("[bold]Channels:[/bold]")
        for channel, cfg in channels.items():
            console.print(f"  {channel}: {cfg}")

    # Check for optional dependencies
    console.print()
    console.print("[bold]Optional Dependencies:[/bold]")

    deps = [
        ("playwright", "Browser automation"),
        ("browser_cookie3", "Cookie extraction"),
        ("yt_dlp", "YouTube transcript extraction (yt-dlp backend)"),
    ]

    # Check for GetYouTubeTranscript API key
    config = load_config()
    yt_api_key = config.get("api_keys", {}).get("youtube_transcript_api_key") or config.get("channels", {}).get("youtube", {}).get("getyoutubetranscript_api_key")
    import os
    if not yt_api_key:
        yt_api_key = os.environ.get("NEXUS_ENGINE_YOUTUBE_TRANSCRIPT_API_KEY")

    if yt_api_key:
        console.print("  getyoutubetranscript: [green]Configured[/green] (YouTube transcript API backend)")
    else:
        console.print("  getyoutubetranscript: [yellow]Not configured[/yellow] (YouTube transcript API backend - set youtube_transcript_api_key to enable)")

    for module, desc in deps:
        try:
            __import__(module)
            console.print(f"  {module}: [green]Available[/green] ({desc})")
        except ImportError:
            console.print(f"  {module}: [yellow]Not installed[/yellow] ({desc})")


@main.command()
@click.argument("key", required=False)
@click.argument("value", required=False)
@click.option("--list", "list_keys", is_flag=True, help="List all configured keys")
def configure(key: str | None, value: str | None, list_keys: bool) -> None:
    """Configure API keys and settings.

    Examples:
        nexus-engine configure groq_api_key "your-key-here"
        nexus-engine configure --list
    """
    if list_keys:
        config = load_config()
        api_keys = config.get("api_keys", {})
        if api_keys:
            table = Table(show_header=True, header_style="bold")
            table.add_column("Key")
            table.add_column("Value (masked)")
            for k, v in api_keys.items():
                masked = f"{v[:4]}...{v[-4:]}" if len(v) > 8 else "****"
                table.add_row(k, masked)
            console.print(table)
        else:
            console.print("[yellow]No API keys configured[/yellow]")
        return

    if not key or not value:
        console.print("[red]Error:[/red] Both KEY and VALUE required. Use: nexus-engine configure KEY VALUE")
        sys.exit(1)

    set_api_key(key, value)
    console.print(f"[green]Set {key}[/green]")


@main.command()
@click.argument("query")
@click.option("--limit", "-l", default=10, help="Maximum results")
def search(query: str, limit: int) -> None:
    """Search across all enabled channels (placeholder)."""
    console.print("[yellow]Search not yet implemented[/yellow]")
    console.print(f"Query: {query}, Limit: {limit}")


@main.command()
@click.argument("url")
def read(url: str) -> None:
    """Read content from a URL (placeholder)."""
    console.print("[yellow]Read not yet implemented[/yellow]")
    console.print(f"URL: {url}")


@main.group()
def youtube() -> None:
    """YouTube channel commands."""
    pass


@youtube.command("search")
@click.argument("query")
@click.option("--limit", "-l", default=10, help="Maximum results")
def youtube_search(query: str, limit: int) -> None:
    """Search YouTube videos."""
    console.print(f"[cyan]Searching YouTube for:[/cyan] {query}")
    results = search_youtube(query, limit)
    if not results:
        console.print("[yellow]No results found[/yellow]")
        return
    table = Table(show_header=True, header_style="bold")
    table.add_column("Title", style="white", max_width=50)
    table.add_column("Channel", style="cyan", max_width=25)
    table.add_column("Duration", style="yellow", justify="right")
    table.add_column("Views", style="green", justify="right")
    table.add_column("ID", style="dim", max_width=15)
    for video in results:
        duration = video.get("duration")
        dur_str = f"{duration//60}:{duration%60:02d}" if duration else "N/A"
        views = video.get("view_count")
        views_str = f"{views:,}" if views else "N/A"
        table.add_row(
            video.get("title", "N/A")[:50],
            video.get("channel", "N/A")[:25],
            dur_str,
            views_str,
            video.get("id", "N/A"),
        )
    console.print(table)


@youtube.command("transcript")
@click.argument("url_or_id")
@click.option("--lang", "-l", default="en", help="Subtitle language code")
@click.option("--backend", type=click.Choice(["yt-dlp", "getyoutubetranscript"]), default=None, help="Transcript backend to use")
def youtube_transcript(url_or_id: str, lang: str, backend: str | None) -> None:
    """Extract transcript from a YouTube video."""
    video_id = extract_video_id(url_or_id) or url_or_id
    console.print(f"[cyan]Fetching transcript for video:[/cyan] {video_id}")
    if backend:
        console.print(f"[cyan]Using backend:[/cyan] {backend}")
    result = get_transcript(video_id, lang, backend=backend)
    if not result:
        return
    segments = result.get("segments", [])
    if not segments:
        console.print("[yellow]No transcript segments found[/yellow]")
        return
    console.print(f"[green]Found {len(segments)} transcript segments[/green]")
    for seg in segments:
        start = seg.get("start", 0)
        text = seg.get("text", "")
        console.print(f"[dim]{start:>7.2f}s[/dim] {text}")


@youtube.command("info")
@click.argument("url_or_id")
def youtube_info(url_or_id: str) -> None:
    """Get video metadata."""
    video_id = extract_video_id(url_or_id) or url_or_id
    console.print(f"[cyan]Fetching info for video:[/cyan] {video_id}")
    info = get_video_info(video_id)
    if not info:
        console.print("[red]Failed to fetch video info[/red]")
        return
    console.print(f"[bold]Title:[/bold] {info.get('title', 'N/A')}")
    console.print(f"[bold]Channel:[/bold] {info.get('channel', 'N/A')}")
    console.print(f"[bold]Duration:[/bold] {info.get('duration', 'N/A')}s")
    console.print(f"[bold]Views:[/bold] {info.get('view_count', 'N/A')}")
    console.print(f"[bold]Likes:[/bold] {info.get('like_count', 'N/A')}")
    console.print(f"[bold]Upload date:[/bold] {info.get('upload_date', 'N/A')}")
    if info.get("description"):
        desc = info["description"][:500]
        console.print(f"[bold]Description:[/bold] {desc}...")


def main_entry() -> None:
    """Entry point for setuptools."""
    main()


if __name__ == "__main__":
    main_entry()
