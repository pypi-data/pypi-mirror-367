"""
Sync command for AirPilot CLI.
Handles real-time vendor synchronization (premium feature).
"""

import click

from ..license import require_license
from ..ui.panels import show_sync_help_panel, show_sync_panel


@click.command()
@click.option("--help", "help_flag", is_flag=True, help="Show this message and exit")
@require_license("sync")
def sync(help_flag: bool) -> None:
    """Premium: Real-time vendor synchronization

    Synchronizes .air directory with all configured AI vendor formats.
    Requires valid AirPilot license.
    """
    if help_flag:
        show_sync_help_panel()
        return

    show_sync_panel()
