"""
User interface components for AirPilot CLI.
"""

from .panels import (
    show_backup_panel,
    show_error_panel,
    show_git_panel,
    show_init_help_panel,
    show_license_group_help_panel,
    show_license_help_panel,
    show_license_install_help_panel,
    show_license_remove_help_panel,
    show_license_status_help_panel,
    show_license_status_panel,
    show_main_help_panel,
    show_scaffolding_panel,
    show_success_panel,
    show_sync_help_panel,
    show_sync_panel,
    show_version_panel,
)
from .prompts import confirm_action, confirm_merge, confirm_overwrite

__all__ = [
    "show_version_panel",
    "show_main_help_panel",
    "show_success_panel",
    "show_error_panel",
    "show_license_status_panel",
    "show_license_help_panel",
    "show_license_group_help_panel",
    "show_license_install_help_panel",
    "show_license_remove_help_panel",
    "show_license_status_help_panel",
    "show_init_help_panel",
    "show_sync_help_panel",
    "show_sync_panel",
    "show_scaffolding_panel",
    "show_git_panel",
    "show_backup_panel",
    "confirm_action",
    "confirm_overwrite",
    "confirm_merge",
]
