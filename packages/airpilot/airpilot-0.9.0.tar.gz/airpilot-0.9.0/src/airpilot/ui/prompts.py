"""
User interaction prompts for AirPilot CLI.
"""

from rich.prompt import Confirm


def confirm_action(message: str) -> bool:
    """Ask user for confirmation"""
    return Confirm.ask(message)


def confirm_overwrite(path: str) -> bool:
    """Ask user to confirm overwrite operation"""
    return Confirm.ask(f"Overwrite existing {path}?")


def confirm_merge(directory: str) -> bool:
    """Ask user to confirm merge operation"""
    return Confirm.ask(f"Merge with existing {directory} directory?")
