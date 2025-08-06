"""Command-line interface for Victoria Emergency poller."""

import logging
from pathlib import Path

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

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
@click.version_option(version="0.2.0", prog_name="vicalerts")
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


@cli.command()
@click.option(
    "--db",
    type=click.Path(exists=True),
    default="vicalerts.sqlite",
    help="Database file path",
)
@click.option(
    "--all", "show_all", is_flag=True, help="Show all events including inactive/removed"
)
@click.option(
    "--type", "feed_type", type=click.Choice(["incident", "warning"]), help="Filter by feed type"
)
@click.option("--category", help="Filter by category")
@click.option("--status", help="Filter by status (e.g., Safe, Going, Minor)")
@click.option("--limit", type=int, help="Limit number of results")
@click.option(
    "--format", 
    type=click.Choice(["table", "json", "csv"]), 
    default="table",
    help="Output format"
)
def events(db: str, show_all: bool, feed_type: str, category: str, status: str, limit: int, format: str):
    """List all tracked events."""
    from datetime import datetime
    from .database import Database
    import json
    import csv
    import sys
    
    if not Path(db).exists():
        console.print(f"[red]Database not found: {db}")
        raise click.Abort()
    
    database = Database(db)
    events_list = database.get_all_events(
        show_all=show_all,
        feed_type=feed_type,
        category=category,
        status=status,
        limit=limit
    )
    
    if not events_list:
        console.print("[yellow]No events found matching criteria")
        return
    
    # Format output based on chosen format
    if format == "json":
        print(json.dumps(events_list, indent=2, default=str))
    elif format == "csv":
        if events_list:
            writer = csv.DictWriter(
                sys.stdout, 
                fieldnames=events_list[0].keys(),
                extrasaction='ignore'
            )
            writer.writeheader()
            writer.writerows(events_list)
    else:  # table format
        table = Table(title=f"Victoria Emergency Events ({len(events_list)} found)")
        
        # Add columns
        table.add_column("Event ID", style="cyan", no_wrap=True)
        table.add_column("Headline", style="bold")
        table.add_column("Location", max_width=30)
        table.add_column("Status", no_wrap=True)
        table.add_column("Category", no_wrap=True)
        table.add_column("Last Updated", no_wrap=True)
        
        # Check if we have is_active data
        has_is_active = any("is_active" in event for event in events_list)
        if has_is_active and show_all:
            table.add_column("Active", no_wrap=True)
        
        # Add rows with color coding based on status
        for event in events_list:
            # Determine row style based on status
            status_style = "white"
            if event["status"]:
                status_lower = event["status"].lower()
                if status_lower in ["going", "active"]:
                    status_style = "red"
                elif status_lower in ["under control", "minor"]:
                    status_style = "yellow"
                elif status_lower in ["safe", "patrolled", "complete"]:
                    status_style = "green"
            
            # Format timestamp
            try:
                last_updated = datetime.fromisoformat(event["last_seen"].replace("Z", "+00:00"))
                last_updated_str = last_updated.strftime("%Y-%m-%d %H:%M")
            except:
                last_updated_str = event["last_seen"][:16]
            
            # Build row data
            row_data = [
                str(event["event_id"]),
                event["headline"] or event["source_org"] or "N/A",
                event["location"] or "N/A",
                f"[{status_style}]{event['status'] or 'N/A'}[/{status_style}]",
                event["category1"] or event["feed_type"],
                last_updated_str,
            ]
            
            if has_is_active and show_all:
                is_active = event.get("is_active", 1)
                active_str = "[green]Yes[/green]" if is_active else "[red]No[/red]"
                row_data.append(active_str)
            
            table.add_row(*row_data)
        
        console.print(table)
        
        # Add summary
        if not show_all and has_is_active:
            console.print(f"\n[dim]Showing active events only. Use --all to see all events.[/dim]")


if __name__ == "__main__":
    cli()
