"""
Content and structure builders for AirPilot.
"""

from .config import (
    create_airpilot_global_config,
    create_airpilot_project_config,
)
from .content import create_global_prompts, create_global_rules, create_global_workflows
from .domains import create_domains_structure
from .scaffold import create_air_standard

__all__ = [
    "create_airpilot_global_config",
    "create_airpilot_project_config",
    "create_air_standard",
    "create_global_rules",
    "create_global_prompts",
    "create_global_workflows",
    "create_domains_structure",
]
