"""
Git operations for AirPilot CLI.
"""

import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

console = Console()


def init_git_if_needed(project_dir: Path) -> None:
    """Initialize Git repository if not already present"""
    git_dir = project_dir / ".git"
    if not git_dir.exists():
        try:
            subprocess.run(
                ["git", "init"], cwd=project_dir, check=True, capture_output=True
            )
            console.print(
                Panel(
                    "[green]Git repository initialized successfully[/green]",
                    title="Git Initialized",
                    border_style="green",
                )
            )
        except subprocess.CalledProcessError:
            console.print(
                Panel(
                    "[yellow]Could not initialize Git (git not available)[/yellow]",
                    title="Git Warning",
                    border_style="yellow",
                )
            )
        except FileNotFoundError:
            console.print(
                Panel(
                    "[yellow]Git not found - skipping Git initialization[/yellow]",
                    title="Git Warning",
                    border_style="yellow",
                )
            )


def get_github_username() -> Optional[str]:
    """Get GitHub username slug from GitHub CLI or existing remote"""
    try:
        # Try to get from GitHub CLI first (most reliable for actual username slug)
        result = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            capture_output=True,
            text=True,
            check=True,
        )
        username = result.stdout.strip()
        if username:
            return username
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        # Try to get from existing .air remote if it exists
        air_dir = Path.home() / ".air"
        if air_dir.exists() and (air_dir / ".git").exists():
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=air_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            remote_url = result.stdout.strip()

            # Extract username from GitHub URL
            if "github.com" in remote_url:
                if remote_url.startswith("https://github.com/"):
                    username = remote_url.split("github.com/")[1].split("/")[0]
                    return username
                elif remote_url.startswith("git@github.com:"):
                    username = remote_url.split("git@github.com:")[1].split("/")[0]
                    return username
    except subprocess.CalledProcessError:
        pass

    try:
        # Fallback: try to get from global git config (but this might be display name)
        result = subprocess.run(
            ["git", "config", "--global", "github.user"],
            capture_output=True,
            text=True,
            check=True,
        )
        username = result.stdout.strip()
        if username:
            return username
    except subprocess.CalledProcessError:
        pass

    return None


def setup_air_git_repo(air_dir: Path, github_repo: str) -> None:
    """Setup git repository in .air directory with proper remote"""
    import os

    original_cwd = Path.cwd()

    try:
        os.chdir(air_dir)

        # Initialize git if needed
        if not (air_dir / ".git").exists():
            subprocess.run(["git", "init"], check=True, capture_output=True)
            subprocess.run(
                ["git", "branch", "-M", "main"], check=True, capture_output=True
            )

        # Set up remote
        try:
            # Try to get existing remote
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True,
            )
            existing_remote = result.stdout.strip()

            # Update remote if different
            if existing_remote != github_repo:
                subprocess.run(
                    ["git", "remote", "set-url", "origin", github_repo],
                    check=True,
                    capture_output=True,
                )
        except subprocess.CalledProcessError:
            # No remote exists, add it
            subprocess.run(
                ["git", "remote", "add", "origin", github_repo],
                check=True,
                capture_output=True,
            )

    finally:
        os.chdir(original_cwd)
