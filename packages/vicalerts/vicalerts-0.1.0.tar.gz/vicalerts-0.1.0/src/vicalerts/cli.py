"""Command-line interface for Victoria Emergency poller."""

import logging
from pathlib import Path

import click
from rich.console import Console
from rich.logging import RichHandler

from .poller import Poller, PollerWithProgress

console = Console()

# Configure logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)

logger = logging.getLogger("vicalerts")


@click.group()
@click.version_option(version="0.1.0", prog_name="vicalerts")
def cli():
    """VicAlerts feed poller and change tracker."""
    pass


@cli.command()
@click.option("--once", is_flag=True, help="Run once and exit")
@click.option(
    "--interval", type=int, default=60, help="Polling interval in seconds (default: 60)"
)
@click.option(
    "--db", type=click.Path(), default="vicalerts.sqlite", help="Database file path"
)
@click.option(
    "--progress/--no-progress",
    default=True,
    help="Show countdown progress (default: enabled)",
)
def run(once: bool, interval: int, db: str, progress: bool):
    """Start polling the Victoria Emergency feed."""

    # Validate interval
    if interval < 10:
        console.print("[red]Error: Interval must be at least 10 seconds")
        raise click.Abort()

    # Create poller
    PollerClass = PollerWithProgress if progress and not once else Poller
    poller = PollerClass(db_path=db, interval=interval)

    try:
        if once:
            console.print("[blue]Running single poll...")
            poller.run_once()
        else:
            poller.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user")
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}")
        raise click.Abort()


@cli.command()
@click.option(
    "--db",
    type=click.Path(exists=True),
    default="vicalerts.sqlite",
    help="Database file path",
)
def stats(db: str):
    """Show database statistics."""
    from .database import Database

    if not Path(db).exists():
        console.print(f"[red]Database not found: {db}")
        raise click.Abort()

    database = Database(db)
    stats = database.get_stats()

    console.print("\n[bold]Victoria Emergency Database Statistics[/bold]\n")
    console.print(f"Total feeds archived: {stats['total_feeds']}")
    console.print(f"Total events tracked: {stats['total_events']}")
    console.print(f"Total versions: {stats['total_versions']}")

    if stats["events_by_type"]:
        console.print("\n[bold]Events by type:[/bold]")
        for feed_type, count in sorted(stats["events_by_type"].items()):
            console.print(f"  {feed_type}: {count}")


@cli.command()
@click.option(
    "--db",
    type=click.Path(exists=True),
    default="vicalerts.sqlite",
    help="Database file path",
)
@click.argument("event_id", type=int)
def history(db: str, event_id: int):
    """Show version history for an event."""
    from .database import Database

    database = Database(db)
    versions = database.get_event_versions(event_id)

    if not versions:
        console.print(f"[red]No event found with ID: {event_id}")
        raise click.Abort()

    console.print(f"\n[bold]History for Event {event_id}[/bold]\n")

    for i, version in enumerate(versions):
        console.print(f"[cyan]Version {i + 1} - {version['version_ts']}[/cyan]")
        console.print(f"Status: {version['status'] or 'N/A'}")
        console.print(f"Headline: {version['headline'] or 'N/A'}")
        console.print(f"Location: {version['location'] or 'N/A'}")

        if version["lat"] and version["lon"]:
            console.print(f"Coordinates: {version['lat']:.6f}, {version['lon']:.6f}")

        console.print()


if __name__ == "__main__":
    cli()
