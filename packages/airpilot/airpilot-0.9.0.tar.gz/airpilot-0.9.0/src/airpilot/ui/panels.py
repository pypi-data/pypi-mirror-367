"""
Reusable Panel components for consistent UI formatting.
"""

from pathlib import Path
from typing import Any, Dict

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..utils.version import get_version

console = Console()


def show_version_panel() -> None:
    """Display version information panel"""
    console.print(
        Panel(
            f"[bold]AirPilot CLI[/bold]\n"
            f"Version: [green]{get_version()}[/green]\n"
            f"Universal Intelligence Control",
            title="Version Information",
            border_style="blue",
        )
    )


def show_main_help_panel() -> None:
    """Display main help panel"""
    console.print(
        Panel(
            Text.from_markup(
                "[bold blue]AirPilot[/bold blue] - Universal Intelligence Control\n"
                f"Version: [green]{get_version()}[/green]\n\n"
                "Where [cyan].git[/cyan] gives us version control, [cyan].air[/cyan] gives us intelligence control.\n\n"
                "Commands:\n"
                "  [bold]air init[/bold]              Initialize current directory\n"
                "  [bold]air init <project>[/bold]    Create new project with .air\n"
                "  [bold]air init --global[/bold]     Initialize system-level intelligence\n"
                "  [bold]air license[/bold]           Manage AirPilot license\n"
                "  [bold]air license help[/bold]      Complete licensing instructions\n"
                "  [bold]air push[/bold]              Push .air directory to GitHub\n"
                "  [bold]air pull[/bold]              Pull .air directory from GitHub\n"
                "  [bold]air status[/bold]            Check system status\n"
                "  [bold]air sync[/bold]              Premium: Real-time vendor sync\n\n"
                "For premium features, run [dim]air license help[/dim] to get started.\n"
                "Run [dim]air <command> --help[/dim] for more information."
            ),
            title="AirPilot",
            border_style="blue",
        )
    )


def show_success_panel(message: str, title: str = "Success") -> None:
    """Display success panel"""
    console.print(Panel(f"[green]{message}[/green]", title=title, border_style="green"))


def show_error_panel(message: str, title: str = "Error") -> None:
    """Display error panel"""
    console.print(Panel(f"[red]{message}[/red]", title=title, border_style="red"))


def show_license_status_panel(info: Dict[str, Any]) -> None:
    """Display license status panel"""
    plan = info.get("plan", "Free")
    features = info.get("features", [])
    licensed = info.get("licensed", False)

    if licensed:
        status_color = "green"
        status_text = "Active"
    else:
        status_color = "blue"
        status_text = "Free Plan"

    features_text = (
        "\n".join([f"• {feature}" for feature in features])
        if features
        else "• Basic initialization and configuration"
    )

    console.print(
        Panel(
            f"[bold]Plan:[/bold] [{status_color}]{plan}[/{status_color}]\n"
            f"[bold]Status:[/bold] [{status_color}]{status_text}[/{status_color}]\n\n"
            f"[bold]Available Features:[/bold]\n{features_text}",
            title="AirPilot License Status",
            border_style=status_color,
        )
    )


def show_license_group_help_panel() -> None:
    """Display license group command help panel"""
    console.print(
        Panel(
            Text.from_markup(
                "[bold blue]air license[/bold blue] - Manage AirPilot license\n\n"
                "[bold]Usage:[/bold]\n"
                "  [cyan]air license[/cyan]                  Show current license status\n"
                "  [cyan]air license <command>[/cyan]        Run license management command\n\n"
                "[bold]Available Commands:[/bold]\n"
                "  [cyan]install <key>[/cyan]               Install a license key\n"
                "  [cyan]remove[/cyan]                      Remove stored license (revert to free)\n"
                "  [cyan]status[/cyan]                      Show detailed license information\n"
                "  [cyan]help[/cyan]                        Complete licensing instructions\n\n"
                "[bold]Examples:[/bold]\n"
                "  [dim]air license[/dim]                    Check current license status\n"
                "  [dim]air license install <key>[/dim]      Install your purchased license\n"
                "  [dim]air license help[/dim]               Get complete licensing guide\n\n"
                "[bold]Options:[/bold]\n"
                "  [cyan]--help[/cyan]                      Show this help message"
            ),
            title="License Management",
            border_style="blue",
        )
    )


