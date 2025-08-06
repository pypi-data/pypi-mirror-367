"""
Pull command for AirPilot CLI.
Handles pulling .air directory from GitHub repository.
"""

import subprocess
from pathlib import Path
from typing import Optional

import click

from ..ui.panels import show_error_panel, show_pull_help_panel, show_success_panel
from ..ui.prompts import confirm_action
from ..utils.git import get_github_username, setup_air_git_repo


@click.command()
@click.option("--repo", help="GitHub repository URL (overrides default)")
@click.option("--force", is_flag=True, help="Force pull and overwrite local changes")
@click.option("--help", "help_flag", is_flag=True, help="Show this message and exit")
def pull(repo: Optional[str], force: bool, help_flag: bool) -> None:
    """Pull .air directory from GitHub

    Syncs your global ~/.air directory from GitHub repository.
    Works from any directory location.
    """
    if help_flag:
        show_pull_help_panel()
        return

    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    air_dir = Path.home() / ".air"

    # Get GitHub repository URL
    if repo:
        github_repo = repo
    else:
        username = get_github_username()
        if not username:
            show_error_panel(
                "Could not determine GitHub username.\n\n"
                "[bold]Solutions:[/bold]\n"
                '• Set up git config: [cyan]git config --global user.name "YourName"[/cyan]\n'
                "• Or specify repo manually: [cyan]air pull --repo https://github.com/user/repo[/cyan]",
                title="GitHub Username Not Found",
            )
            return
        github_repo = f"https://github.com/{username}/.air"

    # Check if we need to show clarification message
    current_dir = Path.cwd()
    is_not_home = current_dir != Path.home()
    has_local_air = (current_dir / ".air").exists()

    content = (
        f"[bold]Pulling .air directory from GitHub[/bold]\n\n"
        f"[bold]Remote:[/bold] [cyan]{github_repo}[/cyan]\n"
        f"[bold]Local:[/bold] [cyan]{air_dir}[/cyan]\n\n"
    )

    if is_not_home and has_local_air:
        content += (
            "[yellow]Note: Syncing global ~/.air (not current project)[/yellow]\n"
        )

    content += "[dim]Preparing to sync your intelligence control...[/dim]"

    console.print(Panel(content, title="AirPilot GitHub Pull", border_style="blue"))

    try:
        # Handle first-time setup (no .air directory)
        if not air_dir.exists():
            console.print(
                Panel(
                    f"[yellow]No .air directory found[/yellow]\n\n"
                    f"[bold]Cloning from GitHub:[/bold]\n"
                    f"[cyan]{github_repo}[/cyan]",
                    title="First-Time Setup",
                    border_style="yellow",
                )
            )

            # Clone the repository
            subprocess.run(
                ["git", "clone", github_repo, str(air_dir)],
                check=True,
                capture_output=True,
            )

            show_success_panel(
                f"[green]SUCCESS: .air directory cloned from GitHub![/green]\n\n"
                f"[bold]Repository:[/bold] [cyan]{github_repo}[/cyan]\n"
                f"[bold]Location:[/bold] [cyan]{air_dir}[/cyan]\n\n"
                f"Your intelligence control is now set up locally.",
                title="AirPilot Clone Complete",
            )
            return

        # Setup git repository in existing .air directory
        setup_air_git_repo(air_dir, github_repo)

        # Check for local changes before pulling
        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(air_dir)

            # Check if there are uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True
            )
            has_changes = bool(result.stdout.strip())

            if has_changes and not force:
                console.print(
                    Panel(
                        "[yellow]Local changes detected in .air directory[/yellow]\n\n"
                        "[bold]Options:[/bold]\n"
                        "• Use [cyan]--force[/cyan] to overwrite local changes\n"
                        "• Or commit your changes first: [cyan]air push[/cyan]\n\n"
                        "[bold]Continue and overwrite local changes?[/bold]",
                        title="Local Changes Found",
                        border_style="yellow",
                    )
                )
                if not confirm_action("Continue and overwrite local changes?"):
                    show_error_panel("Pull cancelled by user", title="Cancelled")
                    return

            # Fetch from remote
            subprocess.run(["git", "fetch", "origin"], check=True, capture_output=True)

            # Force reset to remote (remote always wins)
            subprocess.run(
                ["git", "reset", "--hard", "origin/main"],
                check=True,
                capture_output=True,
            )

            # Clean untracked files
            subprocess.run(["git", "clean", "-fd"], check=True, capture_output=True)

            show_success_panel(
                f"[green]SUCCESS: .air directory pulled from GitHub![/green]\n\n"
                f"[bold]Repository:[/bold] [cyan]{github_repo}[/cyan]\n"
                f"[bold]Branch:[/bold] main\n"
                f"[bold]Strategy:[/bold] Force pull (remote changes win)\n\n"
                f"Your local intelligence control is now synchronized.",
                title="AirPilot Pull Complete",
            )

        finally:
            os.chdir(original_cwd)

    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode() if e.stderr else "Unknown git error"

        if (
            "could not read Username" in error_output
            or "Authentication failed" in error_output
        ):
            show_error_panel(
                "[red]GitHub authentication failed[/red]\n\n"
                "[bold]Solutions:[/bold]\n"
                "• Set up GitHub credentials: [cyan]git config --global credential.helper store[/cyan]\n"
                "• Or install GitHub CLI: [cyan]gh auth login[/cyan]\n"
                "• Or use personal access token in repository URL",
                title="Authentication Error",
            )
        elif (
            "repository not found" in error_output.lower()
            or "not found" in error_output.lower()
        ):
            show_error_panel(
                f"[red]Repository not found: {github_repo}[/red]\n\n"
                "[bold]Solutions:[/bold]\n"
                "• Verify the repository exists on GitHub\n"
                "• Check repository name and permissions\n"
                "• Create the repository first with: [cyan]air push[/cyan]\n"
                "• Or specify a different repo: [cyan]air pull --repo <url>[/cyan]",
                title="Repository Not Found",
            )
        else:
            show_error_panel(
                f"[red]Git operation failed[/red]\n\n"
                f"[bold]Error:[/bold] {error_output}\n\n"
                "[bold]Possible solutions:[/bold]\n"
                "• Check your internet connection\n"
                "• Verify GitHub repository exists and you have access\n"
                "• Try again in a few moments",
                title="Pull Failed",
            )
    except Exception as e:
        show_error_panel(
            f"[red]Unexpected error during pull operation[/red]\n\n"
            f"[bold]Error:[/bold] {str(e)}\n\n"
            "Please try again or contact support if the issue persists.",
            title="Pull Error",
        )
