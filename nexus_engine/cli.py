"""Main CLI entrypoint for Nexus Engine."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from .config import (
    DEFAULT_CONFIG_DIR,
    get_api_key,
    get_config_file,
    load_config,
    save_config,
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
        ("yt_dlp", "YouTube transcript extraction"),
    ]

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
def configure(key: Optional[str], value: Optional[str], list_keys: bool) -> None:
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
    console.print(f"[yellow]Search not yet implemented[/yellow]")
    console.print(f"Query: {query}, Limit: {limit}")


@main.command()
@click.argument("url")
def read(url: str) -> None:
    """Read content from a URL (placeholder)."""
    console.print(f"[yellow]Read not yet implemented[/yellow]")
    console.print(f"URL: {url}")


def main_entry() -> None:
    """Entry point for setuptools."""
    main()


if __name__ == "__main__":
    main_entry()
