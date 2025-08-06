"""
Initialization commands for AirPilot CLI.
Handles current directory, global, and new project initialization.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click

from ..builders.config import (
    create_airpilot_global_config,
    create_airpilot_project_config,
)
from ..builders.scaffold import create_air_standard
from ..ui.panels import show_error_panel, show_init_help_panel
from ..ui.prompts import confirm_action
from ..utils.backup import backup_ai_vendors, backup_existing_air, detect_air_standard
from ..utils.git import init_git_if_needed


@click.command()
@click.argument("project_name", required=False)
@click.option(
    "--global",
    "global_init",
    is_flag=True,
    help="Initialize system-level intelligence control",
)
@click.option(
    "--force", is_flag=True, help="Overwrite existing .air directory (with backup)"
)
@click.option("--help", "help_flag", is_flag=True, help="Show this message and exit")
def init(
    project_name: Optional[str], global_init: bool, force: bool, help_flag: bool
) -> None:
    """Initialize .air intelligence control

    PROJECT_NAME    Create new project directory with .air (optional)
    """
    if help_flag:
        show_init_help_panel()
        return

    try:
        if global_init:
            init_global_intelligence()
        elif project_name:
            init_new_project(project_name, force)
        else:
            init_current_directory(force)
    except KeyboardInterrupt:
        show_error_panel("Operation cancelled by user", title="Cancelled")
        sys.exit(1)
    except Exception as e:
        show_error_panel(f"Error: {e}", title="Error")
        sys.exit(1)


def init_global_intelligence() -> None:
    """Initialize system-level intelligence control at ~/.airpilot FILE and ~/.air/ DIRECTORY

    CRITICAL ARCHITECTURE:
    - ~/.airpilot = AirPilot configuration FILE (not directory!)
    - ~/.air/ = Air content DIRECTORY
    - These must NEVER be intertwined
    """
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    home = Path.home()
    # CRITICAL: .airpilot is a FILE, not a directory!
    airpilot_file = home / ".airpilot"
    air_dir = home / ".air"

    console.print(
        Panel(
            "[bold]Initializing System-Level Intelligence Control[/bold]\n\n"
            f"Creating:\n"
            f"• {airpilot_file} (AirPilot configuration FILE)\n"
            f"• {air_dir} (.air standard DIRECTORY)",
            title="Global Intelligence",
            border_style="green",
        )
    )

    # Check for existing files/directories
    existing = []
    if airpilot_file.exists():
        existing.append(str(airpilot_file))
    if air_dir.exists():
        existing.append(str(air_dir))

    if existing:
        console.print(
            Panel(
                f"[yellow]Found existing files/directories:[/yellow]\n"
                f"• {chr(10).join(existing)}\n\n"
                f"[bold]Continue and merge with existing?[/bold]",
                title="Existing Files Found",
                border_style="yellow",
            )
        )
        if not confirm_action("Continue and merge with existing?"):
            show_error_panel("Operation cancelled", title="Cancelled")
            return

    # Create AirPilot configuration FILE (not directory!)
    try:
        create_airpilot_global_config(home)
    except Exception as e:
        show_error_panel(
            f"Failed to create AirPilot configuration:\n{str(e)}\n\n"
            f"[bold]Possible solutions:[/bold]\n"
            f"• Check that {airpilot_file} is not a directory\n"
            f"• Verify you have write permissions to your home directory\n"
            f"• Try removing {airpilot_file} manually if it's corrupted",
            title="Configuration Error",
        )
        return

    # Create .air standard implementation
    try:
        create_air_standard(air_dir)
    except Exception as e:
        show_error_panel(
            f"Failed to create .air standard:\n{str(e)}\n\n"
            f"[bold]Possible solutions:[/bold]\n"
            f"• Check that {air_dir} is a directory, not a file\n"
            f"• Verify you have write permissions to your home directory\n"
            f"• Try removing {air_dir} manually if it's corrupted",
            title="Air Standard Error",
        )
        return

    console.print(
        Panel(
            f"[green]SUCCESS: System-level intelligence control initialized![/green]\n\n"
            f"[bold]Next steps:[/bold]\n"
            f"• Configure your preferences in [cyan]{airpilot_file}[/cyan]\n"
            f"• Add global rules and prompts to [cyan]{air_dir}/[/cyan]\n"
            f"• Run [cyan]air init[/cyan] in project directories to inherit from global",
            title="Global Intelligence Control Initialized",
            border_style="green",
        )
    )


def init_current_directory(force: bool) -> None:
    """Initialize .air in current directory

    CRITICAL ARCHITECTURE:
    - project/.airpilot = AirPilot configuration FILE (not directory!)
    - project/.air/ = Air content DIRECTORY
    - These must NEVER be intertwined
    """
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    current_dir = Path.cwd()

    console.print(
        Panel(
            f"[bold]Initializing Intelligence Control[/bold]\n\n"
            f"Directory: {current_dir}",
            title="Project Intelligence",
            border_style="blue",
        )
    )

    # Check for existing .air directory
    air_dir = current_dir / ".air"
    if air_dir.exists() and not force:
        if detect_air_standard(air_dir):
            console.print(
                Panel(
                    "[yellow]Found existing .air standard directory[/yellow]\n\n"
                    "[bold]Merge with existing .air directory?[/bold]",
                    title="Existing .air Directory Found",
                    border_style="yellow",
                )
            )
            if not confirm_action("Merge with existing .air directory?"):
                show_error_panel("Operation cancelled", title="Cancelled")
                return
        else:
            backup_path = backup_existing_air(air_dir)
            console.print(
                Panel(
                    f"[yellow]Found non-standard .air directory[/yellow]\n\n"
                    f"[bold]Backup location:[/bold]\n"
                    f"[blue]{backup_path}[/blue]",
                    title="Directory Backed Up",
                    border_style="blue",
                )
            )

    # Initialize or check Git
    init_git_if_needed(current_dir)

    # Backup existing AI vendor directories
    backup_ai_vendors(current_dir)

    # Create .air standard structure
    create_air_standard(air_dir, is_project=True)

    # Create .airpilot project config
    create_airpilot_project_config(current_dir)

    console.print(
        Panel(
            "[green]SUCCESS: Project intelligence control initialized![/green]\n\n"
            "[bold]Next steps:[/bold]\n"
            "• Add project rules to [cyan].air/rules/[/cyan]\n"
            "• Configure vendors in [cyan].airpilot[/cyan]\n"
            "• Install AirPilot VSCode extension for automatic sync",
            title="Project Intelligence Control Initialized",
            border_style="green",
        )
    )


def init_new_project(project_name: str, force: bool) -> None:
    """Create new project directory with .air intelligence control"""
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    project_dir = Path.cwd() / project_name

    console.print(
        Panel(
            f"[bold]Creating New Project with Intelligence Control[/bold]\n\n"
            f"Project: {project_name}\n"
            f"Location: {project_dir}",
            title="New Project",
            border_style="green",
        )
    )

    # Check if directory already exists
    if project_dir.exists() and not force:
        console.print(
            Panel(
                f"[red]Directory '{project_name}' already exists[/red]\n\n"
                f"[bold]Continue with existing directory?[/bold]",
                title="Directory Exists",
                border_style="red",
            )
        )
        if not confirm_action("Continue with existing directory?"):
            show_error_panel("Operation cancelled", title="Cancelled")
            return

    # Create project directory
    project_dir.mkdir(exist_ok=True)

    # Change to project directory
    os.chdir(project_dir)

    # Initialize the project
    init_current_directory(force)

    console.print(
        Panel(
            f"[green]SUCCESS: New project '{project_name}' created successfully![/green]\n\n"
            f"[bold]Project location:[/bold]\n"
            f"[cyan]{project_dir}[/cyan]",
            title="Project Created",
            border_style="green",
        )
    )
