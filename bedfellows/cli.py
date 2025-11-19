"""
Modern command-line interface for Bedfellows.

Uses Click for a user-friendly CLI experience.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from bedfellows import __version__
from bedfellows.config import Config
from bedfellows.database import DatabaseManager, init_database
from bedfellows.models import (
    init_models,
    create_all_tables,
    FecCandidates,
    FecCommittees,
    FecCommitteeContributions,
    FecContributions,
    FinalScores,
)
from bedfellows.fetchers import (
    CandidateFetcher,
    CommitteeFetcher,
    ContributionFetcher,
)
from bedfellows.exporters import JSONExporter, CSVExporter, DatasetteExporter

console = Console()


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@click.group()
@click.version_option(version=__version__)
@click.option("--config", "-c", help="Path to configuration file", type=click.Path())
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cli(ctx, config, verbose):
    """
    Bedfellows - FEC Campaign Finance Relationship Analysis

    Analyze relationships between PAC donors and recipients using
    Federal Election Commission data.
    """
    setup_logging(verbose)

    # Load configuration
    ctx.ensure_object(dict)
    ctx.obj["config"] = Config(config_file=config)
    ctx.obj["verbose"] = verbose

    # Setup logging from config
    if not verbose:
        ctx.obj["config"].setup_logging()


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize database and create tables."""
    config = ctx.obj["config"]

    console.print("[bold]Initializing Bedfellows database...[/bold]")

    # Initialize database
    db_manager = DatabaseManager(config)
    db = db_manager.get_database()

    # Initialize models
    init_models(db)

    # Create tables
    create_all_tables()

    # Show database info
    stats = db_manager.get_stats()
    console.print(f"[green]✓[/green] Database initialized: {stats['type']}")

    if stats["type"] == "sqlite":
        console.print(f"  Location: {stats['path']}")


@cli.group()
def fetch():
    """Download FEC data files."""
    pass


@fetch.command("candidates")
@click.option("--cycle", "-c", help="Election cycle (e.g., 2024)")
@click.option("--all", "all_cycles", is_flag=True, help="Download all cycles")
@click.pass_context
def fetch_candidates(ctx, cycle, all_cycles):
    """Download FEC candidate master files."""
    config = ctx.obj["config"]
    data_dir = config["data_dir"]

    fetcher = CandidateFetcher(data_dir=data_dir)

    try:
        files = fetcher.fetch_candidates(cycle=cycle, all_cycles=all_cycles)
        console.print(f"[green]✓[/green] Downloaded {len(files)} file(s)")
        for f in files:
            console.print(f"  {f}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}", style="bold red")
        sys.exit(1)


@fetch.command("committees")
@click.option("--cycle", "-c", help="Election cycle (e.g., 2024)")
@click.option("--all", "all_cycles", is_flag=True, help="Download all cycles")
@click.pass_context
def fetch_committees(ctx, cycle, all_cycles):
    """Download FEC committee master files."""
    config = ctx.obj["config"]
    data_dir = config["data_dir"]

    fetcher = CommitteeFetcher(data_dir=data_dir)

    try:
        files = fetcher.fetch_committees(cycle=cycle, all_cycles=all_cycles)
        console.print(f"[green]✓[/green] Downloaded {len(files)} file(s)")
        for f in files:
            console.print(f"  {f}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}", style="bold red")
        sys.exit(1)


@fetch.command("contributions")
@click.argument("cycle")
@click.option(
    "--type",
    "contrib_type",
    type=click.Choice(["committee", "individual", "other"]),
    default="committee",
    help="Type of contributions",
)
@click.pass_context
def fetch_contributions(ctx, cycle, contrib_type):
    """Download FEC contribution files for a cycle."""
    config = ctx.obj["config"]
    data_dir = config["data_dir"]

    fetcher = ContributionFetcher(data_dir=data_dir)

    try:
        files = fetcher.fetch_contributions(cycle, contribution_type=contrib_type)
        console.print(f"[green]✓[/green] Downloaded {len(files)} file(s)")
        for f in files:
            console.print(f"  {f}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}", style="bold red")
        sys.exit(1)


