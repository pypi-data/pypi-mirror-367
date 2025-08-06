"""License validation system for AirPilot CLI."""

import functools
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List


class LicenseManager:
    """Manages license validation and storage for AirPilot CLI."""

    def __init__(self) -> None:
        """Initialize the license manager."""
        self.config_file = Path.home() / ".airpilot"

        # PoC license key - loaded from environment variable
        self.poc_license_key = os.getenv(
            "AIRPILOT_POC_LICENSE", "airpilot-poc-demo2025-7c57b476"
        )

        # Plan feature mappings
        self.plan_features = {
            "free": ["init", "init_global", "init_project"],
            "poc": ["init", "init_global", "init_project", "sync", "cloud"],
            "pro": [
                "init",
                "init_global",
                "init_project",
                "sync",
                "cloud",
                "analytics",
                "backup",
            ],
            "enterprise": [
                "init",
                "init_global",
                "init_project",
                "sync",
                "cloud",
                "analytics",
                "backup",
                "teams",
                "sso",
            ],
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load license configuration from disk."""
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file) as f:
                data = json.load(f)
                return dict(data) if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save license configuration to disk."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
            # Make config readable only by owner
            self.config_file.chmod(0o600)
        except OSError as e:
            raise RuntimeError(f"Failed to save license config: {e}") from e

    def _validate_key_format(self, license_key: str) -> bool:
        """Validate license key format: airpilot-{plan}-{hash}-{checksum}"""
        parts = license_key.split("-")

        if len(parts) != 4:
            return False

        prefix, plan, hash_part, checksum = parts

        # Check prefix
        if prefix != "airpilot":
            return False

        # Check plan is valid
        if plan not in self.plan_features:
            return False

        # Check hash part (at least 8 chars)
        if len(hash_part) < 8:
            return False

        # Validate checksum (8 chars)
        if len(checksum) != 8:
            return False

        # Verify checksum calculation
        expected_checksum = hashlib.md5(
            f"{prefix}-{plan}-{hash_part}".encode()
        ).hexdigest()[:8]
        return checksum == expected_checksum

    def _validate_license(self, license_key: str) -> bool:
        """Validate license key against current validation method."""
        # PoC: Check against hardcoded key
        if license_key == self.poc_license_key:
            return True

        # Also validate format for future keys
        return self._validate_key_format(license_key)

    def _extract_plan_from_key(self, license_key: str) -> str:
        """Extract plan type from license key."""
        try:
            return license_key.split("-")[1]
        except IndexError:
            return "free"

    def install_license(self, license_key: str) -> bool:
        """Install and validate a license key."""
        if not self._validate_license(license_key):
            return False

        plan = self._extract_plan_from_key(license_key)
        features = self.plan_features.get(plan, self.plan_features["free"])

        config = {
            "license_key": license_key,
            "plan": plan,
            "features": features,
            "validated_at": time.time(),
            "installed_at": time.time(),
        }

        self._save_config(config)
        return True

    def remove_license(self) -> bool:
        """Remove stored license and revert to free plan."""
        if self.config_file.exists():
            try:
                self.config_file.unlink()
                return True
            except OSError:
                return False
        return True

    def get_current_plan(self) -> str:
        """Get current license plan."""
        config = self._load_config()
        plan = config.get("plan", "free")
        return str(plan)

    def get_features(self) -> List[str]:
        """Get available features for current plan."""
        config = self._load_config()
        features = config.get("features", self.plan_features["free"])
        return (
            list(features) if isinstance(features, list) else self.plan_features["free"]
        )

    def has_feature(self, feature: str) -> bool:
        """Check if current plan includes a specific feature."""
        return feature in self.get_features()

    def is_licensed(self) -> bool:
        """Check if user has any valid license (not free plan)."""
        return self.get_current_plan() != "free"

    def get_license_info(self) -> Dict[str, Any]:
        """Get complete license information."""
        config = self._load_config()

        if not config:
            return {
                "plan": "free",
                "features": self.plan_features["free"],
                "licensed": False,
            }

        return {
            "plan": config.get("plan", "free"),
            "features": config.get("features", self.plan_features["free"]),
            "licensed": config.get("plan", "free") != "free",
            "installed_at": config.get("installed_at"),
            "validated_at": config.get("validated_at"),
        }

    def generate_poc_key(self) -> str:
        """Generate the PoC license key for distribution."""
        return self.poc_license_key


def require_license(feature: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to require license for premium features."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            license_manager = LicenseManager()

            if not license_manager.has_feature(feature):
                from rich.console import Console
                from rich.panel import Panel

                console = Console()
                current_plan = license_manager.get_current_plan()
                available_features = ", ".join(license_manager.get_features())

                console.print(
                    Panel(
                        f"[red]Premium Feature Required[/red]\n\n"
                        f"The '{feature}' feature requires a valid AirPilot license.\n\n"
                        f"Current plan: {current_plan.upper()}\n"
                        f"Available features: {available_features}\n\n"
                        f"To get a license:\n"
                        f"1. Email: shaneholloman@gmail.com\n"
                        f"2. Subject: AirPilot License Request\n"
                        f"3. Include your name and use case\n\n"
                        f"Once you have your key:\n"
                        f"air license install <your-license-key>",
                        title="License Required",
                        border_style="red",
                    )
                )
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_license_manager() -> LicenseManager:
    """Get a LicenseManager instance."""
    return LicenseManager()
