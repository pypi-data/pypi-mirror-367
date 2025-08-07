"""
Configuration management for CNHK MCP server.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration for the CNHK MCP server."""

    def __init__(self, config_path: Optional[str] = None):
        # Check environment variable first
        env_config_path = os.getenv('CNHKMCP_CONFIG_PATH')
        self.config_path = config_path or env_config_path or self._get_default_config_path()
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        # Look for config in multiple locations
        possible_paths = [
            # Current directory
            Path.cwd() / "config" / "cnhk-config.json",
            # User home directory  
            Path.home() / ".cnhkmcp" / "cnhk-config.json",
            # Package directory
            Path(__file__).parent.parent.parent / "config" / "cnhk-config.json"
        ]
        
        for config_file in possible_paths:
            if config_file.exists():
                return str(config_file)
        
        # Return the user home directory path as default (where it should be created)
        return str(Path.home() / ".cnhkmcp" / "cnhk-config.json")

    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
            else:
                logger.warning(f"Configuration file not found: {self.config_path}")
                self._config = {}
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

    def save(self) -> None:
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Saved configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def get_credentials(self) -> Optional[Dict[str, str]]:
        """Get stored credentials."""
        email = self.get('credentials.email')
        password = self.get('credentials.password')
        
        if email and password:
            return {'email': email, 'password': password}
        
        return None

    def set_credentials(self, email: str, password: str) -> None:
        """Set and save credentials."""
        self.set('credentials.email', email)
        self.set('credentials.password', password)
        self.save()

    def get_default_settings(self) -> Dict[str, Any]:
        """Get default simulation settings."""
        return self.get('defaults', {
            'instrumentType': 'EQUITY',
            'region': 'USA',
            'universe': 'TOP3000',
            'delay': 1,
            'decay': 0,
            'neutralization': 'SUBUNIV',
            'truncation': 0.08,
            'testPeriod': 'P1Y6M',
            'unitHandling': 'VERIFY',
            'nanHandling': 'ELIMINATE',
            'language': 'FASTEXPR',
            'visualization': True
        })


# Global configuration manager instance
config_manager = ConfigManager()