def show_license_install_help_panel() -> None:
    """Display license install command help panel"""
    console.print(
        Panel(
            Text.from_markup(
                "[bold blue]air license install[/bold blue] - Install a license key\n\n"
                "[bold]Usage:[/bold]\n"
                "  [cyan]air license install <key>[/cyan]    Install your AirPilot license key\n\n"
                "[bold]Arguments:[/bold]\n"
                "  [cyan]KEY[/cyan]                         Your AirPilot license key\n\n"
                "[bold]License Key Format:[/bold]\n"
                "  [yellow]airpilot-<plan>-<hash>-<checksum>[/yellow]\n\n"
                "[bold]Examples:[/bold]\n"
                "  [dim]air license install airpilot-poc-ABC123-DEF456[/dim]\n\n"
                "[bold]After Installation:[/bold]\n"
                "• Run [cyan]air license[/cyan] to verify installation\n"
                "• Access premium features like [cyan]air sync[/cyan]\n"
                "• License is stored securely in your home directory\n\n"
                "[bold]Need a License?[/bold]\n"
                "Run [cyan]air license help[/cyan] for complete instructions\n\n"
                "[bold]Options:[/bold]\n"
                "  [cyan]--help[/cyan]                      Show this help message"
            ),
            title="Install License Key",
            border_style="green",
        )
    )


def show_license_remove_help_panel() -> None:
    """Display license remove command help panel"""
    console.print(
        Panel(
            Text.from_markup(
                "[bold blue]air license remove[/bold blue] - Remove stored license\n\n"
                "[bold]Usage:[/bold]\n"
                "  [cyan]air license remove[/cyan]           Remove license and revert to free plan\n\n"
                "[bold]Description:[/bold]\n"
                "Removes your stored AirPilot license and reverts to the free plan.\n"
                "You will be prompted to confirm this action.\n\n"
                "[bold]What happens:[/bold]\n"
                "• License file is securely deleted\n"
                "• Premium features become unavailable\n"
                "• Free features ([cyan]air init[/cyan], [cyan]air license[/cyan]) remain available\n"
                "• You can reinstall a license anytime with [cyan]air license install[/cyan]\n\n"
                "[bold]Confirmation Required:[/bold]\n"
                "You will be asked to confirm before removal\n\n"
                "[bold]Options:[/bold]\n"
                "  [cyan]--help[/cyan]                      Show this help message"
            ),
            title="Remove License",
            border_style="yellow",
        )
    )


def show_license_status_help_panel() -> None:
    """Display license status command help panel"""
    console.print(
        Panel(
            Text.from_markup(
                "[bold blue]air license status[/bold blue] - Show detailed license status\n\n"
                "[bold]Usage:[/bold]\n"
                "  [cyan]air license status[/cyan]           Show comprehensive license information\n\n"
                "[bold]Information Displayed:[/bold]\n"
                "• Current license plan (Free, PoC, Pro, Enterprise)\n"
                "• License status (Active/Inactive)\n"
                "• Available features for your plan\n"
                "• Installation timestamp (if licensed)\n\n"
                "[bold]Free Plan Features:[/bold]\n"
                "• [cyan]air init[/cyan] - Initialize .air directories\n"
                "• [cyan]air init --global[/cyan] - System-level intelligence\n"
                "• [cyan]air license[/cyan] - License management\n\n"
                "[bold]Premium Plan Features:[/bold]\n"
                "• [cyan]air sync[/cyan] - Real-time vendor synchronization\n"
                "• [cyan]air cloud[/cyan] - Cloud backup and sync (coming soon)\n\n"
                "[bold]Options:[/bold]\n"
                "  [cyan]--help[/cyan]                      Show this help message"
            ),
            title="License Status Details",
            border_style="blue",
        )
    )


