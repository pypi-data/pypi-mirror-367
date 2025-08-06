"""
Configuration file builders for AirPilot.
Creates .airpilot configuration files and related config structures.
"""

import json
from pathlib import Path


def create_airpilot_global_config(home_dir: Path) -> None:
    """Create global .airpilot configuration file in user home directory

    CRITICAL ARCHITECTURE:
    - Creates ~/.airpilot FILE (not directory!)
    - Combines VSCode extension settings with Python CLI settings
    - Provides system-wide defaults that projects can inherit/override
    - Compatible with VSCode extension and future TypeScript CLI
    """
    config = {
        "// Welcome to AirPilot Global Configuration": "This file provides system-wide defaults for both VSCode extension and Python CLI",
        "// Project-level .airpilot files can override any of these settings": "",
        # VSCode Extension Settings (global defaults)
        "enabled": True,
        "source": "~/.air/rules/",  # Global air directory
        "sourceIsDirectory": True,
        "indexFileName": "index.md",
        "defaultFormat": "markdown",
        "autoSync": True,
        "showStatus": True,
        # Complete vendor definitions (based on VSCode extension)
        "vendors": {
            "augment": {
                "enabled": False,
                "path": ".augment/guidelines/",
                "format": "markdown",
                "isDirectory": True,
            },
            "claude": {
                "enabled": True,
                "path": ".claude/",
                "format": "markdown",
                "isDirectory": True,
            },
            "cline": {
                "enabled": False,
                "path": ".clinerules/rules/",
                "format": "markdown",
                "isDirectory": True,
            },
            "codex": {
                "enabled": False,
                "path": ".codex/",
                "format": "markdown",
                "isDirectory": True,
            },
            "copilot": {
                "enabled": True,
                "path": ".github/copilot-instructions/",
                "format": "markdown",
                "isDirectory": True,
            },
            "cursor": {
                "enabled": False,
                "path": ".cursor/rules/",
                "format": "markdown",
                "isDirectory": True,
            },
            "roo": {
                "enabled": False,
                "path": ".roo/rules/",
                "format": "markdown",
                "isDirectory": True,
            },
            "warpdeck": {
                "enabled": False,
                "path": ".warpdeck/rules/",
                "format": "markdown",
                "isDirectory": True,
            },
            "windsurf": {
                "enabled": False,
                "path": ".windsurf/rules/",
                "format": "markdown",
                "isDirectory": True,
            },
        },
        "customVendors": {"vendors": {}},
        # Python CLI Settings (new section)
        "cli": {
            "version": "0.7.8",
            "user": {
                "name": "",
                "email": "",
                "preferences": {
                    "default_domain": "software",
                    "auto_backup": True,
                    "sync_on_change": True,
                    "premium_features": False,
                },
            },
            "paths": {
                "global_air_path": str(Path.home() / ".air"),
                "config_file": str(home_dir / ".airpilot"),
            },
            "features": {
                "real_time_sync": False,  # Premium feature
                "cloud_backup": False,  # Premium feature
                "analytics": False,  # Premium feature
            },
            "created": "2025-01-06",
        },
    }

    airpilot_file = home_dir / ".airpilot"

    # Handle legacy .airpilot directory (architectural violation)
    if airpilot_file.exists() and airpilot_file.is_dir():
        raise ValueError(
            f"CRITICAL ARCHITECTURE VIOLATION: {airpilot_file} exists as a DIRECTORY!\n"
            f"AirPilot configuration must be a FILE, never a directory.\n\n"
            f"Please remove the directory: rm -rf {airpilot_file}\n"
            f"Then run 'air init --global' again to create the correct FILE."
        )

    # Create .airpilot FILE if it doesn't exist
    if not airpilot_file.exists():
        with open(airpilot_file, "w") as f:
            json.dump(config, f, indent=4)


def create_airpilot_project_config(project_dir: Path) -> None:
    """Create .airpilot project configuration file"""
    config = {
        "enabled": True,
        "source": ".air/rules/",
        "sourceIsDirectory": True,
        "indexFileName": "index.md",
        "defaultFormat": "markdown",
        "autoSync": True,
        "showStatus": True,
        "vendors": {
            "claude": {
                "enabled": True,
                "path": ".claude/",
                "format": "markdown",
                "isDirectory": True,
            },
            "copilot": {
                "enabled": True,
                "path": ".github/copilot-instructions/",
                "format": "markdown",
                "isDirectory": True,
            },
        },
    }

    airpilot_file = project_dir / ".airpilot"
    if not airpilot_file.exists():
        with open(airpilot_file, "w") as f:
            json.dump(config, f, indent=2)


# REMOVED: create_air_config_file function
# This function violated the fundamental architecture by placing .airpilot files
# inside .air directories. AirPilot configuration must remain separate from
# .air content directories. Use create_airpilot_config() and
# create_airpilot_project_config() instead.
