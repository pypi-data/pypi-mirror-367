"""
Configuration management for GwaniCLI.
Handles loading and saving user preferences to ~/.config/gwanicli/config.toml
"""

import os
import toml
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for GwaniCLI settings."""

    DEFAULT_CONFIG = {
        'translation': 'en.sahih',
        'cache_ttl': 86400,  # 24 hours in seconds
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Custom path to config file (optional)
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Use XDG config directory or fallback to ~/.config
            config_dir = Path.home() / '.config' / 'gwanicli'
            self.config_path = config_dir / 'config.toml'

        self._config_data = {}
        self._ensure_config_exists()
        self._load_config()

    def _ensure_config_exists(self):
        """Create config directory and file if they don't exist."""
        try:
            # Create config directory
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Create config file with defaults if it doesn't exist
            if not self.config_path.exists():
                logger.info(f"Creating new config file at {self.config_path}")
                self._save_config(self.DEFAULT_CONFIG)

        except OSError as e:
            logger.error(f"Failed to create config directory: {e}")
            raise

    def _load_config(self):
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config_data = toml.load(f)

            # Merge with defaults to ensure all keys exist
            for key, default_value in self.DEFAULT_CONFIG.items():
                if key not in self._config_data:
                    self._config_data[key] = default_value

            logger.debug(f"Loaded config from {self.config_path}")

        except FileNotFoundError:
            logger.warning(
                f"Config file not found at {self.config_path}, using defaults")
            self._config_data = self.DEFAULT_CONFIG.copy()
        except toml.TomlDecodeError as e:
            logger.error(f"Invalid TOML in config file: {e}")
            logger.warning("Using default configuration")
            self._config_data = self.DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._config_data = self.DEFAULT_CONFIG.copy()

    def _save_config(self, config_data: Optional[Dict[str, Any]] = None):
        """Save configuration to file."""
        data_to_save = config_data or self._config_data

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                toml.dump(data_to_save, f)
            logger.debug(f"Saved config to {self.config_path}")

        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key doesn't exist

        Returns:
            Configuration value or default
        """
        return self._config_data.get(key, default)

    def set(self, key: str, value: Any):
        """
        Set a configuration value and save to file.

        Args:
            key: Configuration key
            value: Value to set
        """
        self._config_data[key] = value
        self._save_config()
        logger.info(f"Updated config: {key} = {value}")

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            Dictionary of all configuration values
        """
        return self._config_data.copy()

    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self._config_data = self.DEFAULT_CONFIG.copy()
        self._save_config()
        logger.info("Reset configuration to defaults")

    def reload(self):
        """Reload configuration from file."""
        self._load_config()
        logger.info("Reloaded configuration from file")

    def get_config_path(self) -> str:
        """Get the path to the configuration file."""
        return str(self.config_path)

    def validate_config(self) -> bool:
        """
        Validate current configuration values.

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate translation format
            translation = self.get('translation', '')
            if not isinstance(translation, str) or not translation:
                logger.error("Invalid translation setting")
                return False

            # Validate cache_ttl
            cache_ttl = self.get('cache_ttl', 0)
            if not isinstance(cache_ttl, int) or cache_ttl < 0:
                logger.error("Invalid cache_ttl setting")
                return False

            return True

        except Exception as e:
            logger.error(f"Config validation failed: {e}")
            return False

    def __repr__(self):
        return f"Config(path='{self.config_path}', data={self._config_data})"