@cli.group()
def load():
    """Load data into database."""
    pass


@load.command("candidates")
@click.argument("csv_file", type=click.Path(exists=True))
@click.pass_context
def load_candidates(ctx, csv_file):
    """Load candidate data from CSV file."""
    config = ctx.obj["config"]

    # Initialize database
    db_manager = DatabaseManager(config)
    db = db_manager.get_database()
    init_models(db)

    try:
        count = FecCandidates.load_from_csv(csv_file)
        console.print(f"[green]✓[/green] Loaded {count} candidate records")
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}", style="bold red")
        sys.exit(1)


@load.command("committees")
@click.argument("csv_file", type=click.Path(exists=True))
@click.pass_context
def load_committees(ctx, csv_file):
    """Load committee data from CSV file."""
    config = ctx.obj["config"]

    # Initialize database
    db_manager = DatabaseManager(config)
    db = db_manager.get_database()
    init_models(db)

    try:
        count = FecCommittees.load_from_csv(csv_file)
        console.print(f"[green]✓[/green] Loaded {count} committee records")
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}", style="bold red")
        sys.exit(1)


@load.command("contributions")
@click.argument("csv_file", type=click.Path(exists=True))
@click.pass_context
def load_contributions(ctx, csv_file):
    """Load contribution data from CSV file."""
    config = ctx.obj["config"]

    # Initialize database
    db_manager = DatabaseManager(config)
    db = db_manager.get_database()
    init_models(db)

    try:
        count = FecCommitteeContributions.load_from_csv(csv_file)
        console.print(f"[green]✓[/green] Loaded {count} contribution records")
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}", style="bold red")
        sys.exit(1)


@cli.group()
def export():
    """Export results to various formats."""
    pass


@export.command("json")
@click.argument("output_file")
@click.option("--table", "-t", default="final_scores", help="Table to export")
@click.option("--limit", "-l", type=int, help="Limit number of records")
@click.option("--pretty/--compact", default=True, help="Format JSON output")
@click.pass_context
def export_json(ctx, output_file, table, limit, pretty):
    """Export results to JSON format."""
    config = ctx.obj["config"]

    # Initialize database
    db_manager = DatabaseManager(config)
    db = db_manager.get_database()
    init_models(db)

    try:
        # Get model by table name
        model = FinalScores if table == "final_scores" else None
        if model is None:
            console.print(f"[red]✗[/red] Unknown table: {table}", style="bold red")
            sys.exit(1)

        # Export
        exporter = JSONExporter(output_file, pretty=pretty)
        exporter.export_model(model, limit=limit)

        console.print(f"[green]✓[/green] Exported to {output_file}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}", style="bold red")
        sys.exit(1)


@export.command("csv")
@click.argument("output_file")
@click.option("--table", "-t", default="final_scores", help="Table to export")
@click.option("--limit", "-l", type=int, help="Limit number of records")
@click.pass_context
def export_csv(ctx, output_file, table, limit):
    """Export results to CSV format."""
    config = ctx.obj["config"]

    # Initialize database
    db_manager = DatabaseManager(config)
    db = db_manager.get_database()
    init_models(db)

    try:
        # Get model by table name
        model = FinalScores if table == "final_scores" else None
        if model is None:
            console.print(f"[red]✗[/red] Unknown table: {table}", style="bold red")
            sys.exit(1)

        # Export
        exporter = CSVExporter(output_file)
        exporter.export_model(model, limit=limit)

        console.print(f"[green]✓[/green] Exported to {output_file}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}", style="bold red")
        sys.exit(1)


