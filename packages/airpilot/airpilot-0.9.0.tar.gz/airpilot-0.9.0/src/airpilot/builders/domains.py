"""
Domain-specific builders for .air standard.
Creates domain structure and domain-specific content.
"""

from pathlib import Path


def create_domains_structure(air_dir: Path) -> None:
    """Create domains structure with software, health, and legal domains"""
    domains_dir = air_dir / "domains"
    domains_dir.mkdir(exist_ok=True)

    # Domains README
    domains_readme = """# Domains

Domain-specific intelligence organization.

## Purpose

Organize AI intelligence by life and work domains, each containing the complete set of AI management primitives.

## Available Domains

- **software/** - Development, coding, technical work
- **health/** - Medical research, wellness, fitness
- **legal/** - Contracts, compliance, legal research

## Domain Structure

Each domain contains:
- `rules/` - Domain-specific AI behavior guidelines
- `prompts/` - Domain-specific instruction templates
- `workflows/` - Domain-specific process documentation
- `frameworks/` - Domain-specific organizational patterns
- `tools/` - Domain-specific scripts and configurations

## Adding Domains

Create new domain directories following the same structure for any area where you need specialized AI intelligence.
"""

    domains_readme_file = domains_dir / "README.md"
    if not domains_readme_file.exists():
        with open(domains_readme_file, "w") as f:
            f.write(domains_readme)

    # Create each domain
    create_software_domain(domains_dir)
    create_health_domain(domains_dir)
    create_legal_domain(domains_dir)


def create_software_domain(domains_dir: Path) -> None:
    """Create software domain with complete structure"""
    software_dir = domains_dir / "software"
    software_dir.mkdir(exist_ok=True)

    # Software domain README
    software_readme = """# Software Domain

Development, coding, and technical work intelligence.

## Purpose

Specialized AI intelligence for software development, coding standards, technical documentation, and engineering workflows.

## Focus Areas

- Code quality and best practices
- Architecture and design patterns
- Development workflows and tooling
- Technical documentation
- Code review and debugging

## Structure

- `rules/` - Development AI behavior and coding standards
- `prompts/` - Development instruction templates
- `workflows/` - Development process documentation
- `frameworks/` - Development framework definitions
- `tools/` - Development scripts and configurations
"""

    software_readme_file = software_dir / "README.md"
    if not software_readme_file.exists():
        with open(software_readme_file, "w") as f:
            f.write(software_readme)

    # Create software domain subdirectories
    create_domain_subdirectory(
        software_dir, "rules", "Development AI behavior and coding standards."
    )
    create_domain_subdirectory(
        software_dir, "prompts", "Development instruction templates."
    )
    create_domain_subdirectory(
        software_dir, "workflows", "Development process documentation."
    )
    create_domain_subdirectory(
        software_dir, "frameworks", "Development framework definitions."
    )
    create_domain_subdirectory(
        software_dir, "tools", "Development scripts and configurations.", is_tools=True
    )


def create_health_domain(domains_dir: Path) -> None:
    """Create health domain with complete structure"""
    health_dir = domains_dir / "health"
    health_dir.mkdir(exist_ok=True)

    # Health domain README
    health_readme = """# Health Domain

Medical research, wellness, and fitness intelligence.

## Purpose

Specialized AI intelligence for health-related activities, medical research, wellness planning, and fitness optimization.

## Focus Areas

- Medical research and literature review
- Wellness and preventive care
- Fitness and nutrition planning
- Health data analysis
- Privacy and HIPAA compliance

## Structure

- `rules/` - Medical AI behavior and privacy compliance
- `prompts/` - Medical instruction templates
- `workflows/` - Medical process documentation
- `frameworks/` - Medical framework definitions
- `tools/` - Medical scripts and configurations
"""

    health_readme_file = health_dir / "README.md"
    if not health_readme_file.exists():
        with open(health_readme_file, "w") as f:
            f.write(health_readme)

    # Create health domain subdirectories
    create_domain_subdirectory(
        health_dir, "rules", "Medical AI behavior and privacy compliance."
    )
    create_domain_subdirectory(health_dir, "prompts", "Medical instruction templates.")
    create_domain_subdirectory(
        health_dir, "workflows", "Medical process documentation."
    )
    create_domain_subdirectory(
        health_dir, "frameworks", "Medical framework definitions."
    )
    create_domain_subdirectory(
        health_dir, "tools", "Medical scripts and configurations.", is_tools=True
    )


def create_legal_domain(domains_dir: Path) -> None:
    """Create legal domain with complete structure"""
    legal_dir = domains_dir / "legal"
    legal_dir.mkdir(exist_ok=True)

    # Legal domain README
    legal_readme = """# Legal Domain

Contracts, compliance, and legal research intelligence.

## Purpose

Specialized AI intelligence for legal work, contract analysis, compliance requirements, and legal research.

## Focus Areas

- Contract review and analysis
- Regulatory compliance
- Legal research and precedent
- Risk assessment
- Privacy and data protection

## Structure

- `rules/` - Legal AI behavior and compliance
- `prompts/` - Contract analysis and legal templates
- `workflows/` - Legal process documentation
- `frameworks/` - Legal framework definitions
- `tools/` - Legal scripts and configurations
"""

    legal_readme_file = legal_dir / "README.md"
    if not legal_readme_file.exists():
        with open(legal_readme_file, "w") as f:
            f.write(legal_readme)

    # Create legal domain subdirectories
    create_domain_subdirectory(legal_dir, "rules", "Legal AI behavior and compliance.")
    create_domain_subdirectory(
        legal_dir, "prompts", "Contract analysis and legal templates."
    )
    create_domain_subdirectory(legal_dir, "workflows", "Legal process documentation.")
    create_domain_subdirectory(legal_dir, "frameworks", "Legal framework definitions.")
    create_domain_subdirectory(
        legal_dir, "tools", "Legal scripts and configurations.", is_tools=True
    )


def create_domain_subdirectory(
    domain_dir: Path, subdir_name: str, description: str, is_tools: bool = False
) -> None:
    """Create a domain subdirectory with appropriate content"""
    subdir = domain_dir / subdir_name
    subdir.mkdir(exist_ok=True)

    # Capitalize first letter for title
    title = subdir_name.capitalize()
    domain_name = domain_dir.name.capitalize()

    content = f"""# {domain_name} Domain {title}

{description}

## Purpose

Domain-specific {subdir_name} for {domain_dir.name} intelligence and AI interactions.

## Usage

Add your {domain_dir.name}-specific {subdir_name} here to customize AI behavior for this domain.
"""

    filename = "README.md" if is_tools else "index.md"
    content_file = subdir / filename
    if not content_file.exists():
        with open(content_file, "w") as f:
            f.write(content)