def show_sync_help_panel() -> None:
    """Display sync command help panel"""
    console.print(
        Panel(
            Text.from_markup(
                "[bold blue]air sync[/bold blue] - Premium: Real-time vendor synchronization\n\n"
                "[bold]Usage:[/bold]\n"
                "  [cyan]air sync[/cyan]                     Start real-time vendor synchronization\n\n"
                "[bold]Description:[/bold]\n"
                "Synchronizes .air directory with all configured AI vendor formats.\n"
                "Monitors your .air directory for changes and automatically updates\n"
                "vendor-specific formats (Claude, Cursor, Cline, GitHub Copilot, etc.)\n\n"
                "[bold]Requirements:[/bold]\n"
                "• Valid AirPilot license ([cyan]air license help[/cyan] for details)\n"
                "• Existing .air directory ([cyan]air init[/cyan] to create)\n"
                "• Configured .airpilot file with vendor settings\n\n"
                "[bold]What it does:[/bold]\n"
                "• Monitors .air/rules/ for changes\n"
                "• Automatically converts to vendor formats\n"
                "• Updates .claude/, .cursor/, .cline/, etc.\n"
                "• Provides real-time sync status\n\n"
                "[bold]Options:[/bold]\n"
                "  [cyan]--help[/cyan]                      Show this help message"
            ),
            title="Premium Sync Command",
            border_style="green",
        )
    )


def show_init_help_panel() -> None:
    """Display init command help panel"""
    console.print(
        Panel(
            Text.from_markup(
                "[bold blue]air init[/bold blue] - Initialize .air intelligence control\n\n"
                "[bold]Usage:[/bold]\n"
                "  [cyan]air init[/cyan]                    Initialize current directory\n"
                "  [cyan]air init <project>[/cyan]          Create new project with .air\n"
                "  [cyan]air init --global[/cyan]           Initialize system-level intelligence\n\n"
                "[bold]Options:[/bold]\n"
                "  [cyan]--global[/cyan]                    Initialize ~/.airpilot/ and ~/.air/\n"
                "  [cyan]--force[/cyan]                     Overwrite existing .air directory (with backup)\n"
                "  [cyan]--help[/cyan]                      Show this help message\n\n"
                "[bold]Examples:[/bold]\n"
                "  [dim]air init[/dim]                      Add .air to current directory\n"
                "  [dim]air init my-project[/dim]           Create new project with intelligence control\n"
                "  [dim]air init --global[/dim]             Set up system-wide AI intelligence\n"
                "  [dim]air init --force[/dim]              Force overwrite existing .air directory\n\n"
                "[bold]What gets created:[/bold]\n"
                "• [cyan].air/[/cyan] directory with standard structure\n"
                "• [cyan].airpilot[/cyan] configuration file\n"
                "• Git repository (if needed)\n"
                "• Domain-specific intelligence organization"
            ),
            title="Initialize Intelligence Control",
            border_style="blue",
        )
    )


def show_license_help_panel() -> None:
    """Display license help panel"""
    console.print(
        Panel(
            Text.from_markup(
                "[bold blue]AirPilot Licensing[/bold blue]\n\n"
                "[bold]Current Status:[/bold] Free Plan (basic features only)\n\n"
                "[bold]Free Features:[/bold]\n"
                "• Initialize .air directories ([cyan]air init[/cyan])\n"
                "• Global intelligence setup ([cyan]air init --global[/cyan])\n"
                "• License management ([cyan]air license[/cyan])\n\n"
                "[bold]Premium Features:[/bold]\n"
                "• Real-time vendor synchronization ([cyan]air sync[/cyan])\n"
                "• Advanced workflow automation\n"
                "• Priority support\n\n"
                "[bold]Getting a License:[/bold]\n"
                "1. Visit: [cyan]https://airpilot.dev/pricing[/cyan]\n"
                "2. Choose your plan and complete purchase\n"
                "3. Install your license: [cyan]air license install <your-key>[/cyan]\n\n"
                "[bold]Environment Variable (Development):[/bold]\n"
                "Set [cyan]AIRPILOT_POC_LICENSE[/cyan] for development access\n\n"
                "Questions? Contact: [cyan]shaneholloman@gmail.com[/cyan]"
            ),
            title="AirPilot Licensing",
            border_style="blue",
        )
    )


