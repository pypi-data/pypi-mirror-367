"""
Utility functions for AirPilot CLI.
"""

from .backup import backup_ai_vendors, backup_existing_air, detect_air_standard
from .git import init_git_if_needed
from .version import get_version

__all__ = [
    "init_git_if_needed",
    "backup_existing_air",
    "backup_ai_vendors",
    "detect_air_standard",
    "get_version",
]
