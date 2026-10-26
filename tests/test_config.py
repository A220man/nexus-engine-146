"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest

from nexus_engine.config import (
    DEFAULT_CONFIG,
    deep_merge,
    get_api_key,
    get_config_dir,
    get_config_file,
    load_config,
    save_config,
    set_api_key,
)


def test_deep_merge():
    """Test deep merge functionality."""
    base = {"a": 1, "b": {"x": 10, "y": 20}}
    override = {"b": {"x": 100}, "c": 3}
    result = deep_merge(base, override)
    assert result == {"a": 1, "b": {"x": 100, "y": 20}, "c": 3}


def test_load_config_defaults(monkeypatch):
    """Test loading config when file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_file = config_dir / "config.yaml"
        monkeypatch.setenv("NEXUS_ENGINE_CONFIG_DIR", str(config_dir))
        monkeypatch.setenv("NEXUS_ENGINE_CONFIG_FILE", str(config_file))

        config = load_config()
        assert config == DEFAULT_CONFIG


def test_save_and_load_config(monkeypatch):
    """Test saving and loading config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_file = config_dir / "config.yaml"
        monkeypatch.setenv("NEXUS_ENGINE_CONFIG_DIR", str(config_dir))
        monkeypatch.setenv("NEXUS_ENGINE_CONFIG_FILE", str(config_file))

        # Save a custom config
        custom_config = {
            "api_keys": {"test_key": "test_value"},
            "channels": {"youtube": {"backend": "api"}},
        }
        save_config(custom_config)

        # Load it back
        loaded = load_config()
        assert loaded["api_keys"]["test_key"] == "test_value"
        assert loaded["channels"]["youtube"]["backend"] == "api"
        # Defaults should be merged in
        assert "browser" in loaded


def test_set_and_get_api_key(monkeypatch):
    """Test setting and getting API keys."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_file = config_dir / "config.yaml"
        monkeypatch.setenv("NEXUS_ENGINE_CONFIG_DIR", str(config_dir))
        monkeypatch.setenv("NEXUS_ENGINE_CONFIG_FILE", str(config_file))

        set_api_key("test_key", "test_value")
        assert get_api_key("test_key") == "test_value"

        # Test environment variable override
        monkeypatch.setenv("NEXUS_ENGINE_TEST_KEY", "env_value")
        assert get_api_key("test_key") == "env_value"


def test_get_config_dir_creates_directory(monkeypatch):
    """Test that get_config_dir creates the directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "nexus-engine"
        monkeypatch.setenv("NEXUS_ENGINE_CONFIG_DIR", str(config_dir))

        result = get_config_dir()
        assert result == config_dir
        assert config_dir.exists()