def show_sync_panel() -> None:
    """Display sync panel"""
    console.print(
        Panel(
            "[bold blue]Premium Sync Feature[/bold blue]\n\n"
            "[green]Congratulations![/green] You have access to AirPilot's premium sync feature.\n\n"
            "[bold]What sync does:[/bold]\n"
            "• Monitors your .air directory for changes\n"
            "• Automatically syncs rules to vendor-specific formats\n"
            "• Keeps Claude, Cursor, Cline, and other AI tools in perfect sync\n"
            "• Provides real-time updates across your entire AI workflow\n\n"
            "[yellow]Note:[/yellow] Full sync implementation coming in v0.7.0\n"
            "[dim]This preview confirms your license is working correctly.[/dim]",
            title="Premium Sync",
            border_style="green",
        )
    )


def show_scaffolding_panel(air_dir: Path) -> None:
    """Display scaffolding progress panel"""
    console.print(
        Panel(
            f"[bold blue]Creating .air standard structure[/bold blue]\n\n"
            f"[bold]Directory:[/bold] [cyan]{air_dir}[/cyan]\n"
            f"[bold]Standard:[/bold] Universal Intelligence Control\n\n"
            f"[dim]Building comprehensive AI workflow infrastructure...[/dim]",
            title="Scaffolding .air Standard",
            border_style="blue",
        )
    )


def show_git_panel(message: str, title: str = "Git") -> None:
    """Display git operation panel"""
    if "successfully" in message.lower():
        border_style = "green"
        message = f"[green]{message}[/green]"
    elif "warning" in title.lower() or "not found" in message.lower():
        border_style = "yellow"
        message = f"[yellow]{message}[/yellow]"
    else:
        border_style = "blue"
        message = f"[blue]{message}[/blue]"

    console.print(Panel(message, title=title, border_style=border_style))


def show_backup_panel(message: str, title: str = "Backup") -> None:
    """Display backup operation panel"""
    console.print(Panel(f"[blue]{message}[/blue]", title=title, border_style="blue"))


def show_push_help_panel() -> None:
    """Display push command help panel"""
    console.print(
        Panel(
            Text.from_markup(
                "[bold blue]air push[/bold blue] - Push .air directory to GitHub\n\n"
                "[bold]Usage:[/bold]\n"
                "  [cyan]air push[/cyan]                     Push to default repository\n"
                "  [cyan]air push --repo <url>[/cyan]        Push to specific repository\n\n"
                "[bold]Description:[/bold]\n"
                "Pushes your global ~/.air directory to GitHub repository.\n"
                "Works from any directory location on your system.\n\n"
                "[bold]Default Repository:[/bold]\n"
                "• Auto-detects GitHub username from git config\n"
                "• Defaults to [cyan]https://github.com/{username}/.air[/cyan]\n"
                "• Creates repository automatically if GitHub CLI is installed\n\n"
                "[bold]Sync Strategy:[/bold]\n"
                "• Force push (local changes always win)\n"
                "• All files in ~/.air are synchronized\n"
                "• Automatic commit with timestamp\n\n"
                "[bold]Requirements:[/bold]\n"
                "• Git installed and configured\n"
                "• GitHub authentication set up\n"
                "• Existing ~/.air directory ([cyan]air init --global[/cyan] to create)\n\n"
                "[bold]Options:[/bold]\n"
                "  [cyan]--repo <url>[/cyan]                 Override default repository URL\n"
                "  [cyan]--help[/cyan]                       Show this help message"
            ),
            title="AirPilot GitHub Push",
            border_style="blue",
        )
    )


