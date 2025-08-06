"""
Status command for AirPilot CLI.
Handles checking system and GitHub integration status.
"""

import subprocess
from pathlib import Path
from typing import Tuple

import click

from ..ui.panels import show_github_status_panel, show_status_help_panel
from ..utils.git import get_github_username


@click.command()
@click.option("--github", is_flag=True, help="Check GitHub integration status")
@click.option("--help", "help_flag", is_flag=True, help="Show this message and exit")
def status(github: bool, help_flag: bool) -> None:
    """Check AirPilot system status

    Displays current system status and integration health.
    Use --github flag to check GitHub integration specifically.
    """
    if help_flag:
        show_status_help_panel()
        return

    if github:
        check_github_status()
    else:
        # For now, default to GitHub status. Could expand later for general status
        check_github_status()


def check_github_status() -> None:
    """Check and display GitHub integration status"""
    checks = []
    overall_status = "ready"
    next_steps = []

    # Check 1: GitHub CLI installation and authentication
    gh_cli_status = check_github_cli()
    checks.append(gh_cli_status)
    if not gh_cli_status[0]:
        overall_status = "setup_needed"
        if "not installed" in gh_cli_status[1]:
            next_steps.append(
                "Install GitHub CLI: [cyan]brew install gh[/cyan] (or visit github.com/cli/cli)"
            )
        elif "not authenticated" in gh_cli_status[1]:
            next_steps.append("Authenticate with GitHub: [cyan]gh auth login[/cyan]")

    # Check 2: Git configuration
    git_config_status = check_git_config()
    checks.append(git_config_status)
    if not git_config_status[0]:
        overall_status = "setup_needed"
        next_steps.append(
            'Configure Git: [cyan]git config --global user.name "Your Name"[/cyan]'
        )
        next_steps.append(
            'Configure Git: [cyan]git config --global user.email "your@email.com"[/cyan]'
        )

    # Check 3: .air directory exists
    air_dir_status = check_air_directory()
    checks.append(air_dir_status)
    if not air_dir_status[0]:
        overall_status = "setup_needed"
        next_steps.append("Initialize .air directory: [cyan]air init --global[/cyan]")

    # Check 4: Git repository in .air (only if .air exists)
    air_git_status = (True, ".air directory not initialized yet")
    if air_dir_status[0]:
        air_git_status = check_air_git_repo()
        checks.append(air_git_status)
        if not air_git_status[0]:
            overall_status = "setup_needed"

    # Check 5: GitHub repository exists (only if we have username and gh CLI)
    github_repo_status = (True, "Cannot check - prerequisites not met")
    username = get_github_username()
    if gh_cli_status[0] and username:
        github_repo_status = check_github_repository(username)
        checks.append(github_repo_status)
        if not github_repo_status[0] and "not found" in github_repo_status[1]:
            # Repository not existing is not necessarily an error - user might want to create it
            next_steps.append(
                "Create repository: [cyan]air push[/cyan] (will create repo automatically)"
            )

    show_github_status_panel(checks, overall_status, next_steps)


def check_github_cli() -> Tuple[bool, str]:
    """Check if GitHub CLI is installed and authenticated"""
    try:
        # Check if gh CLI is installed
        subprocess.run(["gh", "--version"], check=True, capture_output=True)

        # Check if authenticated
        result = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True
        )
        if result.returncode == 0:
            return (True, "GitHub CLI installed and authenticated")
        else:
            return (False, "GitHub CLI installed but not authenticated")
    except FileNotFoundError:
        return (False, "GitHub CLI not installed")
    except subprocess.CalledProcessError:
        return (False, "GitHub CLI installed but not authenticated")


def check_git_config() -> Tuple[bool, str]:
    """Check if git is configured with user name and email"""
    try:
        name_result = subprocess.run(
            ["git", "config", "--global", "user.name"],
            capture_output=True,
            text=True,
            check=True,
        )

        email_result = subprocess.run(
            ["git", "config", "--global", "user.email"],
            capture_output=True,
            text=True,
            check=True,
        )

        name = name_result.stdout.strip()
        email = email_result.stdout.strip()

        if name and email:
            return (True, f"Git configured ({name}, {email})")
        else:
            return (False, "Git configuration incomplete")
    except subprocess.CalledProcessError:
        return (False, "Git not configured")


def check_air_directory() -> Tuple[bool, str]:
    """Check if ~/.air directory exists"""
    air_dir = Path.home() / ".air"
    if air_dir.exists() and air_dir.is_dir():
        return (True, "~/.air directory exists")
    else:
        return (False, "~/.air directory not found")


def check_air_git_repo() -> Tuple[bool, str]:
    """Check if ~/.air is a git repository with proper remote"""
    air_dir = Path.home() / ".air"
    git_dir = air_dir / ".git"

    if not git_dir.exists():
        return (False, "~/.air is not a git repository")

    try:
        # Check if remote origin exists
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=air_dir,
            capture_output=True,
            text=True,
            check=True,
        )

        remote_url = result.stdout.strip()
        if "github.com" in remote_url and ".air" in remote_url:
            return (True, f"Git repository with remote: {remote_url}")
        else:
            return (
                False,
                f"Git repository but remote may not be .air repo: {remote_url}",
            )
    except subprocess.CalledProcessError:
        return (False, "Git repository but no remote origin configured")


def check_github_repository(username: str) -> Tuple[bool, str]:
    """Check if the GitHub repository exists"""
    try:
        subprocess.run(
            ["gh", "repo", "view", f"{username}/.air"], check=True, capture_output=True
        )
        return (True, f"GitHub repository {username}/.air exists")
    except subprocess.CalledProcessError:
        return (False, f"GitHub repository {username}/.air not found")
