"""Tests for CLI commands."""

from click.testing import CliRunner

from nexus_engine.cli import main


def test_cli_help():
    """Test CLI help output."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Nexus Engine" in result.output
    assert "configure" in result.output
    assert "doctor" in result.output


def test_cli_version():
    """Test CLI version output."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_doctor_command():
    """Test doctor command runs without error."""
    runner = CliRunner()
    result = runner.invoke(main, ["doctor"])
    assert result.exit_code == 0
    assert "Nexus Engine Doctor" in result.output
    assert "Config file:" in result.output


def test_configure_list():
    """Test configure --list."""
    runner = CliRunner()
    result = runner.invoke(main, ["configure", "--list"])
    assert result.exit_code == 0


def test_configure_set_key():
    """Test configure key value."""
    runner = CliRunner()
    result = runner.invoke(main, ["configure", "test_key", "test_value"])
    assert result.exit_code == 0
    assert "Set test_key" in result.output
