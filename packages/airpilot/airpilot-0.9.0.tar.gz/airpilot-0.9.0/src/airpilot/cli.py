#!/usr/bin/env python3
"""
AirPilot CLI - Universal Intelligence Control

Command-line interface for initializing and managing .air directories
and AirPilot global intelligence control.
"""

import sys
from typing import Optional

import click

from .commands.init import init
from .commands.license import license
from .commands.pull import pull
from .commands.push import push
from .commands.status import status
from .commands.sync import sync
from .ui.panels import show_error_panel, show_main_help_panel, show_version_panel
from .utils.version import get_version

__version__ = get_version()


class AirPilotGroup(click.Group):
    """Custom Click Group that handles unknown commands with Panel UI"""

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        """Override to handle unknown commands with Panel UI"""
        rv = super().get_command(ctx, cmd_name)
        if rv is not None:
            return rv

        # Command not found - show beautiful error panel
        show_error_panel(
            f"Unknown command '[yellow]{cmd_name}[/yellow]'\n\n"
            f"[bold]Available commands:[/bold]\n"
            f"• [cyan]air init[/cyan] - Initialize intelligence control\n"
            f"• [cyan]air license[/cyan] - Manage AirPilot license\n"
            f"• [cyan]air push[/cyan] - Push .air directory to GitHub\n"
            f"• [cyan]air pull[/cyan] - Pull .air directory from GitHub\n"
            f"• [cyan]air status[/cyan] - Check system status\n"
            f"• [cyan]air sync[/cyan] - Premium: Real-time vendor sync\n\n"
            f"Run [dim]air --help[/dim] for more information.",
            title="Command Not Found",
        )
        sys.exit(1)


@click.group(cls=AirPilotGroup, invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version number")
@click.option("--help", "help_flag", is_flag=True, help="Show this message and exit")
@click.pass_context
def cli(ctx: click.Context, version: bool, help_flag: bool) -> None:
    """AirPilot - Universal Intelligence Control

    Where .git gives us version control, .air gives us intelligence control.
    """
    if version:
        show_version_panel()
        return

    if help_flag:
        show_main_help_panel()
        return

    if ctx.invoked_subcommand is None:
        show_main_help_panel()


# Register commands
cli.add_command(init)
cli.add_command(license)
cli.add_command(pull)
cli.add_command(push)
cli.add_command(status)
cli.add_command(sync)


def main() -> None:
    """Main entry point for the CLI"""
    import subprocess
    from pathlib import Path

    # Execute the native binary if it exists
    binary_path = Path(__file__).parent / "airpilot"
    if binary_path.exists():
        result = subprocess.run([str(binary_path)] + sys.argv[1:])
        sys.exit(result.returncode)

    # Fallback to Python CLI
    # Support both 'airpilot' and 'air' commands
    if len(sys.argv) > 0:
        if sys.argv[0].endswith("air"):
            # Called as 'air' - all good
            pass
        elif sys.argv[0].endswith("airpilot"):
            # Called as 'airpilot' - also good
            pass

    cli()


if __name__ == "__main__":
    main()
