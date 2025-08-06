# smooth_operator/cli/commands/upstream_commands.py
import click
import json
import asyncio
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ...operations.updater.runner import UpstreamUpdater
from ...operations.updater.batch import BatchProcessor
from ...channels.terminus import Terminus
from ...utils.filtering import filter_sites
from .. import coro


@click.group()
def upstream():
    """
    Upstream update commands.
    """
    pass


@upstream.command("update")
@click.argument("manifests", nargs=-1, type=click.Path(exists=True))
@click.option("--site", "-s", multiple=True, help="Sites to include")
@click.option("--exclude", "-e", multiple=True, help="Sites to exclude")
@click.option("--tag", multiple=True, help="Filter sites by tag")
@click.option("--dry-run", is_flag=True, help="Simulate updates without making changes")
@click.option("--parallel", is_flag=True, help="Run updates in parallel")
@click.option("--max-workers", type=int, default=5, help="Max parallel workers")
@click.option("--re-run", is_flag=True, help="Re-run completed sites")
@click.option("--start-stage", help="Stage to start from")
@click.option("--stop-stage", help="Stage to stop at")
@click.option("--format", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.option("--refresh", is_flag=True, help="Force a refresh of the Pantheon site list")
@click.option("--batch", is_flag=True, help="Enable batch processing for large site lists")
@click.option("--batch-size", type=int, default=10, help="Number of sites per batch")
@click.option("--wait", type=int, default=60, help="Seconds to wait between batches")
@coro
@click.pass_context
async def update(
    ctx,
    manifests,
    site,
    exclude,
    tag,
    dry_run,
    parallel,
    max_workers,
    re_run,
    start_stage,
    stop_stage,
    format,
    refresh,
    batch,
    batch_size,
    wait,
):
    """
    Run upstream updates according to manifest.
    """
    debug = ctx.obj.get("DEBUG", False)

    if not manifests:
        click.echo("Error: At least one manifest file is required.", err=True)
        return

    # Get all sites from Terminus
    terminus = Terminus(debug=debug)
    all_sites = terminus.get_sites()

    # Filter sites
    sites_to_update = filter_sites(
        sites=all_sites,
        include=[s.name for s in all_sites if s.name in site] if site else None,
        exclude=list(exclude),
        tags=list(tag)
    )

    site_names_to_update = [s.name for s in sites_to_update]

    if not site_names_to_update:
        click.echo("No sites found matching the criteria.")
        return

    if batch:
        processor = BatchProcessor(
            sites=sites_to_update,
            manifest_path=list(manifests),
            batch_size=batch_size,
            wait_between_batches=wait,
            max_workers_per_batch=max_workers,
            dry_run=dry_run,
            debug=debug,
            re_run=re_run,
        )
        results = await processor.process()
    else:
        # Create and execute updater
        updater = UpstreamUpdater(
            manifest_path=list(manifests),
            sites=site_names_to_update,
            parallel=parallel,
            max_workers=max_workers,
            debug=debug,
            re_run=re_run,
            start_stage=start_stage,
            stop_stage=stop_stage,
            refresh=refresh,
        )
        # Execute the update
        results = await updater.execute(dry_run=dry_run)

    # Output results
    if format == "json":
        click.echo(json.dumps(results, indent=2))
    else:
        _display_rich_results(results)


def _display_rich_results(results: dict):
    """Display update results using rich."""
    console = Console()

    # Overall summary panel
    overall_success = all(site_res.get('success', False) for site_res in results.get('sites', {}).values())
    success_text = Text("Yes", style="green") if overall_success else Text("No", style="red")

    summary_table = Table.grid(expand=True)
    summary_table.add_column(justify="right", style="bold")
    summary_table.add_column()
    summary_table.add_row("Overall Success:", success_text)
    summary_table.add_row("Sites Processed:", str(results.get('sites_processed', 0)))
    summary_table.add_row("Elapsed Time:", f"{results.get('elapsed_time', 0):.2f}s")

    console.print(Panel(summary_table, title="[bold blue]Update Summary[/bold blue]", expand=False))

    # Site-specific results
    for site_name, site_result in results.get('sites', {}).items():
        success = site_result.get("success", False)
        status = Text("Success", style="green") if success else Text("Failed", style="red")

        site_panel_title = f"[bold]{site_name}[/bold]: {status}"

        if site_result.get("skipped"):
            console.print(Panel(f"Skipped: {site_result.get('reason')}", title=site_panel_title, border_style="yellow"))
            continue

        task_table = Table(show_header=True, header_style="bold magenta", box=None)
        task_table.add_column("Task ID")
        task_table.add_column("Status")
        task_table.add_column("Details")

        for task_id, task_result in site_result.get("tasks", {}).items():
            task_status_text = ""
            details = ""

            if task_result.get("dry_run"):
                task_status_text = Text("Dry Run", style="cyan")
                would_run = "Would run" if task_result.get("would_run", True) else "Would skip"
                details = f"{would_run} - {task_result.get('description', '')}"
            elif task_result.get("skipped"):
                task_status_text = Text("Skipped", style="yellow")
                details = task_result.get('reason', '')
            elif task_result.get("success", False):
                task_status_text = Text("Success", style="green")
            else:
                task_status_text = Text("Failed", style="red")
                details = task_result.get("error", "Unknown error")

            task_table.add_row(task_id, task_status_text, details)

        console.print(Panel(task_table, title=site_panel_title, border_style="green" if success else "red"))
