"""
.air directory structure scaffolding.
Creates the standard .air directory structure and core files.
"""

from pathlib import Path

from ..ui.panels import show_scaffolding_panel
from .content import (
    create_global_frameworks,
    create_global_prompts,
    create_global_rules,
    create_global_tools,
    create_global_workflows,
)
from .domains import create_domains_structure


def create_air_standard(air_dir: Path, is_project: bool = False) -> None:
    """Create complete .air standard directory structure with scaffolding

    CRITICAL ARCHITECTURE RULE:
    This function ONLY creates content for .air/ directories.
    It must NEVER create .airpilot files inside .air directories.
    .airpilot files must be created separately by create_airpilot_project_config()
    """
    show_scaffolding_panel(air_dir)

    air_dir.mkdir(exist_ok=True)

    # CRITICAL: Do NOT create .airpilot file inside .air directory
    # AirPilot configuration must be separate from .air content
    # The .airpilot file should be in the parent directory or ~/.airpilot/

    # Create main README
    create_air_readme(air_dir, is_project)

    # Create top-level directories and files
    create_global_rules(air_dir)
    create_global_prompts(air_dir)
    create_global_workflows(air_dir)
    create_global_frameworks(air_dir)
    create_global_tools(air_dir)

    # Create domains structure
    create_domains_structure(air_dir)

    # Project-specific additions
    if is_project:
        create_project_context(air_dir)


def create_air_readme(air_dir: Path, is_project: bool) -> None:
    """Create main README for .air directory"""
    scope = "Project" if is_project else "Global"
    readme_content = f"""# {scope} Intelligence Control

This directory follows the universal .air standard for AI intelligence control.

> *Where .git gives us version control, .air gives us intelligence control.*

## The Five Core AI Management Primitives

### 1. Rules
AI behavior guidelines, coding standards, domain constraints

### 2. Prompts
Specific instructions and templates for AI interactions

### 3. Workflows
Process documentation, memory systems, project context

### 4. Frameworks
Project management patterns and organizational methodologies

### 5. Tools
Scripts, MCP configurations, automation, domain-specific utilities

## Structure

- `rules/` - {"Project-level" if is_project else "Global"} rules across all domains
- `prompts/` - {"Project-level" if is_project else "Global"} prompts across all domains
- `workflows/` - {"Project-level" if is_project else "Global"} workflows across all domains
- `frameworks/` - {"Project-level" if is_project else "Global"} framework definitions
- `tools/` - {"Project-level" if is_project else "Global"} tools, scripts, MCP configurations
- `domains/` - Domain-specific intelligence organization
{"- `context/` - Project session state (not synced to vendors)" if is_project else ""}

## Getting Started

1. Add your AI rules to `rules/index.md`
2. Create reusable prompts in `prompts/index.md`
3. Configure workflows in `workflows/index.md`
4. Explore domain-specific organization in `domains/`

## Configuration Hierarchy

Settings are applied in this order (later overrides earlier):

{"1. **Global Base**: `~/.air/` provides universal foundation" if is_project else ""}
{"2. **Domain Specific**: `~/.air/domains/{domain}/` adds domain expertise" if is_project else ""}
{"3. **Project Base**: `/project/.air/` adds project-specific context (this directory)" if is_project else ""}
{"4. **Project Domain**: `/project/.air/domains/{domain}/` provides final overrides" if is_project else ""}
{"" if is_project else "1. **Global Base**: `~/.air/` provides universal foundation (this directory)"}
{"" if is_project else "2. **Domain Specific**: `~/.air/domains/{domain}/` adds domain expertise"}
{"" if is_project else "3. **Project Base**: `/project/.air/` adds project-specific context"}
{"" if is_project else "4. **Project Domain**: `/project/.air/domains/{domain}/` provides final overrides"}

For more information, see: https://github.com/shaneholloman/airpilot
"""

    readme_file = air_dir / "README.md"
    if not readme_file.exists():
        with open(readme_file, "w") as f:
            f.write(readme_content)


def create_project_context(air_dir: Path) -> None:
    """Create project-specific context directory"""
    context_dir = air_dir / "context"
    context_dir.mkdir(exist_ok=True)

    # Active focus file
    active_focus_content = """# Active Focus

Current work focus and priorities.

## Current Sprint

### Primary Objectives
- [Add your current primary objectives here]

### Secondary Goals
- [Add secondary goals here]

### Blockers
- [Add any current blockers here]

## Recent Decisions

### [Date] - Decision Title
- **Context**: Why this decision was needed
- **Decision**: What was decided
- **Impact**: How this affects the project

## Next Steps

### Immediate (This Week)
- [Add immediate next steps]

### Short Term (This Month)
- [Add short-term goals]

### Long Term (This Quarter)
- [Add long-term objectives]
"""

    active_focus_file = context_dir / "active-focus.md"
    if not active_focus_file.exists():
        with open(active_focus_file, "w") as f:
            f.write(active_focus_content)

    # History file
    history_content = """# Project Timeline and Decisions

Project timeline and major decisions.

## Project Overview

### Started
- **Date**: [Project start date]
- **Objective**: [Main project objective]
- **Success Criteria**: [How success will be measured]

## Major Milestones

### [Date] - Milestone Name
- **Achievement**: What was accomplished
- **Impact**: How this moved the project forward
- **Lessons**: What was learned

## Decision Log

### [Date] - Decision Title
- **Context**: Situation requiring decision
- **Options**: Alternatives considered
- **Decision**: What was chosen and why
- **Outcome**: Results of the decision

## Key Learnings

### Technical
- [Technical insights gained]

### Process
- [Process improvements discovered]

### Team
- [Team collaboration learnings]
"""

    history_file = context_dir / "history.md"
    if not history_file.exists():
        with open(history_file, "w") as f:
            f.write(history_content)