def show_pull_help_panel() -> None:
    """Display pull command help panel"""
    console.print(
        Panel(
            Text.from_markup(
                "[bold blue]air pull[/bold blue] - Pull .air directory from GitHub\n\n"
                "[bold]Usage:[/bold]\n"
                "  [cyan]air pull[/cyan]                     Pull from default repository\n"
                "  [cyan]air pull --repo <url>[/cyan]        Pull from specific repository\n"
                "  [cyan]air pull --force[/cyan]             Force pull and overwrite local changes\n\n"
                "[bold]Description:[/bold]\n"
                "Pulls your global ~/.air directory from GitHub repository.\n"
                "Works from any directory location on your system.\n\n"
                "[bold]Default Repository:[/bold]\n"
                "• Auto-detects GitHub username from git config\n"
                "• Defaults to [cyan]https://github.com/{username}/.air[/cyan]\n"
                "• Clones repository if ~/.air doesn't exist\n\n"
                "[bold]Sync Strategy:[/bold]\n"
                "• Force pull (remote changes always win)\n"
                "• All files in ~/.air are synchronized\n"
                "• Prompts before overwriting local changes\n\n"
                "[bold]First-Time Setup:[/bold]\n"
                "• Automatically clones repository if ~/.air doesn't exist\n"
                "• Sets up git repository structure\n"
                "• Preserves existing files with confirmation\n\n"
                "[bold]Requirements:[/bold]\n"
                "• Git installed and configured\n"
                "• GitHub authentication set up\n"
                "• Existing GitHub repository (create with [cyan]air push[/cyan])\n\n"
                "[bold]Options:[/bold]\n"
                "  [cyan]--repo <url>[/cyan]                 Override default repository URL\n"
                "  [cyan]--force[/cyan]                      Force overwrite local changes\n"
                "  [cyan]--help[/cyan]                       Show this help message"
            ),
            title="AirPilot GitHub Pull",
            border_style="blue",
        )
    )


def show_status_help_panel() -> None:
    """Display status command help panel"""
    console.print(
        Panel(
            Text.from_markup(
                "[bold blue]air status[/bold blue] - Check AirPilot system status\n\n"
                "[bold]Usage:[/bold]\n"
                "  [cyan]air status[/cyan]                   Check general system status\n"
                "  [cyan]air status --github[/cyan]          Check GitHub integration status\n\n"
                "[bold]Description:[/bold]\n"
                "Displays current system status and integration health.\n"
                "Helps diagnose setup issues and provides next steps.\n\n"
                "[bold]GitHub Integration Checks:[/bold]\n"
                "• GitHub CLI installation and authentication\n"
                "• Git configuration (user.name, user.email)\n"
                "• ~/.air directory existence\n"
                "• Git repository setup in ~/.air\n"
                "• GitHub repository existence\n\n"
                "[bold]Status Indicators:[/bold]\n"
                "• [green]✓[/green] Ready and working correctly\n"
                "• [red]✗[/red] Needs attention or setup\n"
                "• [yellow]?[/yellow] Cannot check (prerequisites missing)\n\n"
                "[bold]Next Steps:[/bold]\n"
                "Based on status results, you'll get specific commands to run\n"
                "to complete your setup or fix any issues.\n\n"
                "[bold]Options:[/bold]\n"
                "  [cyan]--github[/cyan]                     Check GitHub integration specifically\n"
                "  [cyan]--help[/cyan]                       Show this help message"
            ),
            title="AirPilot System Status",
            border_style="blue",
        )
    )


def show_github_status_panel(
    checks: list, overall_status: str, next_steps: list
) -> None:
    """Display GitHub integration status panel"""

    # Build the status content
    content_lines = []

    for success, message in checks:
        if success:
            content_lines.append(f"[green]✓[/green] {message}")
        else:
            content_lines.append(f"[red]✗[/red] {message}")

    content = "\n".join(content_lines)

    # Add overall status
    if overall_status == "ready":
        content += "\n\n[bold green]Status: Ready for push/pull operations[/bold green]"
        border_style = "green"
    else:
        content += "\n\n[bold yellow]Status: Setup needed[/bold yellow]"
        border_style = "yellow"

        # Add next steps if any
        if next_steps:
            content += "\n\n[bold]Next steps:[/bold]"
            for step in next_steps:
                content += f"\n• {step}"

    console.print(
        Panel(content, title="AirPilot GitHub Status", border_style=border_style)
    )
