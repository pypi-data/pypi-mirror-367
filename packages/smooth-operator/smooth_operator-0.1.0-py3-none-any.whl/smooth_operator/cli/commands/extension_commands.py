# smooth_operator/cli/commands/extension_commands.py
import click
import json
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from ...channels.terminus import Terminus
from ...channels.lando import Lando
from ...core.models import Site
from .. import coro


@click.group()
def extension():
    """
    Extension management commands.
    """
    pass


@extension.command("inventory")
@click.option("--site", "-s", required=True, help="Site to analyze")
@click.option("--local", is_flag=True, help="Use local environment instead of Pantheon")
@click.option("--format", type=click.Choice(["table", "json"]), default="table", help="Output format")
@coro
@click.pass_context
async def inventory(ctx, site, local, format):
    """
    Get extension inventory for a site.
    """
    if local:
        lando = Lando(debug=ctx.obj.get("DEBUG", False))
        core_info = await lando.get_core_project_info() or {}
        noncore_info = await lando.get_noncore_project_info() or {}

        extensions = {}
        for name, project in core_info.items():
            extensions[name] = {"name": name, "project": project, "type": "core"}
        for name, project in noncore_info.items():
            extensions[name] = {"name": name, "project": project, "type": "non-core"}
    else:
        terminus = Terminus(debug=ctx.obj.get("DEBUG", False))
        if site not in terminus.sites:
            click.echo(f"Site {site} not found", err=True)
            return

        success, output = await terminus.execute(f"drush {site}.dev pm:list --format=json")
        if not success:
            click.echo(f"Error getting extensions: {output}", err=True)
            return

        try:
            extensions = json.loads(''.join(output))
        except (json.JSONDecodeError, TypeError):
            click.echo("Failed to parse extension list", err=True)
            return

    # Output the results
    if format == "json":
        click.echo(json.dumps(extensions, indent=2))
    else:
        console = Console()
        table = Table(title=f"Extensions for {site}")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Project", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Type", style="blue")

        for name, ext_data in sorted(extensions.items()):
            project = ext_data.get("project", "unknown")
            status = ext_data.get("status", "unknown")
            ext_type = ext_data.get("type", "unknown")
            table.add_row(name, project, status, ext_type)

        console.print(table)
