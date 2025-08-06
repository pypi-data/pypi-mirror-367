import click
import json
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from ...channels.terminus import Terminus
from ...core.models import Site
from .. import coro


@click.group()
def site():
    """
    Site management commands.
    """
    pass


@site.command("list")
@click.option("--filter", "-f", help="Filter sites by name")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@coro
@click.pass_context
async def list_sites(ctx, filter, json_output):
    """
    List Pantheon sites.
    """
    terminus = Terminus(debug=ctx.obj.get("DEBUG", False))
    sites = terminus.get_sites()

    if filter:
        sites = [s for s in sites if filter.lower() in s.name.lower()]

    if json_output:
        # Convert Site objects to dicts for JSON output
        click.echo(json.dumps([s.model_dump() for s in sites], indent=2))
    else:
        console = Console()
        table = Table(title="Pantheon Sites")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("ID", style="magenta")
        table.add_column("Framework", style="green")
        table.add_column("Organization", style="blue")
        table.add_column("Service Level", style="yellow")

        for site_obj in sites:
            table.add_row(
                site_obj.name,
                site_obj.site_id,
                site_obj.framework,
                site_obj.organization,
                site_obj.service_level
            )

        console.print(table)


@site.command("clone")
@click.argument("source_site")
@click.argument("target_site")
@click.option("--source-env", default="live", help="Source environment")
@click.option("--target-env", default="dev", help="Target environment")
@click.option("--db-only", is_flag=True, help="Clone database only")
@click.option("--files-only", is_flag=True, help="Clone files only")
@coro
@click.pass_context
async def clone_site(ctx, source_site, target_site, source_env, target_env, db_only, files_only):
    """
    Clone one site to another.
    """
    terminus = Terminus(debug=ctx.obj.get("DEBUG", False))

    # Check if sites exist
    all_sites = terminus.sites
    if source_site not in all_sites:
        click.echo(f"Source site {source_site} not found", err=True)
        return

    if target_site not in all_sites:
        click.echo(f"Target site {target_site} not found", err=True)
        return

    # Determine content type
    if db_only:
        content_type = "database"
    elif files_only:
        content_type = "files"
    else:
        content_type = "all"

    # Clone the site
    success, output = await terminus.clone_content(
        source_site=source_site,
        source_env=source_env,
        target_site=target_site,
        target_env=target_env,
        content_type=content_type
    )

    if success:
        click.echo(f"Successfully cloned {source_site} ({source_env}) to {target_site} ({target_env})")
    else:
        click.echo(f"Failed to clone site: {output}", err=True)
