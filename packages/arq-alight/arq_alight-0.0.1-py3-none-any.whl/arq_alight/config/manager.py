"""Configuration manager for Arq Alight."""

import json
from pathlib import Path

from arq_alight.core.exceptions import ConfigError


class ConfigManager:
    """Manages local configuration for Arq Alight."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize configuration manager.

        Args:
            config_dir: Directory to store config files. Defaults to ~/.alight
        """
        self.config_dir = config_dir or Path.home() / ".alight"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {
                "version": 1,
                "computer_names": {},
                "default_backup_paths": {},
            }

        try:
            with open(self.config_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise ConfigError(f"Failed to load config: {e}") from e

    def _save_config(self, config: dict) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except OSError as e:
            raise ConfigError(f"Failed to save config: {e}") from e

    def get_computer_name(self, uuid: str) -> str:
        """Get friendly name for computer UUID.

        Args:
            uuid: Computer UUID

        Returns:
            Friendly name if set, otherwise returns the UUID
        """
        config = self._load_config()
        return config.get("computer_names", {}).get(uuid, uuid)

    def set_computer_name(self, uuid: str, name: str) -> None:
        """Set friendly name for computer UUID.

        Args:
            uuid: Computer UUID
            name: Friendly name to set
        """
        config = self._load_config()
        if "computer_names" not in config:
            config["computer_names"] = {}
        config["computer_names"][uuid] = name
        self._save_config(config)

    def remove_computer_name(self, uuid: str) -> None:
        """Remove friendly name for computer UUID.

        Args:
            uuid: Computer UUID
        """
        config = self._load_config()
        if "computer_names" in config and uuid in config["computer_names"]:
            del config["computer_names"][uuid]
            self._save_config(config)

    def list_computer_names(self) -> dict[str, str]:
        """Get all UUID to name mappings.

        Returns:
            Dictionary mapping UUIDs to friendly names
        """
        config = self._load_config()
        return config.get("computer_names", {}).copy()

    def get_default_backup_path(self, name: str) -> str | None:
        """Get default backup path by name.

        Args:
            name: Name of the backup path configuration

        Returns:
            S3 path if configured, None otherwise
        """
        config = self._load_config()
        return config.get("default_backup_paths", {}).get(name)

    def set_default_backup_path(self, name: str, path: str) -> None:
        """Set default backup path.

        Args:
            name: Name for this backup path configuration
            path: S3 path (e.g., s3://bucket/path)
        """
        config = self._load_config()
        if "default_backup_paths" not in config:
            config["default_backup_paths"] = {}
        config["default_backup_paths"][name] = path
        self._save_config(config)

    def list_default_backup_paths(self) -> dict[str, str]:
        """Get all default backup paths.

        Returns:
            Dictionary mapping names to S3 paths
        """
        config = self._load_config()
        return config.get("default_backup_paths", {}).copy()
