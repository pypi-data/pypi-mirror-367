# smooth_operator/cli.py
import click
import sys
import asyncio
from .utils.logging import configure_logging
from .commands.site_commands import site
from .commands.extension_commands import extension
from .commands.upstream_commands import upstream

def coro(f):
    """A decorator to run asyncio coroutines with Click."""
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        return asyncio.run(f(ctx, *args, **kwargs))
    return wrapper

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
    configure_logging(level=log_level, file_path=log_file)

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