@cli.command()
@click.option("--port", "-p", type=int, help="Port for Datasette server")
@click.option("--host", "-h", default="127.0.0.1", help="Host to bind to")
@click.option("--no-browser", is_flag=True, help="Don't open browser")
@click.pass_context
def serve(ctx, port, host, no_browser):
    """Launch Datasette web interface for data exploration."""
    config = ctx.obj["config"]

    # Get port from config if not specified
    if port is None:
        port = config["datasette_port"]

    # Check if using SQLite
    if config["database_type"] != "sqlite":
        console.print(
            "[yellow]⚠[/yellow] Datasette works best with SQLite. "
            "Consider using SQLite as your database backend.",
            style="yellow",
        )
        console.print(
            "  You can export your current database to SQLite using the export command."
        )
        sys.exit(1)

    try:
        # Initialize database
        db_manager = DatabaseManager(config)
        db = db_manager.get_database()

        # Create Datasette exporter
        db_path = config["sqlite_path"]
        exporter = DatasetteExporter(db_path, port=port)

        # Create metadata
        exporter.create_metadata()

        # Launch Datasette
        console.print(f"[bold]Launching Datasette on {host}:{port}...[/bold]")
        console.print(f"Database: {db_path}")

        process = exporter.launch_datasette(
            open_browser=not no_browser, host=host
        )

        console.print("\n[green]✓[/green] Datasette is running!")
        console.print(f"  URL: http://{host}:{port}")
        console.print("  Press Ctrl+C to stop")

        # Wait for process
        try:
            process.wait()
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopping Datasette...[/yellow]")
            process.terminate()
            process.wait()

    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}", style="bold red")
        sys.exit(1)


@cli.command()
@click.pass_context
def validate(ctx):
    """Validate data quality and integrity."""
    config = ctx.obj["config"]

    console.print("[bold]Validating database...[/bold]\n")

    # Initialize database
    db_manager = DatabaseManager(config)
    db = db_manager.get_database()
    init_models(db)

    try:
        from bedfellows.validation import validate_data

        results = validate_data(db)

        # Results are already printed by validate_data
        if results["valid"]:
            console.print("\n[green]✓[/green] Data validation passed!", style="bold green")
        else:
            console.print(f"\n[red]✗[/red] Data validation failed with {len(results['errors'])} error(s)", style="bold red")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]✗[/red] Error during validation: {e}", style="bold red")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show database status and statistics."""
    config = ctx.obj["config"]

    # Initialize database
    db_manager = DatabaseManager(config)
    db = db_manager.get_database()
    init_models(db)

    # Get stats
    stats = db_manager.get_stats()

    # Create table
    table = Table(title="Bedfellows Database Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Database Type", stats["type"])

    if stats["type"] == "sqlite":
        table.add_row("Path", str(stats.get("path", "N/A")))
        if "size_mb" in stats:
            table.add_row("Size", f"{stats['size_mb']} MB")
    else:
        table.add_row("Host", str(stats.get("host", "N/A")))
        table.add_row("Database", str(stats.get("database", "N/A")))

    table.add_row("Connected", "Yes" if stats["connected"] else "No")

    console.print(table)

    # Try to get record counts
    try:
        if not db.is_closed():
            counts_table = Table(title="Record Counts")
            counts_table.add_column("Table", style="cyan")
            counts_table.add_column("Records", style="green")

            for model in [FecCandidates, FecCommittees, FecContributions, FinalScores]:
                try:
                    count = model.select().count()
                    counts_table.add_row(model._meta.table_name, f"{count:,}")
                except:
                    counts_table.add_row(model._meta.table_name, "N/A")

            console.print(counts_table)
    except Exception as e:
        console.print(f"[yellow]Could not retrieve record counts: {e}[/yellow]")


