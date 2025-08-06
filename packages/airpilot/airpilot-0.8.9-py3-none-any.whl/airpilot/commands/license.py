"""
License management commands for AirPilot CLI.
Handles license installation, removal, status, and help.
"""

from typing import Optional

import click

from ..license import LicenseManager
from ..ui.panels import (
    show_license_group_help_panel,
    show_license_help_panel,
    show_license_install_help_panel,
    show_license_remove_help_panel,
    show_license_status_help_panel,
    show_license_status_panel,
)
from ..ui.prompts import confirm_action


@click.group(invoke_without_command=True)
@click.option("--help", "help_flag", is_flag=True, help="Show this message and exit")
@click.pass_context
def license(ctx: click.Context, help_flag: bool) -> None:
    """Manage AirPilot license"""
    if help_flag:
        show_license_group_help_panel()
        return

    if ctx.invoked_subcommand is None:
        license_manager = LicenseManager()
        info = license_manager.get_license_info()
        show_license_status_panel(info)

        if not info["licensed"]:
            from rich.console import Console
            from rich.panel import Panel

            console = Console()
            console.print(
                Panel(
                    "[bold]Premium Features Available:[/bold]\n"
                    "• [blue]air sync[/blue] - Real-time vendor synchronization\n"
                    "• [blue]air cloud[/blue] - Cloud backup and sync (coming soon)\n\n"
                    "[bold]To get a license:[/bold]\n"
                    "1. Email: shaneholloman@gmail.com\n"
                    "2. Subject: AirPilot License Request\n"
                    "3. Include your name and use case\n\n"
                    "[bold]Once you have your key:[/bold]\n"
                    "air license install <your-license-key>",
                    title="Premium Features",
                    border_style="cyan",
                )
            )


@license.command()
@click.argument("key", required=False)
@click.option("--help", "help_flag", is_flag=True, help="Show this message and exit")
def install(key: Optional[str], help_flag: bool) -> None:
    """Install a license key"""
    if help_flag:
        show_license_install_help_panel()
        return

    if not key:
        show_license_install_help_panel()
        return

    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    license_manager = LicenseManager()

    if license_manager.install_license(key):
        info = license_manager.get_license_info()
        console.print(
            Panel(
                f"[green]SUCCESS: License installed![/green]\n\n"
                f"[bold]Plan:[/bold] {info['plan'].upper()}\n"
                f"[bold]Features:[/bold] {', '.join(info['features'])}\n\n"
                f"You can now use premium features like [green]air sync[/green]",
                title="License Installation Complete",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel(
                "[red]Invalid license key[/red]\n\n"
                "[bold]To get a license:[/bold]\n"
                "• Email: [blue]shaneholloman@gmail.com[/blue]\n"
                "• Subject: [green]AirPilot License Request[/green]\n"
                "• Include your name and use case\n\n"
                "[bold]Example format:[/bold]\n"
                "[yellow]airpilot-poc-XXXXXXXX-XXXXXXXX[/yellow]",
                title="License Installation Failed",
                border_style="red",
            )
        )


@license.command()
@click.option("--help", "help_flag", is_flag=True, help="Show this message and exit")
def remove(help_flag: bool) -> None:
    """Remove stored license and revert to free plan"""
    if help_flag:
        show_license_remove_help_panel()
        return

    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    license_manager = LicenseManager()

    if confirm_action("Remove license and revert to free plan?"):
        if license_manager.remove_license():
            console.print(
                Panel(
                    "[green]License removed successfully[/green]\n\n"
                    "[bold]Status:[/bold] Reverted to free plan\n"
                    "[bold]Available features:[/bold] init, init_global, init_project\n\n"
                    "To reinstall a license, use: [green]air license install <key>[/green]",
                    title="License Removed",
                    border_style="yellow",
                )
            )
        else:
            console.print(
                Panel(
                    "[red]Failed to remove license[/red]\n\n"
                    "This may be due to file permissions or the license file being in use.\n\n"
                    "For help, contact: [blue]shaneholloman@gmail.com[/blue]",
                    title="License Removal Failed",
                    border_style="red",
                )
            )


@license.command()
@click.option("--help", "help_flag", is_flag=True, help="Show this message and exit")
def status(help_flag: bool) -> None:
    """Show detailed license status"""
    if help_flag:
        show_license_status_help_panel()
        return

    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    license_manager = LicenseManager()
    info = license_manager.get_license_info()

    console.print(
        Panel(
            f"[bold]Plan:[/bold] {info['plan'].upper()}\n"
            f"[bold]Licensed:[/bold] {'Yes' if info['licensed'] else 'No'}\n"
            f"[bold]Features:[/bold] {', '.join(info['features'])}\n\n"
            f"[bold]Free Features:[/bold]\n"
            f"• air init - Initialize .air in current directory\n"
            f"• air init --global - Initialize system-level intelligence\n"
            f"• air init <project> - Create new project with .air\n\n"
            f"[bold]Premium Features:[/bold]\n"
            f"• air sync - Real-time vendor synchronization\n"
            f"• air cloud - Cloud backup and sync (coming soon)",
            title="AirPilot License Status",
            border_style="blue",
        )
    )


@license.command()
def help() -> None:
    """Show complete licensing instructions"""
    show_license_help_panel()
