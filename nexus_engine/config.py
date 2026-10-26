"""Configuration management for Nexus Engine."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


DEFAULT_CONFIG_DIR = Path.home() / ".config" / "nexus-engine"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG: Dict[str, Any] = {
    "api_keys": {},
    "channels": {
        "youtube": {
            "backend": "yt-dlp",
            "getyoutubetranscript_api_key": None,
        }
    },
    "browser": {
        "enabled": False,
    },
}


def get_config_dir() -> Path:
    """Get the configuration directory, creating it if necessary."""
    config_dir = Path(os.environ.get("NEXUS_ENGINE_CONFIG_DIR", DEFAULT_CONFIG_DIR))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the configuration file path."""
    return Path(os.environ.get("NEXUS_ENGINE_CONFIG_FILE", get_config_dir() / "config.yaml"))


def load_config() -> Dict[str, Any]:
    """Load configuration from file, merging with defaults."""
    config_file = get_config_file()
    if not config_file.exists():
        return DEFAULT_CONFIG.copy()

    with open(config_file, "r") as f:
        user_config = yaml.safe_load(f) or {}

    # Deep merge with defaults
    return deep_merge(DEFAULT_CONFIG.copy(), user_config)


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_file = get_config_file()
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def get_api_key(key_name: str) -> Optional[str]:
    """Get an API key from config or environment."""
    # First check environment variable
    env_var = f"NEXUS_ENGINE_{key_name.upper()}"
    if env_value := os.environ.get(env_var):
        return env_value

    # Then check config file
    config = load_config()
    return config.get("api_keys", {}).get(key_name)


def set_api_key(key_name: str, value: str) -> None:
    """Set an API key in the configuration."""
    config = load_config()
    if "api_keys" not in config:
        config["api_keys"] = {}
    config["api_keys"][key_name] = value
    save_config(config)


def get_channel_config(channel: str) -> Dict[str, Any]:
    """Get configuration for a specific channel."""
    config = load_config()
    return config.get("channels", {}).get(channel, {})
