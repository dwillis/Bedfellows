"""Tests for configuration module."""

import os
import tempfile
from pathlib import Path

import pytest

from bedfellows.config import Config


def test_default_config():
    """Test default configuration values."""
    config = Config(load_env=False)

    assert config["database_type"] == "sqlite"
    assert config["sqlite_path"] == "data/bedfellows.db"
    assert config["fec_bulk_data_url"] == "https://www.fec.gov/files/bulk-downloads/"


def test_get_database_config_sqlite():
    """Test SQLite database configuration."""
    config = Config(load_env=False)
    db_config = config.get_database_config()

    assert db_config["type"] == "sqlite"
    assert "database" in db_config


def test_get_score_weights():
    """Test score weights retrieval."""
    config = Config(load_env=False)
    weights = config.get_score_weights()

    assert "exclusivity" in weights
    assert "report_type" in weights
    assert "periodicity" in weights
    assert "maxed_out" in weights
    assert "length" in weights
    assert "race_focus" in weights

    # All default weights should be 1.0
    for weight in weights.values():
        assert weight == 1.0


def test_config_from_env():
    """Test configuration from environment variables."""
    # Set environment variables
    os.environ["DATABASE_TYPE"] = "mysql"
    os.environ["MYSQL_HOST"] = "testhost"
    os.environ["MYSQL_PORT"] = "3307"

    config = Config(load_env=True)

    assert config["database_type"] == "mysql"
    assert config["mysql_host"] == "testhost"
    assert config["mysql_port"] == 3307

    # Clean up
    del os.environ["DATABASE_TYPE"]
    del os.environ["MYSQL_HOST"]
    del os.environ["MYSQL_PORT"]


def test_config_from_file():
    """Test configuration from INI file."""
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write("""[database]
type = postgresql
postgres_host = pghost
postgres_port = 5433

[fec]
data_dir = /tmp/data
""")
        config_file = f.name

    try:
        config = Config(config_file=config_file, load_env=False)

        assert config["database_type"] == "postgresql"
        assert config["postgres_host"] == "pghost"
        assert config["postgres_port"] == 5433
        assert config["data_dir"] == "/tmp/data"
    finally:
        os.unlink(config_file)
