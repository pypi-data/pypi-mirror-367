# smooth_operator/cli/__init__.py
import click
import sys
from ..utils.logging import configure_logging
from .commands.site_commands import site
from .commands.extension_commands import extension
from .commands.upstream_commands import upstream


@click.group()
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Enable debug output"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    default="INFO",
    help="Set logging level"
)
@click.option(
    "--log-file",
    type=click.Path(),
    help="Log to file instead of stdout"
)
@click.pass_context
def cli(ctx, debug, log_level, log_file):
    """
    Smooth Operator: CLI client for managing Drupal sites across multiple operation channels.
    """
    # Configure logging
    configure_logging(level=log_level, output_file=log_file)

    # Create context object
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug


# Register command groups
cli.add_command(site)
cli.add_command(extension)
cli.add_command(upstream)


def main():
    """
    Main entry point for the CLI.
    """
    cli(obj={})


if __name__ == "__main__":
    main()

# smooth_operator/cli/commands/site_commands.py
import click
from typing import List, Optional
from ...channels.terminus import Terminus
from ...core.site import Site


@click.group()
def site():
    """
    Site management commands.
    """
    pass


@site.command("list")
@click.option("--filter", "-f", help="Filter sites by name")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@click.pass_context
def list_sites(ctx, filter, json_output):
    """
    List Pantheon sites.
    """
    terminus = Terminus(debug=ctx.obj.get("DEBUG", False))
    sites = terminus.sites

    if filter:
        sites = [s for s in sites if filter.lower() in s.lower()]

    if json_output:
        import json
        click.echo(json.dumps(sites))
    else:
        click.echo(f"Found {len(sites)} sites:")
        for site_name in sites:
            click.echo(f"- {site_name}")


@site.command("clone")
@click.argument("source_site")
@click.argument("target_site")
@click.option("--source-env", default="live", help="Source environment")
@click.option("--target-env", default="dev", help="Target environment")
@click.option("--db-only", is_flag=True, help="Clone database only")
@click.option("--files-only", is_flag=True, help="Clone files only")
@click.pass_context
def clone_site(ctx, source_site, target_site, source_env, target_env, db_only, files_only):
    """
    Clone one site to another.
    """
    terminus = Terminus(debug=ctx.obj.get("DEBUG", False))

    # Check if sites exist
    if source_site not in terminus.sites:
        click.echo(f"Source site {source_site} not found", err=True)
        return

    if target_site not in terminus.sites:
        click.echo(f"Target site {target_site} not found", err=True)
        return

    # Create Site objects
    source = Site(name=source_site)
    target = Site(name=target_site)

    # Determine content type
    if db_only:
        content_type = "database"
    elif files_only:
        content_type = "files"
    else:
        content_type = "all"

    # Clone the site
    result = source.clone(
        source_env=source_env,
        target_site=target,
        target_env=target_env,
        content_type=content_type
    )

    if result["success"]:
        click.echo(f"Successfully cloned {source_site} ({source_env}) to {target_site} ({target_env})")
    else:
        click.echo(f"Failed to clone site: {result['output']}", err=True)