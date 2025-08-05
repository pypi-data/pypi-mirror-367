"""nus CLI for managing software updates."""
# mypy: disable-error-code="misc"

from __future__ import annotations

import platform
from importlib.metadata import version

import typer

from nus.logging_setup import logger

app = typer.Typer(
    name="nus",
    no_args_is_help=True,
)


@app.command(name="version")
def show_version() -> None:
    """Show the current version number of nus.

    Show the version number:
        nus version

    Example output:
        0.1.0
    """
    logger.info("Command `version` called.")
    typer.echo(version("nus"))
    logger.info("Version displayed successfully.")


@app.command()
def info() -> None:
    """Display information about the nus application.

    Show application information:
        nus info

    Example output:
        Application Version: 0.1.0
        Python Version: 3.8.20 (CPython)
        Platform: Darwin
    """
    logger.info("Command `info` called.")
    python_version = platform.python_version()
    python_implementation = platform.python_implementation()
    typer.echo(f"Application Version: {version('nus')}")
    typer.echo(f"Python Version: {python_version} ({python_implementation})")
    typer.echo(f"Platform: {platform.system()}")
    logger.info("Application information displayed successfully.")
