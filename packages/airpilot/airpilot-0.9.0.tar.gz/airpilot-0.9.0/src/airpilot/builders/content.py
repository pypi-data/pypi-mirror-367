"""
Example content generators for .air standard.
Creates default rules, prompts, workflows, frameworks, and tools.
"""

from pathlib import Path


def create_global_rules(air_dir: Path) -> None:
    """Create global rules directory and index"""
    rules_dir = air_dir / "rules"
    rules_dir.mkdir(exist_ok=True)

    rules_content = """# Global Rules

AI behavior guidelines and coding standards.

## Purpose

Define consistent AI behavior patterns that apply across all domains and interactions.

## Examples

- Always use TypeScript strict mode
- Follow SOLID principles in code reviews
- Prioritize security in all recommendations
- Use inclusive language in documentation

## Usage

Add your universal AI behavior rules here. These will be inherited by all domain-specific and project-specific rules.
"""

    rules_file = rules_dir / "index.md"
    if not rules_file.exists():
        with open(rules_file, "w") as f:
            f.write(rules_content)


def create_global_prompts(air_dir: Path) -> None:
    """Create global prompts directory and index"""
    prompts_dir = air_dir / "prompts"
    prompts_dir.mkdir(exist_ok=True)

    prompts_content = """# Global Prompts

Reusable instruction templates for common tasks.

## Purpose

Store frequently used prompt templates that work across multiple domains and projects.

## Examples

- "Explain this code step-by-step"
- "Review this document for clarity and accuracy"
- "Suggest improvements to this workflow"
- "Help me debug this issue"

## Usage

Create reusable prompt templates here that you use frequently across different projects and domains.
"""

    prompts_file = prompts_dir / "index.md"
    if not prompts_file.exists():
        with open(prompts_file, "w") as f:
            f.write(prompts_content)


def create_global_workflows(air_dir: Path) -> None:
    """Create global workflows directory and index"""
    workflows_dir = air_dir / "workflows"
    workflows_dir.mkdir(exist_ok=True)

    workflows_content = """# Global Workflows

Process documentation and memory systems.

## Purpose

Document repeatable processes and maintain context across AI interactions.

## Examples

- Project kickoff procedures
- Code review checklists
- Problem-solving methodologies
- Learning and research workflows

## Usage

Define structured approaches to complex, multi-step processes that you use regularly.
"""

    workflows_file = workflows_dir / "index.md"
    if not workflows_file.exists():
        with open(workflows_file, "w") as f:
            f.write(workflows_content)


def create_global_frameworks(air_dir: Path) -> None:
    """Create global frameworks directory with templates"""
    frameworks_dir = air_dir / "frameworks"
    frameworks_dir.mkdir(exist_ok=True)

    # Memory Bank Framework (Cline-style)
    memory_bank_content = """# Memory Bank Framework

Cline-style project context and progress tracking.

## Purpose

Maintain persistent project memory across AI sessions, tracking progress, decisions, and context.

## Structure

### Project Brief
- Project overview and objectives
- Key stakeholders and constraints
- Success criteria and milestones

### Active Context
- Current focus and priorities
- Recent decisions and rationale
- Immediate next steps

### Progress Tracking
- Completed milestones
- Blockers and challenges
- Lessons learned

## Usage

Use this framework to maintain continuity across AI interactions, ensuring context is preserved and progress is tracked systematically.
"""

    memory_bank_file = frameworks_dir / "memory-bank.md"
    if not memory_bank_file.exists():
        with open(memory_bank_file, "w") as f:
            f.write(memory_bank_content)

    # Conversation Framework (Claude-style)
    conversation_content = """# Conversation Framework

Claude-style session history and knowledge base.

## Purpose

Maintain conversational context and build cumulative knowledge across AI interactions.

## Structure

### Session History
- Previous conversation summaries
- Key insights and discoveries
- Decision points and outcomes

### Knowledge Base
- Domain-specific learnings
- Best practices discovered
- Common patterns and solutions

### Context Threads
- Ongoing discussion topics
- Related concepts and connections
- Future exploration areas

## Usage

Use this framework to build conversational intelligence that improves over time and maintains rich context.
"""

    conversation_file = frameworks_dir / "conversation.md"
    if not conversation_file.exists():
        with open(conversation_file, "w") as f:
            f.write(conversation_content)

    # Workflow Framework (Windsurf-style)
    workflow_content = """# Workflow Framework

Windsurf-style memories, tasks, and planning.

## Purpose

Organize work into structured workflows with memory, task management, and strategic planning.

## Structure

### Memories
- Important context and decisions
- Patterns and insights
- Historical reference points

### Tasks
- Current work items
- Priorities and dependencies
- Progress and status

### Planning
- Strategic objectives
- Resource allocation
- Timeline and milestones

## Usage

Use this framework for structured project management and strategic thinking with AI assistance.
"""

    workflow_file = frameworks_dir / "workflow.md"
    if not workflow_file.exists():
        with open(workflow_file, "w") as f:
            f.write(workflow_content)


def create_global_tools(air_dir: Path) -> None:
    """Create global tools directory"""
    tools_dir = air_dir / "tools"
    tools_dir.mkdir(exist_ok=True)

    tools_content = """# Global Tools

Scripts, configurations, and automation utilities.

## Purpose

Store reusable tools, scripts, and configurations that enhance AI workflows across all domains.

## Types

### Scripts
- Automation scripts
- Utility functions
- Workflow helpers

### MCP Configurations
- Model Context Protocol setups
- Integration configurations
- Custom tool definitions

### Utilities
- Data processing tools
- File management scripts
- Development utilities

## Usage

Place executable tools and configurations here that you use across multiple projects and domains.
"""

    tools_file = tools_dir / "README.md"
    if not tools_file.exists():
        with open(tools_file, "w") as f:
            f.write(tools_content)
