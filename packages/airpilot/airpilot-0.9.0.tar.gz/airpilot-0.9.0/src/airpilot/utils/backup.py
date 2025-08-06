"""
Backup and restore operations for AirPilot CLI.
"""

import time
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel

console = Console()


def backup_existing_air(air_dir: Path) -> Path:
    """Backup existing non-standard .air directory"""
    timestamp = int(time.time())
    backup_path = air_dir.parent / f".air.backup.{timestamp}"
    air_dir.rename(backup_path)
    return backup_path


def backup_ai_vendors(project_dir: Path) -> None:
    """Backup existing AI vendor directories"""
    vendor_dirs = [
        ".claude",
        ".cursor",
        ".cline",
        ".clinerules",
        ".github/copilot-instructions",
    ]
    found_vendors: List[str] = []

    for vendor in vendor_dirs:
        vendor_path = project_dir / vendor
        if vendor_path.exists():
            found_vendors.append(vendor)

    if found_vendors:
        vendor_list = "\n".join([f"• {v}" for v in found_vendors])
        message = (
            f"[blue]Found existing AI vendor directories:[/blue]\n"
            f"{vendor_list}\n\n"
            f"[bold]Note:[/bold] These will be backed up by AirPilot VSCode extension on first sync"
        )
        console.print(
            Panel(message, title="AI Vendor Directories Detected", border_style="blue")
        )


def detect_air_standard(air_dir: Path) -> bool:
    """Detect if existing .air directory follows the standard"""
    # Check for standard structure indicators
    rules_index = air_dir / "rules" / "index.md"
    return rules_index.exists()
