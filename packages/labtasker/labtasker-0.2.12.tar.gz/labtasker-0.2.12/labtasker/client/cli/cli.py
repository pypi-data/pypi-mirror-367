"""
Implements top level cli (mainly callbacks and setup)
"""

from typing import Optional

import typer
from typing_extensions import Annotated

from labtasker import __version__
from labtasker.client.core.api import health_check
from labtasker.client.core.config import requires_client_config
from labtasker.client.core.exceptions import LabtaskerNetworkError
from labtasker.client.core.logging import stderr_console, stdout_console
from labtasker.client.core.version_checker import check_package_version

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


def version_callback(value: bool):
    if value:
        stdout_console.print(f"Labtasker Version: {__version__}")
        check_package_version(force_check=True, blocking=True)
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option(
            ..., "--version", callback=version_callback, help="Print Labtasker version."
        ),
    ] = None,
):
    if not ctx.invoked_subcommand:
        stdout_console.print(ctx.get_help())
        raise typer.Exit()


@app.command(name="help")
def help_(ctx: typer.Context):
    """Print help."""
    stdout_console.print(ctx.parent.get_help())  # type: ignore[union-attr]
    raise typer.Exit()


@app.command()
@requires_client_config
def health():
    """Check server status and connectivity."""
    try:
        stdout_console.print(health_check())
    except LabtaskerNetworkError as e:
        stderr_console.print(
            "[bold red]Error:[/bold red] Server connection is not healthy.\n"
            f"Detail: {e}"
        )
        raise typer.Exit(-1)
