"""
Version management for AirPilot CLI.
Single-source versioning from pyproject.toml.
"""


def get_version() -> str:
    """Get version from installed package metadata."""
    try:
        from importlib.metadata import version

        return version("airpilot")
    except Exception:
        return "0.6.5"  # Fallback version