@cli.command()
@click.pass_context
def info(ctx):
    """Show configuration information."""
    config = ctx.obj["config"]

    table = Table(title="Bedfellows Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    # Database settings
    table.add_row("Database Type", config["database_type"])

    if config["database_type"] == "sqlite":
        table.add_row("SQLite Path", config["sqlite_path"])

    # Data directory
    table.add_row("Data Directory", config["data_dir"])

    # FEC settings
    table.add_row("FEC URL", config["fec_bulk_data_url"])

    # Score weights
    weights = config.get_score_weights()
    table.add_row("", "")  # Separator
    table.add_row("[bold]Score Weights[/bold]", "")
    for score_type, weight in weights.items():
        table.add_row(f"  {score_type}", str(weight))

    console.print(table)


@cli.command()
@click.option("--mode", type=click.Choice(["overall", "by-cycle"]), default="overall", help="Computation mode")
@click.pass_context
def compute(ctx, mode):
    """Compute relationship scores from loaded data."""
    config = ctx.obj["config"]

    console.print(f"[bold]Computing {mode} relationship scores...[/bold]\n")

    # Initialize database
    db_manager = DatabaseManager(config)
    db = db_manager.get_database()
    init_models(db)

    # Check if we have data
    contrib_count = FecContributions.select().count()
    if contrib_count == 0:
        console.print("[red]✗[/red] No contribution data found!", style="bold red")
        console.print("Please load data first using:")
        console.print("  bedfellows load contributions <file>")
        sys.exit(1)

    console.print(f"Found {contrib_count:,} contribution records")

    try:
        if mode == "overall":
            from bedfellows.calculators import OverallCalculator

            calc_config = {
                "weights": config.get_score_weights()
            }
            calculator = OverallCalculator(db, calc_config)
            calculator.compute_scores()

            # Show results summary
            from bedfellows.models import FinalScores
            total_scores = FinalScores.select().count()
            console.print(f"\n[green]✓[/green] Computed {total_scores:,} relationship scores")

        else:
            console.print("[yellow]⚠[/yellow] By-cycle computation not yet implemented")
            console.print("  Use 'overall' mode for now")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]✗[/red] Error computing scores: {e}", style="bold red")
        import traceback
        if ctx.obj.get("verbose"):
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument("query", required=False)
@click.option("--limit", "-l", type=int, default=20, help="Number of results")
@click.option("--donor", "-d", help="Filter by donor FEC ID")
@click.option("--recipient", "-r", help="Filter by recipient FEC ID")
@click.option("--min-score", "-s", type=float, help="Minimum score threshold")
@click.pass_context
def search(ctx, query, limit, donor, recipient, min_score):
    """Search and analyze computed scores."""
    config = ctx.obj["config"]

    # Initialize database
    db_manager = DatabaseManager(config)
    db = db_manager.get_database()
    init_models(db)

    # Check if scores exist
    score_count = FinalScores.select().count()
    if score_count == 0:
        console.print("[red]✗[/red] No scores found!", style="bold red")
        console.print("Please compute scores first using:")
        console.print("  bedfellows compute")
        sys.exit(1)

    # Build query
    query_obj = FinalScores.select()

    if donor:
        query_obj = query_obj.where(FinalScores.fec_committee_id == donor)

    if recipient:
        query_obj = query_obj.where(FinalScores.other_id == recipient)

    if min_score:
        query_obj = query_obj.where(FinalScores.final_score >= min_score)

    if query:
        # Text search in names
        query_obj = query_obj.where(
            (FinalScores.contributor_name.contains(query.upper())) |
            (FinalScores.recipient_name.contains(query.upper()))
        )

    # Order by score and limit
    query_obj = query_obj.order_by(FinalScores.final_score.desc()).limit(limit)

    results = list(query_obj)

    if not results:
        console.print("[yellow]No results found[/yellow]")
        return

    # Display results in a table
    table = Table(title=f"Top {len(results)} Relationship Scores")
    table.add_column("#", style="dim", width=4)
    table.add_column("Donor", style="cyan", width=30)
    table.add_column("Recipient", style="green", width=30)
    table.add_column("Score", justify="right", style="bold yellow", width=8)
    table.add_column("Count", justify="right", width=8)

    for i, score in enumerate(results, 1):
        table.add_row(
            str(i),
            score.contributor_name[:28] if score.contributor_name else "N/A",
            score.recipient_name[:28] if score.recipient_name else "N/A",
            f"{score.final_score:.4f}",
            str(score.count)
        )

    console.print(table)
    console.print(f"\nShowing {len(results)} of {score_count:,} total scores")


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
