"""Configuration management for ics_calendar_utils with environment variable support."""

import os
import re
from pathlib import Path
from typing import Any

import yaml


class Config:
    """Configuration manager with environment variable substitution."""

    def __init__(self, config_path: Path | None = None):
        """Initialize configuration.

        Args:
            config_path: Path to configuration file. If None, looks for config.yaml
                        in the project's config directory.
        """
        # Load environment variables first
        self._load_environment()

        if config_path is None:
            # Look for config.yaml in project's config directory
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"

        self.config_path = Path(config_path)
        self._config: dict[str, Any] = self._load_config()

    def _load_environment(self) -> None:
        """Load environment variables using hierarchical .env file loading."""
        try:
            from dotenv import load_dotenv

            # Load shared environment first (if exists)
            parent_env = Path(__file__).parent.parent.parent.parent / ".env"
            if parent_env.exists():
                load_dotenv(parent_env, verbose=False)
                print(f"✅ Loaded shared environment from: {parent_env}")

            # Load project-specific environment second (overrides shared)
            project_env = Path(__file__).parent.parent.parent / ".env"
            if project_env.exists():
                load_dotenv(project_env, override=True, verbose=False)
                print(f"✅ Loaded project environment from: {project_env}")

        except ImportError:
            print(
                "⚠️  python-dotenv not installed. Install with: poetry add python-dotenv"
            )

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file with environment variable substitution."""
        if not self.config_path.exists():
            return self._default_config()

        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f) or {}

            # Apply environment variable substitution
            return self._substitute_env_vars(config)
        except (yaml.YAMLError, OSError) as e:
            print(f"Warning: Could not load config from {self.config_path}: {e}")
            return self._default_config()

    def _substitute_env_vars(self, obj: Any) -> Any:
        """Recursively substitute environment variables in configuration."""
        if isinstance(obj, dict):
            return {k: self._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            # Replace ${VAR_NAME} with environment variable value
            def replacer(match):
                var_name = match.group(1)
                return os.environ.get(var_name, match.group(0))

            return re.sub(r"\$\{([^}]+)\}", replacer, obj)
        else:
            return obj

    def _default_config(self) -> dict[str, Any]:
        """Return default configuration."""
        return {
            "app": {
                "name": "ics_calendar_utils",
                "version": "0.1.0",
                "debug": False,
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "settings": {
                "timeout": 30,
                "retry_count": 3,
                "batch_size": 100,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., 'app.name', 'logging.level')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., 'app.debug')
            value: Value to set
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self) -> None:
        """Save current configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False, indent=2)


# Global config instance
config = Config()
