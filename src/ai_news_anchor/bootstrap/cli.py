"""Thin CLI. Parses args, calls one service, prints the result. That's it."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console

from ai_news_anchor import __version__
from ai_news_anchor.bootstrap.container import build_container
from ai_news_anchor.config.settings import Settings
from ai_news_anchor.models.broadcast import BroadcastRequest

app = typer.Typer(help="Generate a personalized AI news anchor broadcast.", no_args_is_help=True)
personas_app = typer.Typer(help="Inspect and validate anchor personas.")
app.add_typer(personas_app, name="personas")
console = Console()


@app.command()
def version() -> None:
    """Print the version string."""
    console.print(f"ai-news-anchor-generator {__version__}")


@app.command()
def render(
    feed: list[str] = typer.Option(..., "--feed", "-f", help="Feed URL (repeatable)."),
    persona: str = typer.Option("neutral-prime", "--persona", "-p"),
    topics: str = typer.Option("", "--topics", "-t", help="Comma-separated interest tags."),
    out: Path | None = typer.Option(None, "--out", "-o"),
) -> None:
    """Render a broadcast from one or more feeds for a given persona."""
    settings = Settings()
    if out is not None:
        settings = settings.model_copy(update={"output_dir": out})
    container = build_container(settings)
    request = BroadcastRequest(
        feed_urls=tuple(feed),
        persona=persona,
        interest_tags=tuple(t.strip() for t in topics.split(",") if t.strip()),
    )
    result = asyncio.run(container.broadcast.run(request))
    console.print(f"[green]rendered[/] {result.audio_path}")
    console.print(f"[green]script[/]   {result.script_path}")


@personas_app.command("list")
def personas_list() -> None:
    """List available anchor personas."""
    from ai_news_anchor.config.personas import load_personas

    for p in load_personas():
        console.print(f"{p.slug:<20} {p.display_name}")


@personas_app.command("validate")
def personas_validate() -> None:
    """Validate every persona YAML on disk."""
    from ai_news_anchor.config.personas import load_personas

    loaded = load_personas()
    console.print(f"[green]ok[/] {len(loaded)} persona(s) valid")


if __name__ == "__main__":
    app()