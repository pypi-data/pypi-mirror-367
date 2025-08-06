"""
Push command for AirPilot CLI.
Handles pushing .air directory to GitHub repository.
"""

import subprocess
from pathlib import Path
from typing import Optional

import click

from ..ui.panels import show_error_panel, show_push_help_panel, show_success_panel
from ..utils.git import get_github_username, setup_air_git_repo


@click.command()
@click.option("--repo", help="GitHub repository URL (overrides default)")
@click.option("--help", "help_flag", is_flag=True, help="Show this message and exit")
def push(repo: Optional[str], help_flag: bool) -> None:
    """Push .air directory to GitHub

    Syncs your global ~/.air directory to GitHub repository.
    Works from any directory location.
    """
    if help_flag:
        show_push_help_panel()
        return

    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    air_dir = Path.home() / ".air"

    # Check if .air directory exists
    if not air_dir.exists():
        show_error_panel(
            "No .air directory found in your home directory.\n\n"
            "[bold]To create .air directory:[/bold]\n"
            "• Run [cyan]air init --global[/cyan] to initialize system-level intelligence\n"
            "• Or run [cyan]air init[/cyan] in a project directory first",
            title="Missing .air Directory",
        )
        return

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
                "• Or specify repo manually: [cyan]air push --repo https://github.com/user/repo[/cyan]",
                title="GitHub Username Not Found",
            )
            return
        github_repo = f"https://github.com/{username}/.air"

    # Check if we need to show clarification message
    current_dir = Path.cwd()
    is_not_home = current_dir != Path.home()
    has_local_air = (current_dir / ".air").exists()

    content = (
        f"[bold]Pushing .air directory to GitHub[/bold]\n\n"
        f"[bold]Local:[/bold] [cyan]{air_dir}[/cyan]\n"
        f"[bold]Remote:[/bold] [cyan]{github_repo}[/cyan]\n\n"
    )

    if is_not_home and has_local_air:
        content += (
            "[yellow]Note: Syncing global ~/.air (not current project)[/yellow]\n"
        )

    content += "[dim]Preparing to sync your intelligence control...[/dim]"

    console.print(Panel(content, title="AirPilot GitHub Push", border_style="blue"))

    try:
        # Setup git repository in .air directory
        setup_air_git_repo(air_dir, github_repo)

        # Check for GitHub CLI first
        has_gh_cli = False
        try:
            subprocess.run(["gh", "--version"], check=True, capture_output=True)
            has_gh_cli = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Perform push operation
        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(air_dir)

            # Add all changes
            subprocess.run(["git", "add", "-A"], check=True, capture_output=True)

            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True
            )
            if not result.stdout.strip():
                show_success_panel(
                    f"[green]No changes to push - .air directory is up to date[/green]\n\n"
                    f"[bold]Repository:[/bold] [cyan]{github_repo}[/cyan]",
                    title="AirPilot Already Up to Date",
                )
                return

            # Commit changes
            import datetime

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subprocess.run(
                ["git", "commit", "-m", f"Auto-sync {timestamp}"],
                check=True,
                capture_output=True,
            )

            # Push with force (local always wins)
            if has_gh_cli:
                # Try to create repo if it doesn't exist
                try:
                    subprocess.run(
                        ["gh", "repo", "view", f"{username}/.air"],
                        check=True,
                        capture_output=True,
                    )
                except subprocess.CalledProcessError:
                    # Repo doesn't exist, create it
                    subprocess.run(
                        [
                            "gh",
                            "repo",
                            "create",
                            ".air",
                            "--private",
                            "--description",
                            "AirPilot Intelligence Control",
                        ],
                        check=True,
                        capture_output=True,
                    )

            # Force push (local wins)
            subprocess.run(
                ["git", "push", "--force", "origin", "main"],
                check=True,
                capture_output=True,
            )

            show_success_panel(
                f"[green]SUCCESS: .air directory pushed to GitHub![/green]\n\n"
                f"[bold]Repository:[/bold] [cyan]{github_repo}[/cyan]\n"
                f"[bold]Branch:[/bold] main\n"
                f"[bold]Strategy:[/bold] Force push (local changes win)\n\n"
                f"Your intelligence control is now backed up to GitHub.",
                title="AirPilot Push Complete",
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
        elif "repository not found" in error_output.lower():
            show_error_panel(
                f"[red]Repository not found: {github_repo}[/red]\n\n"
                "[bold]Solutions:[/bold]\n"
                "• Create the repository on GitHub first\n"
                "• Or install GitHub CLI for automatic repo creation: [cyan]gh auth login[/cyan]\n"
                "• Or specify a different repo: [cyan]air push --repo <url>[/cyan]",
                title="Repository Not Found",
            )
        else:
            show_error_panel(
                f"[red]Git operation failed[/red]\n\n"
                f"[bold]Error:[/bold] {error_output}\n\n"
                "[bold]Possible solutions:[/bold]\n"
                "• Check your internet connection\n"
                "• Verify GitHub repository exists and you have push access\n"
                "• Try again in a few moments",
                title="Push Failed",
            )
    except Exception as e:
        show_error_panel(
            f"[red]Unexpected error during push operation[/red]\n\n"
            f"[bold]Error:[/bold] {str(e)}\n\n"
            "Please try again or contact support if the issue persists.",
            title="Push Error",
        )
